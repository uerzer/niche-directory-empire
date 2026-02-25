# Niche Directory Empire

> Build profitable niche directory websites in 4 days for under $250. Proven system from Frey Chu / Greg Isenberg methodology.

## What This Is

A complete, agent-portable system to build, populate, and monetize niche directory websites at scale. Each directory:
- Launches pre-populated with real verified data
- Costs under $250 to build
- Takes 4 days from idea to live site
- Generates $500–$2,500/month per site at maturity (month 6–12)
- Runs on free hosting (Cloudflare Pages)

**Proven case:** Frey Chu built a Luxury Restroom Trailer directory in 4 days → $273/day ($8,190/month)

---

## Repository Structure

```
niche-directory-empire/
├── docs/                    # All documentation and skill files
│   ├── MASTER-RUNBOOK.md    # Complete system orchestration guide
│   ├── DEPLOY-CHECKLIST.md  # Human steps only
│   ├── SKILL-01-niche-research.md
│   ├── SKILL-02-data-scrape.md
│   ├── SKILL-03-data-clean.md
│   ├── SKILL-04-data-enrich.md
│   ├── SKILL-05-site-build.md
│   ├── SKILL-06-seo-setup.md
│   ├── SKILL-07-outreach.md
│   ├── EXAMPLE-01-luxury-restroom-trailers.md
│   ├── EXAMPLE-02-dementia-care-facilities.md
│   └── EXAMPLE-03-ai-tools-directory.md
├── scripts/                 # Python pipeline scripts
│   ├── 01_scrape.py
│   ├── 02_clean.py
│   ├── 03_verify.py
│   ├── 04_enrich.py
│   ├── 05_images.py
│   ├── 06_generate.py
│   └── 07_deploy.sh
├── templates/               # Jinja2 HTML templates
│   ├── base.html
│   ├── index.html
│   ├── listing.html
│   ├── category.html
│   ├── location.html
│   └── blog_post.html
├── config/
│   ├── niche.example.json
│   └── affiliates.example.json
├── .github/
│   └── workflows/
│       └── deploy.yml
├── requirements.txt
├── .env.example
└── run.py                   # Single entry point — runs full pipeline
```

---

## The 7-Step Pipeline

| Step | Script | Tool | Output |
|------|--------|------|--------|
| 1. Scrape | `01_scrape.py` | Outscraper API | `data/raw_listings.csv` |
| 2. Clean | `02_clean.py` | Python/pandas | `data/clean_listings.csv` |
| 3. Verify | `03_verify.py` | Crawl4AI | `data/verified_listings.csv` |
| 4. Enrich | `04_enrich.py` | Claude API | `data/enriched_listings.csv` |
| 5. Images | `05_images.py` | Claude Vision | `images/{id}/photo_N.jpg` |
| 6. Generate | `06_generate.py` | Jinja2 | `dist/` (full site) |
| 7. Deploy | `07_deploy.sh` | Cloudflare Pages | Live URL |

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/YOUR_USERNAME/niche-directory-empire
cd niche-directory-empire

# 2. Install dependencies
pip install -r requirements.txt
crawl4ai-setup

# 3. Configure
cp .env.example .env
cp config/niche.example.json config/niche.json
cp config/affiliates.example.json config/affiliates.json
# Edit .env with your API keys
# Edit config/niche.json with your niche

# 4. Run full pipeline
python run.py

# 5. Deploy
bash scripts/07_deploy.sh your-directory-name
```

---

## Proven Niches (Pre-Researched)

| Niche | Score | Primary Revenue | Data Source |
|-------|-------|-----------------|-------------|
| Luxury restroom trailers | 22/25 | Lead gen $50–150/lead | Outscraper |
| Dementia care facilities | 23/25 | Referral $500–2000 | CMS.gov free |
| Mental health therapists | 21/25 | Bark.com $100/lead | NPI Registry |
| AI tools by use case | 19/25 | PartnerStack 20–50% recurring | ProductHunt API |
| Ketamine clinics | 22/25 | Lead gen high-ticket | Outscraper |
| Immigration lawyers | 20/25 | Bark.com $100/lead | Outscraper |

---

## Stack (Zero Recurring Cost)

- **Scraping:** Outscraper (~$3/1k records) + Crawl4AI (free/open source)
- **AI:** Claude API (~$5–15/directory build)
- **Hosting:** Cloudflare Pages (free)
- **Database:** Supabase free tier (optional)
- **Build:** Python + Jinja2 (free)
- **Domain:** ~$10/year

**Total per directory: under $250**

---

## Revenue Timeline

- Month 1–3: $0 (Google indexing period)
- Month 3–6: $100–500/month
- Month 6–12: $500–2,500/month
- Portfolio of 10 sites: $5k–25k/month

---

## Give This to Any AI Agent

Every SKILL file in `/docs/` is a self-contained, portable instruction set. Drop any skill file into:
- Claude Projects
- ChatGPT Custom Instructions
- Cursor / Windsurf system prompt
- LangChain / CrewAI agent config
- Any LLM with code execution

The agent gets everything it needs: prompts, scripts, validation checks, expected outputs.

---

## Source

Based on Frey Chu's methodology from Greg Isenberg's Startup Ideas Podcast, Feb 2026: "Claude Code Built Me a $273/Day Online Directory"

Extended with additional niches, affiliate research, and agent-portable skill architecture.