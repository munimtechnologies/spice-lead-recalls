#!/usr/bin/env python3
"""turmeric_xrf.py - read Supplementary Table 8 of Forsyth et al. 2026 (npj Sci Food
10:220, CC BY; 503 turmeric samples from eastern India, lead by handheld XRF) and ask
two questions of it:

1. Lead chromate fingerprint: is the molar Pb:Cr ratio near 1 where both are reported?
2. Raman reach: how many samples hold enough lead chromate for a powder Raman screen
   at 0.5%, 0.1%, 0.05%, 0.025% or 0.005% w/w PbCrO4?

New in 0.2.0: Table S8 is plain text in the supplement, not a ruled table, so
pdfplumber finds no table in it (0.1.0 parsed 0 rows). parse_s8_text() reads the
text lines instead. Table S8 has no chromium column (sampid_, city_final,
all_pb_avg, type_groupfull4, sellstate_bin, turm_major), so question 1 cannot be
asked of it; the results are lead and Raman reach only. --supp-text reads a saved
text dump (data/forsyth2026_supp_text.txt) without pdfplumber or a download.

type_groupfull4: the table legend reads "loose powder=1, packaged powder=2,
double-polished roots=4, single-polished roots=5", but the data hold the codes
1-4. The product code at the end of each sample ID (the field guide's list: 1 loose
powder, 2-3 packaged powder, 4/6/8 polished finger/bulb/mix, 5/7/9 unpolished)
maps one-to-one onto 1, 2, 3 and 4, so 3 is read as polished root and 4 as
unpolished (the legend's single-polished) root.

The table layout is not known in advance, so every page's text and every table
pdfplumber finds are written to --out-dir as well, and parse_report.json says what
was and was not found.

Made by MV2 of Munim, Inc. with AI agents working in his name. Apache-2.0.
"""
import argparse
import csv
import hashlib
import json
import os
import re
import statistics
import sys
import urllib.request

__version__ = "0.2.0"

URLS = [
    "https://static-content.springer.com/esm/art%3A10.1038%2Fs41538-026-00867-8/"
    "MediaObjects/41538_2026_867_MOESM1_ESM.pdf",
    "https://pmc.ncbi.nlm.nih.gov/articles/instance/13357593/bin/41538_2026_867_MOESM1_ESM.pdf",
]
USER_AGENT = "spice-lead-recalls turmeric_xrf (MV2 of Munim, Inc.; mv2@munimtech.com)"
PB, CR, O = 207.2, 51.996, 15.999
PBCRO4 = PB + CR + 4 * O
RAMAN_PCT = [0.5, 0.1, 0.05, 0.025, 0.005]
NYC_BAND = (0.81, 1.78)
WIDE_BAND = (0.5, 2.0)
NONDETECT = re.compile(r"^\s*(<|nd\b|n\.d\.|bdl|lod|<lod|below|not detected|-+$|—$)", re.I)
NUMBER = re.compile(r"-?\d[\d,]*\.?\d*(?:[eE][-+]?\d+)?")

# One Table S8 row as pdfplumber writes it: sample ID, city, lead (ug/g),
# type_groupfull4, sellstate_bin, then turm_major (blank in some rows).
S8_ROW = re.compile(r"^(\d+_[A-Z]{2}[_-]\S+) ([A-Za-z]+) (\d+(?:\.\d+)?) ([1-4]) ([01])(?: ([01]))?$")
S8_TYPES = {"1": "loose powder", "2": "packaged powder", "3": "polished root", "4": "unpolished root"}
S8_GROUPS = [
    ("all", ("loose powder", "packaged powder", "polished root", "unpolished root")),
    ("powder", ("loose powder", "packaged powder")),
    ("root", ("polished root", "unpolished root")),
    ("loose powder", ("loose powder",)),
    ("packaged powder", ("packaged powder",)),
    ("polished root", ("polished root",)),
    ("unpolished root", ("unpolished root",)),
]


def pct_to_pb_ppm(pct):
    """Lead (ug/g) carried by pct % w/w lead chromate."""
    return pct / 100.0 * 1e6 * PB / PBCRO4


def molar_pb_cr(pb, cr):
    if pb is None or cr is None or cr <= 0:
        return None
    return (pb / PB) / (cr / CR)


def parse_value(cell):
    """Return (value, nondetect). value is a float or None."""
    if cell is None:
        return None, False
    text = str(cell).strip()
    if not text:
        return None, False
    if NONDETECT.match(text):
        return None, True
    m = NUMBER.search(text)
    if not m:
        return None, False
    try:
        return float(m.group(0).replace(",", "")), False
    except ValueError:
        return None, False


def find_columns(header):
    """Map a header row to column indexes for lead, chromium, type, state."""
    cols = {}
    for i, cell in enumerate(header):
        h = re.sub(r"\s+", " ", str(cell or "")).strip().lower()
        if not h:
            continue
        if "pb" not in cols and (re.search(r"\bpb\b", h) or "lead" in h):
            cols["pb"] = i
        elif "cr" not in cols and (re.search(r"\bcr\b", h) or "chrom" in h):
            cols["cr"] = i
        elif "type" not in cols and re.search(r"type|form|powder|root|product", h):
            cols["type"] = i
        elif "state" not in cols and re.search(r"state|source|origin", h):
            cols["state"] = i
        elif "city" not in cols and re.search(r"city|market|location", h):
            cols["city"] = i
    return cols if "pb" in cols else None


def rows_from_tables(tables):
    """tables: list of (page_no, rows). Header found once, reused on later pages."""
    out, cols, header = [], None, None
    for page_no, rows in tables:
        for row in rows:
            maybe = find_columns(row)
            if maybe and ("cr" in maybe or cols is None):
                cols, header = maybe, row
                continue
            if cols is None:
                continue
            pb, pb_nd = parse_value(row[cols["pb"]] if cols["pb"] < len(row) else None)
            if pb is None and not pb_nd:
                continue
            rec = {"page": page_no, "pb": pb, "pb_nd": pb_nd, "cr": None, "cr_nd": False}
            if "cr" in cols and cols["cr"] < len(row):
                rec["cr"], rec["cr_nd"] = parse_value(row[cols["cr"]])
            for key in ("type", "state", "city"):
                if key in cols and cols[key] < len(row):
                    rec[key] = re.sub(r"\s+", " ", str(row[cols[key]] or "")).strip()
            out.append(rec)
    return out, cols, header


def parse_s8_text(text):
    """Rows of Table S8 from the supplement's text. Page markers written by this
    script ('=== page N ===') give each row its page; other lines are skipped."""
    out, page = [], None
    for line in text.splitlines():
        line = line.strip()
        m = re.match(r"^=== page (\d+) ===$", line)
        if m:
            page = int(m.group(1))
            continue
        m = S8_ROW.match(line)
        if not m:
            continue
        sid, city, pb, typ, sell, major = m.groups()
        out.append({"page": page, "id": sid, "city": city, "pb": float(pb), "pb_nd": False,
                    "cr": None, "cr_nd": False, "type_code": int(typ), "type": S8_TYPES[typ],
                    "state": "Bihar" if sell == "1" else "other",
                    "turm_major": "" if major is None else major})
    return out


def reach_by_group(rows):
    """Raman reach per product group: of the samples with Pb >= 10 ug/g (the
    paper's cut), how many carry at least each screen's lead equivalent."""
    out = []
    for name, types in S8_GROUPS:
        sub = [r for r in rows if r.get("type") in types]
        hot = [r["pb"] for r in sub if r["pb"] is not None and r["pb"] >= 10]
        row = {"group": name, "n": len(sub), "pb_ge_10": len(hot),
               "pb_ge_100": sum(1 for x in hot if x >= 100),
               "pb_ge_1000": sum(1 for x in hot if x >= 1000),
               "median_pb_of_pb_ge_10": statistics.median(hot) if hot else None}
        for pct in RAMAN_PCT:
            k = sum(1 for x in hot if x >= pct_to_pb_ppm(pct))
            row["caught_%g" % pct] = {"k": k, "pct": round(100.0 * k / len(hot), 1) if hot else None}
        out.append(row)
    return out


def quantiles(values):
    if not values:
        return None
    v = sorted(values)
    if len(v) == 1:
        return {"n": 1, "min": v[0], "q1": v[0], "median": v[0], "q3": v[0], "max": v[-1]}
    q = statistics.quantiles(v, n=4, method="inclusive")
    return {"n": len(v), "min": v[0], "q1": q[0], "median": q[1], "q3": q[2], "max": v[-1]}


def share(values, lo, hi):
    if not values:
        return None
    k = sum(1 for x in values if lo <= x <= hi)
    return {"k": k, "n": len(values), "pct": round(100.0 * k / len(values), 1)}


def analyse(rows):
    res = {"n_rows": len(rows),
           "n_pb_numeric": sum(1 for r in rows if r["pb"] is not None),
           "n_pb_nondetect": sum(1 for r in rows if r["pb_nd"]),
           "n_cr_numeric": sum(1 for r in rows if r["cr"] is not None),
           "n_cr_nondetect": sum(1 for r in rows if r["cr_nd"])}
    for cut in (10, 18, 100):
        sub = [r for r in rows if r["pb"] is not None and r["pb"] >= cut]
        ratios = [molar_pb_cr(r["pb"], r["cr"]) for r in sub]
        ratios = [x for x in ratios if x is not None]
        res["pb_ge_%d" % cut] = {
            "n": len(sub),
            "cr_numeric": sum(1 for r in sub if r["cr"] is not None),
            "cr_nondetect": sum(1 for r in sub if r["cr_nd"]),
            "molar_pb_cr": quantiles(ratios),
            "in_nyc_band_0.81_1.78": share(ratios, *NYC_BAND),
            "in_0.5_2.0": share(ratios, *WIDE_BAND),
        }
    raman = []
    for pct in RAMAN_PCT:
        need = pct_to_pb_ppm(pct)
        row = {"pct_w_w": pct, "pb_ppm_needed": round(need, 1)}
        for cut in (10, 100):
            sub = [r["pb"] for r in rows if r["pb"] is not None and r["pb"] >= cut]
            k = sum(1 for x in sub if x >= need)
            row["caught_of_pb_ge_%d" % cut] = {"k": k, "n": len(sub),
                                               "pct": round(100.0 * k / len(sub), 1) if sub else None}
        raman.append(row)
    res["raman_reach"] = raman
    by_type = {}
    for r in rows:
        t = (r.get("type") or "").lower()
        if t:
            key = "root" if "root" in t else "powder" if "powder" in t else t[:30]
            by_type.setdefault(key, []).append(r)
    res["by_type"] = {}
    for k, v in sorted(by_type.items()):
        hi = [molar_pb_cr(r["pb"], r["cr"]) for r in v if r["pb"] is not None and r["pb"] >= 300]
        res["by_type"][k] = {
            "n": len(v),
            "pb_ge_10": sum(1 for r in v if r["pb"] is not None and r["pb"] >= 10),
            "pb_ge_3205": sum(1 for r in v if r["pb"] is not None
                              and r["pb"] >= pct_to_pb_ppm(0.5)),
            "molar_pb_cr_pb_ge_300": quantiles([x for x in hi if x is not None]),
        }
    mid = [r for r in rows if r["pb"] is not None and 10 <= r["pb"] <= 200]
    res["pb_10_200_cr_missing"] = share([0 if r["cr"] is not None else 1 for r in mid], 1, 1)
    if rows and all("type_code" in r for r in rows):
        res["reach_by_group"] = reach_by_group(rows)
    return res


def fetch(data_dir):
    os.makedirs(data_dir, exist_ok=True)
    path = os.path.join(data_dir, "41538_2026_867_MOESM1_ESM.pdf")
    if os.path.exists(path) and os.path.getsize(path) > 100000:
        return path, "cached"
    last = None
    for url in URLS:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=120) as resp:
                blob = resp.read()
            if blob[:4] != b"%PDF":
                last = "not a PDF from " + url
                continue
            with open(path, "wb") as fh:
                fh.write(blob)
            return path, url
        except Exception as exc:  # try the next mirror
            last = "%s: %s" % (url, exc)
    raise SystemExit("could not fetch the supplement: %s" % last)


def write_md(path, report, res):
    lines = ["# Forsyth et al. 2026, Supplementary Table 8: Pb:Cr and Raman reach",
             "", "turmeric_xrf.py %s. Source: Forsyth JE et al., npj Sci Food 10:220 (2026), "
             "doi:10.1038/s41538-026-00867-8, CC BY 4.0. Lead by handheld XRF." % __version__,
             "", "Parse: %s" % json.dumps(report), ""]
    if res.get("reach_by_group"):
        lines += ["Table S8 has no chromium column, so no Pb:Cr ratio can be read from it.", "",
                  "Of the samples with Pb >= 10 ug/g, how many a screen at each limit (% w/w PbCrO4) catches:", "",
                  "| group | samples | Pb >= 10 | Pb >= 1,000 | median Pb (of >= 10) | "
                  + " | ".join("%g%%" % p for p in RAMAN_PCT) + " |",
                  "|---|---|---|---|---|" + "---|" * len(RAMAN_PCT)]
        for g in res["reach_by_group"]:
            cells = ["%d (%s%%)" % (g["caught_%g" % p]["k"], g["caught_%g" % p]["pct"]) for p in RAMAN_PCT]
            lines.append("| %s | %d | %d | %d | %s | %s |" % (
                g["group"], g["n"], g["pb_ge_10"], g["pb_ge_1000"],
                "%g" % g["median_pb_of_pb_ge_10"] if g["median_pb_of_pb_ge_10"] is not None else "-",
                " | ".join(cells)))
        lines.append("")
    lines += ["```", json.dumps(res, indent=1), "```", ""]
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="/out")
    ap.add_argument("--supp-text", default="",
                    help="read a saved text dump of the supplement instead of the PDF")
    args = ap.parse_args(argv)
    os.makedirs(os.path.join(args.out_dir, "tables"), exist_ok=True)
    tables, texts = [], []
    if args.supp_text:
        with open(args.supp_text, "rb") as fh:
            blob = fh.read()
        report = {"source": args.supp_text, "sha256": hashlib.sha256(blob).hexdigest(),
                  "pages": None, "table8_page": None, "tables": 0}
        full_text = blob.decode("utf-8")
    else:
        import pdfplumber

        pdf_path, source = fetch(args.data_dir)
        with open(pdf_path, "rb") as fh:
            sha = hashlib.sha256(fh.read()).hexdigest()
        report = {"source": source, "sha256": sha, "pages": 0, "table8_page": None, "tables": 0}
        with pdfplumber.open(pdf_path) as pdf:
            report["pages"] = len(pdf.pages)
            for i, page in enumerate(pdf.pages, 1):
                text = page.extract_text() or ""
                texts.append("=== page %d ===\n%s" % (i, text))
                if report["table8_page"] is None and re.search(
                        r"Supplementary\s+Table\s+8|Table\s+S8\b", text, re.I):
                    report["table8_page"] = i
                for j, tbl in enumerate(page.extract_tables() or [], 1):
                    tables.append((i, tbl))
                    with open(os.path.join(args.out_dir, "tables", "p%02d_t%d.csv" % (i, j)),
                              "w", newline="", encoding="utf-8") as fh:
                        csv.writer(fh).writerows(tbl)
        report["tables"] = len(tables)
        full_text = "\n".join(texts)
        with open(os.path.join(args.out_dir, "supp_text.txt"), "w", encoding="utf-8") as fh:
            fh.write(full_text)
    start = report["table8_page"] or 1
    rows, cols, header = rows_from_tables([t for t in tables if t[0] >= start])
    report["parser"] = "tables"
    if not rows:
        rows, cols, header = parse_s8_text(full_text), None, None
        report["parser"] = "s8-text"
    report["columns"] = cols
    report["header"] = header
    report["rows_parsed"] = len(rows)
    with open(os.path.join(args.out_dir, "table8_rows.csv"), "w", newline="",
              encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["page", "id", "type", "state", "city", "pb", "pb_nd",
                                           "cr", "cr_nd", "molar_pb_cr"], extrasaction="ignore")
        w.writeheader()
        for r in rows:
            r = dict(r, molar_pb_cr=molar_pb_cr(r["pb"], r["cr"]))
            w.writerow(r)
    res = analyse(rows) if rows else {}
    with open(os.path.join(args.out_dir, "parse_report.json"), "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=1)
    with open(os.path.join(args.out_dir, "forsyth_pbcr.json"), "w", encoding="utf-8") as fh:
        json.dump({"version": __version__, "parse": report, "results": res}, fh, indent=1)
    write_md(os.path.join(args.out_dir, "forsyth_pbcr.md"), report, res)
    print(json.dumps({"parse": report, "results": res}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
