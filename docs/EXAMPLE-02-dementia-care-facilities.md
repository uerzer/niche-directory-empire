# CONCRETE EXAMPLE 02: Dementia Care Facilities Directory
**Niche:** Memory care / dementia care facilities  
**Recommended by:** Frey Chu (Greg Isenberg podcast) as top-tier niche  
**Revenue model:** Referral fees ($500–$2,000/placement) + lead gen + AdSense  
**Score:** 23/25 (highest scored niche in our research)

---

## NICHE SNAPSHOT

| Field | Value |
|---|---|
| Niche | Dementia / memory care facilities |
| Geography | USA nationwide |
| Primary keyword | "dementia care facilities near me" |
| Monthly searches | ~50,000+ |
| Keyword difficulty | Medium-low (A Place for Mom dominates but is generic) |
| Competition gap | A Place for Mom is massive but sells leads; niche directory with rich data doesn't exist |
| Data source | Google Maps (Outscraper) + CMS (Centers for Medicare & Medicaid Services) free data |
| Build cost | ~$150-200 |
| Time to build | 4-5 days |
| Revenue potential | $5,000-20,000/month at maturity |

---

## WHY THIS NICHE WINS

1. **Highest LTV in any directory niche.** Memory care costs $4,000–$8,000/month per resident. Families research intensively before deciding. A referral is worth $500–$2,000 to a facility.
2. **Free government data available.** CMS Nursing Home Compare has every licensed facility in the USA — names, addresses, star ratings, bed counts, inspection scores. Free download. Zero scraping needed.
3. **Emotionally charged searches.** People searching are in crisis mode. They need information NOW. A clean, trustworthy directory wins instantly.
4. **A Place for Mom is hated.** Families hate being sold to. A directory that informs without a hard sell wins loyalty and converts better.
5. **Frey Chu specifically called this out** as a top-tier niche in the Greg Isenberg podcast.

---

## DATA SOURCE — CMS Free Government Data

**No Outscraper needed for this niche.**

```python
# Download directly — no API key required
# URL: https://data.cms.gov/provider-data/dataset/4pq5-n9py
# File: NH_ProviderInfo_[date].csv — updates monthly
# Records: ~15,000 certified nursing facilities nationwide
# Includes: name, address, phone, ownership type, bed count, 
#           overall star rating, health inspection rating, 
#           staffing rating, quality measure rating

import pandas as pd
import requests
import io

# Direct CSV download
CMS_URL = "https://data.cms.gov/provider-data/api/1/datastore/query/4pq5-n9py/0?offset=0&limit=10000&format=csv"

# Or download full dataset from:
# https://data.cms.gov/provider-data/dataset/4pq5-n9py

df = pd.read_csv("NH_ProviderInfo_Latest.csv")

# Filter to memory care / dementia specialists
memory_care = df[
    df["PROVNAME"].str.contains("memory|dementia|alzheimer|cognitive", case=False, na=False) |
    df["GNRL_CNTL_TYPE_CD"].isin(["Alzheimer Special Care Unit"])
].copy()

# Or take ALL nursing facilities and enrich to identify memory care
# (many facilities offer memory care as a wing, not reflected in name)
print(f"Total facilities: {len(df)}")
print(f"Memory care specific: {len(memory_care)}")
```

**CMS data fields available:**
- PROVNAME (facility name)
- ADDRESS, CITY, STATE, ZIP
- PHONE
- OVERALL_RATING (1-5 stars)
- HEALTH_INSPECTION_RATING
- STAFFING_RATING  
- QUALITY_MEASURE_RATING
- BEDCNT (licensed bed count)
- GNRL_CNTL_TYPE_CD (ownership type)
- CERTIFICATION (Medicare/Medicaid)
- PENALTIES (inspection violations count)

**This is better than Outscraper for this niche** — it's authoritative, free, and includes quality metrics families actually care about.

---

## ENRICHMENT FIELDS (Dementia-Specific)

```json
{
  "memory_care_certified": true,
  "bed_count": 48,
  "care_levels": ["Independent Living", "Assisted Living", "Memory Care", "Skilled Nursing"],
  "medicare_accepted": true,
  "medicaid_accepted": true,
  "private_pay_only": false,
  "monthly_cost_range": "$4,500 - $7,200",
  "staff_to_resident_ratio": "1:6 day shift",
  "secured_unit": true,
  "outdoor_spaces": true,
  "pet_friendly": false,
  "religious_affiliation": null,
  "languages_spoken": ["English", "Spanish"],
  "amenities": ["on-site chapel", "beauty salon", "therapy gym", "garden"],
  "activities": ["music therapy", "art therapy", "reminiscence groups"]
}
```

**Enrichment prompt:**
```
You are enriching a directory listing for a memory care / dementia care facility: {NAME}

CMS Government Data:
- Overall Star Rating: {OVERALL_RATING}/5
- Health Inspection Rating: {HEALTH_INSPECTION_RATING}/5
- Staffing Rating: {STAFFING_RATING}/5
- Licensed Beds: {BEDCNT}
- Medicare Certified: {MEDICARE}
- Medicaid Certified: {MEDICAID}
- Recent Penalties: {PENALTIES}

Website content (scraped):
{SITE_RAW}

Extract and return JSON:
{
  "description": "2-3 compassionate, factual sentences about this facility. Mention star rating and any standout qualities.",
  "care_levels": ["list of care levels offered"],
  "memory_care_certified": true/false/null,
  "monthly_cost_range": "range if found on site, else null",
  "secured_unit": true/false/null,
  "amenities": ["list of amenities"],
  "activities": ["therapeutic or recreational activities"],
  "pet_friendly": true/false/null,
  "languages": ["languages spoken by staff"],
  "religious_affiliation": "affiliation or null"
}

IMPORTANT: Be compassionate. Families in crisis read these. Never say negative things about a facility even if ratings are low — just present facts.
```

---

## SITE STRUCTURE

**config/niche.json:**
```json
{
  "site_name": "MemoryCareDirectory",
  "domain": "memorycaredirectory.com",
  "tagline": "Find Trusted Memory Care Facilities Near You",
  "description": "A comprehensive, independently verified directory of dementia and memory care facilities across the United States. Compare ratings, amenities, and costs.",
  "niche": "memory care facility",
  "niche_singular": "memory care facility",
  "location_type": "local",
  "primary_color": "#4f46e5",
  "accent_color": "#10b981"
}
```

**Pages generated:**
- ~8,000 facility listing pages (full CMS dataset)
- 50 state pages + 200+ major city pages
- Category pages: alzheimers-care, vascular-dementia, lewy-body-dementia, early-onset
- 10 blog posts (see below)
- sitemap.xml with ~8,500 URLs

**Scale advantage:** 8,000+ pages from day one = massive SEO footprint.

---

## MONETIZATION STACK

### Primary: Referral Fees — A Place for Mom Alternative

**A Place for Mom makes $500–$2,000 per successful placement.**
You can do the same thing without the hard sell:

1. Add "Help Me Find a Facility" intake form (Tally.so, free)
2. When family submits their criteria, contact 3 matching facilities
3. Charge facilities $200-500 per qualified family referral (they pay nothing until they convert)
4. At 5 referrals/month: $1,000-2,500/month

**Setup time:** 1 hour (form + email templates)

### Secondary: Paid Listings ($79-199/month)

High-value facilities spend $500-2,000/month on marketing. Your directory is cheap by comparison.

Pitch: "Families searching for dementia care in [City] find your facility at the top of MemoryCareDirectory.com. $99/month for priority placement + enhanced profile."

Target: 20 paying facilities × $99 = $1,980 MRR

### Tertiary: Google AdSense

Memory care CPCs are among the highest in healthcare: $8-25 per click.
At 5,000 visitors/month: $400-800/month AdSense revenue.

### Quaternary: BetterHelp / Telehealth Affiliate

For early-stage dementia families researching options:
- BetterHelp affiliate: 35% recurring commission on therapy subscriptions
- Teladoc affiliate: $50-100/signup
- Place naturally in blog posts about "early signs of dementia" etc.

---

## BLOG CONTENT (10 posts)

1. "How to Choose a Memory Care Facility for a Parent with Dementia"
2. "Memory Care vs Assisted Living: What's the Difference?"
3. "How Much Does Memory Care Cost? (2025 State-by-State Guide)"
4. "Medicare vs Medicaid for Memory Care: What's Actually Covered"
5. "10 Questions to Ask When Touring a Dementia Care Facility"
6. "Early Signs Your Loved One Needs Memory Care"
7. "How to Talk to a Parent About Moving to Memory Care"
8. "What a 5-Star CMS Rating Actually Means for Memory Care Facilities"
9. "Dementia Care Facility Red Flags: What to Watch For"
10. "Transitioning a Parent to Memory Care: A Step-by-Step Guide"

**SEO note:** These keywords have MASSIVE search volume (10k-50k/mo each) and high commercial intent. A single #1 ranking for "how much does memory care cost" = thousands of monthly visitors.

---

## COLD OUTREACH (Facility Administrators)

**Target:** Facility administrators and marketing directors (LinkedIn is best for finding them)

**Subject:** Your facility is listed on MemoryCareDirectory

**Body:**
```
Hi [Name],

I'm reaching out because [Facility Name] is listed on MemoryCareDirectory.com — 
a directory families use when researching memory care options in [City].

Your current CMS star rating of [X]/5 is prominently displayed. 

I'm offering enhanced listings to founding facilities this quarter:
- Priority placement in [City] search results
- Photo gallery + virtual tour embed
- "Family Reviews" widget
- Monthly inquiry reports

Founding price: $99/month (increasing to $199 at Q2)

Worth a 15-minute call?

[Your name]
MemoryCareDirectory.com
```

---

## DOMAIN OPTIONS
- memorycaredirectory.com ✓
- dementiacarefinder.com
- memorycarefacilities.com
- alzheimerscareguide.com

---

## ETHICAL CONSIDERATIONS

This niche involves vulnerable families. Build accordingly:
- Never manipulate emotionally in copy
- Display CMS star ratings prominently and honestly
- Never take hidden payments to rank bad facilities above good ones
- Clearly disclose if a listing is "sponsored" vs organic
- Provide genuinely useful content (the blog posts above save families weeks of research)

**Being ethical IS the moat.** Families recommend trustworthy resources to each other. A Place for Mom has terrible reviews because they hard-sell. You win by being the opposite.
