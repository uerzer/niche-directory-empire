# SKILL: SEO Setup & Content Generation
**Skill ID:** SKILL-06  
**Version:** 1.0  
**Depends on:** SKILL-05 → `dist/` site  
**Outputs to:** Live indexed site  
**Portable to:** Any LLM with web access + Python env

---

## PURPOSE
Get the directory ranking fast. Submit to Google, generate supporting blog content targeting long-tail keywords, set up internal linking, and establish the authority signals Google needs to index and rank the site.

---

## INPUTS
- `dist/` — live deployed site
- `config/niche.json`
- `data/enriched_listings.csv`
- Live domain (must be pointing to Cloudflare Pages)

## OUTPUTS
- Site submitted to Google Search Console
- 10 blog posts in `dist/blog/`
- Internal linking structure complete
- Meta tags optimized on all pages

---

## SEO CHECKLIST (run immediately after deploy)

### 6.1 — Google Search Console Setup
**Human action required** (5 min):
1. Go to https://search.google.com/search-console
2. Add property → Domain type → enter your domain
3. Verify via DNS TXT record (Cloudflare makes this one click)
4. Submit sitemap: `https://yourdomain.com/sitemap.xml`
5. Request indexing on homepage

### 6.2 — On-Page SEO (automated at build time in SKILL-05)
Verify these are present on every listing page:
- [ ] `<title>` — format: `{Business Name} | {City} {Niche} | {SiteName}`
- [ ] `<meta name="description">` — 150-160 chars, includes city + niche keyword
- [ ] `<link rel="canonical">` — points to itself
- [ ] `<h1>` — exactly one, contains business name
- [ ] JSON-LD LocalBusiness schema
- [ ] OG tags for social sharing

**Title formula for listing pages:**
```
{Business Name} — {Niche} in {City}, {State} | {SiteName}
Example: "ABC Luxury Trailers — Restroom Trailer Rental in Austin, TX | LuxuryRestroomFinder"
```

**Title formula for location pages:**
```
{Niche} in {City}, {State} — {Count} Companies | {SiteName}
Example: "Luxury Restroom Trailer Rental in Dallas, TX — 14 Companies | LuxuryRestroomFinder"
```

**Title formula for category pages:**
```
{Category} {Niche} — Find the Best | {SiteName}
Example: "Wedding Restroom Trailer Rental — Find the Best | LuxuryRestroomFinder"
```

---

## 6.3 — BLOG CONTENT GENERATION

Generate 10 supporting articles targeting long-tail keywords. These drive organic traffic and link internally to listing/category pages.

### Blog Post Prompt Template

```
You are an SEO content writer for {SITE_NAME}, a directory of {NICHE} companies.

Write a complete blog post for the keyword: "{TARGET_KEYWORD}"

Requirements:
- Length: 800-1200 words
- Tone: Helpful, informative, not salesy
- Structure: H1, intro paragraph, 3-5 H2 sections, conclusion with CTA
- Naturally mention {SITE_NAME} once as a resource
- Include internal links to: /category/{CATEGORY_SLUG}/ and /location/{STATE}/
- Use real, accurate information (no fabrication)
- End with: "Find {NICHE} companies near you on {SITE_NAME} →"

Target keyword: {TARGET_KEYWORD}
Word count: 1000
Output: Full HTML article content (just the <article> body, not full page)
```

### Keyword Targets by Niche

**Luxury Restroom Trailers:**
```json
[
  "how much does luxury restroom trailer rental cost",
  "luxury restroom trailer vs standard porta potty",
  "wedding restroom trailer rental guide",
  "restroom trailer checklist for outdoor events",
  "luxury portable bathroom rental for corporate events",
  "ADA accessible restroom trailer rental",
  "how many restroom trailers do I need for my event",
  "restroom trailer rental tips for festival organizers",
  "luxury porta potty rental vs permanent restroom",
  "what to look for in a restroom trailer rental company"
]
```

**Dementia Care Facilities:**
```json
[
  "how to choose a memory care facility for a parent",
  "signs your loved one needs memory care",
  "difference between assisted living and memory care",
  "how much does memory care cost per month",
  "questions to ask when touring a dementia care facility",
  "Medicare vs Medicaid for memory care coverage",
  "early stage dementia care options at home vs facility",
  "how to transition a parent to memory care",
  "dementia care facility accreditation what to look for",
  "memory care facility red flags checklist"
]
```

**AI Tools:**
```json
[
  "best AI writing tools compared 2025",
  "free AI tools for small business owners",
  "AI tools that replace employees tasks",
  "how to choose the right AI tool for your workflow",
  "AI image generation tools comparison",
  "AI tools for content creators complete guide",
  "best AI coding assistants for developers",
  "AI tools for marketing teams",
  "AI automation tools that save the most time",
  "AI tools pricing guide freemium vs paid"
]
```

### Blog Generation Script

```python
# scripts/generate_blog.py
import anthropic
import json
import os
import re
from jinja2 import Environment, FileSystemLoader

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

with open("config/niche.json") as f:
    NICHE = json.load(f)

KEYWORDS = [
    # paste keyword list here
]

def generate_post(keyword: str) -> dict:
    prompt = f"""Write a complete, helpful blog post for a directory website called {NICHE['site_name']}.

Target keyword: "{keyword}"
Site niche: {NICHE['niche']}
Site URL: https://{NICHE['domain']}

Requirements:
- 900-1100 words
- HTML format (use <h2>, <p>, <ul>, <strong> tags)
- Helpful and informative, not promotional
- Mention {NICHE['site_name']} naturally once as a resource
- Do not fabricate statistics — use phrases like "according to industry estimates" when approximating

Output JSON:
{{
  "title": "SEO optimized title (60 chars max)",
  "meta_description": "155 char meta description with keyword",
  "slug": "url-friendly-slug",
  "content_html": "<h2>...</h2><p>...</p>..."
}}"""

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )

    text = message.content[0].text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]

    return json.loads(text)

env = Environment(loader=FileSystemLoader("templates"))

for keyword in KEYWORDS:
    print(f"Generating: {keyword}")
    try:
        post = generate_post(keyword)
        slug = post["slug"]
        os.makedirs(f"dist/blog/{slug}", exist_ok=True)

        # Render using blog template
        template = env.get_template("blog_post.html")
        html = template.render(
            niche=NICHE,
            title=post["title"],
            meta_description=post["meta_description"],
            content=post["content_html"],
            slug=slug
        )
        with open(f"dist/blog/{slug}/index.html", "w") as f:
            f.write(html)
        print(f"  Saved: dist/blog/{slug}/index.html")
    except Exception as e:
        print(f"  Error: {e}")
```

---

## 6.4 — INTERNAL LINKING RULES

Every page should link to:
- Homepage (via nav logo)
- 2-3 relevant listing pages
- Relevant category page
- Relevant state location page

Every blog post should link to:
- At least 2 listing pages
- The most relevant category page
- 1 other blog post (once you have >2)

---

## 6.5 — ONGOING SEO MAINTENANCE

**Monthly (15 min):**
- Check Google Search Console for crawl errors
- Add any new listings discovered
- Generate 1-2 new blog posts for new keywords

**Quarterly:**
- Update listings that have changed address/phone
- Remove permanently closed businesses
- Re-run Outscraper for new entrants in the niche

**Year 1 ranking timeline:**
| Month | Expected Traffic | Action |
|---|---|---|
| 1-2 | Near zero | Submit sitemap, wait |
| 3-4 | First trickle (10-50 visitors) | Check GSC for first keywords |
| 4-6 | 100-500 visitors/month | Start cold outreach |
| 6-9 | 500-2000/month | Apply for AdSense, upgrade pitch |
| 9-12 | 2000-10000/month | Revenue compounds |