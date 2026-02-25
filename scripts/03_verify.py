"""
STEP 3: Verify websites using Crawl4AI. Fetch content for enrichment.
Input:  data/clean_listings.csv
Output: data/verified_listings.csv
See docs/SKILL-04-data-enrich.md for full documentation.
"""
import asyncio, pandas as pd, os
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

async def main():
    df = pd.read_csv("data/clean_listings.csv")
    url_col = next((c for c in ["site", "website", "url"] if c in df.columns), None)
    id_col = "place_id" if "place_id" in df.columns else "slug"

    if not url_col:
        print("No URL column found — saving as-is")
        df.to_csv("data/verified_listings.csv", index=False)
        return

    browser_config = BrowserConfig(headless=True, viewport_width=1280)
    run_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS, page_timeout=15000)
    verified = {}

    async with AsyncWebCrawler(config=browser_config) as crawler:
        valid_rows = [(row[url_col], str(row[id_col])) for _, row in df.iterrows() if pd.notna(row.get(url_col))]
        print(f"Verifying {len(valid_rows)} websites...")
        for i, (url, rid) in enumerate(valid_rows):
            try:
                r = await crawler.arun(url=url, config=run_config)
                verified[rid] = {"website_live": r.status_code == 200, "site_raw": (r.markdown or "")[:3000]}
                print(f"  [{i+1}/{len(valid_rows)}] {'OK' if r.status_code==200 else f'HTTP {r.status_code}'}: {url[:50]}")
            except Exception as e:
                verified[rid] = {"website_live": False, "site_raw": ""}

    df["website_live"] = df[id_col].astype(str).map(lambda x: verified.get(x, {}).get("website_live", False))
    df["site_raw"] = df[id_col].astype(str).map(lambda x: verified.get(x, {}).get("site_raw", ""))
    df.to_csv("data/verified_listings.csv", index=False)
    print(f"\n{df['website_live'].sum()} live / {len(df)} total → data/verified_listings.csv")

if __name__ == "__main__":
    asyncio.run(main())