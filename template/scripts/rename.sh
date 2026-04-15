#!/usr/bin/env bash
# One-shot placeholder replacer for the template.
# Usage: ./scripts/rename.sh "My Family" "myfamily" "Your Name" https://github.com/you/myfamily
set -euo pipefail

if [[ $# -ne 4 ]]; then
  echo "Usage: $0 <FAMILY_NAME> <family_slug> <DESIGNER_NAME> <GITHUB_URL>"
  echo "Example: $0 \"Bangkok Grotesk\" bangkokgrotesk \"Jane Doe\" https://github.com/jane/bangkokgrotesk"
  exit 1
fi

FAMILY_NAME="$1"
FAMILY_SLUG="$2"
DESIGNER_NAME="$3"
GITHUB_URL="$4"

# sed -i differs between macOS and Linux
if [[ "$(uname)" == "Darwin" ]]; then SED_INPLACE=(sed -i ""); else SED_INPLACE=(sed -i); fi

# Replace in text files
grep -rl "FAMILY_NAME_PLACEHOLDER\|FAMILY_SLUG_PLACEHOLDER\|DESIGNER_NAME_PLACEHOLDER\|GITHUB_URL_PLACEHOLDER" \
     --include=\*.md --include=\*.yaml --include=\*.yml --include=\*.txt --include=\*.html \
     --include=\*.fea --include=\*.py --include=\*.designspace --include=Makefile . 2>/dev/null | \
while read -r f; do
  "${SED_INPLACE[@]}" -e "s|FAMILY_NAME_PLACEHOLDER|${FAMILY_NAME}|g" \
                       -e "s|FAMILY_SLUG_PLACEHOLDER|${FAMILY_SLUG}|g" \
                       -e "s|DESIGNER_NAME_PLACEHOLDER|${DESIGNER_NAME}|g" \
                       -e "s|GITHUB_URL_PLACEHOLDER|${GITHUB_URL}|g" \
                       "$f"
done

# Rename the designspace and (expected) UFO files
if [[ -f "sources/FAMILY_SLUG_PLACEHOLDER.designspace" ]]; then
  mv "sources/FAMILY_SLUG_PLACEHOLDER.designspace" "sources/${FAMILY_SLUG}.designspace"
fi

echo ""
echo "Renamed to: $FAMILY_NAME ($FAMILY_SLUG)"
echo "Next: drop your UFOs into sources/ as ${FAMILY_SLUG}-{Thin,Light,Regular,Bold,Heavy}.ufo"
