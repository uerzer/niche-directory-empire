# SKILL: Data Scraping
**Skill ID:** SKILL-02  
**Version:** 1.0  
**Depends on:** SKILL-01 (niche_report.json)  
**Outputs to:** SKILL-03 (data clean)  
**Portable to:** Any Python 3.10+ environment with pip access

---

## PURPOSE
Pull raw listing data for the target niche from Google Maps (via Outscraper) or alternative public sources. Output a raw CSV ready for cleaning.

---

## INPUTS
- `niche_report.json` from SKILL-01
- `OUTSCRAPER_API_KEY` environment variable

---

## OUTPUTS
- `data/raw_listings.csv` — all fields from Outscraper, unfiltered

---

## ENVIRONMENT SETUP
```bash
pip install outscraper pandas python-dotenv
```

```bash
# .env
OUTSCRAPER_API_KEY=your_key_here
```

---

## PRIMARY METHOD — Outscraper (Google Maps)

Use when niche = local businesses (contractors, healthcare, rentals, services).

```python
# scripts/01_scrape.py
import os
import json
import pandas as pd
from outscraper import OutscraperClient
from dotenv import load_dotenv

load_dotenv()

def scrape_niche(niche_report_path: str = "niche_report.json") -> str:
    with open(niche_report_path) as f:
        config = json.load(f)

    client = OutscraperClient(api_key=os.getenv("OUTSCRAPER_API_KEY"))

    # Build query list from niche report
    queries = [src["query"] for src in config["data_sources"] if src["source"].startswith("Google Maps")]

    print(f"Running {len(queries)} Outscraper queries...")

    all_results = []
    for query in queries:
        print(f"  Querying: {query}")
        results = client.google_maps_search(
            query,
            limit=500,
            language="en",
            region="us",
            fields=[
                "name", "full_address", "borough", "street",
                "city", "postal_code", "state", "country_code",
                "phone", "site", "email",
                "rating", "reviews", "reviews_link",
                "photo", "working_hours",
                "business_status", "type", "subtypes",
                "latitude", "longitude", "place_id",
                "description", "range", "posts"
            ]
        )
        for query_batch in results:
            all_results.extend(query_batch)
        print(f"  Got {len(all_results)} total so far")

    df = pd.DataFrame(all_results)
    output_path = "data/raw_listings.csv"
    os.makedirs("data", exist_ok=True)
    df.to_csv(output_path, index=False)

    print(f"\nSaved {len(df)} raw listings to {output_path}")
    print(f"Columns: {list(df.columns)}")
    return output_path

if __name__ == "__main__":
    scrape_niche()
```

---

## ALTERNATIVE METHODS

### A — NPI Registry (Healthcare: therapists, doctors, dentists, nurses)
Free government API. No key required. 5.6M records.

```python
# scripts/01_scrape_npi.py
import requests
import pandas as pd
import time

def scrape_npi(taxonomy_code: str, states: list, limit_per_state: int = 200) -> str:
    """
    taxonomy_code examples:
      "101YM0800X" = Mental Health Counselor
      "103T00000X" = Psychologist
      "207Q00000X" = Family Medicine
      "363L00000X" = Nurse Practitioner
    """
    BASE_URL = "https://npiregistry.cms.hhs.gov/api/"
    all_records = []

    for state in states:
        print(f"  Fetching {taxonomy_code} in {state}...")
        skip = 0
        while True:
            params = {
                "taxonomy_description": "",
                "taxonomy_code": taxonomy_code,
                "state": state,
                "limit": 200,
                "skip": skip,
                "version": "2.1",
                "enumeration_type": "NPI-1"  # Individual providers
            }
            resp = requests.get(BASE_URL, params=params)
            data = resp.json()
            results = data.get("results", [])
            if not results:
                break
            for r in results:
                basic = r.get("basic", {})
                addresses = r.get("addresses", [{}])
                addr = addresses[0] if addresses else {}
                taxonomies = r.get("taxonomies", [{}])
                tax = taxonomies[0] if taxonomies else {}
                all_records.append({
                    "npi": r.get("number"),
                    "name": f"{basic.get('first_name','')} {basic.get('last_name','')}".strip(),
                    "credential": basic.get("credential"),
                    "organization": basic.get("organization_name"),
                    "address": addr.get("address_1"),
                    "city": addr.get("city"),
                    "state": addr.get("state"),
                    "zip": addr.get("postal_code"),
                    "phone": addr.get("telephone_number"),
                    "taxonomy": tax.get("desc"),
                    "license_state": tax.get("state"),
                    "license_number": tax.get("license")
                })
            skip += 200
            if skip >= limit_per_state:
                break
            time.sleep(0.5)

    df = pd.DataFrame(all_records)
    output_path = "data/raw_listings.csv"
    os.makedirs("data", exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Saved {len(df)} NPI records")
    return output_path
```

### B — Curlie.org (General categories, CC-licensed, free)
Download dump from https://curlie.org/docs/en/rdf.html.gz (~2.9M entries).

```python
# Parse Curlie RDF dump
import gzip
import xml.etree.ElementTree as ET
import pandas as pd

def parse_curlie(dump_path: str, category_filter: str) -> str:
    records = []
    with gzip.open(dump_path, 'rb') as f:
        tree = ET.parse(f)
        root = tree.getroot()
        for topic in root.findall('Topic'):
            topic_id = topic.get('r:id', '')
            if category_filter.lower() not in topic_id.lower():
                continue
            for link in topic.findall('link1'):
                records.append({
                    "topic": topic_id,
                    "name": link.get('r:resource', '').split('/')[-1],
                    "url": link.get('r:resource', ''),
                    "description": link.findtext('d:Description', '')
                })
    df = pd.DataFrame(records)
    df.to_csv("data/raw_listings.csv", index=False)
    return "data/raw_listings.csv"
```

### C — ProductHunt API (AI tools, apps, software)
```python
import requests
import pandas as pd

def scrape_producthunt(topic: str = "artificial-intelligence", pages: int = 10) -> str:
    # ProductHunt GraphQL API (public, no auth for basic queries)
    GRAPHQL_URL = "https://api.producthunt.com/v2/api/graphql"
    headers = {"Authorization": f"Bearer {os.getenv('PRODUCTHUNT_TOKEN')}"}

    all_posts = []
    for page in range(1, pages + 1):
        query = """
        query($topic: String!, $after: String) {
          posts(topic: $topic, order: VOTES, after: $after) {
            edges { node {
              id name tagline description
              website votesCount
              topics { edges { node { name } } }
              thumbnail { url }
            }}
            pageInfo { endCursor hasNextPage }
          }
        }
        """
        resp = requests.post(GRAPHQL_URL, json={"query": query, "variables": {"topic": topic}}, headers=headers)
        data = resp.json()
        posts = data["data"]["posts"]["edges"]
        for edge in posts:
            node = edge["node"]
            all_posts.append({
                "name": node["name"],
                "tagline": node["tagline"],
                "description": node["description"],
                "website": node["website"],
                "votes": node["votesCount"],
                "thumbnail": node.get("thumbnail", {}).get("url"),
                "topics": ", ".join([t["node"]["name"] for t in node["topics"]["edges"]])
            })

    df = pd.DataFrame(all_posts)
    df.to_csv("data/raw_listings.csv", index=False)
    return "data/raw_listings.csv"
```

---

## COST ESTIMATES

| Method | Cost | Records | Best For |
|---|---|---|---|
| Outscraper free tier | $0 | 500/month | Testing |
| Outscraper standard | $3/1k records | Unlimited | Local businesses |
| NPI Registry | Free | 5.6M | Healthcare |
| Curlie dump | Free | 2.9M | General categories |
| ProductHunt API | Free (limited) | ~10k/topic | Tech tools |

**Rule of thumb:** A directory with 300 verified listings costs ~$1-5 in Outscraper credits to build.

---

## VALIDATION CHECKLIST
After running, verify:
- [ ] `data/raw_listings.csv` exists and is non-empty
- [ ] Has columns: name, address/city/state, phone, website
- [ ] Record count matches expected range from niche_report.json
- [ ] No encoding errors (open in text editor, check for garbled chars)
- [ ] Sample 5 random rows manually — do they look like real businesses?