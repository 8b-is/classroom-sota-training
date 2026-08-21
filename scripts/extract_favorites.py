#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""
extract_favorites.py — turn Apple Music favorites into a corpus source.

The Music app's library DB is a proprietary format, so the honest path is
the XML export: Music → File → Library → Export Library…  (creates
"Music Library.xml"). Every track carries a <key>Loved</key><true/> flag for
songs you favorited. This script extracts them and writes a curated teaching
source the corpus lane picks up automatically.

Usage:
  python scripts/extract_favorites.py ~/Music/Music\ Library.xml
  # → data/sources/music-favorites.md  (then rebuild the corpus)
"""

import argparse
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path


def dict_of(d):
    """The XML's <dict> is key/value pairs; return them as a python dict.
    <true/>/<false/> are empty elements — map them by tag, not text."""
    it = iter(d)
    out = {}
    for k in it:
        v = next(it)
        if v.tag == "true":
            out[k.text] = "true"
        elif v.tag == "false":
            out[k.text] = "false"
        else:
            out[k.text] = v.text if v is not None else None
    return out


def parse_library(path: str):
    root = ET.parse(path).getroot()
    loved = []
    for d in root.iter("dict"):
        # the Tracks dict nests each track as <key><name></key><dict>…</dict>
        pairs = list(d)
        for i in range(0, len(pairs) - 1, 2):
            key = pairs[i]
            val = pairs[i + 1]
            if key.tag != "key" or val.tag != "dict":
                continue
            kv = dict_of(val)
            if kv.get("Loved") == "true":
                loved.append({
                    "name": kv.get("Name", ""),
                    "artist": kv.get("Artist", ""),
                    "album": kv.get("Album", ""),
                    "year": kv.get("Year", ""),
                })
    return loved


def main() -> int:
    ap = argparse.ArgumentParser(description="extract Apple Music favorites into the corpus")
    ap.add_argument("xml", help="the exported Music Library.xml")
    ap.add_argument("--out", default="data/sources/music-favorites.md")
    args = ap.parse_args()

    loved = parse_library(args.xml)
    if not loved:
        sys.exit("no Loved tracks found — export the library fresh (File → Library → Export Library…)")

    loved.sort(key=lambda t: (t["artist"].lower(), t["name"].lower()))
    lines = [
        "# Peter's favorites — the Apple Music library, Loved tracks",
        "",
        f"*{len(loved)} songs favorited in the Apple Music library, extracted from "
        f"the Music Library.xml export. Added to the classroom corpus as a "
        f"teaching source — the music the teacher listens to while the pupil trains.*",
        "",
        "| # | song | artist | album |",
        "|---|------|--------|-------|",
    ]
    for i, t in enumerate(loved, 1):
        lines.append(f"| {i} | {t['name']} | {t['artist']} | {t['album']} |")
    lines.append("")
    lines.append(f"*extracted {datetime.now(timezone.utc).isoformat()}*")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines))
    print(f"favorites: {len(loved)} songs → {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
