#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""myco_census: a names-only census of CFIA's open mycotoxin survey files.

Made with AI agents working in MV2's (Munim, Inc.) name.

The Canadian Food Inspection Agency (CFIA) released its per-sample targeted-survey files for
ochratoxin A, deoxynivalenol (DON) and other mycotoxins on open.canada.ca in October 2026 (Open
Government Licence - Canada). Before any study is pre-registered on one of them, this job records
what can be known without reading a single result value:

  - every matching dataset, its resources, and each CSV's SHA-256, size and row count;
  - the header, and the label counts of the descriptive columns only (product, plan code,
    function, origin, test type, component, unit), plus (product, plan, component) tuples;
  - how many rows each sample number has, and the sampling-date range of each plan code;
  - a FORMAT census of the result column that never reports a value: counts of blank cells,
    "<" values, not-detected tokens, unparseable cells and numeric cells, whether a literal 0
    appears, how many distinct numeric strings there are, and the largest number of rows that
    share one non-zero string (a high count would mean a detection limit is written in place of
    a non-detect, as in CFIA's 2011-12 coumarin file).

Columns not on the descriptive whitelist are reported only by their number of distinct values.
Raw files are kept in /data (named by resource id) for later sealed jobs. Standard library only.

0.1.1: CKAN's package_search returns uploaded resources with a site-relative URL
("/data/dataset/..."), which 0.1.0 could not fetch (only 2 of the 40 CSVs it tried were read). URLs are now
made absolute. The National Chemical Residue Monitoring Program annual-report annexes are listed
but not downloaded, so they cannot use up the file budget. The livestock-feed file's headers
("System ID", "Test Result", "Sampled at - Province", "Mycotoxin", ...) now get their proper roles.
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
import urllib.parse
import urllib.request

VERSION = "0.1.1"
SITE = "https://open.canada.ca/"
API = SITE + "data/api/action/"
QUERIES = ("ochratoxin", "deoxynivalenol", "mycotoxin", "mycotoxins", "aflatoxin", "patulin",
           "fumonisin", "zearalenone", "ergot", "vomitoxin", "alternaria")
UA = {"User-Agent": "Mozilla/5.0 (compatible; mv2-myco-census/0.1; +https://github.com/munimtechnologies)"}
MAX_FILES = 40
# Listed, never downloaded: large multi-hazard annual-report annexes, not mycotoxin surveys.
SKIP_TITLES = ("National Chemical Residue Monitoring Program",)

# Descriptive columns whose labels may be counted (English part of the bilingual header).
LABEL_COLUMNS = ("Function", "Origin", "Product", "Type of Test", "Component", "Unit",
                 "Plan Code", "Commodity", "Analyte", "Sample Type", "Product Type", "Category",
                 "Fiscal Year", "Target Species", "Feed Type", "Ingredient Type",
                 "Ingredient Common Name", "Sampled at", "Mycotoxin", "Country of Origin")
VALUE_PREFIXES = ("Amount", "Result", "Résultat", "Value", "Concentration", "Level",
                  "Test Result")
SAMPLE_PREFIXES = ("Sample No", "Sample Number", "Sample ID", "Sample #", "System ID")
ND_TOKENS = ("nd", "n.d.", "n/d", "not detected", "non détecté", "non detecte", "<lod", "<loq")


def absolute(url):
    """open.canada.ca resource URLs from package_search may be site-relative."""
    if url.startswith("/"):
        return urllib.parse.urljoin(SITE, url)
    return url


def english(name):
    """The English part of a bilingual header cell such as 'Unit – Unité'."""
    s = name.replace("﻿", "").strip()
    for sep in (" – ", " / "):
        if sep in s:
            s = s.split(sep)[0]
    if " - " in s and not s.startswith("Sampled at"):
        s = s.split(" - ")[0]
    return s.strip()


def role(name):
    e = english(name)
    if e.startswith(VALUE_PREFIXES):
        return "value"
    if e.startswith(SAMPLE_PREFIXES) or e == "Sample":
        return "sample"
    if e.startswith("Date"):
        return "date"
    for lab in LABEL_COLUMNS:
        if e == lab or e.startswith(lab + " "):
            return "label:" + lab
    if e in ("Fonction", "Origine", "Produit", "Type d'analyse", "Type d’analyse", "Composant"):
        return "french"
    return "other"


def classify(raw):
    """Format kind of one result cell; never returns the value itself."""
    s = (raw or "").strip()
    if not s:
        return "blank"
    if s.startswith("<"):
        return "lt"
    if s.lower() in ND_TOKENS:
        return "nd_token"
    try:
        v = float(s)
    except ValueError:
        if s.count(",") == 1 and "." not in s:
            try:
                v = float(s.replace(",", "."))
            except ValueError:
                return "bad"
            return "zero" if v == 0 else "numeric_comma"
        return "bad"
    if v != v or v < 0:
        return "bad"
    return "zero" if v == 0 else "numeric"


def _bump(d, k):
    d[k] = d.get(k, 0) + 1


def census_text(text):
    """Census of one decoded CSV. Reports labels and formats only, never a result value."""
    table = list(csv.reader(io.StringIO(text)))
    if not table:
        return {"error": "empty"}
    header = table[0]
    body = [r for r in table[1:] if any(c.strip() for c in r)]
    roles = [role(h) for h in header]
    out = {"header": header, "roles": roles, "n_rows": len(body), "labels": {},
           "other_columns_distinct": {}, "value_columns": [], "rows_per_sample": {},
           "distinct_samples": None, "dates_by_plan": {}, "tuples": {}}

    def col(*names):
        for name in names:
            for i, r in enumerate(roles):
                if r == name:
                    return i
        return None

    def cell(r, i):
        return r[i] if i is not None and i < len(r) else ""

    i_prod = col("label:Product", "label:Ingredient Common Name")
    i_plan = col("label:Plan Code", "label:Fiscal Year")
    i_comp = col("label:Component", "label:Mycotoxin")
    i_samp, i_date = col("sample"), col("date")
    for i, rl in enumerate(roles):
        if rl.startswith("label:"):
            counts = {}
            for r in body:
                _bump(counts, cell(r, i))
            out["labels"][header[i]] = dict(sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])))
        elif rl in ("other", "french"):
            out["other_columns_distinct"][header[i]] = len({cell(r, i) for r in body})
    for i, rl in enumerate(roles):
        if rl != "value":
            continue
        kinds, strings = {}, {}
        for r in body:
            raw = cell(r, i)
            k = classify(raw)
            _bump(kinds, k)
            if k in ("numeric", "numeric_comma"):
                _bump(strings, raw.strip())
        numeric = sum(v for k, v in kinds.items() if k in ("numeric", "numeric_comma", "zero"))
        out["value_columns"].append({
            "column": header[i],
            "non_numeric_kinds": {k: v for k, v in kinds.items()
                                  if k not in ("numeric", "numeric_comma", "zero")},
            "numeric_cells": numeric,
            "literal_zero_present": kinds.get("zero", 0) > 0,
            "comma_decimals_present": kinds.get("numeric_comma", 0) > 0,
            "distinct_nonzero_strings": len(strings),
            "max_rows_sharing_one_nonzero_string": max(strings.values()) if strings else 0,
        })
    if i_samp is not None:
        per = {}
        for r in body:
            _bump(per, cell(r, i_samp))
        out["distinct_samples"] = len(per)
        dist = {}
        for v in per.values():
            _bump(dist, str(v))
        out["rows_per_sample"] = dist
    if i_date is not None:
        rng = {}
        for r in body:
            p, d = cell(r, i_plan), cell(r, i_date).strip()
            if not d:
                continue
            lo, hi = rng.get(p, (d, d))
            rng[p] = (min(lo, d), max(hi, d))
        out["dates_by_plan"] = {p: list(v) for p, v in sorted(rng.items())}
    tuples = {}
    for r in body:
        _bump(tuples, " | ".join((cell(r, i_prod), cell(r, i_plan), cell(r, i_comp))))
    out["tuples"] = dict(sorted(tuples.items()))
    return out


def decode(raw):
    for enc in ("utf-8-sig", "cp1252"):
        try:
            return raw.decode(enc), enc
        except UnicodeDecodeError:
            continue
    return raw.decode("latin-1"), "latin-1"


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


def api(action, **params):
    url = API + action + "?" + urllib.parse.urlencode(params)
    return json.loads(fetch(url).decode("utf-8"))


def find_datasets():
    """Every open.canada.ca dataset that matches a mycotoxin query (CFIA or not; reported)."""
    found = {}
    for q in QUERIES:
        try:
            res = api("package_search", q=q, rows=100)
        except Exception as exc:  # noqa: BLE001
            print(f"  package_search {q}: {exc}")
            continue
        for pkg in res.get("result", {}).get("results", []):
            found.setdefault(pkg["id"], pkg)
    return found


def title_of(pkg):
    t = pkg.get("title_translated") or {}
    return t.get("en") or pkg.get("title") or ""


def wanted(org, title):
    return "Canadian Food Inspection Agency" in org and not title.startswith(SKIP_TITLES)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Names-only census of CFIA mycotoxin files.")
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="/out")
    args = ap.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)
    pkgs = find_datasets()
    datasets, pdfs, n_files = [], [], 0
    for pid, pkg in sorted(pkgs.items(), key=lambda kv: title_of(kv[1])):
        org = (pkg.get("organization") or {}).get("title", "")
        entry = {"id": pid, "title": title_of(pkg), "organization": org,
                 "metadata_created": pkg.get("metadata_created"),
                 "metadata_modified": pkg.get("metadata_modified"), "resources": []}
        for res in pkg.get("resources", []):
            fmt = (res.get("format") or "").upper()
            url = absolute(res.get("url") or "")
            r = {"id": res.get("id"), "name": (res.get("name_translated") or {}).get("en")
                 or res.get("name"), "format": fmt, "url": url}
            if fmt == "PDF" or url.lower().endswith(".pdf"):
                pdfs.append({"dataset": pid, "url": url})
            if fmt == "CSV" and wanted(org, entry["title"]) and n_files < MAX_FILES:
                n_files += 1
                try:
                    raw = fetch(url)
                except Exception as exc:  # noqa: BLE001
                    r["error"] = str(exc)
                    entry["resources"].append(r)
                    continue
                r["sha256"] = hashlib.sha256(raw).hexdigest()
                r["bytes"] = len(raw)
                text, enc = decode(raw)
                r["encoding"] = enc
                r["census"] = census_text(text)
                try:
                    os.makedirs(args.data_dir, exist_ok=True)
                    with open(os.path.join(args.data_dir, f"{r['id']}.csv"), "wb") as fh:
                        fh.write(raw)
                    r["saved_as"] = f"{r['id']}.csv"
                except OSError as exc:
                    r["save_error"] = str(exc)
            entry["resources"].append(r)
        datasets.append(entry)
    result = {"tool": "myco_census", "version": VERSION, "n_datasets": len(datasets),
              "n_csv_read": n_files, "datasets": datasets, "pdf_resources": pdfs}
    with open(os.path.join(args.out_dir, "myco_census.json"), "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=1, ensure_ascii=False)
    for d in datasets:
        print(f"{d['id']}  {d['organization'][:12]}  {d['title']}")
        for r in d["resources"]:
            c = r.get("census") or {}
            print(f"    {r['format']:5} {r.get('id')}  rows={c.get('n_rows')} "
                  f"samples={c.get('distinct_samples')} sha={str(r.get('sha256'))[:16]} "
                  f"{r.get('error', '')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
