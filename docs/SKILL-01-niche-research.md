# SKILL: Niche Research & Validation
**Skill ID:** SKILL-01  
**Version:** 1.0  
**Depends on:** None (first step)  
**Outputs to:** SKILL-02 (data scrape)  
**Portable to:** Any LLM agent with web search access

---

## PURPOSE
Evaluate a niche idea and return a scored go/no-go decision with exact data sources, affiliate matches, and keyword targets. Zero guessing. Every claim backed by a data point.

---

## INPUTS
- `niche_idea` (string) — e.g. "luxury restroom trailers", "dementia care facilities", "AI writing tools"
- `target_geography` (string) — e.g. "USA", "UK", "Texas", "nationwide"

---

## OUTPUTS
A JSON object saved as `niche_report.json`:
```json
{
  "niche": "luxury restroom trailers",
  "geography": "USA",
  "go_decision": true,
  "total_score": 22,
  "monthly_search_volume": 40000,
  "top_keywords": [],
  "competition_gap": "existing directories outdated, poorly monetized",
  "data_sources": [],
  "affiliate_programs": [],
  "monetization_primary": "lead gen",
  "estimated_revenue_at_maturity": "$2000-5000/month",
  "outscraper_query": "",
  "recommended_domain_keywords": []
}
```

---

## STEP-BY-STEP EXECUTION

### Step 1.1 — Keyword Research
Search the web for:
- `"[niche] near me"` — check Google autocomplete suggestions
- `"[niche] [city]"` for 3-5 major US cities
- `"best [niche]"`, `"[niche] directory"`, `"[niche] list"`

For each keyword, estimate:
- **Monthly search volume** — use Google Keyword Planner data in search results, or Ahrefs blog posts referencing volume
- **Keyword difficulty** — look for existing ranking pages; if page 1 has DA<40 sites, difficulty is low
- **CPC** — if CPC > $2, commercial intent is confirmed

**Minimum threshold to proceed:** Primary keyword > 5,000 monthly searches OR 3+ long-tail keywords > 1,000 each.

### Step 1.2 — Competition Audit
Search Google for: `"[niche] directory"`, `"list of [niche]"`, `"[niche] near me"`

For each top-5 result, record:
- Domain name
- Estimated quality (does it have photos? Rich data? Updated recently?)
- Monetization visible (ads? paid listings? lead forms?)
- Approximate DA (check if it's a known brand or obscure site)

**Gap signal:** If top results are Yelp/Google Maps (generic, not niche-specific) OR outdated directories (last updated 2+ years ago), the gap is real.

### Step 1.3 — Data Source Identification
Identify where listing data will come from. Check in this order:

1. **Google Maps** (via Outscraper) — works for any local business category
2. **Government registries** — healthcare (NPI API), law (state bar sites), finance (SEC)
3. **Industry associations** — often have public member directories
4. **Existing directories** — if a competitor has a public list, it's scrapeable
5. **LinkedIn company search** — for B2B niches

Record the Outscraper query string: e.g. `"luxury restroom trailer rental usa"`

### Step 1.4 — Affiliate Program Research
Search for: `"[niche] affiliate program"`, `"[niche] lead generation"`, `"pay per lead [niche]"`

Also check:
- PartnerStack.com — search for SaaS tools in the niche
- ShareASale.com — browse merchant categories
- CJ Affiliate — search by category
- Bark.com — check if niche is listed (pays $50-100/lead for service businesses)
- Specific industry platforms (e.g. Housecall Pro for contractors)

**Minimum viable affiliate:** At least one program paying $25+ per action OR AdSense CPC > $3 for the niche.

### Step 1.5 — Score & Decision

Score on 5 dimensions, 1-5 each:

| Dimension | 1 | 3 | 5 |
|---|---|---|---|
| Search Volume | <1k/mo | 5-20k/mo | >20k/mo |
| Competition Gap | Dominated by brands | Mixed quality | Outdated/generic only |
| Data Availability | Must build manually | Partial public data | Full public data |
| Affiliate Match | None found | $10-25/action | $50+/action |
| Buyer Intent (CPC) | <$0.50 | $1-3 | >$3 |

**Decision:**
- Score 20-25: Strong go. Start immediately.
- Score 15-19: Conditional go. Validate one more dimension.
- Score 10-14: Weak. Find better niche.
- Score <10: Pass.

---

## AGENT PROMPT (copy-paste ready)

```
You are a niche research specialist for directory website businesses.

Your task: Evaluate whether "[NICHE_IDEA]" in "[GEOGRAPHY]" is a viable niche for a directory website.

Using web search, research the following and return a complete niche_report.json:

1. Search "[NICHE_IDEA] near me" and note the top 5 Google results — are they generic (Yelp/Google Maps) or specific directories?
2. Estimate monthly search volume for the primary keyword
3. Identify 3-5 long-tail keyword variants with estimated volume
4. Find the best public data source for scraping listings (Google Maps category name, government API, or industry registry)
5. Search for affiliate programs paying $25+ per action for this niche
6. Score the niche on the 5-dimension rubric (1-5 each)
7. Return go/no-go decision with total score

Output ONLY the JSON object. No commentary.
```

---

## EXAMPLE OUTPUT (Luxury Restroom Trailers)
```json
{
  "niche": "luxury restroom trailer rental",
  "geography": "USA",
  "go_decision": true,
  "total_score": 22,
  "monthly_search_volume": 40000,
  "top_keywords": [
    {"keyword": "luxury restroom trailer rental near me", "volume": 18000, "difficulty": "low", "cpc": 4.50},
    {"keyword": "VIP restroom trailer rental", "volume": 8000, "difficulty": "low", "cpc": 3.80},
    {"keyword": "portable luxury bathroom rental", "volume": 6500, "difficulty": "low", "cpc": 3.20},
    {"keyword": "luxury porta potty rental", "volume": 7500, "difficulty": "low", "cpc": 2.90}
  ],
  "competition_gap": "Top results are generic Yelp pages and one outdated 2019 directory. No specialized, data-rich directory exists.",
  "data_sources": [
    {"source": "Google Maps via Outscraper", "query": "luxury restroom trailer rental usa", "estimated_records": 300},
    {"source": "Google Maps via Outscraper", "query": "VIP portable restroom rental usa", "estimated_records": 150}
  ],
  "affiliate_programs": [
    {"name": "Lead generation (direct)", "payout": "$50-150/qualified lead", "source": "Sell to listed businesses"},
    {"name": "Eventbrite affiliate", "payout": "5% commission", "source": "eventbrite.com/affiliates"},
    {"name": "Google AdSense", "payout": "$3-6 CPM (event searches)", "source": "adsense.google.com"}
  ],
  "monetization_primary": "lead_generation",
  "monetization_secondary": "sponsored_listings",
  "estimated_revenue_at_maturity": "$3000-8000/month",
  "outscraper_query": "luxury restroom trailer rental",
  "recommended_domain_keywords": ["luxuryrestroomtrailers", "vipresstroomrental", "luxuryportablebathrooms"]
}
```