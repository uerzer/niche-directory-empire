# SKILL: Site Generation & Deployment
**Skill ID:** SKILL-05  
**Version:** 1.0  
**Depends on:** SKILL-04 → `data/enriched_listings.csv` + `images/`  
**Outputs to:** SKILL-06 (SEO), live URL  
**Portable to:** Python 3.10+ with Jinja2

---

## PURPOSE
Generate a complete static directory website from enriched CSV data. One HTML page per listing, category pages, location pages, homepage with search. Deploy to Cloudflare Pages for free.

---

## INPUTS
- `data/enriched_listings.csv`
- `images/` folder
- `config/niche.json` — site branding/config
- `config/affiliates.json` — affiliate CTAs

## OUTPUTS
- `dist/` — complete static site ready to deploy

---

## SETUP
```bash
pip install jinja2 pandas markdown2
```

---

## CONFIG FILES

### config/niche.json
```json
{
  "site_name": "LuxuryRestroomFinder",
  "domain": "luxuryrestroomfinder.com",
  "tagline": "Find Premium Portable Restroom Trailers Near You",
  "description": "The most complete directory of luxury restroom trailer rental companies in the United States.",
  "niche": "luxury restroom trailer rental",
  "niche_singular": "luxury restroom trailer company",
  "location_type": "local",
  "primary_color": "#1a56db",
  "accent_color": "#f59e0b",
  "google_analytics_id": "G-XXXXXXXXXX",
  "google_adsense_id": "ca-pub-XXXXXXXXXXXXXXXX"
}
```

### config/affiliates.json
```json
{
  "global_cta": {
    "text": "Get Free Quotes from Top Providers",
    "url": "https://bark.com/find/restroom-trailers/?ref=YOUR_REF",
    "type": "lead_gen"
  },
  "listing_cta": {
    "text": "Request a Quote from This Company",
    "url_template": "https://bark.com/find/restroom-trailers/?ref=YOUR_REF&business={name}",
    "type": "lead_gen"
  },
  "sidebar_cta": {
    "text": "Compare Prices — Free",
    "url": "https://bark.com/find/restroom-trailers/?ref=YOUR_REF",
    "type": "comparison"
  }
}
```

---

## SITE GENERATOR SCRIPT

```python
# scripts/06_generate.py
import os
import json
import math
import pandas as pd
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

# ── Load configs ─────────────────────────────────────────────
with open("config/niche.json") as f:
    NICHE = json.load(f)
with open("config/affiliates.json") as f:
    AFFILIATES = json.load(f)

df = pd.read_csv("data/enriched_listings.csv")
env = Environment(loader=FileSystemLoader("templates"))
os.makedirs("dist", exist_ok=True)

def render(template_name, output_path, **context):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    template = env.get_template(template_name)
    html = template.render(niche=NICHE, affiliates=AFFILIATES,
                           year=datetime.now().year, **context)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

# ── Prepare listing dicts ─────────────────────────────────────────
listings = []
for _, row in df.iterrows():
    images = []
    if pd.notna(row.get("image_paths")) and row.get("image_paths"):
        images = [p.strip() for p in str(row["image_paths"]).split("|") if p.strip()]

    listing = {
        "slug": row["slug"],
        "name": row["name"],
        "address": row.get("full_address") or row.get("address", ""),
        "city": row.get("city", ""),
        "state": row.get("state", ""),
        "phone": row.get("phone", ""),
        "website": row.get("site") or row.get("website", ""),
        "rating": row.get("rating"),
        "reviews": row.get("reviews"),
        "description": row.get("enriched_description") or row.get("description", ""),
        "services": _parse_list(row.get("enriched_services")),
        "service_areas": _parse_list(row.get("enriched_service_areas")),
        "certifications": _parse_list(row.get("enriched_certifications")),
        "tagline": row.get("enriched_tagline", ""),
        "images": images,
        "image_count": len(images),
        "quality_score": row.get("quality_score", 0),
        "is_featured": row.get("is_featured_candidate", False),
        "latitude": row.get("latitude"),
        "longitude": row.get("longitude"),
    }
    listings.append(listing)

def _parse_list(val):
    if pd.isna(val) or not val:
        return []
    if isinstance(val, list):
        return val
    try:
        parsed = json.loads(str(val))
        return parsed if isinstance(parsed, list) else []
    except Exception:
        return []

# Sort: featured first, then by rating desc
listings.sort(key=lambda x: (not x["is_featured"], -(float(x["rating"] or 0))))

# ── 1. Generate listing pages ─────────────────────────────────────
print(f"Generating {len(listings)} listing pages...")
for listing in listings:
    # JSON-LD structured data for SEO
    json_ld = {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "name": listing["name"],
        "address": {
            "@type": "PostalAddress",
            "streetAddress": listing["address"],
            "addressLocality": listing["city"],
            "addressRegion": listing["state"],
            "addressCountry": "US"
        },
        "telephone": listing["phone"],
        "url": listing["website"],
        "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": listing["rating"],
            "reviewCount": listing["reviews"]
        } if listing["rating"] else None,
        "description": listing["description"]
    }
    json_ld = {k: v for k, v in json_ld.items() if v is not None}

    render("listing.html",
           f"dist/listings/{listing['slug']}/index.html",
           listing=listing,
           json_ld=json.dumps(json_ld, indent=2))

# ── 2. Category pages ─────────────────────────────────────────
categories = {}
for l in listings:
    for svc in l.get("services", [])[:2]:
        cat = svc.lower().strip().replace(" ", "-")
        categories.setdefault(cat, []).append(l)

print(f"Generating {len(categories)} category pages...")
for cat_slug, cat_listings in categories.items():
    cat_name = cat_slug.replace("-", " ").title()
    render("category.html",
           f"dist/category/{cat_slug}/index.html",
           category_name=cat_name,
           category_slug=cat_slug,
           listings=cat_listings[:50])

# ── 3. Location pages (state + city) ─────────────────────────────────
by_state = {}
for l in listings:
    if l["state"]:
        by_state.setdefault(l["state"], {})
        if l["city"]:
            by_state[l["state"]].setdefault(l["city"], []).append(l)

print(f"Generating location pages for {len(by_state)} states...")
for state, cities in by_state.items():
    state_slug = state.lower()
    all_state_listings = [l for city_listings in cities.values() for l in city_listings]
    render("location.html",
           f"dist/location/{state_slug}/index.html",
           location_name=state, location_type="state",
           listings=all_state_listings[:50], cities=list(cities.keys()))

    for city, city_listings in cities.items():
        city_slug = city.lower().replace(" ", "-")
        render("location.html",
               f"dist/location/{state_slug}/{city_slug}/index.html",
               location_name=f"{city}, {state}", location_type="city",
               listings=city_listings, cities=[])

# ── 4. Homepage ───────────────────────────────────────────────
featured = [l for l in listings if l["is_featured"]][:12]
recent = listings[:24]
states = sorted(by_state.keys())
render("index.html", "dist/index.html",
       featured=featured, recent=recent,
       total_count=len(listings), states=states,
       categories=list(categories.keys())[:12])

# ── 5. Sitemap ────────────────────────────────────────────────
urls = [f"https://{NICHE['domain']}/"]
for l in listings:
    urls.append(f"https://{NICHE['domain']}/listings/{l['slug']}/")
for cat in categories:
    urls.append(f"https://{NICHE['domain']}/category/{cat}/")
for state, cities in by_state.items():
    urls.append(f"https://{NICHE['domain']}/location/{state.lower()}/")
    for city in cities:
        urls.append(f"https://{NICHE['domain']}/location/{state.lower()}/{city.lower().replace(' ','-')}/")

sitemap_xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
sitemap_xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
for url in urls:
    sitemap_xml += f"  <url><loc>{url}</loc></url>\n"
sitemap_xml += "</urlset>"

with open("dist/sitemap.xml", "w") as f:
    f.write(sitemap_xml)

# ── 6. robots.txt ─────────────────────────────────────────────
with open("dist/robots.txt", "w") as f:
    f.write(f"User-agent: *\nAllow: /\nSitemap: https://{NICHE['domain']}/sitemap.xml\n")

print(f"\nSite generated:")
print(f"  {len(listings)} listing pages")
print(f"  {len(categories)} category pages")
print(f"  {sum(len(c) for c in by_state.values())} city pages + {len(by_state)} state pages")
print(f"  {len(urls)} URLs in sitemap")
print(f"  Output: dist/")
```

---

## HTML TEMPLATES (Jinja2)

### templates/base.html
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{% block title %}{{ niche.site_name }}{% endblock %}</title>
  <meta name="description" content="{% block description %}{{ niche.description }}{% endblock %}">
  <link rel="canonical" href="https://{{ niche.domain }}{% block canonical %}/{% endblock %}">
  {% block json_ld %}{% endblock %}
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; color: #1a1a2e; line-height: 1.6; }
    .container { max-width: 1200px; margin: 0 auto; padding: 0 20px; }
    nav { background: {{ niche.primary_color }}; padding: 16px 0; }
    nav a { color: white; text-decoration: none; font-weight: 600; font-size: 1.2rem; }
    .hero { background: linear-gradient(135deg, {{ niche.primary_color }}, #0d3b8e); color: white; padding: 60px 0; text-align: center; }
    .hero h1 { font-size: 2.5rem; margin-bottom: 16px; }
    .hero p { font-size: 1.2rem; opacity: 0.9; margin-bottom: 32px; }
    .search-box { display: flex; gap: 8px; max-width: 600px; margin: 0 auto; }
    .search-box input { flex: 1; padding: 14px 18px; border: none; border-radius: 8px; font-size: 1rem; }
    .search-box button { padding: 14px 28px; background: {{ niche.accent_color }}; color: white; border: none; border-radius: 8px; font-size: 1rem; font-weight: 600; cursor: pointer; }
    .card { background: white; border: 1px solid #e5e7eb; border-radius: 12px; padding: 20px; transition: box-shadow 0.2s; }
    .card:hover { box-shadow: 0 4px 20px rgba(0,0,0,0.1); }
    .card h3 a { color: {{ niche.primary_color }}; text-decoration: none; }
    .card h3 a:hover { text-decoration: underline; }
    .badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; }
    .badge-featured { background: {{ niche.accent_color }}; color: white; }
    .badge-verified { background: #10b981; color: white; }
    .rating { color: #f59e0b; }
    .cta-box { background: {{ niche.primary_color }}; color: white; padding: 32px; border-radius: 12px; text-align: center; margin: 32px 0; }
    .cta-box a { display: inline-block; padding: 14px 32px; background: {{ niche.accent_color }}; color: white; border-radius: 8px; text-decoration: none; font-weight: 700; font-size: 1.1rem; }
    .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 20px; }
    footer { background: #1f2937; color: #9ca3af; padding: 40px 0; text-align: center; margin-top: 60px; }
    @media (max-width: 768px) { .hero h1 { font-size: 1.8rem; } .search-box { flex-direction: column; } }
  </style>
  <!-- Google Analytics -->
  <script async src="https://www.googletagmanager.com/gtag/js?id={{ niche.google_analytics_id }}"></script>
  <script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','{{ niche.google_analytics_id }}');</script>
</head>
<body>
  <nav><div class="container"><a href="/">{{ niche.site_name }}</a></div></nav>
  {% block content %}{% endblock %}
  <footer><div class="container"><p>&copy; {{ year }} {{ niche.site_name }}. All rights reserved.</p></div></footer>
</body>
</html>
```

### templates/listing.html
```html
{% extends "base.html" %}
{% block title %}{{ listing.name }} — {{ niche.site_name }}{% endblock %}
{% block description %}{{ listing.description[:160] if listing.description else listing.name + ' — ' + niche.niche }}{% endblock %}
{% block canonical %}/listings/{{ listing.slug }}/{% endblock %}
{% block json_ld %}<script type="application/ld+json">{{ json_ld }}</script>{% endblock %}
{% block content %}
<div class="container" style="padding-top:40px;padding-bottom:60px;">
  <div style="display:grid;grid-template-columns:2fr 1fr;gap:32px;">
    <div>
      <div style="margin-bottom:8px;">
        {% if listing.is_featured %}<span class="badge badge-featured">Featured</span>{% endif %}
        <span class="badge badge-verified">Verified</span>
      </div>
      <h1 style="font-size:2rem;margin-bottom:8px;">{{ listing.name }}</h1>
      {% if listing.rating %}
      <div class="rating">
        ★ {{ listing.rating }} ({{ listing.reviews }} reviews)
      </div>
      {% endif %}
      {% if listing.images %}
      <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin:20px 0;">
        {% for img in listing.images[:3] %}
        <img src="/{{ img }}" alt="{{ listing.name }}" style="width:100%;height:160px;object-fit:cover;border-radius:8px;">
        {% endfor %}
      </div>
      {% endif %}
      <p style="font-size:1.1rem;margin:20px 0;color:#374151;">{{ listing.description }}</p>
      {% if listing.services %}
      <h2 style="margin-bottom:12px;">Services</h2>
      <ul style="display:flex;flex-wrap:wrap;gap:8px;list-style:none;margin-bottom:24px;">
        {% for s in listing.services %}<li style="background:#f3f4f6;padding:6px 12px;border-radius:20px;font-size:0.9rem;">{{ s }}</li>{% endfor %}
      </ul>
      {% endif %}
      {% if listing.service_areas %}
      <h2 style="margin-bottom:12px;">Service Areas</h2>
      <p>{{ listing.service_areas | join(', ') }}</p>
      {% endif %}
    </div>
    <div>
      <div class="card" style="margin-bottom:20px;">
        <h3 style="margin-bottom:16px;">Contact</h3>
        {% if listing.phone %}<p style="margin-bottom:8px;">📞 <a href="tel:{{ listing.phone }}">{{ listing.phone }}</a></p>{% endif %}
        {% if listing.address %}<p style="margin-bottom:8px;">📍 {{ listing.address }}, {{ listing.city }}, {{ listing.state }}</p>{% endif %}
        {% if listing.website %}<p><a href="{{ listing.website }}" target="_blank" rel="noopener">🌐 Visit Website</a></p>{% endif %}
      </div>
      <div class="cta-box">
        <p style="margin-bottom:16px;font-weight:600;">Get a Free Quote</p>
        <a href="{{ affiliates.listing_cta.url_template | replace('{name}', listing.name) }}" target="_blank">{{ affiliates.listing_cta.text }}</a>
      </div>
    </div>
  </div>
</div>
{% endblock %}
```

---

## DEPLOYMENT

```bash
# scripts/07_deploy.sh
#!/bin/bash
set -e

PROJECT_NAME=${1:-"my-directory"}
echo "Deploying $PROJECT_NAME to Cloudflare Pages..."

# Install wrangler if needed
if ! command -v wrangler &> /dev/null; then
    npm install -g wrangler
fi

# Deploy
wrangler pages deploy ./dist \
  --project-name="$PROJECT_NAME" \
  --commit-message="Auto-deploy $(date +%Y-%m-%d)"

echo "Deployed! Visit: https://$PROJECT_NAME.pages.dev"
echo "Next: Point your domain in Cloudflare dashboard"
```

```bash
# One-time GitHub Actions setup alternative
# .github/workflows/deploy.yml — see MASTER-RUNBOOK.md for full file
```

---

## VALIDATION CHECKLIST
- [ ] `dist/index.html` exists and loads without errors
- [ ] Spot-check 3 listing pages — all have name, address, description
- [ ] `dist/sitemap.xml` lists correct number of URLs
- [ ] `dist/robots.txt` has correct domain in Sitemap line
- [ ] JSON-LD on listing pages validates at: https://validator.schema.org
- [ ] Images referenced in HTML exist in `dist/` or `images/`
- [ ] Affiliate CTAs have correct ref links