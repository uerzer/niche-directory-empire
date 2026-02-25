# CONCRETE EXAMPLE 03: AI Tools by Use Case Directory
**Niche:** AI tools organized by job-to-be-done / use case  
**Our addition:** Not in the Frey Chu video — identified through affiliate research  
**Revenue model:** PartnerStack recurring affiliates (20-50%) + sponsored listings + AdSense  
**Score:** 19/25 — strong affiliate match, fast-moving data, no scraping risk

---

## NICHE SNAPSHOT

| Field | Value |
|---|---|
| Niche | AI tools directory by use case |
| Geography | Global (English-speaking) |
| Primary keyword | "best AI tools for [use case]" |
| Monthly searches | 500k+ across all use-case variants |
| Keyword difficulty | Medium (Futurepedia, TAAFT exist but are poorly monetized) |
| Competition gap | Existing directories have weak UX, no recurring affiliate links, outdated |
| Data source | ProductHunt API + vendor websites (public, no scraping risk) |
| Build cost | ~$100 (Claude API for enrichment only) |
| Time to build | 3-4 days |
| Revenue potential | $2,000-10,000/month at maturity (recurring affiliate compound) |

---

## WHY THIS NICHE IS DIFFERENT

**No location data needed.** This is a purely digital product directory — no Outscraper, no Google Maps. All data is publicly listed by the vendors themselves on their own websites and ProductHunt.

**Affiliate stacks compound over time.** Every tool you refer a user to that signs up pays you 20-50% recurring for months or years. A single referred annual subscriber to a $100/month tool = $240-600 in affiliate revenue from one click.

**Content stays fresh automatically.** New AI tools launch weekly. Each new tool = a new page = new SEO signal. The directory self-refreshes.

**Competitors are sitting on gold they're not mining.** Futurepedia (200k+ monthly visitors) and There's An AI For That both have minimal affiliate integration. They're leaving millions on the table.

---

## DATA SOURCES (No Outscraper Needed)

### Source 1: ProductHunt API
```python
# Free tier: no API key needed for basic queries
# Full access: apply at api.producthunt.com

import requests

def fetch_ai_tools_from_producthunt(pages=20):
    GRAPHQL_URL = "https://api.producthunt.com/v2/api/graphql"
    headers = {"Authorization": f"Bearer {PRODUCTHUNT_TOKEN}"}
    
    all_tools = []
    after_cursor = None
    
    for page in range(pages):
        query = """
        query($topic: String!, $after: String) {
          posts(topic: $topic, order: VOTES, after: $after, first: 50) {
            edges {
              node {
                id slug name tagline description
                website votesCount reviewsRating
                topics { edges { node { name slug } } }
                thumbnail { url }
                pricingType
                maker { name twitterUsername }
              }
            }
            pageInfo { endCursor hasNextPage }
          }
        }
        """
        variables = {"topic": "artificial-intelligence", "after": after_cursor}
        resp = requests.post(GRAPHQL_URL, json={"query": query, "variables": variables}, headers=headers)
        data = resp.json()["data"]["posts"]
        
        for edge in data["edges"]:
            n = edge["node"]
            all_tools.append({
                "name": n["name"],
                "slug": n["slug"],
                "tagline": n["tagline"],
                "description": n["description"][:500] if n.get("description") else "",
                "website": n.get("website", ""),
                "votes": n.get("votesCount", 0),
                "rating": n.get("reviewsRating"),
                "pricing_type": n.get("pricingType", ""),
                "thumbnail": n.get("thumbnail", {}).get("url", ""),
                "topics": [t["node"]["name"] for t in n.get("topics", {}).get("edges", [])],
                "maker_twitter": n.get("maker", {}).get("twitterUsername", "")
            })
        
        if not data["pageInfo"]["hasNextPage"]:
            break
        after_cursor = data["pageInfo"]["endCursor"]
    
    return all_tools
```

### Source 2: Manual curated list (seed data)
Supplement ProductHunt with manually curated entries for tools not on PH:
```csv
name,website,category,pricing_model,description
ChatGPT,https://chat.openai.com,Writing/Chat,Freemium,"OpenAI's conversational AI assistant"
Claude,https://claude.ai,Writing/Chat,Freemium,"Anthropic's AI assistant"
Midjourney,https://midjourney.com,Image Generation,Paid,"AI image generation via Discord"
Runway,https://runwayml.com,Video Generation,Freemium,"AI video creation and editing"
Cursor,https://cursor.sh,Coding,Freemium,"AI-powered code editor"
Perplexity,https://perplexity.ai,Research,Freemium,"AI-powered search engine"
...
```

### Source 3: Crawl4AI verification + enrichment
Visit each tool's website to extract:
- Current pricing (free/freemium/paid, price points)
- API availability
- Key integrations
- Primary use cases from their own copy

---

## USE CASE TAXONOMY (the secret sauce)

Most AI tool directories sort by category (Writing, Image, Video). Sort by **job to be done** instead — this matches how people actually search.

```json
{
  "use_cases": {
    "write-blog-posts": ["Jasper", "Writesonic", "Copy.ai", "Koala"],
    "generate-images": ["Midjourney", "DALL-E 3", "Stable Diffusion", "Ideogram"],
    "edit-videos": ["Runway", "Pika", "Kling", "HeyGen"],
    "write-code": ["Cursor", "GitHub Copilot", "Codeium", "Tabnine"],
    "transcribe-audio": ["Whisper", "Otter.ai", "Fireflies", "Descript"],
    "summarize-documents": ["Claude", "ChatGPT", "Perplexity", "NotebookLM"],
    "create-presentations": ["Gamma", "Beautiful.ai", "Tome", "Pitch"],
    "automate-workflows": ["Zapier AI", "Make.com", "n8n", "Activepieces"],
    "analyze-data": ["Julius", "ChatCSV", "Rows", "DataSquirrel"],
    "manage-social-media": ["Buffer AI", "Publer", "Lately", "Predis.ai"],
    "build-chatbots": ["Botpress", "Voiceflow", "Landbot", "Tidio AI"],
    "research-competitors": ["Perplexity", "Crayon", "Semrush", "Exploding Topics"],
    "generate-leads": ["Clay", "Apollo AI", "Instantly", "Lemlist"],
    "create-videos": ["HeyGen", "Synthesia", "D-ID", "Colossyan"],
    "write-emails": ["Lavender", "Smartwriter", "Regie.ai", "Reply.io"]
  }
}
```

**This is the moat.** When someone searches "AI tools to write blog posts" or "AI that summarizes PDFs", your use-case pages rank. Futurepedia can't compete because they organize by category, not job.

---

## ENRICHMENT FIELDS (AI Tools-Specific)

```json
{
  "name": "Jasper AI",
  "slug": "jasper-ai",
  "tagline": "AI copilot for marketing teams",
  "description": "Jasper is an AI writing assistant trained on marketing copy. Used by 100k+ businesses for blog posts, ad copy, emails, and social content.",
  "website": "https://jasper.ai",
  "pricing_model": "subscription",
  "price_starting_at": "$39/month",
  "free_tier": false,
  "free_trial_days": 7,
  "api_available": true,
  "use_cases": ["blog-posts", "ad-copy", "social-media", "emails"],
  "integrations": ["Surfer SEO", "Zapier", "Chrome Extension", "Google Docs"],
  "best_for": "Marketing teams and content agencies",
  "not_great_for": "Technical/code writing",
  "affiliate_program": {
    "network": "PartnerStack",
    "commission": "30% recurring",
    "cookie_days": 30,
    "affiliate_url": "https://jasper.partnerstack.com"
  },
  "alternatives": ["writesonic", "copy-ai", "koala"],
  "votes_producthunt": 2847,
  "rating": 4.6,
  "founded_year": 2021,
  "company_stage": "Series A ($125M raised)"
}
```

**Enrichment prompt:**
```
You are enriching a directory listing for an AI software tool: {NAME}

Website content (scraped):
{SITE_RAW}

Extract and return JSON:
{
  "description": "2-3 sentence description for a non-technical audience. What problem does it solve? Who uses it?",
  "pricing_model": "free | freemium | subscription | usage-based | one-time",
  "price_starting_at": "lowest paid tier price or null",
  "free_tier": true/false,
  "free_trial_days": number or null,
  "api_available": true/false/null,
  "use_cases": ["job-to-be-done list, max 5, use kebab-case"],
  "best_for": "one sentence — ideal user persona",
  "integrations": ["list of key integrations mentioned, max 6"],
  "founded_year": year or null,
  "company_stage": "description if mentioned"
}

Return ONLY JSON. Use null for unknown fields.
```

---

## AFFILIATE RESEARCH PER TOOL

Before publishing each tool page, check PartnerStack for its affiliate program:

```python
# Manual lookup — build this table as you go
AFFILIATE_PROGRAMS = {
    "jasper": {"network": "PartnerStack", "commission": "30% recurring", "url": "https://jasper.partnerstack.com"},
    "writesonic": {"network": "PartnerStack", "commission": "30% recurring", "url": "https://writesonic.partnerstack.com"},
    "copy-ai": {"network": "PartnerStack", "commission": "45% recurring 12mo", "url": "https://copy-ai.partnerstack.com"},
    "semrush": {"network": "Impact", "commission": "$200/sale", "url": "https://semrush.com/affiliates"},
    "notion": {"network": "PartnerStack", "commission": "$5-50/signup", "url": "https://notion.partnerstack.com"},
    "hubspot": {"network": "HubSpot", "commission": "$250-1000/sale", "url": "https://hubspot.com/partners/affiliates"},
    "surfer-seo": {"network": "PartnerStack", "commission": "25% recurring", "url": "https://surferseo.partnerstack.com"},
    "zapier": {"network": "PartnerStack", "commission": "referral credit", "url": "https://zapier.partnerstack.com"},
}
```

**On each tool's listing page:** Show the affiliate CTA naturally:
```html
<!-- Embedded naturally in listing page -->
<div class="try-cta">
  <a href="{affiliate_url}" class="try-btn" target="_blank" rel="noopener sponsored">
    Try {name} Free →
  </a>
  {% if free_trial_days %}
  <span class="trial-note">{{ free_trial_days }}-day free trial</span>
  {% endif %}
</div>
```

---

## SITE STRUCTURE

**config/niche.json:**
```json
{
  "site_name": "AIToolsIndex",
  "domain": "aitoolsindex.com",
  "tagline": "Find the Right AI Tool for Any Job",
  "description": "The most organized directory of AI tools, sorted by what you're actually trying to do. 500+ tools across 50+ use cases.",
  "niche": "AI software tools",
  "niche_singular": "AI tool",
  "location_type": "digital",
  "primary_color": "#6d28d9",
  "accent_color": "#f59e0b"
}
```

**Pages generated (500 tools):**
- 500 individual tool pages
- 50 use-case pages ("Best AI Tools for Writing Blog Posts")
- 15 category pages (Writing, Coding, Image, Video, etc.)
- 20 comparison pages ("Jasper vs Copy.ai", "Midjourney vs DALL-E")
- 10 blog posts ("Best Free AI Tools 2025", etc.)
- Sitemap: ~600 URLs

**Comparison pages are high-value:**
- "Jasper vs Writesonic" — 2,000+ monthly searches
- "ChatGPT vs Claude" — 50,000+ monthly searches
- These rank fast because they're highly specific intent

```python
# Auto-generate comparison pages for top tool pairs
comparisons = [
    ("chatgpt", "claude"),
    ("jasper", "writesonic"),
    ("midjourney", "dalle-3"),
    ("cursor", "github-copilot"),
    ("otter-ai", "fireflies"),
]
for tool_a, tool_b in comparisons:
    render("comparison.html", f"dist/compare/{tool_a}-vs-{tool_b}/index.html",
           tool_a=get_tool(tool_a), tool_b=get_tool(tool_b))
```

---

## MONETIZATION STACK

### Primary: PartnerStack Recurring Affiliates

**Math example:**
- 1,000 visitors/month click "Try Jasper" 
- 3% convert to paid ($39/month)
- = 30 customers × $39 × 30% commission = $351/month from one tool page
- 50 tool pages with similar traffic = $17,550/month

This compounds because:
- Affiliate commissions are recurring (you earn every month they stay)
- Each new tool launched = new page = new traffic
- Rankings compound over time

### Secondary: Sponsored "Featured" Placements

AI tool companies spend millions on marketing. Your directory listing is cheap:
- Homepage featured slot: $299/month
- Use-case page featured slot: $149/month
- Email to top 50 tools: "You're listed. Want to be featured?"

### Tertiary: "Verified" Badge Program

Charge tools to get a "Verified by AIToolsIndex" badge:
- Verification: $199 one-time (you review their claims, check if free tier is real, etc.)
- Renewal: $49/year
- Target: 100 tools × $49 = $4,900/year passive

### Quaternary: AdSense
- AI tool searches have CPM of $4-10
- At 10,000 visitors/month = $400-1,000/month

---

## BLOG POSTS (10 targeted)

1. "Best Free AI Tools in 2025 (Tested and Ranked)"
2. "AI Tools That Save the Most Time for Solopreneurs"
3. "Best AI Writing Assistants Compared: Jasper vs Writesonic vs Copy.ai"
4. "The Only AI Tools Guide You Need for Content Creation"
5. "AI Tools for Small Business Owners: What's Worth Paying For"
6. "ChatGPT vs Claude: Which AI Assistant Should You Use?"
7. "Best AI Image Generators: Midjourney vs DALL-E vs Stable Diffusion"
8. "AI Tools for Developers: Cursor vs Copilot vs Codeium"
9. "How to Choose an AI Tool for Your Specific Use Case"
10. "AI Tools That Actually Replace Manual Work (Not Just Assist)"

---

## REVENUE PROJECTION

| Month | Tools Indexed | Monthly Visitors | Est. Revenue |
|---|---|---|---|
| 1-2 | 500 | 200-500 | $0 (indexing) |
| 3-4 | 600 | 500-2,000 | $100-500 |
| 5-6 | 700 | 2,000-8,000 | $500-2,000 |
| 9-12 | 1,000+ | 8,000-30,000 | $2,000-10,000 |

**Compounding factor:** New AI tools launch weekly. Each one you add first = SEO first-mover on that tool's name.

---

## COMPETITIVE EDGE OVER FUTUREPEDIA / TAAFT

| Feature | Futurepedia | There's An AI For That | AIToolsIndex |
|---|---|---|---|
| Organization | Category | Category | Use case (job-to-be-done) |
| Affiliate links | Minimal | None | Every tool page |
| Comparison pages | None | None | Auto-generated |
| Pricing data | Partial | Partial | Verified per tool |
| Free tier flag | No | No | Yes (key filter) |
| API availability | No | No | Yes (dev audience) |
| Alternatives section | No | No | Yes (internal links) |
| Data freshness | Weekly manual | Weekly manual | Automated weekly crawl |

---

## DOMAIN OPTIONS
- aitoolsindex.com ✓
- theaitoolbox.com
- aitoolsfinder.com
- usecaseai.com (emphasizes use-case angle)
- aiforwork.com
