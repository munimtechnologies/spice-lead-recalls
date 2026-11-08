#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""dried-tea-census 0.1.0: a names-only census of CFIA's open 2009-10 "Pesticide Residues and
Metals in Dried Teas" file (open.canada.ca dataset 2782dbc5-ebbb-4ef1-a85f-294a5fe60f47), run
before any result value is read, for docs/dried-tea-2009-0.1.0-prereg.md and its 0.1.1 addendum.

It counts rows, sample numbers (raw and with one trailing "A" removed), labels per sample,
component names, method codes and units, and classifies every result cell only by its SHAPE
(number, "<" number, negative number, text token, blank). It never prints, sums or compares a
result value. Any column whose cells are mostly numbers is reported by shape only. It also
recounts the "Pesticide Screen Components" table of the package's English Information PDF
(addendum item A1). Standard library only, plus pdfminer.six for the PDF part.
Made with AI agents working in MV2's (Munim, Inc.) name. Code Apache-2.0; derived data CC BY 4.0.
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
DATASET = "2782dbc5-ebbb-4ef1-a85f-294a5fe60f47"
BASE = f"https://open.canada.ca/data/dataset/{DATASET}/resource/"
CSV_TARGET = {
    "resource": "6fbadab4-f46f-4ab3-a1a6-e3d857253beb",
    "path": ("fsap-chem-ts-pesticide-residues-and-metals-in-dried-teas-2009-2010_"
             "paaspa-chem-ec-residus-de-pes.csv"),
    "portal_kib": 276,
    "portal_md5": "f21f016693b4608ff7059d28be35bb26",
}
PDF_EN = BASE + ("628e68b6-9d35-4a0c-8514-cd5016623ff7/download/"
                 "pesticides-and-metals-in-dried-teas-information.pdf")
METHODS = ("PESTICIDES-FPH053", "PESTICIDES-LC")
# Element names (English and French) used to recognise metal components.
METALS = {
    "aluminum": "Al", "aluminium": "Al", "antimony": "Sb", "antimoine": "Sb", "arsenic": "As",
    "barium": "Ba", "beryllium": "Be", "béryllium": "Be", "bismuth": "Bi", "boron": "B",
    "bore": "B", "cadmium": "Cd", "calcium": "Ca", "chromium": "Cr", "chrome": "Cr",
    "cobalt": "Co", "copper": "Cu", "cuivre": "Cu", "iron": "Fe", "fer": "Fe", "lead": "Pb",
    "plomb": "Pb", "lithium": "Li", "magnesium": "Mg", "magnésium": "Mg", "manganese": "Mn",
    "manganèse": "Mn", "mercury": "Hg", "mercure": "Hg", "molybdenum": "Mo", "molybdène": "Mo",
    "nickel": "Ni", "selenium": "Se", "sélénium": "Se", "silver": "Ag", "argent": "Ag",
    "strontium": "Sr", "thallium": "Tl", "tin": "Sn", "étain": "Sn", "titanium": "Ti",
    "titane": "Ti", "uranium": "U", "vanadium": "V", "zinc": "Zn",
}
SYMBOLS = set(METALS.values())
MAX_LABELS = 60
MAX_EXAMPLES = 10


def clean(cell):
    """A cell without BOM, edge spaces or repeated inner spaces."""
    return " ".join((cell or "").replace("﻿", "").split())


def norm_name(name):
    """Component name for matching: lower case, one space, straight quotes."""
    s = clean(name).replace("’", "'").replace("‘", "'").replace("`", "'")
    return s.lower()


def head(name):
    """Normalised English part of a header cell: 'Sample_Number / Numero' -> 'sample number'."""
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
        "component": pick(lambda c: c.startswith(("component", "analyte", "compound",
                                                  "parameter"))),
        "test": pick(lambda c: c.startswith(("type of test", "test type"))),
        "value": pick(lambda c: c.startswith(("maxofamount", "amount", "result", "value",
                                              "level", "concentration"))),
        "unit": pick(lambda c: c.startswith(("report unit", "unit"))),
    }


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


def metal_symbol(component):
    """Element symbol if the component names a metal ('Mercury (Hg)', 'Lead', 'Pb'), else None."""
    s = norm_name(component)
    if not s:
        return None
    s = re.sub(r"[\(\)\[\],;:]", " ", s)
    words = s.split()
    if words and words[0] in METALS:
        return METALS[words[0]]
    for w in words:
        if w.capitalize() in SYMBOLS and len(words) <= 3:
            return w.capitalize()
    return None


def base_id(sid):
    """Sample number with one trailing 'A' removed (addendum A4)."""
    return sid[:-1] if sid.endswith("A") and len(sid) > 1 else sid


def _bump(d, k, n=1):
    d[k] = d.get(k, 0) + n


def _cell(r, i):
    return r[i] if i is not None and i < len(r) else ""


def column_profile(header, rows, roles):
    """Per column: shapes only if it is the value column or mostly numbers; otherwise label counts."""
    prof = []
    skip_labels = {roles.get("sample")}
    for i, name in enumerate(header):
        cells = [clean(_cell(r, i)) for r in rows]
        nonblank = [c for c in cells if c]
        numeric = sum(1 for c in nonblank if shape(c) in ("number", "negative-number",
                                                           "lt-number"))
        p = {"index": i, "header": clean(name), "nonblank": len(nonblank)}
        if i == roles.get("value") or (nonblank and numeric * 2 >= len(nonblank)):
            sh = {}
            for c in cells:
                _bump(sh, shape(c))
            p["kind"] = "values (shapes only)"
            p["shapes"] = sh
        else:
            counts = {}
            for c in cells:
                _bump(counts, c)
            p["kind"] = "labels"
            p["distinct"] = len(counts)
            if i in skip_labels or len(counts) > MAX_LABELS:
                p["examples"] = sorted(counts)[:MAX_EXAMPLES]
            else:
                p["counts"] = counts
        prof.append(p)
    return prof


def census(text, pdf_names=None):
    """Names-only census of the CSV text. pdf_names: set of normalised PDF component names."""
    reader = csv.reader(io.StringIO(text))
    header = next(reader, [])
    rows = [r for r in reader if any(c.strip() for c in r)]
    col = find_columns(header)
    out = {"header": [clean(c) for c in header], "columns": col, "rows": len(rows),
           "layout": "long" if col["component"] is not None else "wide or unknown",
           "profile": column_profile(header, rows, col)}
    if col["sample"] is None or col["component"] is None:
        out["error"] = "no sample or component column; see profile"
        return out
    label_cols = [i for i in range(len(header))
                  if i not in {v for v in col.values() if v is not None}]
    label_cols = [p["index"] for p in out["profile"]
                  if p["index"] in label_cols and p["kind"] == "labels" and "counts" in p]
    comps, comp_test, units_by_group, shapes_by_group, tokens = {}, {}, {}, {}, {}
    metal_rows_by_base, groups_by_base, labels_by_base = {}, {}, {}
    suffix = {"metal": {"ends_A": 0, "no_A": 0}, "pesticide": {"ends_A": 0, "no_A": 0}}
    raw_ids, metals, pest_tests, pest_shapes_bad = set(), {}, {}, 0
    pest_names = {}
    for r in rows:
        sid = clean(_cell(r, col["sample"]))
        comp = clean(_cell(r, col["component"]))
        test = clean(_cell(r, col["test"]))
        unit = clean(_cell(r, col["unit"]))
        sh = shape(_cell(r, col["value"])) if col["value"] is not None else "no value column"
        sym = metal_symbol(comp)
        group = "metal" if sym else "pesticide"
        raw_ids.add(sid)
        b = base_id(sid)
        _bump(comps, comp)
        _bump(comp_test, f"{comp} | {test}")
        _bump(units_by_group.setdefault(group, {}), unit)
        _bump(shapes_by_group.setdefault(group, {}), sh)
        if sh == "token":
            _bump(tokens, f"{group}: {clean(_cell(r, col['value']))}")
        _bump(suffix[group], "ends_A" if sid.endswith("A") else "no_A")
        groups_by_base.setdefault(b, set()).add(group)
        labels_by_base.setdefault(b, set()).add(tuple(clean(_cell(r, i)) for i in label_cols))
        if sym:
            _bump(metals.setdefault(sym, {}), comp)
            _bump(metal_rows_by_base, b)
        else:
            _bump(pest_tests, test)
            _bump(pest_names, comp)
            if sh != "number":
                pest_shapes_bad += 1
    metal_dist = {}
    for b, groups in groups_by_base.items():
        if "metal" in groups:
            _bump(metal_dist, str(metal_rows_by_base.get(b, 0)))
    first_labels = {}
    mixed = []
    for b, labs in sorted(labels_by_base.items()):
        if len(labs) > 1:
            mixed.append(b)
        _bump(first_labels, " | ".join(sorted(labs)[0]))
    not_in_pdf = None
    if pdf_names is not None:
        not_in_pdf = sorted(n for n in pest_names if norm_name(n) not in pdf_names)
    out.update({
        "raw_sample_numbers": len(raw_ids),
        "base_samples": len(groups_by_base),
        "base_samples_by_groups": _count(" + ".join(sorted(g)) for g in groups_by_base.values()),
        "sample_number_suffix": suffix,
        "components": comps,
        "component_test": comp_test,
        "metals": {k: metals[k] for k in sorted(metals)},
        "metal_count": len(metals),
        "mercury_named": "Hg" in metals,
        "beryllium_named": "Be" in metals,
        "metal_rows": sum(metal_rows_by_base.values()),
        "metal_rows_per_sample": metal_dist,
        "pesticide_rows": sum(pest_names.values()),
        "pesticide_names": len(pest_names),
        "pesticide_tests": pest_tests,
        "pesticide_rows_not_number_shape": pest_shapes_bad,
        "pesticide_names_not_in_pdf": not_in_pdf,
        "units_by_group": units_by_group,
        "shapes_by_group": shapes_by_group,
        "tokens": tokens,
        "label_columns": [clean(header[i]) for i in label_cols],
        "labels_per_sample": first_labels,
        "mixed_label_samples": mixed[:MAX_EXAMPLES],
        "mixed_label_sample_count": len(mixed),
    })
    return out


def _count(items):
    d = {}
    for it in items:
        _bump(d, it)
    return d


def pdf_table(text):
    """Recount the 'Pesticide Screen Components' table (addendum A1) from the English PDF text."""
    lines = [ln.rstrip() for ln in text.splitlines()]
    stated = {}
    for m in METHODS:
        hit = re.search(re.escape(m) + r" is an? [A-Z]+-MS-based multi-residue method with (\d+)"
                        r" analytes", text)
        stated[m] = int(hit.group(1)) if hit else None
    methods, names = [], []
    i = 0
    while i < len(lines):
        s = lines[i].strip()
        if s in METHODS:
            methods.append(s)
        elif s == "Component":
            i += 1
            while i < len(lines) and lines[i].strip():
                names.append(clean(lines[i]))
                i += 1
            continue
        i += 1
    res = {"stated": stated, "method_rows": _count(methods), "component_rows": len(names),
           "paired": len(methods) == len(names)}
    if res["paired"]:
        per = {m: [norm_name(n) for t, n in zip(methods, names) if t == m] for m in METHODS}
        res["distinct"] = {m: len(set(v)) for m, v in per.items()}
        res["repeated"] = {m: sorted({n for n in v if v.count(n) > 1}) for m, v in per.items()}
        shared = set(per[METHODS[0]]) & set(per[METHODS[1]])
        res["shared"] = sorted(shared)
        res["distinct_all"] = len(set(per[METHODS[0]]) | set(per[METHODS[1]]))
        res["names"] = sorted(set(per[METHODS[0]]) | set(per[METHODS[1]]))
    return res


def _fetch(url, tries=3, pause=10):
    last = None
    for _ in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "mv2-dried-tea-census"})
            with urllib.request.urlopen(req, timeout=300) as resp:
                return resp.read()
        except Exception as exc:  # noqa: BLE001 - retry
            last = exc
            time.sleep(pause)
    raise RuntimeError(f"{url}: {last}")


def decode(raw):
    for enc in ("utf-8-sig", "cp1252"):
        try:
            return raw.decode(enc), enc
        except UnicodeDecodeError:
            continue
    return raw.decode("latin-1"), "latin-1"


def gate(nbytes, kib=CSV_TARGET["portal_kib"]):
    """Gate G1 of 0.1.0: size in the portal's KiB band, read as bytes / 1,024 rounded up."""
    return (kib - 1) * 1024 < nbytes <= kib * 1024


def pdf_part(out_dir):
    try:
        from pdfminer.high_level import extract_text
    except ImportError as exc:
        return {"error": f"pdfminer.six missing: {exc}"}
    raw = _fetch(PDF_EN)
    path = os.path.join(out_dir, "dried_tea_info_en.pdf")
    with open(path, "wb") as fh:
        fh.write(raw)
    res = pdf_table(extract_text(path))
    res["md5"] = hashlib.md5(raw).hexdigest()
    res["bytes"] = len(raw)
    return res


def main(argv=None):
    ap = argparse.ArgumentParser(description="Names-only census of CFIA's 2009-10 dried-tea file.")
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="out")
    args = ap.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)
    res = {"study": "dried-tea-2009-census", "version": VERSION, "dataset": DATASET,
           "resource": CSV_TARGET["resource"], "portal_kib": CSV_TARGET["portal_kib"],
           "portal_md5": CSV_TARGET["portal_md5"]}
    try:
        res["pdf"] = pdf_part(args.out_dir)
    except Exception as exc:  # noqa: BLE001 - recorded; the CSV census still runs
        res["pdf"] = {"error": f"{type(exc).__name__}: {exc}"}
    pdf_names = set(res["pdf"].get("names", [])) or None
    url = BASE + CSV_TARGET["resource"] + "/download/" + CSV_TARGET["path"]
    try:
        raw = _fetch(url)
    except Exception as exc:  # noqa: BLE001
        res["error"] = f"{type(exc).__name__}: {exc}"
        raw = None
    if raw is not None:
        local = os.path.join(args.data_dir, CSV_TARGET["resource"] + ".csv")
        try:
            with open(local, "wb") as fh:
                fh.write(raw)
        except OSError:
            pass
        text, enc = decode(raw)
        res.update({"bytes": len(raw), "kib_rounded_up": -(-len(raw) // 1024),
                    "gate_size_band": gate(len(raw)), "encoding": enc,
                    "sha256": hashlib.sha256(raw).hexdigest(), "md5": hashlib.md5(raw).hexdigest()})
        res["md5_matches_portal"] = res["md5"] == CSV_TARGET["portal_md5"]
        res["census"] = census(text, pdf_names)
    with open(os.path.join(args.out_dir, "dried_tea_census.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=2, sort_keys=True, ensure_ascii=False)
    print(json.dumps(res, indent=2, sort_keys=True, ensure_ascii=False))
    ok = raw is not None and res.get("gate_size_band") and "error" not in res.get("census", {})
    print("CENSUS-DONE", "ok" if ok else "incomplete")
    return 0 if raw is not None else 1


if __name__ == "__main__":
    sys.exit(main())
