"""
Post-build binary patches — applied to every TTF in fonts/.

Covers the Font Bakery FAILs that `gftools fix-font` doesn't catch:
- fsType = 0 (no DRM)
- USE_TYPO_METRICS bit set
- typo/hhea/win metrics synced
- latn + thai script declarations in GSUB/GPOS
- C1 control codepoints stripped from cmap
- copyright (name 0), license (13), license URL (14)

Tune CONFIG below for your project.
"""
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables.otTables import ScriptRecord, Script, DefaultLangSys

CONFIG = {
    "copyright":   "Copyright {YEAR} The {FAMILY} Project Authors (https://github.com/USER/REPO)",
    "license":     ("This Font Software is licensed under the SIL Open Font "
                    "License, Version 1.1. This license is available with a "
                    "FAQ at: https://openfontlicense.org"),
    "license_url": "https://openfontlicense.org",
    "vendor_id":   "XXXX",             # 4 chars, register at https://learn.microsoft.com/typography/vendors/
    "scripts":     ["latn", "thai"],
}

def setname(name, nid, value):
    name.setName(value, nid, 3, 1, 0x409)
    name.setName(value, nid, 1, 0, 0)

def add_scripts(font, table_tag, tags):
    if table_tag not in font: return
    table = font[table_tag].table
    existing = {sr.ScriptTag for sr in table.ScriptList.ScriptRecord}
    dflt = next((sr for sr in table.ScriptList.ScriptRecord if sr.ScriptTag == "DFLT"), None)
    if dflt is None: return
    feats = list(dflt.Script.DefaultLangSys.FeatureIndex)
    for tag in tags:
        if tag in existing: continue
        sr = ScriptRecord()
        sr.ScriptTag = tag
        sr.Script = Script()
        sr.Script.LangSysRecord = []
        sr.Script.LangSysCount = 0
        dls = DefaultLangSys()
        dls.LookupOrder = None
        dls.ReqFeatureIndex = 0xFFFF
        dls.FeatureIndex = list(feats)
        dls.FeatureCount = len(feats)
        sr.Script.DefaultLangSys = dls
        table.ScriptList.ScriptRecord.append(sr)
    table.ScriptList.ScriptRecord.sort(key=lambda s: s.ScriptTag)
    table.ScriptList.ScriptCount = len(table.ScriptList.ScriptRecord)

def patch(path: Path):
    f = TTFont(path)

    # No DRM, typo metrics flag
    f["OS/2"].fsType = 0
    f["OS/2"].fsSelection |= (1 << 7)
    f["OS/2"].achVendID = CONFIG["vendor_id"]

    # Sync vertical metrics (hhea is source of truth — set it in UFOs)
    f["OS/2"].sTypoAscender = f["hhea"].ascent
    f["OS/2"].sTypoDescender = f["hhea"].descent
    f["OS/2"].sTypoLineGap = 0
    f["hhea"].lineGap = 0
    f["OS/2"].usWinAscent = max(f["OS/2"].usWinAscent, f["hhea"].ascent)
    f["OS/2"].usWinDescent = max(f["OS/2"].usWinDescent, -f["hhea"].descent)

    # Strip C1 control codepoints from cmap
    for sub in f["cmap"].tables:
        for cp in range(0x0080, 0x00A0):
            sub.cmap.pop(cp, None)

    # Scripts
    for tbl in ("GSUB", "GPOS"):
        add_scripts(f, tbl, CONFIG["scripts"])

    # Legal name entries
    name = f["name"]
    for nid in (0, 13, 14):
        for rec in list(name.names):
            if rec.nameID == nid:
                name.names.remove(rec)
    setname(name, 0, CONFIG["copyright"])
    setname(name, 13, CONFIG["license"])
    setname(name, 14, CONFIG["license_url"])

    f.save(path)
    print(f"  patched {path.name}")

if __name__ == "__main__":
    root = Path("fonts")
    targets = list(root.rglob("*.ttf"))
    if not targets:
        print("no TTFs found under fonts/ — build first")
        raise SystemExit(1)
    print(f"patching {len(targets)} file(s)")
    for p in targets:
        patch(p)
