#!/usr/bin/env python3
"""cr_baseline: can a spice's own chromium explain a chromate-like Pb:Cr pair?

nyc_spice_lead.py calls a lead/chromium pair "chromate-like" when its molar
Pb:Cr ratio lies in 0.7-2 (PbCrO4 = 1). That test treats all the chromium as
coming with the lead. Plants carry some chromium of their own. Taking a
natural background b off the measured chromium raises the ratio, and the pair
leaves the band once b passes

    edge = Cr - (Pb / 207.2) / 2 * 51.996      (ppm)

This script reads the pairs CSV written by nyc_spice_lead.py and a table of
published natural-chromium ceilings by spice and method
(data/natural_cr_ceilings.csv), and gives each chromate-like pair a
baseline verdict from total chromium alone:

- robust: the edge is above every published ceiling for that spice, so no
  known natural level explains the chromium;
- unresolved: above some ceilings and at or below others (for coriander the
  split follows the analytical method);
- background-limited: at or below every ceiling.

Spices with no ceiling of their own (blends, seasonings) use the "generic"
row. A matrix-specific ceiling always replaces the generic one.

New in 0.2.0: an optional Cr(VI) speciation gate. Natural plant chromium is
Cr(III); the lead-chromate pigment (PbCrO4) is Cr(VI). A total-chromium ratio
cannot tell them apart, but a diphenylcarbazide (DPC) or laboratory speciation
test can. The pairs CSV may carry a per-pair column `cr6_result` with
"positive", "negative" or empty:

- positive -> final_verdict = "cr6-confirmed" (Cr(VI) present on the product),
  whatever the baseline verdict;
- negative -> final_verdict = baseline verdict. A negative DPC is NOT
  exculpatory: Lopez et al. 2022 report a 167 mg/kg-Pb coriander powder that
  developed no colour, so absence of colour is not absence of chromate;
- empty / column absent -> final_verdict = baseline verdict (the 0.1.0 case).

"cr6-confirmed" means hexavalent chromium was confirmed on the product, not
"lead chromate proven". No NYC pair carries a Cr(VI) result, so 0.2.0 changes
no NYC verdict; its value is a correct call on the Lopez worked example and a
tested slot for future speciation data. See docs/cr-baseline-0.2.0-prereg.md.

Outputs: cr_baseline.csv, cr_baseline.json, cr_baseline.md.

Made by MV2 of Munim, Inc. with AI agents working in his name. Apache-2.0.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import sys
import urllib.request

__version__ = "0.2.0"

USER_AGENT = "spice-lead-recalls cr_baseline (MV2 of Munim, Inc.; mv2@munimtech.com)"
HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CEILINGS = os.path.join(HERE, "data", "natural_cr_ceilings.csv")

PB = 207.2
CR = 51.996
# Same band as nyc_spice_lead.py.
CHROMATE_BAND = (0.7, 2.0)
GENERIC = "generic"

# Allowed values of the optional per-pair cr6_result column. Empty means no
# speciation test was run (reported as "untested").
CR6_ALLOWED = ("positive", "negative", "")

# Spice names as NYC staff wrote them. The first match wins, so black pepper
# comes before the chili words.
MATRICES = [
    ("black pepper", ["black pepper", "piper nigrum"]),
    ("coriander", ["coriander", "corriander", "cilantro", "dhania", "dhaniya"]),
    ("cumin", ["cumin", "jeera"]),
    ("turmeric", ["turmeric", "tumeric", "turmeic", "haldi", "holud", "halud"]),
    ("cinnamon", ["cinnamon", "cinammon", "canela"]),
    ("chili/paprika", ["chili", "chilli", "chile", "paprika", "cayenne", "red pepper"]),
    ("curry", ["curry"]),
]

OUT_FIELDS = ["lead_row_id", "chromium_row_id", "collection_date", "investigation_type", "product_name",
              "purchase_country", "lead_ppm", "chromium_ppm", "molar_ratio_pb_cr", "matrix", "ceilings_used",
              "edge_ppm", "highest_ceiling_ppm", "lowest_ceiling_ppm", "baseline_verdict", "speciation",
              "final_verdict", "ceilings_at_or_above_edge"]


def matrix_of(name):
    n = " ".join((name or "").lower().split())
    for matrix, words in MATRICES:
        if any(w in n for w in words):
            return matrix
    return GENERIC


def edge_ppm(pb_ppm, cr_ppm, hi=CHROMATE_BAND[1]):
    """Largest natural chromium (ppm) that can come off cr_ppm before the
    molar Pb:Cr ratio rises above hi."""
    return cr_ppm - (pb_ppm / PB) / hi * CR


def read_ceilings(path):
    out = {}
    with open(path, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            out.setdefault(r["matrix"].strip(), []).append({
                "method": r["method"].strip(),
                "ceiling_ppm": float(r["ceiling_ppm"]),
                "n": r["n"].strip(),
                "source": r["source"].strip(),
            })
    return out


def judge(pb_ppm, cr_ppm, ceilings):
    """(edge, baseline verdict, ceilings at or above the edge) for one pair."""
    e = edge_ppm(pb_ppm, cr_ppm)
    above = [c for c in ceilings if c["ceiling_ppm"] >= e]
    if not above:
        v = "robust"
    elif len(above) == len(ceilings):
        v = "background-limited"
    else:
        v = "unresolved"
    return e, v, above


def speciation_of(raw):
    """Normalise the optional cr6_result cell to 'positive', 'negative' or ''."""
    v = (raw or "").strip().lower()
    if v not in CR6_ALLOWED:
        raise ValueError(
            "cr6_result must be 'positive', 'negative' or empty, got %r" % (raw,))
    return v


def final_of(baseline_verdict, speciation):
    """Fold a Cr(VI) speciation result into the baseline verdict.

    A positive Cr(VI) test confirms hexavalent chromium on the product and
    overrides the ceiling-only verdict. A negative test is not exculpatory and
    leaves the baseline verdict unchanged."""
    if speciation == "positive":
        return "cr6-confirmed"
    return baseline_verdict


def _label(c):
    return "%s %g (%s)" % (c["method"], c["ceiling_ppm"], c["source"])


def assess(pairs, ceilings):
    if GENERIC not in ceilings:
        raise ValueError("the ceilings table needs a '%s' row" % GENERIC)
    rows = []
    for p in pairs:
        if p.get("verdict") != "chromate-like":
            continue
        pb, cr = float(p["lead_ppm"]), float(p["chromium_ppm"])
        m = matrix_of(p.get("product_name", ""))
        used = m if m in ceilings else GENERIC
        cs = ceilings[used]
        e, v, above = judge(pb, cr, cs)
        spec = speciation_of(p.get("cr6_result", ""))
        rows.append({
            "lead_row_id": p.get("lead_row_id", ""),
            "chromium_row_id": p.get("chromium_row_id", ""),
            "collection_date": p.get("collection_date", ""),
            "investigation_type": p.get("investigation_type", ""),
            "product_name": p.get("product_name", ""),
            "purchase_country": p.get("purchase_country", ""),
            "lead_ppm": pb,
            "chromium_ppm": cr,
            "molar_ratio_pb_cr": round((pb / PB) / (cr / CR), 3),
            "matrix": m,
            "ceilings_used": used,
            "edge_ppm": round(e, 2),
            "highest_ceiling_ppm": max(c["ceiling_ppm"] for c in cs),
            "lowest_ceiling_ppm": min(c["ceiling_ppm"] for c in cs),
            "baseline_verdict": v,
            "speciation": spec or "untested",
            "final_verdict": final_of(v, spec),
            "ceilings_at_or_above_edge": "; ".join(_label(c) for c in above),
        })
    rows.sort(key=lambda r: r["edge_ppm"])
    return rows


def _count(rows, key):
    counts = {}
    for r in rows:
        counts[r[key]] = counts.get(r[key], 0) + 1
    return counts


def summarize(rows, meta):
    return {
        "version": __version__,
        "pairs_source": meta.get("pairs_source", ""),
        "pairs_sha256": meta.get("pairs_sha256", ""),
        "ceilings_sha256": meta.get("ceilings_sha256", ""),
        "chromate_band": list(CHROMATE_BAND),
        "chromate_like_pairs": len(rows),
        "verdicts": _count(rows, "baseline_verdict"),
        "final_verdicts": _count(rows, "final_verdict"),
        "speciation": _count(rows, "speciation"),
        "not_robust": [r for r in rows if r["baseline_verdict"] != "robust"],
        "cr6_confirmed": [r for r in rows if r["final_verdict"] == "cr6-confirmed"],
        "rows": rows,
    }


def write_markdown(s, path):
    lines = [
        "# Natural chromium vs NYC's chromate-like spice pairs",
        "",
        "cr_baseline %s. Pairs: %s (sha256 %s). Ceilings sha256 %s." % (
            s["version"], s["pairs_source"], s["pairs_sha256"][:12], s["ceilings_sha256"][:12]),
        "",
        "- Chromate-like pairs (molar Pb:Cr %g-%g): %d." % (
            s["chromate_band"][0], s["chromate_band"][1], s["chromate_like_pairs"]),
    ]
    for v in ("robust", "unresolved", "background-limited"):
        lines.append("- baseline %s: %d." % (v, s["verdicts"].get(v, 0)))
    tested = s["chromate_like_pairs"] - s["speciation"].get("untested", 0)
    lines += [
        "",
        "The **baseline verdict** uses total chromium only. The **final verdict** folds in an "
        "optional Cr(VI) speciation test (`cr6_result` per pair): a positive test confirms "
        "hexavalent chromium on the product and overrides the ceiling-only verdict as "
        "`cr6-confirmed`; a negative test is not exculpatory and leaves the baseline verdict "
        "(Lopez et al. 2022 report a 167 mg/kg-Pb coriander that developed no DPC colour). "
        "%d of %d pairs carry a speciation result; the rest are `untested`, so their final "
        "verdict equals their baseline verdict." % (tested, s["chromate_like_pairs"]),
        "",
        "The edge is the most natural chromium the pair can lose before its ratio rises above %g." % (
            s["chromate_band"][1]),
        "",
        "| Pb row | Cr row | collected | product | bought in | Pb ppm | Cr ppm | molar Pb:Cr | ceilings | edge ppm "
        "| highest ceiling | baseline verdict | speciation | final verdict | ceilings at or above the edge |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in s["rows"]:
        lines.append("| %s | %s | %s | %s | %s | %g | %g | %g | %s | %g | %g | %s | %s | %s | %s |" % (
            r["lead_row_id"], r["chromium_row_id"], r["collection_date"], r["product_name"],
            r["purchase_country"], r["lead_ppm"], r["chromium_ppm"], r["molar_ratio_pb_cr"], r["ceilings_used"],
            r["edge_ppm"], r["highest_ceiling_ppm"], r["baseline_verdict"], r["speciation"], r["final_verdict"],
            r["ceilings_at_or_above_edge"] or "-"))
    lines += [
        "",
        "Ceilings are the highest published natural chromium for each spice and method; they are not limits for "
        "any one sample. NYC's chromium results are total chromium, as sold. `cr6-confirmed` means hexavalent "
        "chromium was confirmed present on the product, not that lead chromate is proven.",
        "",
    ]
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


def write_csv(rows, fields, path):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def load_pairs(src, data_dir):
    if src.startswith(("http://", "https://")):
        os.makedirs(data_dir, exist_ok=True)
        path = os.path.join(data_dir, os.path.basename(src.split("?")[0]))
        if not os.path.exists(path):
            req = urllib.request.Request(src, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=120) as resp, open(path + ".part", "wb") as fh:
                fh.write(resp.read())
            os.replace(path + ".part", path)
    else:
        path = src
    with open(path, "rb") as fh:
        blob = fh.read()
    pairs = list(csv.DictReader(io.StringIO(blob.decode("utf-8-sig"), newline="")))
    return pairs, hashlib.sha256(blob).hexdigest()


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--pairs", default="data/nyc_spice_pb_cr_pairs.csv",
                    help="nyc_spice_pb_cr_pairs.csv from nyc_spice_lead.py (a path or a URL)")
    ap.add_argument("--ceilings", default=DEFAULT_CEILINGS)
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="/out")
    args = ap.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)
    pairs, pairs_sha = load_pairs(args.pairs, args.data_dir)
    with open(args.ceilings, "rb") as fh:
        ceilings_sha = hashlib.sha256(fh.read()).hexdigest()
    rows = assess(pairs, read_ceilings(args.ceilings))
    s = summarize(rows, {"pairs_source": args.pairs, "pairs_sha256": pairs_sha, "ceilings_sha256": ceilings_sha})
    write_csv(rows, OUT_FIELDS, os.path.join(args.out_dir, "cr_baseline.csv"))
    with open(os.path.join(args.out_dir, "cr_baseline.json"), "w", encoding="utf-8") as fh:
        json.dump(s, fh, indent=1, ensure_ascii=False)
    write_markdown(s, os.path.join(args.out_dir, "cr_baseline.md"))
    print(json.dumps({"chromate_like_pairs": s["chromate_like_pairs"], "verdicts": s["verdicts"],
                      "final_verdicts": s["final_verdicts"]}))
    for r in s["not_robust"]:
        print("%s: %s %s, Pb %g Cr %g, edge %g ppm, %s" % (
            r["baseline_verdict"], r["collection_date"], r["product_name"], r["lead_ppm"], r["chromium_ppm"],
            r["edge_ppm"], r["ceilings_at_or_above_edge"]))
    for r in s["cr6_confirmed"]:
        print("cr6-confirmed: %s %s, Pb %g Cr %g, baseline %s" % (
            r["collection_date"], r["product_name"], r["lead_ppm"], r["chromium_ppm"], r["baseline_verdict"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
