"""
STEP 2: Clean and deduplicate raw listings.
Input:  data/raw_listings.csv
Output: data/clean_listings.csv
See docs/SKILL-03-data-clean.md for full documentation.
"""
import pandas as pd, re, json, os

def make_slug(*parts):
    combined = "-".join(str(p) for p in parts if p and str(p) != "nan")
    s = combined.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")[:80]

def main():
    df = pd.read_csv("data/raw_listings.csv", low_memory=False)
    print(f"Input: {len(df)} records")

    if "business_status" in df.columns:
        df = df[~df["business_status"].str.contains("CLOSED|PERMANENTLY", case=False, na=False)]

    df = df.dropna(subset=["name"])
    df = df[df["name"].str.len() > 2]

    if "place_id" in df.columns:
        df = df.drop_duplicates(subset=["place_id"], keep="first")

    city_col = next((c for c in ["city", "borough"] if c in df.columns), None)
    if city_col:
        df["_key"] = df["name"].str.lower().str.strip() + "|" + df[city_col].fillna("").str.lower()
        df = df.drop_duplicates(subset=["_key"]).drop(columns=["_key"])

    url_col = next((c for c in ["site", "website"] if c in df.columns), None)
    phone_col = next((c for c in ["phone", "telephone"] if c in df.columns), None)

    def quality_score(row):
        s = 0
        if url_col and pd.notna(row.get(url_col)): s += 3
        if phone_col and pd.notna(row.get(phone_col)): s += 2
        if pd.notna(row.get("rating")) and float(row.get("rating") or 0) >= 4.0: s += 2
        if pd.notna(row.get("reviews")) and float(row.get("reviews") or 0) >= 10: s += 1
        return s

    df["quality_score"] = df.apply(quality_score, axis=1)
    df["is_featured_candidate"] = df["quality_score"] >= 6

    state_col = next((c for c in ["state"] if c in df.columns), None)
    df["slug"] = df.apply(
        lambda r: make_slug(r["name"], r.get(city_col), r.get(state_col)), axis=1
    )
    slug_counts = df["slug"].value_counts()
    for slug in slug_counts[slug_counts > 1].index:
        mask = df["slug"] == slug
        df.loc[mask, "slug"] = [f"{slug}-{i+1}" for i in range(mask.sum())]

    os.makedirs("data", exist_ok=True)
    df.to_csv("data/clean_listings.csv", index=False)
    print(f"Output: {len(df)} records → data/clean_listings.csv")
    print(f"Featured candidates: {df['is_featured_candidate'].sum()}")

if __name__ == "__main__":
    main()