#!/bin/bash
# Run this once from inside the university-outcomes-dashboard folder
# to create the GitHub repo, push, and enable GitHub Pages.
#
# Prerequisites:
#   1. GitHub CLI installed: https://cli.github.com
#   2. Logged in: gh auth login

set -e

REPO="university-outcomes-dashboard"
echo "→ Creating GitHub repo: $REPO"
gh repo create "$REPO" --public --description "Interactive dashboard comparing 47 Australian university outcomes" --push --source .

echo "→ Enabling GitHub Pages (serving from main branch root)"
gh api "repos/$(gh api user --jq .login)/$REPO/pages" \
  --method POST \
  --field source='{"branch":"main","path":"/"}' 2>/dev/null || true

USER=$(gh api user --jq .login)
echo ""
echo "✓ Done!"
echo "  Repo:      https://github.com/$USER/$REPO"
echo "  Live site: https://$USER.github.io/$REPO"
echo ""
echo "  GitHub Pages usually goes live within 1–2 minutes."
