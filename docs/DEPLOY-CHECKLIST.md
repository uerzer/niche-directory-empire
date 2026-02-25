# Deploy Checklist — Human Steps Only
**What you do. Everything else is automated.**  
**Total time: ~75 min one-time setup + 20 min per new site**

---

## ONE-TIME SETUP (Do once, reuse forever)

### 1. Accounts to Create (50 min total)

#### Infrastructure (Free)
- [ ] **GitHub** — github.com — 5 min — store all code and trigger auto-deploys
- [ ] **Cloudflare** — cloudflare.com — 5 min — free hosting + DNS management
- [ ] **Supabase** — supabase.com — 5 min — free database if you need dynamic search

#### Data & AI APIs
- [ ] **Outscraper** — outscraper.com — 10 min
  - Create account
  - Go to Profile → API Keys → Generate key
  - Save as `OUTSCRAPER_API_KEY` in your password manager
  - Free tier: 500 records/month (enough for testing)
  - Paid: $3/1,000 records (~$1-5 per directory build)

- [ ] **Anthropic** — console.anthropic.com — 5 min
  - Create account + add $20 credit to start
  - Go to API Keys → Create key
  - Save as `ANTHROPIC_API_KEY`
  - Cost per directory: ~$5-15 for enrichment + image verification

#### Affiliate Accounts (20 min total — do in parallel)
- [ ] **Bark.com affiliate** — bark.com/affiliates — 5 min
  - Pays $50-100 per qualified lead submitted
  - Works for: service businesses, contractors, therapists, lawyers
  - Get your referral link immediately on signup

- [ ] **PartnerStack** — partnerstack.com — 5 min
  - Browse marketplace for tools in your niche
  - Apply to relevant programs (approval usually 24-48h)
  - Best for: AI tools, SaaS, B2B software
  - Commissions: 20-50% recurring

- [ ] **ShareASale** — shareasale.com — 5 min
  - General affiliate network — browse by category
  - Apply, usually approved in 1-3 days

#### Payments (for collecting paid listing upgrades)
- [ ] **Stripe** — stripe.com — 10 min
  - Create account, verify identity
  - Go to Payment Links → Create a link for "Pro Listing — $49/month" recurring
  - Save the payment link URL

#### Analytics
- [ ] **Google Analytics** — analytics.google.com — 5 min
  - Create account → Create property → Get Measurement ID (G-XXXXXXXX)
  - Used in every site's config

---

## PER-SITE CHECKLIST (20 min per new directory)

### Before Build (5 min)
- [ ] **Buy domain** — namecheap.com or cloudflare.com/registrar
  - Budget: $10-15/year
  - Naming formula: `[niche-keyword-finder].com` or `[niche]directory.com`
  - Examples: `luxuryrestroomfinder.com`, `memorycaredirectory.com`, `aitoolsindex.com`
  - Tip: Buy on Cloudflare Registrar — DNS is already there, zero propagation delay

- [ ] **Set environment variables** — tell the agent your keys:
  ```
  OUTSCRAPER_API_KEY=your_key
  ANTHROPIC_API_KEY=your_key
  SITE_NAME=LuxuryRestroomFinder
  DOMAIN=luxuryrestroomfinder.com
  NICHE=luxury restroom trailer rental
  GA_ID=G-XXXXXXXXXX
  BARK_AFFILIATE_URL=https://bark.com/find/.../?ref=YOUR_REF
  STRIPE_PAYMENT_LINK=https://buy.stripe.com/YOUR_LINK
  ```

### After Build (10 min)

#### Deploy to Cloudflare Pages
- [ ] Go to dash.cloudflare.com → Pages → Create a project
- [ ] Connect GitHub repo → select the generated site repo
- [ ] Build settings: Build command = none, Output directory = `dist`
- [ ] Click Deploy
- [ ] Takes ~2 minutes

#### Connect Your Domain
- [ ] In Cloudflare Pages → Custom domains → Add domain
- [ ] Type your domain → it auto-adds DNS records (already on Cloudflare if bought there)
- [ ] Wait 1-2 minutes for propagation
- [ ] Test: visit your domain — site should be live

#### Google Search Console (5 min)
- [ ] Go to search.google.com/search-console
- [ ] Add property → URL prefix → enter `https://yourdomain.com`
- [ ] Verify via HTML tag method (paste tag into site `<head>`) OR DNS method if on Cloudflare
- [ ] Go to Sitemaps → Add sitemap → type `sitemap.xml` → Submit
- [ ] Click URL Inspection → enter homepage URL → Request Indexing

### After Launch — Month 2 (15 min)
- [ ] **Google AdSense** — adsense.google.com
  - Apply ONLY after site has 1,000+ monthly visitors (they reject new sites)
  - Paste AdSense code snippet into base template
  - Approval takes 1-2 weeks

- [ ] **Start cold outreach**
  - Export `data/outreach_list.csv`
  - Use agent to generate personalized Email 1 for each business
  - Send via Gmail (manual) or paste into Instantly.ai / Woodpecker for automation
  - Target: 50 emails/day max to avoid spam flags

---

## WHAT AGENTS HANDLE (you do NOT need to touch these)

| Task | Automated By |
|---|---|
| Outscraper data pull | Python script (SKILL-02) |
| Data cleaning + dedup | Python script (SKILL-03) |
| Website verification (Crawl4AI) | Python script (SKILL-04) |
| AI enrichment (Claude) | Python script (SKILL-04) |
| Image extraction + verification | Python script (SKILL-04) |
| HTML site generation (500+ pages) | Python script (SKILL-05) |
| Sitemap + robots.txt | Python script (SKILL-05) |
| Blog post writing | Claude via script (SKILL-06) |
| Affiliate link injection | Auto at build time (SKILL-05) |
| Cold email copy generation | Claude via prompt (SKILL-07) |
| SEO meta tags on all pages | Auto at build time (SKILL-05) |
| JSON-LD schema markup | Auto at build time (SKILL-05) |

---

## TROUBLESHOOTING

**Site not showing after domain connection:**
- Check Cloudflare DNS → should have CNAME record pointing to `your-project.pages.dev`
- Clear browser cache or test in incognito

**Outscraper returns fewer records than expected:**
- Broaden your search query (remove "luxury" → try just "restroom trailer rental")
- Run multiple query variants and merge

**Enrichment returning null for most fields:**
- Site may be JavaScript-rendered → Crawl4AI headless mode needed
- Or site content is behind login/paywall → skip enrichment, use just basic data

**Google Search Console not indexing:**
- Normal for first 4-8 weeks — be patient
- Check Coverage report for crawl errors
- Make sure robots.txt allows Googlebot: `User-agent: * Allow: /`

**Cloudflare Pages build fails:**
- Output directory must exactly match what the script outputs (default: `dist`)
- If using GitHub Actions instead, check Actions tab for error logs

---

## RECOMMENDED TOOLS (Optional Upgrades)

| Tool | Purpose | Cost | Priority |
|---|---|---|---|
| Ahrefs Lite | Keyword research validation | $99/month | Nice to have |
| Instantly.ai | Cold email automation | $37/month | Month 2+ |
| Tally.so | Lead capture forms (free) | Free | Recommended |
| Airtable | Track outreach + leads | Free tier | Recommended |
| Namecheap | Domain purchases | $10-15/domain | Required |
| Loom | Record quick video for claimed listings | Free | Optional |

---

## QUICK REFERENCE — Key URLs

| Resource | URL |
|---|---|
| Outscraper dashboard | app.outscraper.com |
| Anthropic console | console.anthropic.com |
| Cloudflare dashboard | dash.cloudflare.com |
| GitHub | github.com |
| PartnerStack marketplace | app.partnerstack.com/marketplace |
| Bark.com affiliate | bark.com/affiliates |
| Google Search Console | search.google.com/search-console |
| Google Analytics | analytics.google.com |
| Stripe dashboard | dashboard.stripe.com |
| CMS Nursing Home data | data.cms.gov/provider-data |
| NPI Registry | npiregistry.cms.hhs.gov |
| Curlie data dump | curlie.org/docs/en/rdf.html |