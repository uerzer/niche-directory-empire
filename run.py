#!/usr/bin/env python3
"""
Niche Directory Empire — Full Pipeline Runner
Run: python run.py
Runs all 7 steps in sequence. Each step reads from previous step's output.
"""
import os
import sys
import json
import subprocess
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def check_env():
    required = ["OUTSCRAPER_API_KEY", "ANTHROPIC_API_KEY"]
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        print(f"ERROR: Missing environment variables: {', '.join(missing)}")
        print("Copy .env.example to .env and fill in your keys.")
        sys.exit(1)

def check_config():
    if not Path("config/niche.json").exists():
        print("ERROR: config/niche.json not found.")
        print("Copy config/niche.example.json to config/niche.json and configure it.")
        sys.exit(1)
    with open("config/niche.json") as f:
        config = json.load(f)
    if config.get("site_name") == "MySiteDirectory":
        print("ERROR: Please edit config/niche.json with your actual niche settings.")
        sys.exit(1)
    return config

def run_step(step_num: int, script: str, description: str):
    print(f"\n{'='*60}")
    print(f"STEP {step_num}: {description}")
    print(f"{'='*60}")
    result = subprocess.run([sys.executable, f"scripts/{script}"], check=False)
    if result.returncode != 0:
        print(f"\nStep {step_num} failed. Check output above.")
        sys.exit(1)
    print(f"Step {step_num} complete.")

def main():
    print("\nNiche Directory Empire — Pipeline Runner")
    print("="*60)

    check_env()
    config = check_config()

    print(f"\nBuilding directory for: {config['niche']}")
    print(f"Site name: {config['site_name']}")
    print(f"Domain: {config['domain']}")

    # Create directories
    for d in ["data", "images", "dist", "dist/listings", "dist/category", "dist/location", "dist/blog"]:
        Path(d).mkdir(parents=True, exist_ok=True)

    steps = [
        (1, "01_scrape.py",   "Scraping raw listings from Google Maps"),
        (2, "02_clean.py",    "Cleaning and deduplicating data"),
        (3, "03_verify.py",   "Verifying websites with Crawl4AI"),
        (4, "04_enrich.py",   "Enriching listings with Claude AI"),
        (5, "05_images.py",   "Extracting and verifying images"),
        (6, "06_generate.py", "Generating static site (all pages)"),
    ]

    for step_num, script, description in steps:
        run_step(step_num, script, description)

    print("\n" + "="*60)
    print("PIPELINE COMPLETE")
    print("="*60)
    print(f"\nSite generated in: dist/")
    print(f"\nNext steps:")
    print(f"  1. Review dist/index.html in browser")
    print(f"  2. Deploy: bash scripts/07_deploy.sh {config['site_name'].lower()}")
    print(f"  3. Point domain {config['domain']} to Cloudflare Pages")
    print(f"  4. Submit sitemap to Google Search Console")
    print(f"\nSee docs/DEPLOY-CHECKLIST.md for full instructions.")

if __name__ == "__main__":
    main()