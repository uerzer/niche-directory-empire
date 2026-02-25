# SKILL: Cold Outreach & Monetization Activation
**Skill ID:** SKILL-07  
**Version:** 1.0  
**Depends on:** SKILL-06 → live indexed site with traffic  
**Timing:** Start Month 2 (after indexing begins)  
**Portable to:** Any LLM + email sending tool (Gmail, Instantly.ai, Woodpecker)

---

## PURPOSE
Turn listed businesses into paying customers. Three-email sequence to (1) claim free listing, (2) build rapport, (3) pitch paid upgrade. Also covers lead gen setup and affiliate activation.

---

## INPUTS
- `data/enriched_listings.csv` — source of business contacts
- Live site URL
- Affiliate links from `config/affiliates.json`
- Email sending account (Gmail with warmup OR Instantly.ai)

## OUTPUTS
- Contacted business list with response tracking
- Paid listing upgrades (Stripe)
- Active affiliate accounts generating commissions

---

## STEP 7.1 — EXTRACT CONTACT LIST

```python
# scripts/07_outreach_list.py
import pandas as pd

df = pd.read_csv("data/enriched_listings.csv")

# Prioritize: high quality score + has website + has email/phone
url_col = next((c for c in ["site", "website", "url"] if c in df.columns), None)
phone_col = next((c for c in ["phone", "telephone"] if c in df.columns), None)

outreach = df[
    (df["quality_score"] >= 5) &
    df[url_col].notna()
].copy()

# Sort by quality score descending
outreach = outreach.sort_values("quality_score", ascending=False)

# Select columns for outreach
cols = ["name", "slug", phone_col, url_col, "city", "state", "quality_score", "is_featured_candidate"]
outreach = outreach[[c for c in cols if c and c in df.columns]]

outreach.to_csv("data/outreach_list.csv", index=False)
print(f"Outreach list: {len(outreach)} businesses")
print(f"Featured candidates: {outreach['is_featured_candidate'].sum()}")
```

---

## STEP 7.2 — EMAIL SEQUENCES

### Sequence A: Claim Your Listing (Cold)

**Email 1 — Day 0 — Awareness**
```
Subject: {Business Name} is listed on {SiteName} — claim it free

Hi [First Name / Owner],

I was building {SiteName}.com — a directory specifically for {niche} companies — and found {Business Name} on Google Maps.

Your listing is live here: https://{domain}/listings/{slug}/

I'm giving free verified badges to the first 50 businesses who claim their profile this month. It takes about 2 minutes and you can add photos, services, and a contact form.

Want me to send the claim link?

[Your name]
{SiteName}
```

**Email 2 — Day 7 — Social Proof**
```
Subject: Re: {Business Name} on {SiteName}

Quick follow up —

{SiteName} is now getting search traffic for keywords like "{niche} near me" and "{niche} {city}". 

A few companies in your area have already claimed their enhanced listings and are getting inquiry form submissions through the directory.

Your profile is one of the most complete ones we have — it'd be worth 5 minutes to verify it.

Claim here: https://{domain}/listings/{slug}/

[Your name]
```

**Email 3 — Day 14 — Upgrade Pitch**
```
Subject: Last week for founding member pricing — {Business Name}

[First Name],

Wrapping up founding member pricing this week.

Enhanced listings on {SiteName}: $49/month
Includes:
- Priority placement (top of {city} results)  
- Photo gallery (up to 10 photos)
- Lead inquiry form with email notifications
- Verified badge
- Monthly traffic report

We have [X] people/month searching for {niche} in {state}. 

Worth a look: https://{domain}/upgrade/

[Your name]
```

---

### Sequence B: Warm (Responded to Email 1)

**Email B1 — Send claim link**
```
Subject: Re: Your listing claim link

Hi [Name],

Here's your claim link: https://{domain}/claim/{slug}/?token={TOKEN}

Takes about 2 minutes. You can add:
- Up to 5 photos from your website
- Updated description
- Full service list
- Service area map

Once claimed, you get a Verified badge on your listing.

Let me know if you have any questions.

[Your name]
```

**Email B2 — 3 days after claim — Upsell**
```
Subject: Your listing is getting views — upgrade to capture them

Hi [Name],

Your verified listing on {SiteName} has had [X] profile views this week.

The free plan shows your basic info. With the Pro plan ($49/month):
- You appear before unverified listings in search results
- Visitors see a "Request Quote" button that sends leads directly to your email
- You get a monthly report of how many people viewed and contacted you

Most businesses recoup the cost from a single job.

Try it free for 30 days: https://{domain}/upgrade/

[Your name]
```

---

## STEP 7.3 — LEAD GEN SETUP (High-Value Niches)

For niches where leads are worth $500+ (dementia care, legal, medical):

### Option A: Sell leads directly to listed businesses
1. Add inquiry form to every listing page (already in template)
2. Route form submissions to your email
3. Forward qualified leads to the business at $50-200/lead
4. Track with simple Airtable or Notion database

**Lead qualification criteria:**
- Has specific need (not just browsing)
- Has timeline (event date, move-in date, etc.)
- Has budget range confirmed
- Contact info verified

### Option B: Bark.com (instant affiliate, no setup)
- Sign up at bark.com/affiliates
- Get your referral link
- Replace inquiry form "Request Quote" button with Bark.com referral link
- Earn $50-100 per lead submitted through your link
- Zero fulfillment work

### Option C: Pay-per-call (premium)
- Sign up for Invoca or RingPartner
- Get a tracked phone number for each niche
- Replace listed phone with tracked number
- Earn $25-75 per inbound call
- Requires ~$500 setup but highest per-action value

---

## STEP 7.4 — STRIPE PAYMENT INTEGRATION

For collecting paid listing upgrades directly:

```html
<!-- Add to listing claim/upgrade page -->
<!-- Stripe Payment Link (no code required) -->
<!-- 1. Go to dashboard.stripe.com/payment-links -->
<!-- 2. Create product: "Pro Listing — $49/month" recurring -->
<!-- 3. Copy payment link URL -->
<!-- 4. Replace href below -->

<a href="https://buy.stripe.com/YOUR_PAYMENT_LINK" 
   class="upgrade-btn"
   data-listing="{{ listing.slug }}">
  Upgrade to Pro — $49/month
</a>
```

**Stripe webhook (to auto-upgrade listings):**
```python
# Minimal webhook handler — deploy as Cloudflare Worker or Vercel function
import json

def handle_stripe_webhook(event):
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        listing_slug = session["metadata"].get("listing_slug")
        customer_email = session["customer_details"]["email"]
        
        # Update listing in your data store
        upgrade_listing(listing_slug, tier="pro", email=customer_email)
        
        # Send confirmation email
        send_confirmation(customer_email, listing_slug)
```

---

## STEP 7.5 — AFFILIATE ACCOUNT CHECKLIST

Activate these in priority order. Each takes 5-15 min to sign up:

| Program | URL | Payout | When to Apply |
|---|---|---|---|
| Bark.com | bark.com/affiliates | $50-100/lead | Before launch |
| PartnerStack | partnerstack.com | 20-50% recurring | Before launch |
| Google AdSense | adsense.google.com | ~$3-8 CPM | After 1k monthly visitors |
| Housecall Pro | housecallpro.com/partners | $250/signup | After launch |
| ShareASale | shareasale.com | Varies | Before launch |
| A Place for Mom | aplaceformom.com/partners | $500-2000/referral | Healthcare niches only |

---

## OUTREACH TRACKING

Simple CSV to track outreach status:

```csv
name,slug,email,phone,sequence,email_1_sent,email_1_opened,replied,claimed,paid_tier,revenue
ABC Trailers,abc-trailers-austin-tx,,512-555-0100,A,2025-03-01,yes,no,no,free,0
XYZ Events,xyz-events-dallas-tx,info@xyz.com,,A,2025-03-01,yes,yes,yes,pro,49
```

**Target conversion rates (realistic):**
- Email 1 open rate: 40-60% (you're emailing about their own business)
- Reply rate: 10-20%
- Claim rate (free): 15-30% of contacts
- Paid upgrade rate: 5-10% of claimed
- **Net revenue per 100 contacts: ~$200-500/month recurring**

---

## AGENT PROMPT: Full Outreach Sequence

```
You are running cold outreach for {SITE_NAME}, a niche directory for {NICHE}.

Task: Generate personalized Email 1 for each business in the contact list.

For each business, personalize:
- Use their actual business name
- Reference their city
- Use their specific listing URL: https://{DOMAIN}/listings/{SLUG}/
- If they have a high rating, mention it: "Your 4.8-star rating makes you one of the top-rated companies in our directory"
- If they're in a major city, mention local search volume

Output: CSV with columns: name, email, subject, body
Input: [paste outreach_list.csv]
```