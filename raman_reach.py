#!/usr/bin/env python3
"""raman_reach 0.1.0: how much of the lead-adulterated turmeric in eastern Indian markets sits at or above
the level at which bench Raman sees lead chromate?

Grades docs/raman-reach-0.1.0-prereg.md, which was written and committed before any row, header or caption
of the data table was read.

Data: Supplementary Table 8 of Forsyth J.E., Sinha M., Bandekar A., Mistree D., Luby S.P., "Systemic drivers
of toxic food adulteration: lead chromate in turmeric across eastern India", npj Science of Food (2026),
doi:10.1038/s41538-026-00867-8, licensed CC BY 4.0. 503 turmeric samples from 34 cities in five states,
lead by calibrated handheld XRF. The bench-Raman threshold is 0.5% w/w lead chromate (Wageningen FT-Raman,
Food Control 2021), which is about 3,200 ug/g lead.

Made by MV2 of Munim, Inc. with AI agents. Apache-2.0.
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

VERSION = "0.1.0"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/126.0 Safari/537.36 raman_reach/%s (MV2 of Munim, Inc.; mv2@munimtech.com)" % VERSION)
CITATION = ("Forsyth J.E. et al., \"Systemic drivers of toxic food adulteration: lead chromate in turmeric "
            "across eastern India\", npj Science of Food (2026), doi:10.1038/s41538-026-00867-8, CC BY 4.0, "
            "Supplementary Table 8")
PDF_URLS = [
    "https://static-content.springer.com/esm/art%3A10.1038%2Fs41538-026-00867-8/MediaObjects/"
    "41538_2026_867_MOESM1_ESM.pdf",
    "https://pmc.ncbi.nlm.nih.gov/articles/instance/13357593/bin/41538_2026_867_MOESM1_ESM.pdf",
    "https://europepmc.org/articles/PMC13357593/bin/41538_2026_867_MOESM1_ESM.pdf",
]

LEGAL = 10.0          # India's limit for lead in turmeric, ug/g; "above" is strict
RAMAN_PB = 3200.0     # 0.5% w/w PbCrO4 x 0.641 lead mass fraction
LADDER = [10, 50, 100, 320, 640, 1000, 3200, 10000]

N_SAMPLES = (495, 515)
N_ABOVE = (148, 158)
TOP_PB = (6300.0, 6500.0)
MIN_E = 20
HIGH = 500.0
MIN_HIGH_STATE = 3
MIN_HIGH_FORM = 5
PACKAGED_MAX = 100.0
MIN_PACKAGED = 10
RATIO_BAND = (2.0, 8.0)
MIN_RATIO = 20

STATE_RX = [("Bihar", r"bihar"), ("Jharkhand", r"jharkhand"), ("Uttar Pradesh", r"uttar\s*pradesh"),
            ("West Bengal", r"west\s*bengal"), ("Chhattisgarh", r"chh?att?isgarh")]
STATE_ABBR = {"br": "Bihar", "jh": "Jharkhand", "up": "Uttar Pradesh", "wb": "West Bengal",
              "cg": "Chhattisgarh", "ct": "Chhattisgarh"}

MISSING = {"", "-", "–", "—", "na", "n/a", "nan", "none", "missing", "nt", "not tested"}
BELOW = re.compile(r"^(<.*|≤.*|nd|n\.d\.?|bdl|bld|lod|below\b.*|not\s+detected|undetected)$", re.I)
NUM = re.compile(r"^\+?\d+(?:\.\d+)?$")
UNIT_TAIL = re.compile(r"\s*(µg/g|μg/g|ug/g|ppm|mg/kg)$", re.I)
PLUS_MINUS = re.compile(r"\s*(?:±|\+/-)\s*")

PB_HEAD = re.compile(r"\bpb\b|\blead\b", re.I)
CR_HEAD = re.compile(r"\bcr\b|chromium", re.I)
RATIO_HEAD = re.compile(r"chromate|ratio|pb\s*[:/]\s*cr|cr\s*[:/]\s*pb", re.I)
BAD_HEAD = re.compile(r"\b(sd|std|stdev|error|rsd|cv|lod|loq|log|rank)\b|±|%|geometric", re.I)
MEAN_HEAD = re.compile(r"mean|average|avg", re.I)
UNIT_HEAD = re.compile(r"µg|μg|ug/|ppm|mg/kg|conc", re.I)
PPB_HEAD = re.compile(r"ppb|[µμu]g\s*/\s*kg|ng\s*/\s*g", re.I)
ROLE_PATTERNS = [("state", r"\bstate\b"), ("city", r"\bcity\b|district|town"), ("polish", r"polish"),
                 ("market", r"market|wholesale|retail|vendor|shop"),
                 ("form", r"\bform\b|type|product|category|grade"), ("spice", r"spice|commodity|item"),
                 ("period", r"year|phase|date|round|season|survey")]
FILL = ("state", "city", "polish", "market", "form", "spice", "period")
SKIP_ROW = re.compile(r"^(total|mean|median|geometric|overall|average|sd|summary)\b", re.I)
NOT_TURMERIC = re.compile(r"chil+i|coriander|cumin|mirch|dhania", re.I)
PURPOSIVE = re.compile(r"truck|purposive|follow[- ]?up|dec(?:ember)?[\s\-/]*2023", re.I)
FOOTNOTE = re.compile(r"[*†‡§]+$")

CAPTION_8 = re.compile(r"^\s*(Supplementary\s+Table\s+8|Table\s+S8)\b", re.I | re.M)
CAPTION_ANY = re.compile(r"^\s*(Supplementary\s+(Table|Fig)|Table\s+S\d|Fig(?:ure)?\s+S\d)", re.I)
CAP8_SEARCH = r"(Supplementary\s+Table\s+8|Table\s+S8)\b"
OTHER_SEARCH = r"(Supplementary\s+(Table\s+(?!8\b)\d+|Fig(ure)?\.?\s*\d+)|Table\s+S(?!8\b)\d+)\b"
TEXT_SETTINGS = {"vertical_strategy": "text", "horizontal_strategy": "text"}


def norm(cell):
    return re.sub(r"\s+", " ", str(cell if cell is not None else "")).strip()


def parse_value(cell):
    """(value, detected) for a number, (0.0, False) for a below-detection token, None if missing."""
    s = UNIT_TAIL.sub("", FOOTNOTE.sub("", norm(cell))).replace(",", "")
    s = PLUS_MINUS.split(s)[0].strip()
    if s.lower() in MISSING:
        return None
    if NUM.match(s):
        v = float(s)
        return (v, True) if v > 0 else (0.0, False)
    if BELOW.match(s):
        return (0.0, False)
    return None


def pb_score(h):
    h = norm(h)
    if not PB_HEAD.search(h) or RATIO_HEAD.search(h) or BAD_HEAD.search(h):
        return None
    return 3 * bool(MEAN_HEAD.search(h)) + 2 * bool(UNIT_HEAD.search(h))


def cr_score(h):
    h = norm(h)
    if not CR_HEAD.search(h) or RATIO_HEAD.search(h) or BAD_HEAD.search(h):
        return None
    return 3 * bool(MEAN_HEAD.search(h)) + 2 * bool(UNIT_HEAD.search(h))


def unit_factor(h):
    return 0.001 if PPB_HEAD.search(norm(h)) else 1.0


def is_header_row(cells):
    cells = [norm(c) for c in cells]
    if sum(1 for c in cells if c) < 3 or not any(pb_score(c) is not None for c in cells):
        return False
    numeric = 0
    for c in cells:
        v = parse_value(c)
        if v is not None and v[1]:
            numeric += 1
    return numeric <= 1


def find_header(rows):
    for i, row in enumerate(rows):
        if is_header_row(row):
            return i
    return None


def roles_from_header(header):
    header = [norm(h) for h in header]
    pbs = [(pb_score(h), -j, j) for j, h in enumerate(header) if pb_score(h) is not None]
    if not pbs:
        return None
    j = max(pbs)[2]
    roles = {"pb": j, "pb_factor": unit_factor(header[j])}
    crs = [(cr_score(h), -k, k) for k, h in enumerate(header) if k != j and cr_score(h) is not None]
    if crs:
        k = max(crs)[2]
        roles["cr"] = k
        roles["cr_factor"] = unit_factor(header[k])
    used = {roles["pb"], roles.get("cr")}
    for role, pat in ROLE_PATTERNS:
        for c, h in enumerate(header):
            if c not in used and re.search(pat, h, re.I):
                roles[role] = c
                used.add(c)
                break
    return roles


def find_state(text):
    for name, rx in STATE_RX:
        if re.search(r"\b" + rx + r"\b", text or "", re.I):
            return name
    return ""


def norm_state(value):
    v = norm(value)
    return find_state(v) or STATE_ABBR.get(v.lower().strip("."), "")


def form_class(text):
    t = (text or "").lower()
    if re.search(r"packag|packet|sachet|brand", t):
        return "packaged_powder"
    if "powder" in t:
        return "loose_powder"
    if "double" in t:
        return "root_double"
    if "single" in t:
        return "root_single"
    if re.search(r"root|finger|bulb|rhizome|whole", t):
        return "root_other"
    return "unknown"


def build_records(rows, header_idx, roles):
    """One record per data row under the header; returns (records, skipped-row counts)."""
    ncol = len(rows[header_idx])
    records, skipped, last = [], {}, {}
    has_form = roles.get("form") is not None or roles.get("polish") is not None
    for row in rows[header_idx + 1:]:
        cells = [norm(c) for c in row]
        if len(cells) != ncol:
            key = "length-%d" % len(cells)
            skipped[key] = skipped.get(key, 0) + 1
            continue
        if is_header_row(cells) or SKIP_ROW.match(cells[0]):
            continue
        pb = parse_value(cells[roles["pb"]])
        if pb is None:
            skipped["no-lead"] = skipped.get("no-lead", 0) + 1
            continue
        rec = {"row": len(records) + 1}
        for role in FILL:
            j = roles.get(role)
            if j is not None and cells[j]:
                last[role] = cells[j]
            rec[role] = last.get(role, "") if j is not None else ""
        raw = " | ".join(cells)
        context = " ".join([raw] + [rec[r] for r in FILL])
        rec["pb"] = pb[0] * roles["pb_factor"]
        rec["pb_detected"] = pb[1]
        cr = parse_value(cells[roles["cr"]]) if "cr" in roles else None
        rec["cr"] = cr[0] * roles["cr_factor"] if cr else None
        rec["cr_detected"] = bool(cr and cr[1])
        rec["state"] = norm_state(rec["state"]) or find_state(context)
        rec["form_class"] = form_class(" ".join([rec["form"], rec["polish"]]) if has_form else raw)
        rec["turmeric"] = not NOT_TURMERIC.search(context)
        rec["purposive"] = bool(PURPOSIVE.search(context))
        rec["raw"] = raw
        records.append(rec)
    return records, skipped


def systematic(records):
    return [r for r in records if r["turmeric"] and not r["purposive"]]


def verdict(ok, detail):
    return {"result": "met" if ok else "not met", "detail": detail}


def not_gradable(detail):
    return {"result": "not gradable", "detail": detail}


def fmt(x):
    return "" if x is None else "{:,.1f}".format(x)


def grade(records, roles):
    S = systematic(records)
    E = [r for r in S if r["pb"] > LEGAL]
    n, e = len(S), len(E)
    g = {"P1": verdict(N_SAMPLES[0] <= n <= N_SAMPLES[1], "%d samples in S" % n)}
    rest = {"P2": verdict(N_ABOVE[0] <= e <= N_ABOVE[1], "%d samples above 10 ug/g" % e)}
    if S:
        top = max(S, key=lambda r: r["pb"])
        detail = "highest %s ug/g, state %s" % (fmt(top["pb"]), top["state"] or "unknown")
        if top["state"]:
            rest["P3"] = verdict(TOP_PB[0] <= top["pb"] <= TOP_PB[1] and top["state"] == "Bihar", detail)
        else:
            rest["P3"] = not_gradable(detail)
    else:
        rest["P3"] = not_gradable("no samples")
    k = sum(1 for r in S if r["pb"] >= RAMAN_PB)
    if e >= MIN_E:
        rest["P4"] = verdict(10 * k <= e, "%d of %d above-limit samples at or above 3,200 ug/g" % (k, e))
        m = statistics.median([r["pb"] for r in E])
        rest["P5"] = verdict(m < RAMAN_PB / 10, "median lead in E %s ug/g" % fmt(m))
    else:
        rest["P4"] = not_gradable("only %d samples in E" % e)
        rest["P5"] = not_gradable("only %d samples in E" % e)
    H = [r for r in S if r["pb"] >= HIGH]
    if len(H) >= MIN_HIGH_STATE and all(r["state"] for r in H):
        b = sum(1 for r in H if r["state"] == "Bihar")
        rest["P6"] = verdict(2 * b > len(H), "%d of %d samples at or above 500 ug/g from Bihar" % (b, len(H)))
    else:
        rest["P6"] = not_gradable("%d samples at or above 500 ug/g, %d without a state"
                                  % (len(H), sum(1 for r in H if not r["state"])))
    HF = [r for r in H if r["form_class"] != "unknown"]
    if len(HF) >= MIN_HIGH_FORM:
        roots = sum(1 for r in HF if r["form_class"].startswith("root"))
        rest["P7"] = verdict(roots > len(HF) - roots,
                             "%d roots, %d powders at or above 500 ug/g" % (roots, len(HF) - roots))
    else:
        rest["P7"] = not_gradable("%d samples at or above 500 ug/g with a known form" % len(HF))
    PK = [r for r in S if r["form_class"] == "packaged_powder"]
    if len(PK) >= MIN_PACKAGED:
        over = sum(1 for r in PK if r["pb"] > PACKAGED_MAX)
        rest["P8"] = verdict(over == 0, "%d of %d packaged powders above 100 ug/g" % (over, len(PK)))
    else:
        rest["P8"] = not_gradable("%d packaged powders" % len(PK))
    R = [r["pb"] / r["cr"] for r in E if r["cr_detected"] and r["cr"]]
    if "cr" in roles and len(R) >= MIN_RATIO:
        m = statistics.median(R)
        rest["P9"] = verdict(RATIO_BAND[0] <= m <= RATIO_BAND[1],
                             "median Pb:Cr %.2f over %d samples" % (m, len(R)))
    else:
        rest["P9"] = not_gradable("chromium column %s, %d samples with both"
                                  % ("found" if "cr" in roles else "absent", len(R)))
    if g["P1"]["result"] != "met":
        for p, v in rest.items():
            rest[p] = {"result": "not graded (gate failed)", "detail": v["detail"]}
    g.update(rest)
    return g


def pct(k, n):
    return "%.1f%%" % (100.0 * k / n) if n else "n/a"


def group_table(S, key, title):
    groups = {}
    for r in S:
        groups.setdefault(r[key] or "(unknown)", []).append(r)
    lines = ["| %s | n | above 10 | >= 50 | >= 500 | >= 3,200 | max |" % title, "|---|---|---|---|---|---|---|"]
    for name in sorted(groups, key=lambda x: (-len(groups[x]), x)):
        rs = groups[name]
        lines.append("| %s | %d | %d | %d | %d | %d | %s |" % (
            name, len(rs), sum(1 for r in rs if r["pb"] > LEGAL), sum(1 for r in rs if r["pb"] >= 50),
            sum(1 for r in rs if r["pb"] >= HIGH), sum(1 for r in rs if r["pb"] >= RAMAN_PB),
            fmt(max(r["pb"] for r in rs))))
    return lines


def summarize(records, roles, grades, structure):
    S = systematic(records)
    E = [r for r in S if r["pb"] > LEGAL]
    met = sum(1 for v in grades.values() if v["result"] == "met")
    gradable = sum(1 for v in grades.values() if v["result"] in ("met", "not met"))
    L = ["# raman-reach %s: result" % VERSION, "",
         "Source: %s." % CITATION,
         "Supplement sha256 %s; extraction method %s; Table 8 pages %s." % (
             structure.get("sha256", ""), structure.get("method", ""), structure.get("pages", "")), "",
         "## Predictions", "", "| | result | detail |", "|---|---|---|"]
    for p in sorted(grades, key=lambda x: int(x[1:])):
        L.append("| %s | %s | %s |" % (p, grades[p]["result"], grades[p]["detail"]))
    L += ["", "%d of %d gradable predictions met." % (met, gradable), "",
          "Rows parsed %d; in S %d; purposive %d; not turmeric %d; above 10 ug/g in S %d." % (
              len(records), len(S), sum(1 for r in records if r["purposive"]),
              sum(1 for r in records if not r["turmeric"]), len(E)), "",
          "## Ladder (S)", "", "| lead at or above (ug/g) | samples | share of S | share of E |",
          "|---|---|---|---|"]
    for t in LADDER:
        k = sum(1 for r in S if r["pb"] >= t)
        L.append("| %s | %d | %s | %s |" % ("{:,}".format(t), k, pct(k, len(S)),
                                            pct(sum(1 for r in E if r["pb"] >= t), len(E))))
    k = sum(1 for r in S if r["pb"] >= RAMAN_PB)
    L += ["", "A bench-Raman threshold of 3,200 ug/g lead (0.5%% w/w lead chromate) reaches %d of the %d "
          "samples above India's 10 ug/g limit (%s)." % (k, len(E), pct(k, len(E))), ""]
    if S:
        L += ["## By state (S)", ""] + group_table(S, "state", "state") + [""]
        L += ["## By form (S)", ""] + group_table(S, "form_class", "form") + [""]
    R = [r["pb"] / r["cr"] for r in E if r["cr_detected"] and r["cr"]]
    L += ["## Pb:Cr (E, chromium detected)", ""]
    if len(R) >= 2:
        q = statistics.quantiles(R, n=4)
        L.append("%d samples; median %.2f; quartiles %.2f-%.2f (lead chromate 3.98)." % (
            len(R), statistics.median(R), q[0], q[2]))
    else:
        L.append("%d samples with both values." % len(R))
    L += ["", "## Every sample in S at or above 500 ug/g", "",
          "| row | state | city | market | form | lead ug/g | Cr ug/g |", "|---|---|---|---|---|---|---|"]
    for r in sorted((r for r in S if r["pb"] >= HIGH), key=lambda r: -r["pb"]):
        L.append("| %d | %s | %s | %s | %s | %s | %s |" % (r["row"], r["state"], r["city"], r["market"],
                                                          r["form_class"], fmt(r["pb"]), fmt(r["cr"])))
    L += ["", "## Table structure", "", "Header: %s" % " | ".join(structure.get("header", [])),
          "Column roles: %s" % json.dumps(roles, sort_keys=True), "",
          "Data: %s. Prepared by MV2 of Munim, Inc. with AI agents." % CITATION, ""]
    return "\n".join(L), met, gradable


CSV_COLS = ["row", "state", "city", "market", "form", "polish", "form_class", "spice", "period", "turmeric",
            "purposive", "pb", "pb_detected", "cr", "cr_detected", "raw"]


def write_outputs(out_dir, records, roles, grades, structure):
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "raman_reach_samples.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CSV_COLS, extrasaction="ignore")
        w.writeheader()
        for r in records:
            w.writerow(r)
    with open(os.path.join(out_dir, "grades.json"), "w", encoding="utf-8") as f:
        json.dump(grades, f, indent=1, sort_keys=True)
    text, met, gradable = summarize(records, roles, grades, structure)
    with open(os.path.join(out_dir, "summary.md"), "w", encoding="utf-8") as f:
        f.write(text)
    return met, gradable


def download(data_dir):
    path = os.path.join(data_dir, "forsyth2026_supplement.pdf")
    if os.path.exists(path):
        with open(path, "rb") as f:
            if f.read(4) == b"%PDF":
                return path
    errors = []
    for url in PDF_URLS:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=120) as r:
                data = r.read()
            if data[:4] == b"%PDF":
                with open(path, "wb") as f:
                    f.write(data)
                return path
            errors.append("%s: not a PDF" % url)
        except Exception as ex:  # try the next mirror
            errors.append("%s: %s" % (url, ex))
    sys.exit("FAILED: could not download the supplement: " + "; ".join(errors))


def table8_regions(pdf, start):
    """Cropped page regions from the Table 8 caption to the next caption."""
    regions = []
    for i in range(start, len(pdf.pages)):
        page = pdf.pages[i]
        x0, y0, x1, y1 = page.bbox
        top = y0
        if i == start:
            hits = page.search(CAP8_SEARCH, regex=True, case=False)
            if hits:
                top = max(y0, hits[0]["top"])
        ends = [h["top"] for h in page.search(OTHER_SEARCH, regex=True, case=False) if h["top"] > top + 1]
        bottom = min(min(ends), y1) if ends else y1
        if bottom > top + 1:
            regions.append((i, page.crop((x0, top, x1, bottom))))
        if ends:
            break
    return regions


def region_rows(regions, method):
    rows = []
    for _, region in regions:
        if method == "layout":
            for line in (region.extract_text(layout=True) or "").splitlines():
                if line.strip():
                    rows.append(re.split(r"\s{2,}", line.strip()))
        else:
            tables = region.find_tables(TEXT_SETTINGS if method == "text" else {})
            for t in sorted(tables, key=lambda t: t.bbox[1]):
                rows.extend(t.extract())
    return rows


def extract(path):
    """Find Supplementary Table 8 and return (structure, rows, header index or None, raw text)."""
    import pdfplumber
    structure = {"captions": [], "candidates": [], "attempts": []}
    best, raw_text = None, []
    with pdfplumber.open(path) as pdf:
        structure["pages_total"] = len(pdf.pages)
        texts = []
        for i, page in enumerate(pdf.pages):
            t = page.extract_text() or ""
            texts.append(t)
            for line in t.splitlines():
                if CAPTION_ANY.match(line):
                    structure["captions"].append("p%d: %s" % (i + 1, line.strip()[:150]))
        starts = [i for i, t in enumerate(texts) if CAPTION_8.search(t)]
        structure["candidates"] = [i + 1 for i in starts]
        for s in starts:
            regions = table8_regions(pdf, s)
            for _, region in regions:
                raw_text.append(region.extract_text(layout=True) or "")
            for method in ("lines", "text", "layout"):
                attempt = {"start_page": s + 1, "method": method}
                try:
                    rows = region_rows(regions, method)
                    hi = find_header(rows)
                    n = 0
                    if hi is not None:
                        n = len(build_records(rows, hi, roles_from_header(rows[hi]))[0])
                    attempt.update(rows=len(rows), header_found=hi is not None, records=n)
                    if hi is not None and (best is None or n > best[0]):
                        best = (n, rows, hi, method, [i + 1 for i, _ in regions])
                except Exception as ex:  # record and try the next method
                    attempt["error"] = repr(ex)[:300]
                structure["attempts"].append(attempt)
        if not starts:
            raw_text = texts
    if best is None:
        return structure, [], None, "\n\f\n".join(raw_text)
    structure["method"], structure["pages"] = best[3], best[4]
    return structure, best[1], best[2], "\n\f\n".join(raw_text)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data-dir", default="data")
    ap.add_argument("--out-dir", default="out")
    ap.add_argument("--pdf", help="use a local copy of the supplement instead of downloading")
    args = ap.parse_args(argv)
    os.makedirs(args.data_dir, exist_ok=True)
    os.makedirs(args.out_dir, exist_ok=True)
    path = args.pdf or download(args.data_dir)
    with open(path, "rb") as f:
        sha = hashlib.sha256(f.read()).hexdigest()
    structure, rows, hi, raw_text = extract(path)
    structure["sha256"] = sha
    records, roles = [], None
    if hi is not None:
        header = [norm(c) for c in rows[hi]]
        roles = roles_from_header(header)
        records, skipped = build_records(rows, hi, roles)
        tokens = set()
        for row in rows[hi + 1:]:
            if len(row) == len(header):
                v = parse_value(row[roles["pb"]])
                if v is None or not v[1]:
                    tokens.add(norm(row[roles["pb"]])[:20])
        structure.update(header=header, roles=roles, n_rows=len(rows) - hi - 1, n_records=len(records),
                         skipped=skipped, pb_non_numeric=sorted(tokens))
    with open(os.path.join(args.out_dir, "structure.json"), "w", encoding="utf-8") as f:
        json.dump(structure, f, indent=1, sort_keys=True)
    if not records:
        with open(os.path.join(args.out_dir, "table8_text.txt"), "w", encoding="utf-8") as f:
            f.write(raw_text)
        print("raman_reach %s: FAILED: no lead rows parsed; see structure.json" % VERSION)
        return 2
    grades = grade(records, roles)
    met, gradable = write_outputs(args.out_dir, records, roles, grades, structure)
    print("raman_reach %s: %d rows, %d samples in S, %d of %d gradable predictions met"
          % (VERSION, len(records), len(systematic(records)), met, gradable))
    return 0


if __name__ == "__main__":
    sys.exit(main())
