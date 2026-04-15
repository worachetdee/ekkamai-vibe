# {{FAMILY_NAME}}

A Thai–Latin variable font family by {{DESIGNER_NAME}}.

This template is pre-wired for Google Fonts submission: `gftools builder` for
the VF build, Font Bakery in CI, proper OFL metadata, and a `features.fea`
starter with the Thai shaping features shapers expect (`ccmp`, `locl`, `mark`,
`mkmk`).

---

## Quick start

```bash
# 1. Replace placeholders (FAMILY_NAME, FAMILY_SLUG, DESIGNER_NAME, GITHUB_URL)
#    with a single sed pass, then review.
./scripts/rename.sh "My Family" "myfamily" "Your Name" https://github.com/you/myfamily

# 2. Install build tools
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 3. Put your UFOs in sources/ (one per master weight)
#    Expected: {{FAMILY_SLUG}}-Thin.ufo, -Regular.ufo, -Bold.ufo, etc.
#    Update sources/{{FAMILY_SLUG}}.designspace if your axis layout differs.

# 4. Build
make build        # variable + static TTFs into fonts/
make check        # Font Bakery against Google Fonts profile
make clean
```

---

## Repo layout

```
.
├── sources/
│   ├── {{FAMILY_SLUG}}.designspace    # axis + master locations
│   ├── {{FAMILY_SLUG}}-*.ufo          # editable masters
│   ├── features/                      # shared .fea includes (ccmp, thai marks)
│   └── config.yaml                    # gftools builder config
├── fonts/
│   ├── variable/                      # VF output: {Slug}[wght].ttf
│   └── ttf/                           # static output: {Slug}-*.ttf
├── .github/workflows/
│   ├── build.yml                      # build VF + statics on push
│   └── fontbakery.yml                 # GF profile check on every PR
├── scripts/
│   ├── rename.sh                      # one-shot placeholder replacer
│   └── patch_metadata.py              # post-build binary patches
├── AUTHORS.txt
├── CONTRIBUTORS.txt
├── FONTLOG.txt
├── DESCRIPTION.en_us.html
├── OFL.txt
├── Makefile
├── requirements.txt
└── README.md
```

---

## Design requirements for clean GF submission

### Interpolation-compatible masters

Every glyph must have **the same node count and contour count in every master**.
FontLab: Font Info → Masters → "Check compatibility". Glyphs: View → Show
Master Compatibility. Without this, the variable build fails.

### Axis plan

The template assumes a single `wght` axis (100→900, default 400). To add
`wdth` or italic:

1. Export UFOs for each additional master
2. Add `<axis>` + `<source>` entries in the designspace
3. Update `sources/config.yaml` instances

### Thai shaping — the non-negotiables

A Thai font without these is unusable in production:

1. **Anchors on every Thai consonant + every mark glyph.** FontLab auto-builds
   `mark` and `mkmk` from anchor names (`top`, `bottom`, `topleft`, `_top`,
   `_bottom`). No anchors = tone marks stack incorrectly on tall consonants.
2. **`ccmp` feature** for preposed vowel + tone reordering (เ ่ า → sequence
   swaps). The starter `features/thai.fea` has the skeleton.
3. **`locl` THA** for Thai-specific glyph variants (e.g., loopless ก, ธ forms
   for some design contexts).
4. **Declare `thai` script** in GSUB + GPOS (the template does this).

### Whitespace, notdef, and mandatory glyphs

- `space` (U+0020): **empty**, same advance width across all masters
  (recommend 200–260).
- `nbsp` (U+00A0): empty, same width as `space`.
- `.notdef`: **visible shape** (box with X is fine).
- Remove C1 control codepoints (U+0080–U+009F) from cmap.

### Vertical metrics

Ekkamai Vibe's original bug: `OS/2.sTypoAscender` and `sTypoDescender` didn't
match `hhea.ascent`/`descent`. With `fsSelection` bit 7 (`USE_TYPO_METRICS`)
set, apps use typo values → clipped line spacing.

**Rule:** `hhea.ascent == OS/2.sTypoAscender == OS/2.usWinAscent` and
`hhea.descent == OS/2.sTypoDescender == -OS/2.usWinDescent`.
Set these once in the source `fontinfo.plist`; `gftools fix-vertical-metrics`
re-applies after build.

---

## Release flow

```bash
# 1. Bump version in sources/*.ufo fontinfo (openTypeNameVersion)
# 2. Build
make build

# 3. Check
make check

# 4. Snapshot into versions/
make snapshot VERSION=1.001

# 5. Tag + push
git tag v1.001
git push --follow-tags

# 6. Submit to Google Fonts
#    Fork google/fonts, copy fonts/variable/ into ofl/{family_slug}/,
#    open PR following https://googlefonts.github.io/gf-guide/onboarding.html
```

---

## License

SIL Open Font License 1.1 — see `OFL.txt`.
