# SKILL: Data Enrichment + Website Verification + Image Extraction
**Skill ID:** SKILL-04  
**Version:** 1.0  
**Depends on:** SKILL-03 → `data/clean_listings.csv`  
**Outputs to:** SKILL-05 (site build)  
**Portable to:** Python 3.10+ with Anthropic API key

---

## PURPOSE
This skill covers Frey Chu's Steps 3-6: crawl each listing's website, extract structured data, enrich with AI, and pull verified images. Output is a fully enriched dataset ready for site generation.

---

## INPUTS
- `data/clean_listings.csv`
- `ANTHROPIC_API_KEY` env var
- `niche_report.json` (for niche-specific field extraction)

## OUTPUTS
- `data/enriched_listings.csv`
- `images/{place_id}/photo_N.jpg` (up to 5 per listing)

---

## SETUP
```bash
pip install crawl4ai anthropic pandas requests beautifulsoup4 pillow python-dotenv
crawl4ai-setup
```

---

## STEP 3 — WEBSITE VERIFICATION (Crawl4AI)

```python
# scripts/03_verify.py
import asyncio
import pandas as pd
import json
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

async def verify_websites(input_path="data/clean_listings.csv",
                          output_path="data/verified_listings.csv"):
    df = pd.read_csv(input_path)
    url_col = next((c for c in ["site", "website", "url"] if c in df.columns), None)

    if not url_col:
        print("No website column found — skipping verification")
        df.to_csv(output_path, index=False)
        return

    browser_config = BrowserConfig(headless=True, viewport_width=1280)
    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        page_timeout=15000,      # 15 second timeout
        wait_for="domcontentloaded"
    )

    verified_data = {}

    async with AsyncWebCrawler(config=browser_config) as crawler:
        urls_with_ids = [
            (row[url_col], row.get("place_id", row.get("slug", str(i))))
            for i, (_, row) in enumerate(df.iterrows())
            if pd.notna(row.get(url_col))
        ]

        print(f"Verifying {len(urls_with_ids)} websites...")

        for i, (url, record_id) in enumerate(urls_with_ids):
            try:
                result = await crawler.arun(url=url, config=run_config)
                verified_data[str(record_id)] = {
                    "website_live": result.status_code == 200,
                    "site_description": result.markdown[:800] if result.markdown else "",
                    "site_raw": result.markdown[:3000] if result.markdown else ""
                }
                status = "OK" if result.status_code == 200 else f"HTTP {result.status_code}"
                print(f"  [{i+1}/{len(urls_with_ids)}] {status}: {url[:60]}")
            except Exception as e:
                verified_data[str(record_id)] = {
                    "website_live": False,
                    "site_description": "",
                    "site_raw": ""
                }
                print(f"  [{i+1}/{len(urls_with_ids)}] ERROR: {url[:60]} — {str(e)[:40]}")

    # Merge back
    id_col = "place_id" if "place_id" in df.columns else "slug"
    df["website_live"] = df[id_col].astype(str).map(
        lambda x: verified_data.get(x, {}).get("website_live", False)
    )
    df["site_description"] = df[id_col].astype(str).map(
        lambda x: verified_data.get(x, {}).get("site_description", "")
    )
    df["site_raw"] = df[id_col].astype(str).map(
        lambda x: verified_data.get(x, {}).get("site_raw", "")
    )

    # Keep only live sites (or those without websites — they stay in)
    df_live = df[(df["website_live"] == True) | (df[url_col].isna())]
    df_live.to_csv(output_path, index=False)
    print(f"\nVerified: {df['website_live'].sum()} live / {len(df)} total")
    print(f"Saved {len(df_live)} listings to {output_path}")

asyncio.run(verify_websites())
```

---

## STEP 4 — AI ENRICHMENT (Claude)

**CRITICAL RULE:** Always enrich from `site_raw` (scraped content). Never let the LLM invent facts. If a field cannot be found in the content, return `null`.

```python
# scripts/04_enrich.py
import anthropic
import pandas as pd
import json
import os
import time
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Load niche config for field extraction
with open("niche_report.json") as f:
    niche_config = json.load(f)

NICHE_FIELDS = {
    "restroom_trailers": {
        "extra_fields": ["unit_types", "capacity_range", "amenities", "ada_compliant", "service_areas"],
        "field_descriptions": "unit types offered (standard/luxury/VIP), capacity range (e.g. 2-8 stalls), amenities list (AC, mirrors, lighting etc), ADA compliance, geographic service areas"
    },
    "dementia_care": {
        "extra_fields": ["bed_count", "memory_care_certified", "medicare_accepted", "medicaid_accepted", "care_levels"],
        "field_descriptions": "bed/room count, memory care certification, Medicare/Medicaid acceptance, care levels offered"
    },
    "therapists": {
        "extra_fields": ["specialties", "insurance_accepted", "telehealth_available", "age_groups", "modalities"],
        "field_descriptions": "therapy specialties, insurance plans accepted, telehealth availability, age groups served, therapy modalities (CBT/DBT/etc)"
    },
    "ai_tools": {
        "extra_fields": ["pricing_model", "free_tier", "api_available", "integrations", "use_cases"],
        "field_descriptions": "pricing model (free/freemium/paid/usage-based), free tier availability, API access, key integrations, primary use cases"
    },
    "contractors": {
        "extra_fields": ["license_number", "bonded", "insured", "project_types", "service_areas"],
        "field_descriptions": "contractor license number, bonded status, insurance status, project types, service areas"
    }
}

def build_enrichment_prompt(row, niche_key="default"):
    name = row.get("name", "this business")
    site_content = str(row.get("site_raw", ""))[:2500]

    niche_extra = NICHE_FIELDS.get(niche_key, {})
    extra_fields_str = ""
    if niche_extra:
        extra_fields_str = f"""
Also extract these niche-specific fields if present:
{niche_extra.get("field_descriptions", "")}
Include them as: {json.dumps({f: None for f in niche_extra.get("extra_fields", [])})}
"""

    return f"""You are enriching a directory listing for: {name}

Website content (use ONLY this — never invent facts):
---
{site_content if site_content else "[No website content available]"}
---

Extract and return ONLY a valid JSON object with these fields:
{{
  "description": "2-3 sentence professional description of this business and what makes it notable. Use active voice. Do not mention the website.",
  "services": ["list of specific services offered"],
  "service_areas": ["City, State format or region names"],
  "year_founded": null,
  "certifications": ["any certifications, awards, or accreditations mentioned"],
  "social_links": {{"facebook": null, "instagram": null, "linkedin": null}},
  "tagline": "short catchy tagline if present, else null"
  {("," + extra_fields_str) if extra_fields_str else ""}
}}

Rules:
- Return ONLY the JSON object, no commentary
- Use null for any field not found in the content
- Keep description under 150 words
- Services list: max 8 items
- Service areas: max 10 locations"""

def enrich_batch(input_path="data/verified_listings.csv",
                 output_path="data/enriched_listings.csv",
                 niche_key="default",
                 max_records=None):

    df = pd.read_csv(input_path)
    if max_records:
        df = df.head(max_records)

    enriched_fields = []

    for i, (_, row) in enumerate(df.iterrows()):
        print(f"Enriching [{i+1}/{len(df)}]: {row.get('name', 'unknown')[:50]}")

        # Skip if no site content and no description
        if not str(row.get("site_raw", "")).strip() and not str(row.get("description", "")).strip():
            enriched_fields.append({})
            continue

        try:
            prompt = build_enrichment_prompt(row, niche_key)
            message = client.messages.create(
                model="claude-opus-4-5",
                max_tokens=600,
                messages=[{"role": "user", "content": prompt}]
            )
            response_text = message.content[0].text.strip()

            # Clean potential markdown code fences
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]

            enriched = json.loads(response_text)
            enriched_fields.append(enriched)

        except json.JSONDecodeError as e:
            print(f"  JSON parse error: {e}")
            enriched_fields.append({})
        except Exception as e:
            print(f"  Error: {e}")
            enriched_fields.append({})

        # Rate limit: ~50 req/min for Claude
        if i % 10 == 9:
            time.sleep(2)

    # Merge enriched data back
    enrich_df = pd.DataFrame(enriched_fields)
    for col in enrich_df.columns:
        df[f"enriched_{col}"] = enrich_df[col].values

    # Drop the raw content (too large for CSV)
    df = df.drop(columns=["site_raw"], errors="ignore")

    df.to_csv(output_path, index=False)
    print(f"\nEnriched {len(df)} listings → {output_path}")
    return output_path

if __name__ == "__main__":
    enrich_batch(niche_key="restroom_trailers")
```

---

## STEP 5 — IMAGE EXTRACTION (Claude Vision)

```python
# scripts/05_images.py
import anthropic
import requests
import pandas as pd
import base64
import os
import re
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def get_candidate_images(url: str) -> list:
    """Fetch all img tags from a page."""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; DirectoryBot/1.0)"}
        resp = requests.get(url, timeout=10, headers=headers)
        soup = BeautifulSoup(resp.text, "html.parser")
        imgs = []
        for img in soup.find_all("img"):
            src = img.get("src") or img.get("data-src") or ""
            if not src:
                continue
            if src.startswith("//"):
                src = "https:" + src
            elif src.startswith("/"):
                from urllib.parse import urljoin
                src = urljoin(url, src)
            if src.startswith("http"):
                imgs.append(src)
        return imgs[:20]  # Max 20 candidates per site
    except Exception:
        return []

def is_real_business_photo(image_url: str, business_type: str) -> bool:
    """Use Claude Vision to verify the image is a real photo (not icon/stock)."""
    try:
        resp = requests.get(image_url, timeout=10)
        if resp.status_code != 200:
            return False

        # Size filter: skip tiny images (icons, favicons)
        if len(resp.content) < 20000:  # < 20KB
            return False

        # Check it's actually an image
        content_type = resp.headers.get("content-type", "")
        if not any(t in content_type for t in ["jpeg", "jpg", "png", "webp"]):
            return False

        img_data = base64.standard_b64encode(resp.content).decode("utf-8")
        media_type = "image/jpeg" if "jpeg" in content_type or "jpg" in content_type else "image/png"

        message = client.messages.create(
            model="claude-haiku-4-5",  # Use Haiku for cost efficiency on vision checks
            max_tokens=10,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {"type": "base64", "media_type": media_type, "data": img_data}
                    },
                    {
                        "type": "text",
                        "text": f"Is this a real photograph of {business_type} equipment, facilities, staff, or services? Not a logo, icon, banner ad, or generic stock photo? Answer YES or NO only."
                    }
                ]
            }]
        )
        return "YES" in message.content[0].text.upper()

    except Exception:
        return False

def save_image(image_url: str, place_id: str, index: int) -> str | None:
    """Download and save image, return local path."""
    try:
        resp = requests.get(image_url, timeout=10)
        img = Image.open(BytesIO(resp.content))

        # Convert to RGB (handles PNG transparency)
        img = img.convert("RGB")

        # Resize to max 1200px wide while maintaining aspect ratio
        if img.width > 1200:
            ratio = 1200 / img.width
            img = img.resize((1200, int(img.height * ratio)), Image.LANCZOS)

        folder = f"images/{place_id}"
        os.makedirs(folder, exist_ok=True)
        path = f"{folder}/photo_{index}.jpg"
        img.save(path, "JPEG", quality=85)
        return path
    except Exception:
        return None

def extract_images_for_all(input_path="data/enriched_listings.csv",
                           output_path="data/enriched_listings.csv",
                           business_type="business",
                           max_images_per_listing=5):

    df = pd.read_csv(input_path)
    url_col = next((c for c in ["site", "website", "url"] if c in df.columns), None)
    id_col = "place_id" if "place_id" in df.columns else "slug"

    df["image_paths"] = ""
    df["image_count"] = 0

    for i, (idx, row) in enumerate(df.iterrows()):
        if not url_col or pd.isna(row.get(url_col)):
            continue

        url = row[url_col]
        place_id = str(row[id_col])
        print(f"[{i+1}/{len(df)}] Images for: {row.get('name','?')[:40]}")

        candidates = get_candidate_images(url)
        saved_paths = []

        for img_url in candidates:
            if len(saved_paths) >= max_images_per_listing:
                break
            if is_real_business_photo(img_url, business_type):
                path = save_image(img_url, place_id, len(saved_paths) + 1)
                if path:
                    saved_paths.append(path)
                    print(f"  Saved: {path}")

        df.at[idx, "image_paths"] = "|".join(saved_paths)
        df.at[idx, "image_count"] = len(saved_paths)

    df.to_csv(output_path, index=False)
    total_images = df["image_count"].sum()
    listings_with_images = (df["image_count"] > 0).sum()
    print(f"\nImages extracted: {total_images} total across {listings_with_images} listings")
    return output_path

if __name__ == "__main__":
    extract_images_for_all(business_type="luxury restroom trailer rental")
```

---

## COST ESTIMATES

| Operation | Model | Cost per listing | 300 listings |
|---|---|---|---|
| Enrichment | claude-opus-4-5 | ~$0.01 | ~$3 |
| Image verification | claude-haiku-4-5 | ~$0.002/image × 5 | ~$3 |
| Website crawling | Crawl4AI (free) | $0 | $0 |
| **Total enrichment cost** | | **~$0.02** | **~$6** |

---

## VALIDATION CHECKLIST
- [ ] `data/enriched_listings.csv` has `enriched_description` column populated for >60% of rows
- [ ] `images/` folder exists with subfolders per place_id
- [ ] At least 30% of listings have at least 1 verified image
- [ ] No `enriched_description` values contain "I cannot" or "not found" (hallucination signal)