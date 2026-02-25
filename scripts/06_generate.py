"""
STEP 6: Generate complete static site from enriched data.
Input:  data/enriched_listings.csv + images/ + config/
Output: dist/ (complete deployable site)
See docs/SKILL-05-site-build.md for full documentation.
"""
import os, json, re, pandas as pd
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

with open("config/niche.json") as f: NICHE = json.load(f)
with open("config/affiliates.json") as f: AFFILIATES = json.load(f)

df = pd.read_csv("data/enriched_listings.csv")
env = Environment(loader=FileSystemLoader("templates"))
os.makedirs("dist", exist_ok=True)

def render(tmpl, out, **ctx):
    os.makedirs(os.path.dirname(out), exist_ok=True)
    html = env.get_template(tmpl).render(niche=NICHE, affiliates=AFFILIATES, year=datetime.now().year, **ctx)
    with open(out, "w", encoding="utf-8") as f: f.write(html)

def parse_list(v):
    if pd.isna(v) or not v: return []
    try: r = json.loads(str(v)); return r if isinstance(r, list) else []
    except: return []

listings = []
url_col = next((c for c in ["site","website","url"] if c in df.columns), None)
phone_col = next((c for c in ["phone","telephone"] if c in df.columns), None)

for _, row in df.iterrows():
    imgs = [p.strip() for p in str(row.get("image_paths","")).split("|") if p.strip()] if pd.notna(row.get("image_paths")) else []
    listings.append({
        "slug": row["slug"], "name": row["name"],
        "address": row.get("full_address") or row.get("address",""),
        "city": row.get("city",""), "state": row.get("state",""),
        "phone": row.get(phone_col,"") if phone_col else "",
        "website": row.get(url_col,"") if url_col else "",
        "rating": row.get("rating"), "reviews": row.get("reviews"),
        "description": row.get("enriched_description") or row.get("description",""),
        "services": parse_list(row.get("enriched_services")),
        "service_areas": parse_list(row.get("enriched_service_areas")),
        "images": imgs, "is_featured": bool(row.get("is_featured_candidate")),
        "quality_score": row.get("quality_score",0),
        "latitude": row.get("latitude"), "longitude": row.get("longitude"),
    })

listings.sort(key=lambda x: (not x["is_featured"], -(float(x["rating"] or 0))))

print(f"Generating {len(listings)} listing pages...")
for l in listings:
    json_ld = {"@context":"https://schema.org","@type":"LocalBusiness","name":l["name"],
               "address":{"@type":"PostalAddress","addressLocality":l["city"],"addressRegion":l["state"]},
               "telephone":l["phone"],"url":l["website"],"description":l["description"]}
    if l["rating"]: json_ld["aggregateRating"] = {"@type":"AggregateRating","ratingValue":l["rating"],"reviewCount":l["reviews"]}
    render("listing.html", f"dist/listings/{l['slug']}/index.html", listing=l, json_ld=json.dumps(json_ld, indent=2))

categories = {}
for l in listings:
    for svc in l.get("services",[])[:2]:
        cat = re.sub(r"[^a-z0-9]+","-",svc.lower().strip())
        categories.setdefault(cat,[]).append(l)

print(f"Generating {len(categories)} category pages...")
for cat, cat_listings in categories.items():
    render("category.html", f"dist/category/{cat}/index.html",
           category_name=cat.replace("-"," ").title(), category_slug=cat, listings=cat_listings[:50])

by_state = {}
for l in listings:
    if l["state"]:
        by_state.setdefault(l["state"],{})
        if l["city"]: by_state[l["state"]].setdefault(l["city"],[]).append(l)

print(f"Generating location pages...")
for state, cities in by_state.items():
    sl = state.lower()
    all_s = [l for c in cities.values() for l in c]
    render("location.html", f"dist/location/{sl}/index.html", location_name=state, location_type="state", listings=all_s[:50], cities=list(cities.keys()))
    for city, city_listings in cities.items():
        cl = city.lower().replace(" ","-")
        render("location.html", f"dist/location/{sl}/{cl}/index.html", location_name=f"{city}, {state}", location_type="city", listings=city_listings, cities=[])

featured = [l for l in listings if l["is_featured"]][:12]
render("index.html", "dist/index.html", featured=featured, recent=listings[:24],
       total_count=len(listings), states=sorted(by_state.keys()), categories=list(categories.keys())[:12])

urls = [f"https://{NICHE['domain']}/"] + [f"https://{NICHE['domain']}/listings/{l['slug']}/" for l in listings]
for c in categories: urls.append(f"https://{NICHE['domain']}/category/{c}/")
for s, cities in by_state.items():
    urls.append(f"https://{NICHE['domain']}/location/{s.lower()}/")
    for c in cities: urls.append(f"https://{NICHE['domain']}/location/{s.lower()}/{c.lower().replace(' ','-')}/")

with open("dist/sitemap.xml","w") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
    for u in urls: f.write(f"  <url><loc>{u}</loc></url>\n")
    f.write("</urlset>")
with open("dist/robots.txt","w") as f:
    f.write(f"User-agent: *\nAllow: /\nSitemap: https://{NICHE['domain']}/sitemap.xml\n")

print(f"\nSite generated: {len(listings)} listings, {len(categories)} categories, {len(urls)} total URLs")
print("Output: dist/")