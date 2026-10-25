#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""pdf_text: plain-text copies of CFIA's published mycotoxin survey reports.

Made with AI agents working in MV2's (Munim, Inc.) name.

CFIA's survey reports are compressed PDFs, so their printed tables cannot be read without a text
extractor. This fetches each report and writes <name>.txt (pages separated by a form feed and a
'=== page N ===' line) with pypdf, plus the PDF's SHA-256, so later pre-registrations can quote
CFIA's printed figures exactly. Reports only; no survey data file is read here.
0.1.1: site-relative open.canada.ca resource URLs are made absolute.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import sys
import time
import urllib.parse
import urllib.request

from pypdf import PdfReader

SITE = "https://open.canada.ca/"
BASE = "https://inspection.canada.ca/DAM/DAM-food-aliments/STAGING/text-texte/"
LEGACY = "https://inspection.canada.ca/sites/default/files/legacy/DAM/DAM-food-aliments/STAGING/text-texte/"
REPORTS = {
    "don-infant-cereal-2018-19": BASE + "deoxynivalenol_infant_cereal_1671718288841_eng.pdf",
    "ota-selected-foods-2012-2022": LEGACY + "bct_pth_ochratoxin_a_slctd_fds_1671645086779_eng.pdf",
    "ota-grains-2018-19": BASE + "ochratoxin_grains_apr_2018_mar_2019_1593541026427_eng.pdf",
    "multi-mycotoxins-milled-grain-2015-18": BASE + "multi-mycotoxins_in_milled_grain_products-april_1_2015_to_march_31_2018_1697482956573_eng.pdf",
}
UA = {"User-Agent": "Mozilla/5.0 (compatible; mv2-pdf-text/0.1; +https://github.com/munimtechnologies)"}


def absolute(url):
    if url.startswith("/"):
        return urllib.parse.urljoin(SITE, url)
    return url


def fetch(url, tries=3, pause=8):
    last = None
    for _ in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=120) as resp:
                return resp.read()
        except Exception as exc:  # noqa: BLE001 - retry, then report
            last = exc
            time.sleep(pause)
    raise RuntimeError(f"{url}: {last}")


def extract(raw):
    reader = PdfReader(io.BytesIO(raw))
    parts = []
    for i, page in enumerate(reader.pages, 1):
        parts.append(f"=== page {i} ===\n{page.extract_text() or ''}")
    return "\n\f".join(parts), len(reader.pages)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Text copies of CFIA mycotoxin reports.")
    ap.add_argument("--out-dir", default="/out/reports")
    ap.add_argument("--census", default="/out/myco_census.json",
                    help="also extract any PDF resource the census found")
    args = ap.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)
    todo = dict(REPORTS)
    if os.path.exists(args.census):
        with open(args.census, encoding="utf-8") as fh:
            for k, p in enumerate(json.load(fh).get("pdf_resources", [])):
                todo.setdefault(f"resource-{p['dataset'][:8]}-{k}", absolute(p["url"]))
    index = {}
    for name, url in todo.items():
        try:
            raw = fetch(url)
            text, pages = extract(raw)
        except Exception as exc:  # noqa: BLE001 - reported, the rest still run
            index[name] = {"url": url, "error": str(exc)}
            print(f"FAIL {name}: {exc}")
            continue
        with open(os.path.join(args.out_dir, name + ".txt"), "w", encoding="utf-8") as fh:
            fh.write(text)
        index[name] = {"url": url, "sha256": hashlib.sha256(raw).hexdigest(),
                       "bytes": len(raw), "pages": pages, "chars": len(text)}
        print(f"OK {name}: {pages} pages, {len(text)} chars")
    with open(os.path.join(args.out_dir, "index.json"), "w", encoding="utf-8") as fh:
        json.dump(index, fh, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
