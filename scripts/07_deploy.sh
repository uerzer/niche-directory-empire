#!/bin/bash
set -e
PROJECT_NAME=${1:-"my-directory"}
echo "Deploying $PROJECT_NAME to Cloudflare Pages..."
if ! command -v wrangler &> /dev/null; then
    echo "Installing wrangler..."
    npm install -g wrangler
fi
wrangler pages deploy ./dist \
  --project-name="$PROJECT_NAME" \
  --commit-message="Deploy $(date +%Y-%m-%d-%H%M)"
echo ""
echo "Deployed to: https://$PROJECT_NAME.pages.dev"
echo "Next: Add your custom domain in dash.cloudflare.com > Pages > $PROJECT_NAME > Custom domains"