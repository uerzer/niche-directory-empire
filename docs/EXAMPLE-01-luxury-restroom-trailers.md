# CONCRETE EXAMPLE 01: Luxury Restroom Trailer Directory
**Based on:** Frey Chu's actual build (Greg Isenberg podcast, Feb 2026)  
**Result:** $273/day ($8,190/month) in 4 days for under $250  
**Status:** Proven, replicable

---

## NICHE SNAPSHOT

| Field | Value |
|---|---|
| Niche | Luxury restroom trailer rental |
| Geography | USA nationwide |
| Primary keyword | "luxury restroom trailer rental near me" |
| Monthly searches | ~40,000 |
| Keyword difficulty | Low (no dominant niche directory) |
| Competition gap | Top results: generic Yelp, outdated directories |
| Build cost | Under $250 |
| Time to build | 4 days |
| Revenue at launch | $273/day (lead gen) |

---

## WHY THIS NICHE WORKS

1. **High ticket:** Luxury restroom trailers rent for $2,000–$5,000/day. Businesses pay generously for leads.
2. **Decision research phase:** Event planners, wedding coordinators, and corporate buyers research before buying — they use directories.
3. **Data moat:** Enriched, verified, image-rich listings are impossible to replicate via simple Google Maps search.
4. **No dominant player:** Nobody owns "luxury restroom trailers" the way Zillow owns real estate.
5. **Recurring demand:** Weddings, festivals, corporate events — year-round need.

---

## STEP-BY-STEP EXECUTION

### Day 1 — Scrape & Clean

**Outscraper queries to run:**
```python
queries = [
    "luxury restroom trailer rental",
    "VIP portable restroom rental",
    "luxury porta potty rental",
    "upscale restroom trailer rental",
    "portable luxury bathroom rental",
    "restroom trailer rental wedding",
    "event restroom trailer rental"
]
# Expected yield: 300-500 raw records across USA
```

**Expected after cleaning:**
- Input: ~450 records
- After removing closed/dupes: ~280 records
- With websites: ~180 records
- Featured candidates (quality score ≥7): ~60 records

---

### Day 2 — Verify & Enrich

**Crawl4AI verification targets:** Every record with a website URL (~180 sites)

**Enrichment fields specific to this niche:**
```json
{
  "unit_types": ["Standard", "Luxury", "VIP", "Royal Flush", "Spa"],
  "capacity_range": "2-stall to 10-stall configurations",
  "amenities": ["AC/Heat", "Vanity mirrors", "Flush toilets", "Running water", "Music system", "Ambient lighting"],
  "ada_compliant": true,
  "power_required": "standard 20-amp outlet or generator",
  "service_areas": ["Texas", "California", "Florida"],
  "minimum_rental": "4-hour minimum typical",
  "delivery_radius": "up to 150 miles"
}
```

**Image extraction focus:** Look for photos of the trailers themselves — exterior shots, interior setup, event photos. Filter out: logos, staff headshots, generic stock.

**Enrichment prompt (niche-specific):**
```
You are enriching a directory listing for a luxury restroom trailer rental company: {NAME}

From the website content below, extract:
1. description: 2-3 sentence professional description emphasizing luxury/quality
2. unit_types: types of trailers offered (VIP, Royal, standard, etc.)
3. capacity: stall configurations available (e.g., "2 to 8 stalls")
4. amenities: list of luxury features (AC, mirrors, music, etc.)
5. service_areas: geographic areas served
6. ada_compliant: true/false/null
7. events_served: types of events they serve (weddings, corporate, festivals, etc.)

Website content:
{SITE_RAW}

Return ONLY valid JSON. Use null for unknown fields.
```

---

### Day 3 — Build Site

**config/niche.json:**
```json
{
  "site_name": "LuxuryRestroomFinder",
  "domain": "luxuryrestroomfinder.com",
  "tagline": "Find Premium Portable Restroom Trailers for Your Event",
  "description": "The most complete directory of luxury and VIP restroom trailer rental companies in the United States. Find verified providers for weddings, corporate events, and festivals.",
  "niche": "luxury restroom trailer rental",
  "niche_singular": "luxury restroom trailer company",
  "location_type": "local",
  "primary_color": "#1e3a5f",
  "accent_color": "#c9a84c"
}
```

**config/affiliates.json:**
```json
{
  "global_cta": {
    "text": "Get Free Quotes from Top Providers",
    "url": "https://bark.com/find/restroom-trailer-hire/?ref=YOUR_REF",
    "type": "lead_gen"
  },
  "listing_cta": {
    "text": "Request a Free Quote",
    "url_template": "https://bark.com/find/restroom-trailer-hire/?ref=YOUR_REF",
    "type": "lead_gen"
  },
  "sidebar_cta": {
    "text": "Compare Restroom Trailer Prices",
    "url": "https://bark.com/find/restroom-trailer-hire/?ref=YOUR_REF",
    "type": "comparison"
  }
}
```

**Pages generated:**
- 280 listing pages (one per verified company)
- ~18 category pages: wedding, corporate-events, festivals, outdoor-weddings, ada-accessible, etc.
- ~45 state/city location pages
- 10 blog posts (see below)
- sitemap.xml with 353 URLs

**10 blog post targets:**
1. "How Much Does Luxury Restroom Trailer Rental Cost? (2025 Guide)"
2. "Luxury Restroom Trailer vs Standard Porta Potty: What's the Difference?"
3. "How Many Restroom Trailers Do I Need for My Wedding?"
4. "Best Luxury Restroom Trailers for Outdoor Weddings"
5. "Corporate Event Restroom Trailer Checklist"
6. "ADA-Accessible Restroom Trailer Rental Guide"
7. "Festival Restroom Solutions: Luxury vs Standard"
8. "Restroom Trailer Rental Tips from Event Planners"
9. "VIP Bathroom Trailer Rental for Construction Sites"
10. "How to Choose a Restroom Trailer Rental Company"

---

### Day 4 — Deploy + Submit

```bash
# Buy domain: luxuryrestroomfinder.com (~$10 on Namecheap)
# Deploy:
wrangler pages deploy ./dist --project-name=luxuryrestroomfinder

# Point domain in Cloudflare dashboard (5 min)
# Submit sitemap to Google Search Console
```

---

## MONETIZATION STACK

### Primary: Lead Generation (Month 1+)
**Method:** Inquiry form on every listing page → sell leads to businesses

Lead value in this niche: $50-150/qualified lead
- "I need a 4-stall luxury trailer for a wedding in Austin on June 15, 100 guests, budget $2,000" = $100 lead
- Sell to 3 competing businesses = $300 revenue from 1 lead

**Setup:**
1. Add Typeform/Tally inquiry form to all listing pages
2. Route submissions to your email
3. Forward to 2-3 businesses in that city
4. Charge $75-150/lead on net-30 terms

### Secondary: Bark.com Affiliate (Month 1+)
- No setup beyond affiliate signup
- Replace "Get Quote" buttons with Bark referral links
- Earn $50-100 per submitted request
- Fully passive — no fulfillment

### Tertiary: Sponsored Listings (Month 2+)
- Email high-quality-score businesses
- Offer homepage featured slot: $199/month
- Offer priority placement in their city: $79/month
- Target: 5 sponsors × $99/month = $495 MRR

### Long-term: AdSense (Month 6+)
- Apply once traffic hits 1,000+ visitors/month
- Event/luxury CPM: $4-8
- At 5,000 visitors/month: $200-400/month additional

---

## REVENUE PROJECTION

| Month | Visitors | Revenue Source | Est. Revenue |
|---|---|---|---|
| 1-2 | 50-200 | None (indexing) | $0 |
| 3 | 200-500 | First affiliate clicks | $50-200 |
| 4-5 | 500-2,000 | Affiliate + first leads | $300-800 |
| 6 | 2,000-5,000 | Leads + sponsors + AdSense | $1,000-3,000 |
| 9-12 | 5,000-15,000 | Full stack | $3,000-8,000 |

**Frey Chu's actual result:** $273/day = $8,190/month. His site had been live ~6 months before the podcast.

---

## COLD OUTREACH SCRIPT (Specific to this niche)

**Subject:** Your restroom trailer company is listed on LuxuryRestroomFinder

**Body:**
```
Hi [Name],

I found [Company Name] while building LuxuryRestroomFinder.com — a directory specifically for luxury and VIP restroom trailer rental companies.

Your listing is live: https://luxuryrestroomfinder.com/listings/[slug]/

We're already getting search traffic for "luxury restroom trailer rental [City]" and similar keywords.

I'm offering free verified badges + photo galleries to founding members this month. Want me to send the upgrade link?

[Your name]
LuxuryRestroomFinder.com
```

---

## DOMAIN OPTIONS
- luxuryrestroomfinder.com ✓ (recommended)
- viprestroomtrailers.com
- premiumrestroomrental.com
- eliterestroomtrailers.com

---