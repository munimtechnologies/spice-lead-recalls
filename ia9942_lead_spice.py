#!/usr/bin/env python3
"""ia9942_lead_spice 0.1.1: firms on FDA's Red Lists for lead in spices (Import Alerts 99-42 and 28-13).

Grades docs/ia9942-lead-spice-0.1.0-prereg.md, which was written and committed before
any Red List entry was counted by country, spice or year. Did FDA's border listings
for lead in spices fall after 2020, the way gross lead fell in NYC's case-investigation
spices (georgia_trend 0.1.0), or not?

Import Alert 99-42 ("Detention without physical examination of foods due to heavy
metal (toxic element) contamination") lists firms by country. Each product line has an
FDA product code (industry 28 = spices, flavors and salts), a "Date Published", a
"Desc", optional "Notes" (often "DWPE date: MM/DD/YYYY") and "Problems" (e.g. LEAD;).

The job freezes the current page and Wayback Machine copies of it, then:
  lead-spice line   product code industry 28 and Problems contains LEAD
  listing date      the date after "DWPE date" in Notes, else the line's Date Published
  lead-spice firm   (country, firm name) with at least one lead-spice line; its listing
                    date is the earliest over those lines
  E                 lead-spice firms listed 2016-2020, counted on the latest 2021 Wayback
                    copy (else the latest 2020 copy); fallback: the current page, flagged
  L                 lead-spice firms listed 2021-2025, counted on the current page

Changes in 0.1.1 (docs/ia9942-lead-spice-0.1.1-deviation.md):
  parsing only    a field label alone on its line ("Problems:") takes the value lines
                  under it ("LEAD;", "CADMIUM;"); "DWPE date" may be followed by ":",
                  ";" or "-"; a product code may read "54 - - - --"; gzip-encoded
                  Wayback copies are decoded; rate-limited fetches back off longer
  deviation       the 2021 copy of 99-42 says lead in spices then fell under Import
                  Alert 28-13, so E as registered is empty by construction. E_D adds
                  the latest 2021 (else 2020) Wayback copy of 28-13, where every
                  industry-28 line counts as a lead-spice line. The registered grade is
                  still reported, flagged.

Made by MV2 of Munim, Inc. with AI agents. Apache-2.0.
"""
import argparse
import csv
import gzip
import html
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from html.parser import HTMLParser

VERSION = "0.1.1"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/126.0 Safari/537.36 ia9942_lead_spice/%s (MV2 of Munim, Inc.; mv2@munimtech.com)"
      % VERSION)
PAGE = "https://www.accessdata.fda.gov/cms_ia/importalert_1167.html"
ALERTS = {"99-42": "accessdata.fda.gov/cms_ia/importalert_1167.html",
          "28-13": "accessdata.fda.gov/cms_ia/importalert_1143.html"}
EXTRA_PAGES = {"ia4502": "https://www.accessdata.fda.gov/cms_ia/importalert_118.html"}
CDX = "https://web.archive.org/cdx/search/cdx"

EARLY = (2016, 2020)
LATE = (2021, 2025)
MIN_FIRMS = 10
NYC_TOP5 = ("GEORGIA", "BANGLADESH", "PAKISTAN", "INDIA", "RUSSIA")

BLOCK_TAGS = {"br", "p", "div", "tr", "td", "th", "li", "ul", "ol", "table", "h1", "h2",
              "h3", "h4", "h5", "h6", "hr", "section", "article", "header", "footer"}
CODE_RE = re.compile(r"^(\d{2})\s*([A-Z-])\s*([A-Z-])\s*([A-Z-])\s*([0-9A-Z-]{2})(?=\s|$)\s*(.*)$")
DATE_LABEL_RE = re.compile(r"^Date Published\s*:\s*(.*)$", re.I)
FIRM_DATE_RE = re.compile(r"^Date Published\s+:", re.I)
FIELD_RE = re.compile(r"^(Desc|Notes|Problems)\s*:\s*(.*)$", re.I)
VALUE_RE = re.compile(r"^(?:[A-Z][A-Z ]*;\s*)+$")
DATE_RE = re.compile(r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b")
DWPE_RE = re.compile(r"DWPE\s*date\s*[:;-]?\s*(\d{1,2}/\d{1,2}/\d{4})", re.I)
LEAD_RE = re.compile(r"\bLEAD\b", re.I)
TITLE_RE = re.compile(r"^Import Alert\s*#\s*(\d{2}-\d{2})")

SPICES = (
    ("cinnamon", re.compile(r"CINNAMON|CASSIA", re.I)),
    ("turmeric", re.compile(r"TURMERIC|CURCUMA|HALDI", re.I)),
    ("chili", re.compile(r"CHIL+I|CHILE|PAPRIKA|CAYENNE|RED PEPPER|PEPPER,\s*RED", re.I)),
    ("cumin", re.compile(r"CUMIN", re.I)),
    ("coriander", re.compile(r"CORIANDER", re.I)),
    ("ginger", re.compile(r"GINGER", re.I)),
    ("curry_masala", re.compile(r"CURRY|MASALA", re.I)),
)


class _Text(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip += 1
        if tag in BLOCK_TAGS:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self.skip:
            self.skip -= 1
        if tag in BLOCK_TAGS:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def html_to_lines(text):
    p = _Text()
    p.feed(text)
    p.close()
    lines = []
    for raw in "".join(p.parts).split("\n"):
        line = re.sub(r"\s+", " ", html.unescape(raw).replace("\xa0", " ")).strip()
        if line:
            lines.append(line)
    return lines


def merge_fields(lines):
    """Join a field label left alone on its line with the value lines printed under it.

    The live page prints "Problems:" on one line and "LEAD;" (or "CADMIUM; LEAD;") on
    the next; older copies print one problem per line. Only lines that look like
    problem values (upper-case words ending in ";") are taken.
    """
    out = []
    i, n = 0, len(lines)
    while i < n:
        f = FIELD_RE.match(lines[i])
        if f and not f.group(2).strip():
            vals = []
            j = i + 1
            while j < n and VALUE_RE.match(lines[j]):
                vals.append(lines[j])
                j += 1
            out.append(("%s: %s" % (f.group(1), " ".join(vals))).strip())
            i = j
            continue
        out.append(lines[i])
        i += 1
    return out


def to_iso(mdy):
    m = DATE_RE.search(mdy or "")
    if not m:
        return ""
    return "%s-%02d-%02d" % (m.group(3), int(m.group(1)), int(m.group(2)))


def parse(lines):
    """Product lines of the Red List, one dict per line, with its firm and country."""
    lines = merge_fields(lines)
    out = []
    firm = None
    heading = ""
    cur = None
    last_address = -1
    block = 0
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        nxt = lines[i + 1] if i + 1 < n else ""
        code = CODE_RE.match(line)
        after = lines[i + 2] if i + 2 < n else ""
        # the code and its product text may sit on one line or on two
        split = bool(code and not code.group(6) and nxt and DATE_LABEL_RE.match(after))
        if code and (DATE_LABEL_RE.match(nxt) or split):
            cur = {"country": firm["country"] if firm else "", "firm": firm["name"] if firm else "",
                   "firm_address": firm["address"] if firm else "",
                   "address_country": firm["address_country"] if firm else "",
                   "code": "".join(code.group(1, 2, 3, 4, 5)), "industry": code.group(1),
                   "product": nxt if split else code.group(6), "date_published": "", "desc": "",
                   "notes": "", "problems": "", "block": block}
            out.append(cur)
            i += 2 if split else 1
            continue
        if DATE_LABEL_RE.match(nxt) and not DATE_LABEL_RE.match(line) and not FIELD_RE.match(line):
            address = lines[i + 2] if i + 2 < n else ""
            token = address.rsplit(",", 1)[-1].strip().upper() if "," in address else ""
            prev = lines[i - 1] if i >= 1 else ""
            if prev and i - 1 != last_address and not CODE_RE.match(prev) \
                    and not FIELD_RE.match(prev) and not DATE_LABEL_RE.match(prev) and len(prev) <= 60:
                heading = prev.strip().upper()
            block += 1
            firm = {"name": line.strip().upper(), "address": address,
                    "country": heading or token, "address_country": token}
            last_address = i + 2
            cur = None
            i += 3
            continue
        m = DATE_LABEL_RE.match(line)
        if m and cur is not None and not cur["date_published"]:
            cur["date_published"] = to_iso(m.group(1))
        f = FIELD_RE.match(line)
        if f and cur is not None:
            key = f.group(1).lower()
            cur[key] = (cur[key] + " " + f.group(2)).strip()
        i += 1
    return out


def listing_date(line):
    m = DWPE_RE.search(line.get("notes") or "")
    if m:
        return to_iso(m.group(1))
    return line.get("date_published") or ""


def is_lead_spice(line, problems_seen=True, alert="99-42"):
    if line["industry"] != "28":
        return False
    if alert == "28-13":       # the whole alert is lead in spices
        return True
    if problems_seen:
        return bool(LEAD_RE.search(line.get("problems") or ""))
    text = " ".join((line.get("desc") or "", line.get("notes") or "", line.get("product") or ""))
    return bool(LEAD_RE.search(text))


def spice_tags(text):
    tags = [name for name, rx in SPICES if rx.search(text or "")]
    return tags or ["other"]


def firms(lines, alert="99-42"):
    """Lead-spice firms keyed by (country, firm): earliest listing date and spice tags."""
    problems_seen = any(l.get("problems") for l in lines)
    out = {}
    for line in lines:
        if not is_lead_spice(line, problems_seen, alert):
            continue
        key = (line["country"], line["firm"])
        date = listing_date(line)
        rec = out.setdefault(key, {"country": line["country"], "firm": line["firm"],
                                   "listing_date": "", "tags": set(), "n_lines": 0})
        rec["n_lines"] += 1
        if date and (not rec["listing_date"] or date < rec["listing_date"]):
            rec["listing_date"] = date
        rec["tags"].update(spice_tags(line["product"] + " " + line.get("desc", "")))
    return out


def union(*sets):
    """Merge firm dicts: one record per (country, firm), earliest date, all tags."""
    out = {}
    for fs in sets:
        for key, r in fs.items():
            rec = out.setdefault(key, {"country": r["country"], "firm": r["firm"],
                                       "listing_date": "", "tags": set(), "n_lines": 0})
            rec["n_lines"] += r["n_lines"]
            rec["tags"] |= set(r["tags"])
            d = r["listing_date"]
            if d and (not rec["listing_date"] or d < rec["listing_date"]):
                rec["listing_date"] = d
    return out


def norm(text):
    return re.sub(r"[^A-Z0-9]+", " ", (text or "").upper()).strip()


def without(fs, others):
    """Firms in fs whose normalised (country, name) is not among others."""
    seen = {(norm(r["country"]), norm(r["firm"])) for r in others.values()}
    return {k: r for k, r in fs.items() if (norm(r["country"]), norm(r["firm"])) not in seen}


def year_of(rec):
    d = rec.get("listing_date") or ""
    return int(d[:4]) if d[:4].isdigit() else None


def in_span(rec, span):
    y = year_of(rec)
    return y is not None and span[0] <= y <= span[1]


def tag_counts(recs):
    counts = {}
    for r in recs:
        for t in r["tags"]:
            counts[t] = counts.get(t, 0) + 1
    return counts


def strict_top(counts, tag):
    """True when tag has strictly more firms than every other tag."""
    mine = counts.get(tag, 0)
    return mine > 0 and all(v < mine for k, v in counts.items() if k != tag)


def grade(early_firms, late_firms, early_source):
    """The five pre-registered predictions."""
    e = [r for r in early_firms.values() if in_span(r, EARLY)]
    l = [r for r in late_firms.values() if in_span(r, LATE)]
    ne, nl = len(e), len(l)
    gradable = ne + nl >= MIN_FIRMS
    ce, cl = tag_counts(e), tag_counts(l)
    georgia = sum(1 for r in e if r["country"] == "GEORGIA")
    grades = {
        "gradable": gradable,
        "early_source": early_source,
        "E": ne, "L": nl,
        "P1_L_greater_than_E": {"met": nl > ne if gradable else None},
        "P2_L_at_least_2E": {"met": nl >= 2 * ne if gradable else None},
        "P3_cinnamon_top_spice_in_L": {"counts": cl, "met": strict_top(cl, "cinnamon") if nl else None},
        "P4_turmeric_top_spice_in_E": {"counts": ce, "met": strict_top(ce, "turmeric") if ne else None},
        "P5_no_georgia_firm_in_E": {"georgia_firms": georgia, "met": georgia == 0},
    }
    grades["n_met"] = sum(1 for g in grades.values() if isinstance(g, dict) and g.get("met") is True)
    grades["E_by_country"] = country_counts(e)
    grades["L_by_country"] = country_counts(l)
    return grades


def country_counts(recs):
    counts = {}
    for r in recs:
        counts[r["country"]] = counts.get(r["country"], 0) + 1
    return dict(sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])))


def by_listing_year(fs):
    counts = {}
    for r in fs.values():
        y = year_of(r)
        counts[str(y)] = counts.get(str(y), 0) + 1
    return dict(sorted(counts.items()))


def decode(raw):
    """Wayback 'id_' copies can come back still gzip-encoded."""
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    return raw.decode("utf-8", errors="replace")


def fetch(url, tries=4):
    last = None
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=120) as resp:
                return decode(resp.read())
        except Exception as exc:  # network errors are reported, not hidden
            last = exc
            time.sleep(30 * (k + 1) if "429" in str(exc) else 5 * (k + 1))
    raise RuntimeError("fetch failed: %s: %s" % (url, last))


def wayback_index(target):
    q = urllib.parse.urlencode({"url": target, "output": "json",
                                "fl": "timestamp,statuscode,original", "filter": "statuscode:200"})
    rows = json.loads(fetch(CDX + "?" + q) or "[]")
    return [{"timestamp": r[0], "original": r[2]} for r in rows[1:]]


def latest_in_year(index, year):
    hits = [r for r in index if r["timestamp"][:4] == str(year)]
    return max(hits, key=lambda r: r["timestamp"]) if hits else None


def wayback_url(rec):
    return "https://web.archive.org/web/%sid_/%s" % (rec["timestamp"], rec["original"])


def firm_rows(fs, source):
    return [{"source": source, "country": r["country"], "firm": r["firm"],
             "listing_date": r["listing_date"], "tags": ";".join(sorted(r["tags"])),
             "n_lines": r["n_lines"]} for r in sorted(fs.values(), key=lambda r: (r["country"], r["firm"]))]


def write_csv(path, rows, fields):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def check(lines, parsed, alert):
    merged = merge_fields(lines)
    titles = [TITLE_RE.match(l).group(1) for l in lines if TITLE_RE.match(l)]
    return {"alert_on_page": titles[0] if titles else "",
            "text_lines": len(lines),
            "problems_lines_in_text": sum(1 for l in merged if l.lower().startswith("problems")),
            "parsed_lines": len(parsed),
            "parsed_lines_with_problems": sum(1 for p in parsed if p["problems"]),
            "firm_date_lines_in_text": sum(1 for l in lines if FIRM_DATE_RE.match(l)),
            "parsed_firm_blocks": len({p["block"] for p in parsed}),
            "industry28_lines": sum(1 for p in parsed if p["industry"] == "28"),
            "lead_spice_lines": sum(1 for p in parsed if is_lead_spice(
                p, any(q["problems"] for q in parsed), alert)),
            "mentions_28_13": any("28-13" in l for l in lines)}


def snapshot(out_dir, name, raw, alert):
    with open(os.path.join(out_dir, name + ".html"), "w", encoding="utf-8") as fh:
        fh.write(raw)
    lines = html_to_lines(raw)
    with open(os.path.join(out_dir, name + ".txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    parsed = parse(lines)
    fields = ["country", "address_country", "firm", "firm_address", "code", "industry", "product",
              "date_published", "desc", "notes", "problems"]
    write_csv(os.path.join(out_dir, name + "_lines.csv"), parsed, fields)
    with open(os.path.join(out_dir, name + "_check.json"), "w", encoding="utf-8") as fh:
        json.dump(check(lines, parsed, alert), fh, indent=2)
    return parsed


def early_pick(by_year):
    for year in (2021, 2020):
        if year in by_year and by_year[year]["lines"]:
            return year
    return None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out-dir", default="out")
    ap.add_argument("--pause", type=float, default=20.0, help="seconds between Wayback fetches")
    args = ap.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)
    log = {"version": VERSION, "fetched_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}

    current = snapshot(args.out_dir, "ia9942_current", fetch(PAGE), "99-42")
    late_firms = firms(current)
    log["current_lines"] = len(current)
    for name, url in EXTRA_PAGES.items():
        try:
            with open(os.path.join(args.out_dir, name + "_current.html"), "w", encoding="utf-8") as fh:
                fh.write(fetch(url))
        except RuntimeError as exc:
            log[name] = str(exc)

    by_year = {"99-42": {}, "28-13": {}}
    prefix = {"99-42": "ia9942", "28-13": "ia2813"}
    for alert, target in ALERTS.items():
        try:
            index = wayback_index(target)
        except Exception as exc:
            log["wayback_index_error_" + alert] = str(exc)
            continue
        log["wayback_captures_" + alert] = len(index)
        for year in range(2015, 2027):
            rec = latest_in_year(index, year)
            if not rec:
                continue
            time.sleep(args.pause)
            try:
                parsed = snapshot(args.out_dir, "%s_wayback_%s" % (prefix[alert], rec["timestamp"]),
                                  fetch(wayback_url(rec)), alert)
            except RuntimeError as exc:
                log["wayback_%s_%d" % (alert, year)] = str(exc)
                continue
            by_year[alert][year] = {"timestamp": rec["timestamp"], "lines": len(parsed),
                                    "firms": firms(parsed, alert)}

    # as registered: E on the latest 2021 (else 2020) copy of 99-42 alone
    y = early_pick(by_year["99-42"])
    if y is None:
        early_firms, src = late_firms, "current page (survivorship-biased fallback)"
    else:
        early_firms, src = by_year["99-42"][y]["firms"], "99-42 wayback %s" % by_year["99-42"][y]["timestamp"]
    registered = grade(early_firms, late_firms, src)
    registered["flag"] = ("invalid by scope if the early 99-42 copy sends lead in spices to "
                          "Import Alert 28-13 (see deviation note)")

    # deviation: E_D adds the latest 2021 (else 2020) copy of 28-13
    y13 = early_pick(by_year["28-13"])
    deviation = None
    if y13 is not None:
        parts = [by_year["28-13"][y13]["firms"]]
        src_d = "28-13 wayback %s" % by_year["28-13"][y13]["timestamp"]
        if y13 in by_year["99-42"]:
            parts.append(by_year["99-42"][y13]["firms"])
            src_d += " + 99-42 wayback %s" % by_year["99-42"][y13]["timestamp"]
        early_d = union(*parts)
        deviation = grade(early_d, late_firms, src_d)
        all_2813 = union(*[info["firms"] for info in by_year["28-13"].values()])
        robust = grade(early_d, without(late_firms, all_2813), src_d + "; L without firms seen on any 28-13 copy")
        log["deviation_robustness_L_not_on_2813"] = robust
        log["nyc_top5_in_E_D"] = {c: sum(1 for r in early_d.values() if in_span(r, EARLY) and c in r["country"])
                                  for c in NYC_TOP5}
    log["nyc_top5_in_L"] = {c: sum(1 for r in late_firms.values() if in_span(r, LATE) and c in r["country"])
                            for c in NYC_TOP5}
    log.update({"grades_as_registered": registered, "grades_deviation_E_D": deviation,
                "current_page_only": grade(late_firms, late_firms, "current page only (survivorship-biased)"),
                "current_lead_spice_firms_by_listing_year": by_listing_year(late_firms)})

    rows = firm_rows(late_firms, "current")
    for alert in ALERTS:
        for year, info in sorted(by_year[alert].items()):
            rows += firm_rows(info["firms"], "%s_wayback_%s" % (prefix[alert], info["timestamp"]))
    write_csv(os.path.join(args.out_dir, "lead_spice_firms.csv"), rows,
              ["source", "country", "firm", "listing_date", "tags", "n_lines"])

    stock = []
    for year in range(2015, 2027):
        a, b = by_year["99-42"].get(year), by_year["28-13"].get(year)
        if not a and not b:
            continue
        both = union(a["firms"] if a else {}, b["firms"] if b else {})
        stock.append({"snapshot_year": year,
                      "ts_9942": a["timestamp"] if a else "", "firms_9942": len(a["firms"]) if a else "",
                      "ts_2813": b["timestamp"] if b else "", "firms_2813": len(b["firms"]) if b else "",
                      "firms_union": len(both)})
    stock.append({"snapshot_year": "current", "ts_9942": log["fetched_utc"],
                  "firms_9942": len(late_firms), "ts_2813": "", "firms_2813": "",
                  "firms_union": len(late_firms)})
    write_csv(os.path.join(args.out_dir, "stock_by_snapshot.csv"), stock,
              ["snapshot_year", "ts_9942", "firms_9942", "ts_2813", "firms_2813", "firms_union"])

    with open(os.path.join(args.out_dir, "grades.json"), "w", encoding="utf-8") as fh:
        json.dump(log, fh, indent=2, default=sorted)
    print(json.dumps(log, indent=2, default=sorted))
    return 0


if __name__ == "__main__":
    sys.exit(main())
