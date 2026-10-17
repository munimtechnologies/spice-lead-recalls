#!/usr/bin/env python3
"""cfia_spice_auth 0.1.0: lead chromate, dyes and fillers in CFIA's spice authenticity surveillance.

Grades docs/cfia-spice-auth-0.1.0-prereg.md, which was written and committed before
any outcome value (assessment code or note) in the three data files was read. Does
Canada's risk-based spice surveillance, 2020-2023, still find lead chromate, in which
spices and from which declared origins, and how does it compare with dyes and fillers?

The Canadian Food Inspection Agency (CFIA) publishes one CSV per fiscal year on the
Open Government Portal ("Spices Authenticity Summary Data", dataset 2d34ba67-f4a3-
4c54-95f5-6073b59ad880, Open Government Licence - Canada). One row is one sample:
sample number, where it was sampled (province), declared origin or dealer location,
product name, assessment (S = satisfactory, U-I = unsatisfactory, INV = investigative)
and optional notes in English and French.

  unit          one row (sample) with a sample number or product, pooled over the files
  assessment    S; U (any code starting U, or "insatisfaisant"); INV (starting INV);
                other codes are kept as OTHER
  lead          English + French notes match LEAD_RE (lead, chromate, chromium, Pb, plomb)
  dye           notes match DYE_RE and not LEAD_RE
  filler        notes match FILLER_RE (wheat, starch, shells, foreign plant material ...)
  spice         first SPICES pattern matching the English product name
  origins       declared origin split on / , ; & + "and" "or"; single = exactly one

Made by MV2 of Munim, Inc. with AI agents. Apache-2.0.
"""
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
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/126.0 Safari/537.36 cfia_spice_auth/%s (MV2 of Munim, Inc.; mv2@munimtech.com)"
      % VERSION)
DATASET = "https://open.canada.ca/data/en/dataset/2d34ba67-f4a3-4c54-95f5-6073b59ad880"
BASE = "https://open.canada.ca/data/dataset/2d34ba67-f4a3-4c54-95f5-6073b59ad880/resource/"
FILES = (
    ("2020-2021", BASE + "ff9ed34b-9f8a-4e65-bbce-5f2cdb454a00/download/"
     "cfia_acia-1225-spices_misrepresentation_2020-2021.csv"),
    ("2021-2022", BASE + "c35a1243-2a3e-47d2-9cdd-a48c2fcef232/download/"
     "cfia_acia-1317-v3-dai_2021-22_spice025587.csv"),
    ("2022-2023", BASE + "a349dcdb-092a-4000-a109-445669357520/download/"
     "cfia_acia-1507-pt-1-spices_026840.csv"),
)
SUPPLEMENTS = (
    ("2020-2021", "txt", BASE + "cced019e-d2ec-456b-820c-c14901da247b/download/"
     "cfia_acia-1225-supplemental_information_for_the_spices_authenticity_surveillance.txt"),
    ("2021-2022", "pdf", BASE + "cc13eb28-c0d5-4fd7-8272-236478a0f741/download/"
     "cfia_acia-18900859-v1-supplemental_information_for_the_spice_authenticity_surveillance_summary_r.pdf"),
    ("2022-2023", "pdf", BASE + "dbb26cfa-aacf-42db-89b1-f6752b65ac57/download/"
     "cfia_acia-1507-spices-pt-2-en.pdf"),
)

LEAD_RE = re.compile(r"\blead\b|chromat|chromium|\bpb\b|plomb", re.I)
DYE_RE = re.compile(
    r"colou?r|colorant|\bdyes?\b|teinture|sudan|soudan|tartrazine|rhodamine|orange\s*ii\b|"
    r"\bazo\b|metanil|sunset yellow|allura|ponceau|carmoisine|erythrosine|quinoline|"
    r"amaranth|auramine|butter yellow|para red|acid red", re.I)
FILLER_RE = re.compile(
    r"filler|\bstarch|amidon|wheat|\bbl[ée]\b|gluten|shell|coque|peanut|arachide|almond|"
    r"amande|\bnuts?\b|foreign|[ée]trang|husk|sawdust|\bbran\b|flour|farine|extraneous|"
    r"plant material|mati[èe]re v[ée]g[ée]tale|substitut|\bstems?\b|\btiges?\b|cereal|"
    r"c[ée]r[ée]ale|\brice\b|\briz\b|\bcorn\b|ma[ïi]s\b|maize|barley|\borge\b|chickpea|"
    r"\bsoy|\bwood\b|\bbois\b|other plant|bulking|dilut", re.I)

SPICES = (
    ("turmeric", re.compile(r"turmeric|tumeric|curcuma", re.I)),
    ("ginger", re.compile(r"ginger|gingembre", re.I)),
    ("paprika", re.compile(r"paprika", re.I)),
    ("chili", re.compile(r"chil+i|chile|cayenne|red pepper|crushed pepper|piment", re.I)),
    ("cinnamon", re.compile(r"cinnamon|cassia|cannelle", re.I)),
    ("cumin", re.compile(r"cumin", re.I)),
    ("coriander", re.compile(r"coriander|coriandre", re.I)),
    ("black_pepper", re.compile(r"black pepper|poivre noir", re.I)),
    ("white_pepper", re.compile(r"white pepper|poivre blanc", re.I)),
    ("oregano", re.compile(r"oregano|origan", re.I)),
    ("saffron", re.compile(r"saffron|safran", re.I)),
    ("curry", re.compile(r"curry|masala", re.I)),
    ("garlic", re.compile(r"garlic|\bail\b", re.I)),
    ("onion", re.compile(r"onion|oignon", re.I)),
    ("cardamom", re.compile(r"cardamom", re.I)),
    ("clove", re.compile(r"clove|girofle", re.I)),
    ("nutmeg", re.compile(r"nutmeg|muscade", re.I)),
    ("mustard", re.compile(r"mustard|moutarde", re.I)),
    ("fenugreek", re.compile(r"fenugreek|fenugrec", re.I)),
    ("sumac", re.compile(r"sumac", re.I)),
    ("herbs", re.compile(r"basil|thyme|rosemary|parsley|\bsage\b|\bdill\b|\bbay\b|laurel|mint", re.I)),
)
YELLOW_BROWN = ("turmeric", "ginger")
SOUTH_ASIA = ("INDIA", "PAKISTAN", "BANGLADESH", "SRI LANKA", "NEPAL")
P2_MAX_SHARE = 0.03
ORIGIN_SPLIT = re.compile(r"\s*(?:/|,|;|&|\+|\band\b|\bor\b|\bet\b|\bou\b)\s*", re.I)


def decode(raw):
    for enc in ("utf-8-sig", "cp1252"):
        try:
            return raw.decode(enc), enc
        except UnicodeDecodeError:
            pass
    return raw.decode("latin-1"), "latin-1"


def _first(header, pattern, exclude=None):
    for i, h in enumerate(header):
        if re.search(pattern, h, re.I) and not (exclude and re.search(exclude, h, re.I)):
            return i
    return None


def find_header(table):
    """Index of the header row: the first of the top 15 rows with a cell starting
    "Sample" and a cell naming the assessment (or result)."""
    for i, row in enumerate(table[:15]):
        cells = [c or "" for c in row]
        if (any(re.match(r"\s*sample", c, re.I) for c in cells)
                and any(re.search(r"assess|valuation|result", c, re.I) for c in cells)):
            return i
    return None


def find_columns(header):
    cols = {
        "sample": _first(header, r"^\s*sample", r"from|assess|result"),
        "sampled_from": _first(header, r"sampled from|province"),
        "origin": _first(header, r"origin|dealer|country", r"^\s*origine|^\s*pays"),
        "product": _first(header, r"product|commodity", r"^\s*nom\b"),
        "assessment": _first(header, r"assess|valuation|result"),
    }
    notes = [i for i, h in enumerate(header) if re.search(r"note|comment|remarque", h, re.I)]
    cols["notes_en"] = notes[0] if notes else None
    cols["notes_fr"] = notes[1] if len(notes) > 1 else None
    missing = [k for k in ("sample", "product", "assessment") if cols[k] is None]
    if missing:
        raise ValueError("missing columns %s in header %r" % (missing, header))
    return cols


def norm_assessment(value):
    s = re.sub(r"\s+", "", value or "").upper()
    if not s:
        return ""
    if s == "S" or s.startswith("SATIS"):
        return "S"
    if s.startswith("U") or s.startswith("INSAT"):
        return "U"
    if s.startswith("INV"):
        return "INV"
    return "OTHER"


def spice_of(product):
    for name, rx in SPICES:
        if rx.search(product or ""):
            return name
    return "other"


def split_origins(value):
    s = (value or "").strip()
    if not s:
        return []
    return [p.strip().upper() for p in ORIGIN_SPLIT.split(s) if p and p.strip()]


def classify(notes):
    lead = bool(LEAD_RE.search(notes))
    return {"lead": lead,
            "dye": bool(DYE_RE.search(notes)) and not lead,
            "filler": bool(FILLER_RE.search(notes))}


def _cell(row, i):
    if i is None or i >= len(row):
        return ""
    return (row[i] or "").strip()


def parse_file(raw, year):
    """Rows of one fiscal year's CSV, plus a parse check."""
    text, enc = decode(raw)
    table = list(csv.reader(io.StringIO(text)))
    h = find_header(table)
    if h is None:
        raise ValueError("no header row in the first 15 rows of %s" % year)
    header = [c.strip() for c in table[h]]
    cols = find_columns(header)
    rows = []
    for raw_row in table[h + 1:]:
        sample = _cell(raw_row, cols["sample"])
        product = _cell(raw_row, cols["product"])
        if not sample and not product:
            continue
        notes_en = _cell(raw_row, cols["notes_en"])
        notes_fr = _cell(raw_row, cols["notes_fr"])
        notes = " | ".join(n for n in (notes_en, notes_fr) if n)
        origin = _cell(raw_row, cols["origin"])
        code = _cell(raw_row, cols["assessment"])
        r = {"year": year, "sample": sample, "sampled_from": _cell(raw_row, cols["sampled_from"]),
             "origin": origin, "origins": split_origins(origin), "product": product,
             "spice": spice_of(product), "assessment_raw": code,
             "assessment": norm_assessment(code), "notes_en": notes_en, "notes_fr": notes_fr,
             "notes": notes}
        r.update(classify(notes))
        rows.append(r)
    codes = {}
    for r in rows:
        codes[r["assessment_raw"]] = codes.get(r["assessment_raw"], 0) + 1
    u = [r for r in rows if r["assessment"] == "U"]
    check = {"year": year, "encoding": enc, "header_row": h, "header": header,
             "columns": {k: (header[v] if v is not None else None) for k, v in cols.items()},
             "rows": len(rows), "assessment_codes": codes,
             "notes_nonempty": sum(1 for r in rows if r["notes"]),
             "u_rows": len(u), "u_rows_with_notes": sum(1 for r in u if r["notes"])}
    return rows, check


def _status(gradable, met):
    if not gradable:
        return "not gradable"
    return "met" if met else "not met"


def grade(rows):
    n = len(rows)
    u = [r for r in rows if r["assessment"] == "U"]
    u_noted = sum(1 for r in u if r["notes"])
    notes_ok = bool(u) and 2 * u_noted >= len(u)
    lc = [r for r in rows if r["lead"]]
    lc_u = sum(1 for r in u if r["lead"])
    fill_u = sum(1 for r in u if r["filler"])
    tg = sum(1 for r in lc if r["spice"] in YELLOW_BROWN)
    single = [r for r in lc if len(r["origins"]) == 1]
    sa = sum(1 for r in single if r["origins"][0] in SOUTH_ASIA)
    p = {
        "P1": {"prediction": "at least one sample's notes name lead chromate (lead/chromate/Pb)",
               "value": len(lc), "status": _status(notes_ok, len(lc) >= 1)},
        "P2": {"prediction": "lead-chromate samples are at most 3% of all samples",
               "value": "%d of %d" % (len(lc), n),
               "status": _status(notes_ok and n > 0, n > 0 and len(lc) <= P2_MAX_SHARE * n)},
        "P3": {"prediction": "among unsatisfactory samples, filler notes outnumber lead notes",
               "value": "filler %d vs lead %d of %d U" % (fill_u, lc_u, len(u)),
               "status": _status(notes_ok, fill_u > lc_u)},
        "P4": {"prediction": "at least half of lead-chromate samples are turmeric or ginger",
               "value": "%d of %d" % (tg, len(lc)),
               "status": _status(notes_ok and bool(lc), 2 * tg >= len(lc))},
        "P5": {"prediction": "at least half of single-origin lead-chromate samples declare a "
                             "South Asian origin (India, Pakistan, Bangladesh, Sri Lanka, Nepal)",
               "value": "%d of %d" % (sa, len(single)),
               "status": _status(notes_ok and bool(single), 2 * sa >= len(single))},
    }
    return {"version": VERSION, "rows": n, "u_rows": len(u), "u_rows_with_notes": u_noted,
            "notes_gradable": notes_ok, "predictions": p,
            "met": sum(1 for v in p.values() if v["status"] == "met"),
            "gradable": sum(1 for v in p.values() if v["status"] != "not gradable")}


def _tally(rows, key):
    out = {}
    for r in rows:
        k = key(r)
        t = out.setdefault(k, {"n": 0, "S": 0, "U": 0, "INV": 0, "OTHER": 0, "": 0,
                               "lead": 0, "dye": 0, "filler": 0})
        t["n"] += 1
        t[r["assessment"]] += 1
        for c in ("lead", "dye", "filler"):
            t[c] += int(r[c])
    return dict(sorted(out.items()))


def origin_key(r):
    if not r["origins"]:
        return "(blank)"
    return r["origins"][0] if len(r["origins"]) == 1 else "(multiple)"


def describe(rows):
    flagged = [r for r in rows if r["assessment"] in ("U", "INV") or r["lead"]]
    return {
        "by_year": _tally(rows, lambda r: r["year"]),
        "by_spice": _tally(rows, lambda r: r["spice"]),
        "by_year_spice": _tally(rows, lambda r: "%s %s" % (r["year"], r["spice"])),
        "by_origin": _tally(rows, origin_key),
        "georgia_rows": sum(1 for r in rows if "GEORGIA" in r["origins"]),
        "lead_rows": [{k: r[k] for k in ("year", "sample", "sampled_from", "origin", "product",
                                         "spice", "assessment_raw", "notes")}
                      for r in rows if r["lead"]],
        "flagged_rows": [{k: r[k] for k in ("year", "sample", "origin", "product",
                                            "assessment_raw", "notes", "lead", "dye", "filler")}
                         for r in flagged],
    }


def fetch(url, tries=4, pause=10):
    last = None
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=120) as resp:
                return resp.read()
        except Exception as e:  # noqa: BLE001 - retried, then raised
            last = e
            time.sleep(pause * (k + 1))
    raise last


def write_rows(path, rows):
    keys = ["year", "sample", "sampled_from", "origin", "product", "spice", "assessment_raw",
            "assessment", "lead", "dye", "filler", "notes_en", "notes_fr"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(keys)
        for r in rows:
            w.writerow([int(r[k]) if isinstance(r[k], bool) else r[k] for k in keys])


def summary_md(result, checks):
    lines = ["# cfia_spice_auth %s" % VERSION, "",
             "Source: CFIA, Spices Authenticity Summary Data, %s (Open Government Licence - "
             "Canada)." % DATASET, "",
             "| file | rows | encoding | U rows | U rows with notes | sha256 |", "|---|---|---|---|---|---|"]
    for year, c in sorted(checks.items()):
        if "error" in c:
            lines.append("| %s | ERROR: %s | | | | |" % (year, c["error"]))
        else:
            lines.append("| %s | %d | %s | %d | %d | %s |" % (year, c["rows"], c["encoding"],
                         c["u_rows"], c["u_rows_with_notes"], c.get("sha256", "")[:12]))
    g = result["grade"]
    lines += ["", "## Pre-registered predictions (%d met of %d gradable)" % (g["met"], g["gradable"]),
              "", "| | prediction | value | status |", "|---|---|---|---|"]
    for k, v in g["predictions"].items():
        lines.append("| %s | %s | %s | %s |" % (k, v["prediction"], v["value"], v["status"]))
    d = result["descriptive"]
    for title, key in (("By year", "by_year"), ("By spice", "by_spice"), ("By declared origin", "by_origin")):
        lines += ["", "## %s (descriptive)" % title, "",
                  "| | n | S | U | INV | other | lead | dye | filler |", "|---|---|---|---|---|---|---|---|---|"]
        for k, t in d[key].items():
            lines.append("| %s | %d | %d | %d | %d | %d | %d | %d | %d |" % (
                k, t["n"], t["S"], t["U"], t["INV"], t["OTHER"] + t[""], t["lead"], t["dye"], t["filler"]))
    lines += ["", "## Lead-chromate rows", ""]
    for r in d["lead_rows"]:
        lines.append("- %s %s %s, %s (%s): %s" % (r["year"], r["sample"], r["product"], r["origin"],
                                                  r["assessment_raw"], r["notes"]))
    if not d["lead_rows"]:
        lines.append("- none")
    lines += ["", "Made by MV2 of Munim, Inc. with AI agents. Code Apache-2.0; derived data CC BY 4.0.", ""]
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--data-dir", default=None, help="read cfia_spices_<year>.csv from here if present")
    ap.add_argument("--out-dir", default="out")
    ap.add_argument("--no-supplements", action="store_true")
    a = ap.parse_args(argv)
    os.makedirs(a.out_dir, exist_ok=True)
    rows, checks = [], {}
    for year, url in FILES:
        name = "cfia_spices_%s.csv" % year
        local = os.path.join(a.data_dir, name) if a.data_dir else None
        if local and os.path.exists(local):
            with open(local, "rb") as f:
                raw = f.read()
            src = local
        else:
            try:
                raw = fetch(url)
            except Exception as e:  # noqa: BLE001
                checks[year] = {"error": "download failed: %s" % e, "source": url}
                continue
            src = url
            with open(os.path.join(a.out_dir, name), "wb") as f:
                f.write(raw)
        try:
            got, check = parse_file(raw, year)
        except ValueError as e:
            checks[year] = {"error": str(e), "source": src}
            continue
        check.update(source=src, bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
        checks[year] = check
        rows.extend(got)
    if not a.no_supplements:
        for year, ext, url in SUPPLEMENTS:
            try:
                raw = fetch(url, tries=2)
                with open(os.path.join(a.out_dir, "cfia_spices_%s_supplement.%s" % (year, ext)), "wb") as f:
                    f.write(raw)
            except Exception as e:  # noqa: BLE001 - supplements are descriptive only
                print("supplement %s failed: %s" % (year, e), file=sys.stderr)
    result = {"grade": grade(rows), "descriptive": describe(rows), "checks": checks}
    write_rows(os.path.join(a.out_dir, "cfia_spice_auth_rows.csv"), rows)
    with open(os.path.join(a.out_dir, "grades.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=1, ensure_ascii=False)
    with open(os.path.join(a.out_dir, "summary.md"), "w", encoding="utf-8") as f:
        f.write(summary_md(result, checks))
    g = result["grade"]
    print("cfia_spice_auth %s: %d rows, %d of %d gradable predictions met"
          % (VERSION, g["rows"], g["met"], g["gradable"]))
    return 0 if all("error" not in c for c in checks.values()) and len(checks) == len(FILES) else 1


if __name__ == "__main__":
    sys.exit(main())
