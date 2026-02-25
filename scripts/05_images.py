"""
STEP 5: Extract and verify business images using Claude Vision.
Input:  data/enriched_listings.csv
Output: images/{place_id}/photo_N.jpg + updated CSV
See docs/SKILL-04-data-enrich.md for full documentation.
"""
import anthropic, requests, pandas as pd, base64, os
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
from urllib.parse import urljoin
from dotenv import load_dotenv
load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

with open("config/niche.json") as f:
    NICHE = json.load(f)

def get_images(url):
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "html.parser")
        imgs = []
        for img in soup.find_all("img"):
            src = img.get("src") or img.get("data-src") or ""
            if src.startswith("//"): src = "https:" + src
            elif src.startswith("/"): src = urljoin(url, src)
            if src.startswith("http"): imgs.append(src)
        return imgs[:15]
    except: return []

def is_real_photo(img_url):
    try:
        r = requests.get(img_url, timeout=8)
        if r.status_code != 200 or len(r.content) < 20000: return False
        ct = r.headers.get("content-type", "")
        if not any(t in ct for t in ["jpeg","jpg","png","webp"]): return False
        data = base64.standard_b64encode(r.content).decode()
        mt = "image/jpeg" if "jpeg" in ct or "jpg" in ct else "image/png"
        msg = client.messages.create(model="claude-haiku-4-5", max_tokens=10,
            messages=[{"role":"user","content":[
                {"type":"image","source":{"type":"base64","media_type":mt,"data":data}},
                {"type":"text","text":f"Is this a real photo of {NICHE['niche']} services/facilities (not logo/icon/stock)? YES or NO only."}
            ]}])
        return "YES" in msg.content[0].text.upper()
    except: return False

def save_img(img_url, pid, idx):
    try:
        r = requests.get(img_url, timeout=8)
        img = Image.open(BytesIO(r.content)).convert("RGB")
        if img.width > 1200: img = img.resize((1200, int(img.height*1200/img.width)), Image.LANCZOS)
        p = f"images/{pid}/photo_{idx}.jpg"
        os.makedirs(f"images/{pid}", exist_ok=True)
        img.save(p, "JPEG", quality=85)
        return p
    except: return None

def main():
    df = pd.read_csv("data/enriched_listings.csv")
    url_col = next((c for c in ["site","website","url"] if c in df.columns), None)
    id_col = "place_id" if "place_id" in df.columns else "slug"
    df["image_paths"] = ""; df["image_count"] = 0
    for i, (idx, row) in enumerate(df.iterrows()):
        if not url_col or pd.isna(row.get(url_col)): continue
        pid = str(row[id_col]); saved = []
        print(f"[{i+1}/{len(df)}] {str(row.get('name',''))[:40]}")
        for img_url in get_images(row[url_col]):
            if len(saved) >= 5: break
            if is_real_photo(img_url):
                p = save_img(img_url, pid, len(saved)+1)
                if p: saved.append(p); print(f"  Saved: {p}")
        df.at[idx, "image_paths"] = "|".join(saved)
        df.at[idx, "image_count"] = len(saved)
    df.to_csv("data/enriched_listings.csv", index=False)
    print(f"\nTotal images: {df['image_count'].sum()} across {(df['image_count']>0).sum()} listings")

if __name__ == "__main__":
    main()