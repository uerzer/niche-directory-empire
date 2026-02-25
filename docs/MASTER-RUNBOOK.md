# Niche Directory Empire - Master Runbook
## Agent-Portable Orchestration Document
**Version:** 2.0 | **Source:** Frey Chu / Greg Isenberg methodology + extended research
**Purpose:** Give any AI agent (Claude, GPT, Cursor, CrewAI, LangChain) everything needed to build and deploy a profitable niche directory from scratch.

---

## WHAT THIS IS

A repeatable 7-step system to build niche directory websites that:
- Launch pre-populated with real data (no chicken-and-egg problem)
- Rank on Google for high-intent local/niche searches
- Generate $500-2,500/month per site at maturity (month 6-12)
- Cost under $250 to build, ~$10/month to run
- Take 4 days to build, 15 min/week to maintain

**Proven case:** Frey Chu built a Luxury Restroom Trailer directory in 4 days for under $250. Revenue: $273/day ($8,190/month) from lead generation + sponsored listings.

---

## AGENT ROLES IN THIS SYSTEM

| Agent Role | Runs On | Responsibility |
|---|---|---|
| Orchestrator | Any LLM | Reads this runbook, delegates to specialists |
| Data Agent | Python env | Steps 1-2: scrape + clean |
| Enrichment Agent | Python + LLM API | Steps 3-4: crawl + enrich |
| Vision Agent | LLM with vision | Step 5: image extraction |
| Build Agent | Node/Python env | Step 6-7: generate site + deploy |
| SEO Agent | Any LLM | Post-launch: content + sitemap |
| Outreach Agent | Any LLM + email | Month 2+: cold email campaigns |

**If running as a single agent:** Execute all steps sequentially. Each step produces a file output that feeds the next step.

---

## THE 7-STEP PIPELINE

### STEP 1 — Scrape Raw Data
**Tool:** Outscraper (Google Maps API wrapper)
**Input:** Niche category + target geography
**Output:** `raw_listings.csv`

**What to extract:**
- Business name
- Full address (street, city, state, zip)
- Phone number
- Website URL
- Google rating + review count
- Business hours
- Business status (OPERATIONAL / CLOSED)
- Google Place ID
- Latitude / Longitude
- Business category/type
- Photos count

**Python implementation:**
```python
from outscraper import OutscraperClient
import pandas as pd

client = OutscraperClient(api_key=OUTSCRAPER_API_KEY)

queries = [
    "luxury restroom trailer rental usa",
    "portable restroom trailer rental usa",
    "VIP restroom trailer rental usa"
]

results = client.google_maps_search(
    queries,
    limit=500,
    language='en',
    region='us'
)

# Flatten and save
rows = []
for query_results in results:
    for place in query_results:
        rows.append(place)

df = pd.DataFrame(rows)
df.to_csv('raw_listings.csv', index=False)
print(f"Extracted {len(df)} listings")
```

**Alternative (free):** Use Curlie.org download (CC-licensed, 2.9M entries) or government data (NPI registry for healthcare).

---

### STEP 2 — Clean Data
**Tool:** Python (pandas) + LLM for edge cases
**Input:** `raw_listings.csv`
**Output:** `clean_listings.csv`

**Cleaning operations:**
1. Remove `business_status != OPERATIONAL`
2. Remove rows missing name, address, or phone
3. Deduplicate by place_id (then by name+address if no place_id)
4. Standardize phone format: `(555) 555-5555`
5. Validate website URLs (check format, not dead-link yet)
6. Normalize state abbreviations
7. Flag entries with rating < 3.0 for manual review
8. Strip HTML/special chars from names

**Python implementation:**
```python
import pandas as pd
import re

df = pd.read_csv('raw_listings.csv')

# Remove closed
df = df[df['business_status'] == 'OPERATIONAL']

# Remove missing essentials
df = df.dropna(subset=['name', 'full_address', 'phone'])

# Deduplicate
df = df.drop_duplicates(subset=['place_id'])
df = df.drop_duplicates(subset=['name', 'full_address'])

# Standardize phone
def clean_phone(p):
    digits = re.sub(r'\D', '', str(p))
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    return p

df['phone'] = df['phone'].apply(clean_phone)

# Flag low ratings
df['needs_review'] = df['rating'] < 3.0

df.to_csv('clean_listings.csv', index=False)
print(f"Clean listings: {len(df)}")
```

---

### STEP 3 — Website Verification (Crawl4AI)
**Tool:** Crawl4AI (open source, free)
**Input:** `clean_listings.csv` (website column)
**Output:** `verified_listings.csv` + `site_content/` folder

**What to verify:**
- Website is live (HTTP 200)
- Extract business description from homepage
- Extract any structured data (hours, services, areas)
- Flag redirects, parked domains, 404s

**Python implementation:**
```python
import asyncio
import pandas as pd
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

df = pd.read_csv('clean_listings.csv')

browser_config = BrowserConfig(headless=True, viewport_width=1280)
crawler_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS)

async def verify_website(crawler, url, place_id):
    try:
        result = await crawler.arun(url=url, config=crawler_config)
        return {
            'place_id': place_id,
            'website_live': result.status_code == 200,
            'description': result.markdown[:500] if result.markdown else '',
            'raw_content': result.markdown[:2000] if result.markdown else ''
        }
    except Exception as e:
        return {'place_id': place_id, 'website_live': False, 'description': '', 'raw_content': ''}

async def verify_all():
    results = []
    async with AsyncWebCrawler(config=browser_config) as crawler:
        tasks = [
            verify_website(crawler, row['site'], row['place_id'])
            for _, row in df.iterrows()
            if pd.notna(row.get('site'))
        ]
        results = await asyncio.gather(*tasks)
    return results

verification_results = asyncio.run(verify_all())
verify_df = pd.DataFrame(verification_results)
df = df.merge(verify_df, on='place_id', how='left')
df = df[df['website_live'] == True]  # Keep only live sites
df.to_csv('verified_listings.csv', index=False)
print(f"Verified listings: {len(df)}")
```

---

### STEP 4 — Data Enrichment
**Tool:** Claude API (with web_search tool enabled) or GPT-4 with browsing
**Input:** `verified_listings.csv` + `raw_content` from Step 3
**Output:** `enriched_listings.csv`

**CRITICAL:** Always use web search specification. Never let the LLM hallucinate facts about a business.

**What to enrich per listing:**
- Professional description (2-3 sentences, SEO-optimized)
- Service categories (from website content)
- Niche-specific attributes (see per-niche config below)
- Service areas / coverage geography
- Year established (if findable)
- Social media links
- Specialties / certifications

**Enrichment prompt template:**
```
You are enriching a directory listing for [BUSINESS NAME].

Website content scraped:
---
[RAW_CONTENT from Step 3]
---

Using ONLY the information in the website content above (do not invent facts),
extract and return a JSON object with:
{
  "description": "2-3 sentence professional description of this business",
  "services": ["list", "of", "services"],
  "service_areas": ["City, State", ...],
  "specialties": ["any", "certifications", "or", "awards"],
  "year_founded": null or YYYY,
  "social_links": {"facebook": "", "instagram": "", "linkedin": ""}
}

If a field cannot be determined from the content, use null.
NEVER invent information not present in the scraped content.
```

**Niche-specific attributes to add:**

| Niche | Extra Fields |
|---|---|
| Restroom trailers | capacity, unit_types[], amenities[], ADA_compliant |
| Healthcare/therapists | specialties[], insurance_accepted[], telehealth |
| Dementia care | bed_count, memory_care_certified, medicare_accepted |
| AI tools | pricing_model, free_tier, api_available, integrations[] |
| Contractors | license_number, bonded, insured, project_types[] |

---

### STEP 5 — Image Extraction (Claude Vision)
**Tool:** Claude Vision API / GPT-4 Vision
**Input:** Business website URLs from `verified_listings.csv`
**Output:** `images/` folder + image URLs added to `enriched_listings.csv`

**Process:**
1. For each listing, fetch the business website
2. Extract all `<img>` tags
3. Filter: skip logos, icons, stock photos (<50KB)
4. Download images that appear to be product/facility photos
5. Use Vision API to verify: "Is this an actual photo of [business type] services/facility? Yes/No"
6. Keep only verified=Yes images (max 5 per listing)
7. Store as: `images/{place_id}/photo_1.jpg`

**Python implementation:**
```python
import anthropic
import requests
from bs4 import BeautifulSoup
import base64
import os

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

def verify_image_with_vision(image_url, business_type):
    response = requests.get(image_url, timeout=10)
    if response.status_code != 200:
        return False
    
    img_data = base64.standard_b64encode(response.content).decode("utf-8")
    content_type = response.headers.get('content-type', 'image/jpeg')
    
    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=100,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": content_type, "data": img_data}},
                {"type": "text", "text": f"Is this a real photo of {business_type} services, facilities, or equipment (not a logo, icon, or generic stock photo)? Answer only YES or NO."}
            ]
        }]
    )
    return "YES" in message.content[0].text.upper()
```

---

### STEP 6 — Site Generation
**Tool:** Python (Jinja2 templating) → static HTML OR Next.js with data files
**Input:** `enriched_listings.csv` + `images/` folder
**Output:** Complete static website

**Pages to generate:**
1. `index.html` — Homepage with search + featured listings
2. `listings/[slug].html` — One page per listing (SEO gold)
3. `category/[category].html` — Category index pages
4. `location/[state]/[city].html` — City/state pages for local SEO
5. `blog/[slug].html` — 10 supporting SEO articles
6. `sitemap.xml` — Auto-generated
7. `robots.txt`

**URL slug formula:**
```python
import re
def make_slug(name, city, state):
    s = f"{name}-{city}-{state}"
    s = s.lower()
    s = re.sub(r'[^a-z0-9]+', '-', s)
    s = s.strip('-')
    return s
# "ABC Trailers, Austin, TX" -> "abc-trailers-austin-tx"
```

**Tech stack decision:**
- **Simple/fast:** Pure Python + Jinja2 → generates static HTML → deploy to Cloudflare Pages
- **Feature-rich:** Next.js with JSON data files → Vercel deploy (free tier)
- **Recommended:** Static HTML for speed + SEO simplicity

**Affiliate injection:** Every listing page gets niche-appropriate affiliate CTAs injected at build time from `config/affiliates.json`.

---

### STEP 7 — Deploy
**Tool:** GitHub + Cloudflare Pages (free) or Vercel (free)
**Input:** Generated site files
**Output:** Live URL

**Cloudflare Pages deploy (recommended):**
```bash
# One-time setup
npm install -g wrangler
wrangler login

# Deploy
wrangler pages deploy ./dist --project-name=my-directory-name
```

**Or via GitHub Actions (fully automated):**
```yaml
# .github/workflows/deploy.yml
name: Deploy to Cloudflare Pages
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy
        uses: cloudflare/pages-action@v1
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
          projectName: my-directory
          directory: dist
```

---

## POST-LAUNCH OPERATIONS

### Week 2: SEO Setup
1. Add domain to Google Search Console
2. Submit sitemap: `https://yourdomain.com/sitemap.xml`
3. Add structured data (JSON-LD LocalBusiness schema) — already in template
4. Set up Google Analytics 4

### Month 2+: Cold Outreach
**Sequence (3 emails, 7 days apart):**

Email 1 — Claim your listing:
```
Subject: Your business is listed on [DirectoryName] - claim it free

Hi [Name],

I found [Business Name] while building [DirectoryName].com — a directory for [niche] in [region].

Your listing is live at: [URL]

I'm offering free verified badges to founding members this month. Just reply and I'll upgrade your listing at no cost.

[Your name]
```

Email 2 — Social proof:
```
Subject: Re: [Business Name] on [DirectoryName]

Following up — we're now getting [X] monthly searches for [niche keywords].

A few businesses have already claimed enhanced listings. Yours is one of the most complete profiles we have.

Worth a quick call?
```

Email 3 — Upgrade pitch:
```
Subject: Last chance — enhanced listing expires Friday

[Name], enhanced listings on [DirectoryName] are $49/month.

That includes: priority placement, photo gallery, contact form with lead notifications, and a verified badge.

We have [X] visitors searching for [niche] this month. Want the leads?

[Link to upgrade]
```

---

## MONETIZATION CONFIGURATION

### Per-Niche Affiliate Stack

```json
{
  "restroom_trailers": {
    "primary": "Lead gen - sell to businesses at $50-150/lead",
    "secondary": "AdSense - high CPM for event/rental searches",
    "affiliate_tools": ["eventbrite_affiliate", "wedding_wire_affiliate"]
  },
  "dementia_care": {
    "primary": "A Place for Mom referral - $500-2000/placement",
    "secondary": "Care.com affiliate",
    "affiliate_tools": ["caregiver_insurance", "telehealth_platforms"]
  },
  "therapists": {
    "primary": "Bark.com affiliate - $50-100/lead",
    "secondary": "BetterHelp affiliate - 35% recurring",
    "affiliate_tools": ["psychology_today_premium", "telehealth_platforms"]
  },
  "ai_tools": {
    "primary": "PartnerStack - 20-50% recurring per tool",
    "secondary": "Direct affiliate programs per tool",
    "affiliate_tools": ["openai_affiliate", "anthropic_credits", "midjourney"]
  },
  "contractors": {
    "primary": "Housecall Pro - $250/signup",
    "secondary": "Bark.com - $50-100/lead",
    "affiliate_tools": ["insurance_affiliates", "quickbooks_affiliate"]
  }
}
```

### Pricing Tiers (inject into every site)
```
Free:     Basic listing (name, address, phone, link)
Basic:    $29/month — photos, description, contact form
Pro:      $79/month — priority placement, analytics, review widget
Featured: $199/month — homepage placement, badge, dedicated support
```

---

## NICHE SELECTION CRITERIA

Score each potential niche on 5 dimensions (1-5 each, max 25):

| Dimension | What to Check | Tool |
|---|---|---|
| Search Volume | Monthly searches for "[niche] near me" | Ahrefs / Google Keyword Planner |
| Competition | Existing directories quality | Manual Google search |
| Data Availability | Public data sources exist | Google Maps, govt APIs |
| Affiliate Match | Programs paying $50+ per action | PartnerStack, ShareASale |
| Buyer Intent | Are searchers ready to spend? | CPC > $2 indicates commercial intent |

**Minimum viable niche:** Score 15+, at least one affiliate paying $50+/action or AdSense CPC > $3.

**Best niches 2025-2026 (pre-scored):**

| Niche | Score | Primary Monetization |
|---|---|---|
| Luxury restroom trailers | 22/25 | Lead gen $50-150/lead |
| Dementia care facilities | 23/25 | Referral $500-2000/placement |
| Mental health therapists | 21/25 | Bark.com $100/lead |
| Immigration lawyers | 20/25 | Bark.com $100/lead |
| AI tools by use case | 19/25 | PartnerStack 20-50% recurring |
| Plasma donation centers | 18/25 | AdSense (high CPM) |
| Ketamine clinics | 22/25 | Lead gen high-ticket |
| ADA bathroom contractors | 20/25 | Lead gen + Housecall Pro |
| Stem cell treatment centers | 21/25 | Lead gen high-ticket |
| Senior living facilities | 24/25 | A Place for Mom referral |

---

## WHAT REQUIRES HUMAN ACTION

The following cannot be automated and require you to act once:

| Action | When | Est. Time | Link |
|---|---|---|---|
| Buy domain (~$10) | Per site | 5 min | namecheap.com |
| Outscraper account + API key | Once | 10 min | outscraper.com |
| Cloudflare account | Once | 5 min | cloudflare.com |
| GitHub account | Once | 5 min | github.com |
| Anthropic API key (Claude) | Once | 5 min | console.anthropic.com |
| PartnerStack account | Once | 10 min | partnerstack.com |
| Bark.com affiliate signup | Once | 10 min | bark.com/affiliates |
| Google AdSense (after traffic) | After site has 1k visitors | 10 min | adsense.google.com |
| Stripe (for paid upgrades) | Once | 15 min | stripe.com |
| Google Search Console | Per site | 5 min | search.google.com/search-console |

**Total one-time setup time: ~75 minutes**
**Per site after setup: ~20 minutes** (domain + GSC + review)

---

## FILE OUTPUT STRUCTURE

After completing all 7 steps, your working directory should look like:

```
project/
├── data/
│   ├── raw_listings.csv          # Step 1 output
│   ├── clean_listings.csv        # Step 2 output
│   ├── verified_listings.csv     # Step 3 output
│   └── enriched_listings.csv     # Step 4 output
├── images/
│   └── {place_id}/
│       ├── photo_1.jpg           # Step 5 output
│       └── photo_2.jpg
├── dist/                         # Step 6 output (deploy this)
│   ├── index.html
│   ├── sitemap.xml
│   ├── robots.txt
│   ├── listings/
│   │   └── {slug}/index.html
│   ├── category/
│   │   └── {category}/index.html
│   ├── location/
│   │   └── {state}/{city}/index.html
│   └── blog/
│       └── {slug}/index.html
├── config/
│   ├── niche.json                # Niche config
│   └── affiliates.json           # Affiliate links
└── scripts/
    ├── 01_scrape.py
    ├── 02_clean.py
    ├── 03_verify.py
    ├── 04_enrich.py
    ├── 05_images.py
    ├── 06_generate.py
    └── 07_deploy.sh
```

---

## SCALING TO A PORTFOLIO

Once site #1 is live and indexed:
1. Reuse all scripts — change only `config/niche.json`
2. Target: 1 new directory every 2 weeks
3. At 5 sites: consolidate affiliate accounts, negotiate better rates
4. At 10 sites: portfolio worth $150k-500k on Flippa (30-40x monthly revenue)
5. Optionally: layer newsletter on each directory (Ghost CMS) for defensibility

**Compound effect:** Each new directory takes less time because:
- Scripts already written and tested
- Affiliate accounts already approved
- Domain/hosting patterns established
- SEO content templates reusable

---

*Runbook version 2.0 — Based on Frey Chu / Greg Isenberg methodology*
*Stack: Outscraper + Crawl4AI + Claude API + Static HTML + Cloudflare Pages*