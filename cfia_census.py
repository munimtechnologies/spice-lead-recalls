#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""cfia-census 0.1.0: a names-only structure census of three open CFIA targeted-survey files, run
before any result value is read, so later pre-registrations can map file labels to each report's
product types blind:

- "Polycyclic Aromatic Hydrocarbons in Selected Foods - 2019-2020" (dataset 4884f9d1-...)
- "Bisphenol A and BPA Alternatives in Selected Canned Foods and Infant Formula - April 1, 2018
  to March 31, 2019" (dataset b8686c21-...)
- "Open Data for Chemistry Targeted Surveys - 2020-21 Bisphenol A and BPA Alternatives in
  Selected Canned Foods" (dataset 5b36b36d-...)

All three are on open.canada.ca under the Open Government Licence - Canada. For each file it
counts rows, samples, components, product and commodity labels (per sample), origins and declared
functions, units, plan codes and test types, and classifies every result cell only by its SHAPE
(number, '<' number, negative number, text token, blank). It never prints, sums or compares a
result value. Standard library only. Made with AI agents working in MV2's (Munim, Inc.) name.
Code Apache-2.0; derived data CC BY 4.0.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import re
import sys
import time
import urllib.request

VERSION = "0.1.0"
TARGETS = (
    {"name": "pah-2019",
     "dataset": "4884f9d1-0a59-4c8e-85ca-157d13411d19",
     "resource": "d5b3cca2-4ccf-4aed-a4d1-0af540422575",
     "path": "fsap_chem_ts_2019-2020_pahs_in_selected_foods_-_open_data.csv",
     "size": 831190, "md5": "0bb033bbcdab8305839d0a8716def1b3"},
    {"name": "bpa-2018",
     "dataset": "b8686c21-a8ef-4037-8478-353ed45a0145",
     "resource": "7a20917c-8aa9-4af6-8ce4-13620ef3af59",
     "path": ("cfia_acia-15084827-v1-chem-ts_2018-19_bpa-and-bpa-alternatives-in-selected-foods_"
              "data-for-open-d.csv"),
     "size": 289825, "md5": "5cf4d04c1e4db3825dc51cfe09ea6415"},
    {"name": "bpa-2020",
     "dataset": "5b36b36d-4f8b-4b0c-b407-42b8076b3730",
     "resource": "df188f89-3dba-4650-bfbb-e4c46f89d21a",
     "path": ("cfia_acia-1351-v1-open_data_for_chem_ts_survey_-_2020-21_-_bisphenol_a_and_bpa_"
              "alternatives_in_s.csv"),
     "size": 285553, "md5": "31a4ca35a9f46e0d59cc637314c744a9"},
)
ID_RE = re.compile(r"^C\d{4}[A-Z]+(\d{4,6})(D?)$")
MAX_EXAMPLES = 10


def clean(cell):
    """A cell without BOM, edge spaces or repeated inner spaces."""
    return " ".join((cell or "").replace("﻿", "").split())


def head(name):
    """Normalised English part of a header cell: 'PLAN_CODE' -> 'plan code'."""
    h = clean(name).strip('"').lower().replace("_", " ")
    return " ".join(h.split("/")[0].split())


def find_columns(header):
    """Map roles to column indexes by the English header (None if absent)."""
    h = [head(c) for c in header]

    def pick(test):
        for i, c in enumerate(h):
            if test(c):
                return i
        return None

    return {
        "sample": pick(lambda c: c.startswith("sample") and "type" not in c and "date" not in c),
        "region": pick(lambda c: c.startswith("region")),
        "commodity": pick(lambda c: c == "commodity"),
        "function": pick(lambda c: c == "function"),
        "origin": pick(lambda c: c == "origin"),
        "product": pick(lambda c: c == "product" or c.startswith("product ")),
        "date": pick(lambda c: c.startswith("date sampled")),
        "test": pick(lambda c: c.startswith("type of test")),
        "component": pick(lambda c: c.startswith("component")),
        "value": pick(lambda c: c.startswith("maxofamount") or c.startswith("amount")
                      or c.startswith("result")),
        "unit": pick(lambda c: c.startswith("report unit") or c.startswith("unit")),
        "plan": pick(lambda c: c.startswith("plan code") or c == "plan"),
    }


KEY = ("sample", "product", "component", "value", "unit")


def _is_number(s):
    if s.count(",") == 1 and "." not in s:
        s = s.replace(",", ".")
    try:
        float(s)
    except ValueError:
        return False
    return True


def shape(raw):
    """The shape of a result cell, never its value."""
    s = clean(raw)
    if not s:
        return "blank"
    if s.startswith("<"):
        return "lt-number" if _is_number(s[1:].strip()) else "token"
    if not _is_number(s):
        return "token"
    return "negative-number" if s.startswith("-") else "number"


def _bump(d, k, n=1):
    d[k] = d.get(k, 0) + n


def _cell(r, i):
    return r[i] if i is not None and i < len(r) else ""


def census(text):
    rows = csv.reader(io.StringIO(text))
    header = next(rows, [])
    col = find_columns(header)
    out = {"header": [clean(c) for c in header], "columns": col, "rows": 0, "units": {},
           "units_by_component": {}, "plans": {}, "tests": {}, "regions": {}, "shapes": {},
           "shapes_by_component": {}, "tokens": {}, "components": {}}
    if any(col[k] is None for k in KEY):
        out["error"] = "missing key column"
        return out
    by = {}
    for r in rows:
        if not any(c.strip() for c in r):
            continue
        out["rows"] += 1
        comp = clean(_cell(r, col["component"]))
        unit = clean(_cell(r, col["unit"]))
        sh = shape(_cell(r, col["value"]))
        _bump(out["components"], comp)
        _bump(out["units"], unit)
        _bump(out["units_by_component"].setdefault(comp, {}), unit)
        _bump(out["plans"], clean(_cell(r, col["plan"])))
        _bump(out["tests"], clean(_cell(r, col["test"])))
        _bump(out["regions"], clean(_cell(r, col["region"])))
        _bump(out["shapes"], sh)
        _bump(out["shapes_by_component"].setdefault(comp, {}), sh)
        if sh == "token":
            _bump(out["tokens"], clean(_cell(r, col["value"])))
        sid = clean(_cell(r, col["sample"]))
        labels = tuple(clean(_cell(r, col[k])) for k in
                       ("product", "commodity", "function", "origin", "region", "date"))
        s = by.setdefault(sid, {"labels": set(), "components": []})
        s["labels"].add(labels)
        s["components"].append(comp)
    out.update(samples_census(by))
    return out


def samples_census(by):
    res = {"samples": len(by), "rows_per_sample": {}, "mixed_label_samples": [],
           "repeated_component_samples": {}, "missing_component_samples": {},
           "products": {}, "commodities": {}, "product_commodity": {}, "product_function": {},
           "product_origin_top": {}, "ids_bad": [], "ids_bad_count": 0, "ids_dup_suffix": [],
           "id_range": None, "id_gaps": 0, "product_id_runs": {}}
    all_comps = set()
    for s in by.values():
        all_comps.update(s["components"])
    nums = []
    for sid, s in sorted(by.items()):
        m = ID_RE.match(sid)
        if m:
            nums.append(int(m.group(1)))
            if m.group(2):
                res["ids_dup_suffix"].append(sid)
        else:
            res["ids_bad_count"] += 1
            if len(res["ids_bad"]) < MAX_EXAMPLES:
                res["ids_bad"].append(sid)
        _bump(res["rows_per_sample"], str(len(s["components"])))
        if len(s["labels"]) > 1:
            res["mixed_label_samples"].append(sid)
        rep = sorted({c for c in s["components"] if s["components"].count(c) > 1})
        if rep:
            res["repeated_component_samples"][sid] = rep
        miss = sorted(all_comps - set(s["components"]))
        if miss:
            res["missing_component_samples"][sid] = miss
        product, commodity, function, origin, _region, _date = sorted(s["labels"])[0]
        _bump(res["products"], product)
        _bump(res["commodities"], commodity)
        _bump(res["product_commodity"], f"{product} | {commodity}")
        _bump(res["product_function"].setdefault(product, {}), function or "(blank)")
        _bump(res["product_origin_top"].setdefault(product, {}), origin or "(blank)")
        runs = res["product_id_runs"].setdefault(product, [])
        n = int(m.group(1)) if m else None
        if n is not None:
            if runs and runs[-1][1] == n - 1:
                runs[-1][1] = n
            else:
                runs.append([n, n])
    if nums:
        nums.sort()
        res["id_range"] = [nums[0], nums[-1]]
        res["id_gaps"] = (nums[-1] - nums[0] + 1) - len(set(nums))
    return res


def _fetch(url, tries=2, pause=5):
    last = None
    for _ in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "mv2-cfia-census"})
            with urllib.request.urlopen(req, timeout=300) as resp:
                return resp.read()
        except Exception as exc:  # noqa: BLE001 - retry, then try the next host
            last = exc
            time.sleep(pause)
    raise RuntimeError(f"{url}: {last}")


def load(target, data_dir):
    local = os.path.join(data_dir, target["resource"] + ".csv") if data_dir else ""
    if local and os.path.exists(local):
        with open(local, "rb") as fh:
            raw = fh.read()
        if len(raw) == target["size"]:
            return raw, "data-volume"
    errors = []
    for host in ("https://open.canada.ca", "https://ouvert.canada.ca"):
        url = (f"{host}/data/dataset/{target['dataset']}/resource/{target['resource']}/download/"
               f"{target['path']}")
        try:
            raw = _fetch(url)
        except Exception as exc:  # noqa: BLE001
            errors.append(str(exc))
            continue
        try:
            if local:
                with open(local, "wb") as fh:
                    fh.write(raw)
        except OSError:
            pass
        return raw, url
    raise RuntimeError("no copy: " + "; ".join(errors))


def decode(raw):
    for enc in ("utf-8-sig", "cp1252"):
        try:
            return raw.decode(enc), enc
        except UnicodeDecodeError:
            continue
    return raw.decode("latin-1"), "latin-1"


def run_target(target, data_dir):
    res = {"study": f"{target['name']}-census", "version": VERSION,
           "dataset": target["dataset"], "resource": target["resource"],
           "portal_size": target["size"], "portal_md5": target["md5"]}
    try:
        raw, src = load(target, data_dir)
    except Exception as exc:  # noqa: BLE001 - recorded, the other files still run
        res["error"] = f"{type(exc).__name__}: {exc}"
        return res
    text, enc = decode(raw)
    res.update({"source": src, "bytes": len(raw), "size_matches_portal": len(raw) == target["size"],
                "encoding": enc, "sha256": hashlib.sha256(raw).hexdigest(),
                "md5": hashlib.md5(raw).hexdigest()})
    res["md5_matches_portal"] = res["md5"] == target["md5"]
    res["census"] = census(text)
    return res


def main(argv=None):
    ap = argparse.ArgumentParser(description="Names-only census of three CFIA survey files.")
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="out")
    args = ap.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)
    ok = 0
    for target in TARGETS:
        res = run_target(target, args.data_dir)
        if "error" not in res and "error" not in res["census"]:
            ok += 1
        with open(os.path.join(args.out_dir, f"{target['name']}_census.json"), "w",
                  encoding="utf-8") as fh:
            json.dump(res, fh, indent=2, sort_keys=True, ensure_ascii=False)
        print(json.dumps(res, indent=2, sort_keys=True, ensure_ascii=False))
    print(f"CENSUS-DONE {ok}/{len(TARGETS)}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
