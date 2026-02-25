"""
STEP 1: Scrape raw listings from Google Maps via Outscraper.
Output: data/raw_listings.csv
See docs/SKILL-02-data-scrape.md for full documentation.
"""
import os, json, pandas as pd
from outscraper import OutscraperClient
from dotenv import load_dotenv

load_dotenv()

def main():
    with open("config/niche.json") as f:
        config = json.load(f)

    client = OutscraperClient(api_key=os.getenv("OUTSCRAPER_API_KEY"))
    queries = config.get("outscraper_queries", [config.get("niche", "") + " usa"])

    print(f"Running {len(queries)} queries...")
    all_results = []
    for q in queries:
        print(f"  Query: {q}")
        results = client.google_maps_search(q, limit=500, language="en", region="us")
        for batch in results:
            all_results.extend(batch)
        print(f"  Total so far: {len(all_results)}")

    os.makedirs("data", exist_ok=True)
    df = pd.DataFrame(all_results)
    df.to_csv("data/raw_listings.csv", index=False)
    print(f"\nSaved {len(df)} raw listings to data/raw_listings.csv")

if __name__ == "__main__":
    main()