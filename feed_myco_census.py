#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""feed-myco-census: a names-only census of CFIA's open livestock-feed mycotoxin file.

Made with AI agents working in MV2's (Munim, Inc.) name.

The Canadian Food Inspection Agency (CFIA) publishes, on open.canada.ca under the Open
Government Licence - Canada, the results of its "Mycotoxin Monitoring Program for Livestock
Feeds" for April 1, 2000 - March 31, 2018 (dataset 2d636f59-5f04-4725-afae-376850bc71d4;
English CSV resource b8cad53e-0a93-4366-a764-246fbc980c1f). As far as we have found there is
no published analysis of this file.

This script reads ONLY the structure of that file: the SHA-256, the exact column headers, the
row and distinct-sample counts, the rows-per-sample distribution, the distinct labels (and their
row counts) for the low-cardinality categorical columns, and a file-level FORMAT census of the
Test result column (how many cells are below-LOQ "<" censored, numeric, blank, zero or token).

It deliberately does NOT compute any analysis outcome that a later blind pre-registration will
test: it does not report detection rates by mycotoxin or by year, it does not report the
distribution, minimum or maximum of the detected (numeric) values, and it does not enumerate the
distinct limit-of-quantification values embedded in the "<" cells (the censoring-limit drift
across the 19 years is itself a planned blind target). This keeps the later study blind.

Standard library only. Code Apache-2.0; derived summary CC BY 4.0. Not a finding about any
product, brand or health risk, and not individual dietary, veterinary or medical advice.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import sys
import time
import urllib.request

VERSION = "0.1.0"

DATASET = "2d636f59-5f04-4725-afae-376850bc71d4"
RESOURCE = "b8cad53e-0a93-4366-a764-246fbc980c1f"
FILENAME = ("Mycotoxin_Monitoring_Program_for_Livestock_Feeds_-_Results_from_"
            "April_1_2000_-_March_31_2018.csv")
URLS = (
    "https://active.inspection.gc.ca/opengov/eng/open-data/" + FILENAME,
    f"https://open.canada.ca/data/dataset/{DATASET}/resource/{RESOURCE}/download/{FILENAME}",
    f"https://ouvert.canada.ca/data/dataset/{DATASET}/resource/{RESOURCE}/download/{FILENAME}",
)

# Columns whose distinct values are reported in full only when the cardinality is at or below
# this cap; otherwise just the cardinality (and, for a feel, the most common values) is reported.
CARD_CAP = 80

# Non-detect word tokens seen in CFIA files (in case any appear here); the primary non-detect
# marker in this file is the "<" (below limit of quantification) prefix.
ND_TOKENS = ("nd", "n.d.", "n/d", "not detected", "non détecté", "non detecte", "<loq", "< loq")


# ---------------------------------------------------------------------------
# Pure helpers (unit-tested offline).
# ---------------------------------------------------------------------------
def clean(cell):
    return (cell or "").replace("﻿", "").strip()


def classify_result(raw):
    """Classify one Test-result cell into a FORMAT kind, revealing no numeric value.

    Returns one of: "blank", "censored", "zero", "numeric", "token", "bad".
    "censored" = a below-LOQ "<" cell; "numeric" = a detected quantified value (> 0).
    """
    s = clean(raw)
    if not s:
        return "blank"
    low = s.lower()
    if s.startswith("<") and low not in ("<loq", "< loq"):
        return "censored"
    if low in ND_TOKENS:
        return "token"
    t = s
    if t.count(",") == 1 and "." not in t:
        t = t.replace(",", ".")
    try:
        v = float(t)
    except ValueError:
        return "bad"
    if v != v or v < 0:
        return "bad"
    return "zero" if v == 0 else "numeric"


def find_col(header, *needles):
    """Index of the first column whose cleaned, lowercased name contains all needles."""
    for i, c in enumerate(header):
        name = clean(c).lower()
        if all(n in name for n in needles):
            return i
    return None


def bump(d, k):
    d[k] = d.get(k, 0) + 1


def profile_categorical(values):
    """Distinct-value counts for one column, capped for high-cardinality columns."""
    counts = {}
    for v in values:
        bump(counts, v)
    distinct = len(counts)
    ordered = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    out = {"distinct": distinct}
    if distinct <= CARD_CAP:
        out["values"] = dict(sorted(counts.items()))
    else:
        # High cardinality (e.g. ingredient common name): report only the shape, not every label.
        out["top"] = dict(ordered[:40])
        out["note"] = f"high cardinality ({distinct}); showing 40 most common labels only"
    return out


def census(text):
    """Build the names-only census dict from the decoded CSV text."""
    table = list(csv.reader(io.StringIO(text)))
    header = [clean(c) for c in table[0]]
    body = [r for r in table[1:] if any(c.strip() for c in r)]

    cols = {
        "fiscal_year": find_col(header, "fiscal"),
        "system_id": find_col(header, "system"),
        "species": find_col(header, "species"),
        "feed_type": find_col(header, "feed", "type"),
        "province": find_col(header, "province"),
        "mycotoxin": find_col(header, "mycotoxin"),
        "result": find_col(header, "result"),
        "unit": find_col(header, "unit"),
        "ingredient_type": find_col(header, "ingredient", "type"),
        "ingredient_name": find_col(header, "ingredient", "name"),
    }

    def column(key):
        i = cols[key]
        if i is None:
            return None
        return [clean(r[i]) if i < len(r) else "" for r in body]

    # File-level FORMAT census of the Test-result column (no numeric values revealed).
    result_kinds = {}
    result_vals = column("result") or []
    for v in result_vals:
        bump(result_kinds, classify_result(v))

    # Rows-per-sample distribution over distinct System IDs.
    rows_per_sample_dist = {}
    distinct_samples = None
    sids = column("system_id")
    if sids is not None:
        per = {}
        for s in sids:
            bump(per, s)
        distinct_samples = len(per)
        for n in per.values():
            bump(rows_per_sample_dist, str(n))

    categorical = {}
    for key in ("fiscal_year", "species", "feed_type", "province", "mycotoxin", "unit",
                "ingredient_type", "ingredient_name"):
        vals = column(key)
        if vals is not None:
            categorical[key] = profile_categorical(vals)

    return {
        "columns_in_order": header,
        "n_columns": len(header),
        "column_index": cols,
        "n_rows": len(body),
        "distinct_system_ids": distinct_samples,
        "rows_per_sample_distribution": dict(sorted(
            rows_per_sample_dist.items(), key=lambda kv: int(kv[0]))),
        "result_format_kinds": dict(sorted(result_kinds.items())),
        "categorical": categorical,
    }


# ---------------------------------------------------------------------------
# Data loading (network only here; this is a census so we COMPUTE the SHA-256).
# ---------------------------------------------------------------------------
def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def fetch(url, tries=3, pause=8):
    last = None
    for _ in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "mv2-feed-myco-census"})
            with urllib.request.urlopen(req, timeout=180) as resp:
                return resp.read()
        except Exception as exc:  # noqa: BLE001 - retry, then try the next host
            last = exc
            time.sleep(pause)
    raise RuntimeError(f"{url}: {last}")


def load(data_dir):
    """Return (raw_bytes, source). Prefer a local copy in the data volume, else download."""
    path = os.path.join(data_dir, RESOURCE + ".csv") if data_dir else ""
    if path and os.path.exists(path):
        with open(path, "rb") as fh:
            return fh.read(), "data-volume"
    errors = []
    for url in URLS:
        try:
            raw = fetch(url, tries=2, pause=5)
        except Exception as exc:  # noqa: BLE001
            errors.append(str(exc))
            continue
        if path:
            try:
                os.makedirs(data_dir, exist_ok=True)
                with open(path, "wb") as fh:
                    fh.write(raw)
            except OSError:
                pass
        return raw, url
    raise RuntimeError("no copy of the livestock-feed file: " + "; ".join(errors))


def decode(raw):
    for enc in ("utf-8-sig", "cp1252"):
        try:
            return raw.decode(enc), enc
        except UnicodeDecodeError:
            continue
    return raw.decode("latin-1"), "latin-1"


def main(argv=None):
    ap = argparse.ArgumentParser(description="Names-only census of the CFIA livestock-feed file.")
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="out")
    args = ap.parse_args(argv)

    raw, source = load(args.data_dir)
    text, enc = decode(raw)
    cen = census(text)
    out = {
        "study": "feed-myco-census",
        "version": VERSION,
        "dataset": DATASET,
        "resource": RESOURCE,
        "filename": FILENAME,
        "provenance": {"sha256": sha256(raw), "bytes": len(raw), "encoding": enc,
                       "source": source},
        "census": cen,
        "note": ("Names-only census: labels, counts and result FORMAT only. No detection rate, "
                 "numeric distribution or distinct LOQ value is reported, so a later blind "
                 "pre-registration stays blind."),
    }
    os.makedirs(args.out_dir, exist_ok=True)
    with open(os.path.join(args.out_dir, "feed_myco_census.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, sort_keys=True)
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
