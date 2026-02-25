"""
STEP 4: Enrich listings with Claude AI using scraped website content.
Input:  data/verified_listings.csv
Output: data/enriched_listings.csv
See docs/SKILL-04-data-enrich.md for full documentation.
IMPORTANT: Never hallucinate — enrich only from scraped site_raw content.
"""
import anthropic, pandas as pd, json, os, time
from dotenv import load_dotenv
load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

with open("config/niche.json") as f:
    NICHE = json.load(f)

def enrich_row(row):
    name = row.get("name", "this business")
    site_content = str(row.get("site_raw", ""))[:2500]
    if not site_content.strip():
        return {}
    extra = NICHE.get("niche_enrichment_fields", {})
    extra_str = f"\nAlso extract: {json.dumps(extra)}" if extra else ""
    prompt = f"""Enrich this directory listing for: {name}
Niche: {NICHE['niche']}

Website content (use ONLY this, never invent facts):
---
{site_content}
---

Return ONLY a JSON object:
{{
  "description": "2-3 sentence professional description",
  "services": ["list of services, max 8"],
  "service_areas": ["City, State format, max 10"],
  "year_founded": null,
  "certifications": [],
  "tagline": null{extra_str}
}}"""
    try:
        msg = client.messages.create(model="claude-opus-4-5", max_tokens=600,
                                      messages=[{"role": "user", "content": prompt}])
        text = msg.content[0].text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"): text = text[4:]
        return json.loads(text)
    except Exception as e:
        print(f"  Error: {e}")
        return {}

def main():
    df = pd.read_csv("data/verified_listings.csv")
    print(f"Enriching {len(df)} listings...")
    enriched = []
    for i, (_, row) in enumerate(df.iterrows()):
        print(f"  [{i+1}/{len(df)}] {str(row.get('name',''))[:40]}")
        enriched.append(enrich_row(row))
        if i % 10 == 9: time.sleep(1)
    enrich_df = pd.DataFrame(enriched)
    for col in enrich_df.columns:
        df[f"enriched_{col}"] = enrich_df[col].values
    df = df.drop(columns=["site_raw"], errors="ignore")
    df.to_csv("data/enriched_listings.csv", index=False)
    print(f"\nEnriched → data/enriched_listings.csv")

if __name__ == "__main__":
    main()