# SKILL: Data Cleaning
**Skill ID:** SKILL-03  
**Version:** 1.0  
**Depends on:** SKILL-02 → `data/raw_listings.csv`  
**Outputs to:** SKILL-04 (enrich)  
**Portable to:** Any Python 3.10+ environment

---

## PURPOSE
Transform raw scraped data into a clean, deduplicated, standardized dataset. Remove garbage, normalize formats, flag quality issues. This is what separates a real directory from a scrape dump.

---

## INPUTS
- `data/raw_listings.csv`

## OUTPUTS
- `data/clean_listings.csv`
- `data/cleaning_report.json` (stats on what was removed and why)

---

## SETUP
```bash
pip install pandas phonenumbers tldextract
```

---

## FULL CLEANING SCRIPT

```python
# scripts/02_clean.py
import pandas as pd
import re
import json
import os
import tldextract
from urllib.parse import urlparse

def clean_listings(input_path: str = "data/raw_listings.csv",
                   output_path: str = "data/clean_listings.csv") -> dict:

    df = pd.read_csv(input_path, low_memory=False)
    report = {"input_count": len(df), "removed": {}, "output_count": 0}

    print(f"Starting with {len(df)} records")

    # ── 1. Remove permanently closed businesses ────────────────────────────────
    if "business_status" in df.columns:
        before = len(df)
        df = df[df["business_status"].isin(["OPERATIONAL", None, float("nan")])]
        df = df[~df["business_status"].str.contains("CLOSED|PERMANENTLY", case=False, na=False)]
        removed = before - len(df)
        report["removed"]["closed_businesses"] = removed
        print(f"  Removed {removed} closed businesses")

    # ── 2. Drop rows missing essential fields ────────────────────────────────
    essential = ["name"]
    # Add address fields if present
    for col in ["full_address", "address", "city", "state"]:
        if col in df.columns:
            essential.append(col)
            break

    before = len(df)
    df = df.dropna(subset=essential)
    removed = before - len(df)
    report["removed"]["missing_essentials"] = removed
    print(f"  Removed {removed} missing essential fields")

    # ── 3. Deduplicate ─────────────────────────────────────────────────────
    before = len(df)
    if "place_id" in df.columns:
        df = df.drop_duplicates(subset=["place_id"], keep="first")

    # Secondary dedup by name + city
    name_col = "name"
    city_col = next((c for c in ["city", "borough"] if c in df.columns), None)
    if city_col:
        df["_dedup_key"] = (
            df[name_col].str.lower().str.strip() + "|" +
            df[city_col].fillna("").str.lower().str.strip()
        )
        df = df.drop_duplicates(subset=["_dedup_key"], keep="first")
        df = df.drop(columns=["_dedup_key"])

    removed = before - len(df)
    report["removed"]["duplicates"] = removed
    print(f"  Removed {removed} duplicates")

    # ── 4. Normalize phone numbers ───────────────────────────────────────────
    def normalize_phone(p):
        if pd.isna(p):
            return None
        digits = re.sub(r"\D", "", str(p))
        if len(digits) == 11 and digits[0] == "1":
            digits = digits[1:]
        if len(digits) == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        return str(p).strip() if str(p).strip() else None

    phone_col = next((c for c in ["phone", "telephone", "phone_number"] if c in df.columns), None)
    if phone_col:
        df[phone_col] = df[phone_col].apply(normalize_phone)

    # ── 5. Clean and validate website URLs ────────────────────────────────────
    url_col = next((c for c in ["site", "website", "url"] if c in df.columns), None)
    if url_col:
        def clean_url(u):
            if pd.isna(u) or str(u).strip() in ["", "nan"]:
                return None
            u = str(u).strip()
            if not u.startswith("http"):
                u = "https://" + u
            try:
                parsed = urlparse(u)
                ext = tldextract.extract(u)
                if not ext.domain or not ext.suffix:
                    return None
                # Filter out social media profiles (not business sites)
                blocked = ["facebook.com", "instagram.com", "twitter.com",
                           "linkedin.com", "yelp.com", "google.com"]
                if any(b in u for b in blocked):
                    return None
                return u
            except Exception:
                return None

        df[url_col] = df[url_col].apply(clean_url)

    # ── 6. Normalize state to abbreviation ────────────────────────────────────
    STATE_MAP = {
        "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
        "California": "CA", "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE",
        "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID",
        "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS",
        "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
        "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS",
        "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV",
        "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY",
        "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK",
        "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
        "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT",
        "Vermont": "VT", "Virginia": "VA", "Washington": "WA", "West Virginia": "WV",
        "Wisconsin": "WI", "Wyoming": "WY"
    }
    state_col = next((c for c in ["state", "region"] if c in df.columns), None)
    if state_col:
        df[state_col] = df[state_col].apply(
            lambda s: STATE_MAP.get(str(s).strip(), str(s).strip().upper()[:2]) if pd.notna(s) else None
        )

    # ── 7. Strip HTML and special characters from name ────────────────────────────
    def clean_name(n):
        if pd.isna(n):
            return None
        n = re.sub(r"<[^>]+>", "", str(n))       # strip HTML
        n = re.sub(r"[^\w\s\-\.\,\&\']", "", n)   # keep safe chars
        n = " ".join(n.split())                    # normalize whitespace
        return n.strip()

    df["name"] = df["name"].apply(clean_name)
    df = df[df["name"].str.len() > 2]  # Remove single-char or empty names

    # ── 8. Add quality score ─────────────────────────────────────────────────
    def quality_score(row):
        score = 0
        if pd.notna(row.get(phone_col)): score += 2
        if pd.notna(row.get(url_col)): score += 3
        if pd.notna(row.get("rating")) and float(row.get("rating", 0) or 0) >= 4.0: score += 2
        if pd.notna(row.get("reviews")) and float(row.get("reviews", 0) or 0) >= 10: score += 1
        if pd.notna(row.get("description")) and len(str(row.get("description", ""))) > 50: score += 2
        return score

    df["quality_score"] = df.apply(quality_score, axis=1)
    df["is_featured_candidate"] = df["quality_score"] >= 7

    # ── 9. Generate URL slug ─────────────────────────────────────────────────
    def make_slug(*parts):
        combined = "-".join(str(p) for p in parts if pd.notna(p) and str(p).strip())
        slug = combined.lower()
        slug = re.sub(r"[^a-z0-9]+", "-", slug)
        slug = slug.strip("-")
        return slug[:80]  # Max 80 chars

    city_col2 = next((c for c in ["city", "borough"] if c in df.columns), None)
    state_col2 = next((c for c in ["state", "region"] if c in df.columns), None)

    df["slug"] = df.apply(
        lambda r: make_slug(r["name"], r.get(city_col2), r.get(state_col2)),
        axis=1
    )

    # Ensure slug uniqueness
    slug_counts = df["slug"].value_counts()
    dupes = slug_counts[slug_counts > 1].index
    for slug in dupes:
        mask = df["slug"] == slug
        df.loc[mask, "slug"] = [f"{slug}-{i+1}" for i in range(mask.sum())]

    # ── 10. Save ─────────────────────────────────────────────────────────
    os.makedirs("data", exist_ok=True)
    df.to_csv(output_path, index=False)

    report["output_count"] = len(df)
    report["retention_rate"] = f"{len(df)/report['input_count']*100:.1f}%"
    report["featured_candidates"] = int(df["is_featured_candidate"].sum())
    report["has_website"] = int(df[url_col].notna().sum()) if url_col else 0

    with open("data/cleaning_report.json", "w") as f:
        json.dump(report, f, indent=2)

    print(f"\nCleaning complete:")
    print(f"  Input:  {report['input_count']}")
    print(f"  Output: {report['output_count']} ({report['retention_rate']} retained)")
    print(f"  Featured candidates: {report['featured_candidates']}")

    return report

if __name__ == "__main__":
    clean_listings()
```

---

## QUALITY THRESHOLDS

| Metric | Minimum Acceptable |
|---|---|
| Retention rate | >40% (if <40%, check if Outscraper query was too broad) |
| Has website | >30% of records |
| Has phone | >60% of records |
| Featured candidates | >10% of records |

---

## CLEANING REPORT EXAMPLE
```json
{
  "input_count": 487,
  "removed": {
    "closed_businesses": 23,
    "missing_essentials": 41,
    "duplicates": 67
  },
  "output_count": 356,
  "retention_rate": "73.1%",
  "featured_candidates": 89,
  "has_website": 241
}
```

---

## NOTES FOR AGENT
- Never modify the raw_listings.csv — always write to clean_listings.csv
- If retention rate < 40%, report it and ask whether to broaden the Outscraper query
- The `quality_score` field drives upsell targeting in outreach (SKILL-07)
- The `slug` field is used as the URL path for every listing page
- `is_featured_candidate = True` means this business is worth pitching for a paid upgrade