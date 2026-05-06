#!/bin/bash
# Build and stage for GitHub Pages deployment.
# Output goes to /Users/nairne/claude-central-hub/tia-972/
# Live URL: https://theastark1-cpu.github.io/claude-central-hub/tia-972/
set -euo pipefail
export PATH="$HOME/.local/node/bin:$PATH"
cd "$(dirname "$0")"
VITE_BASE="/claude-central-hub/tia-972/" npm run build
DEPLOY_DIR="$(cd .. && pwd)/tia-972"
rm -rf "$DEPLOY_DIR"
mkdir -p "$DEPLOY_DIR"
cp -R dist/. "$DEPLOY_DIR/"
cp -R public/data "$DEPLOY_DIR/"
echo "Built into $DEPLOY_DIR. Now: cd .. && git add tia-972 && git commit -m '...' && git push"
