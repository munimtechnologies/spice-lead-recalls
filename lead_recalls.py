#!/usr/bin/env python3
"""spice-lead-recalls: U.S. FDA food recalls for lead in spices, from openFDA.

Reads every food enforcement report in openFDA's bulk file (public domain,
https://open.fda.gov/apis/food/enforcement/), keeps the recalls whose reason
names lead as a contaminant, sorts them by spice, parses the lead level FDA
quotes (ppm, ppb, mg/kg, ug/g, mg/g) and asks one question for screening
tools: how many recalled spices carried enough lead for a Raman screen to see
lead chromate at all?

Reported Raman limit: about 0.5% w/w lead chromate in turmeric powder
(Erasmus et al., Food Control 2021, doi:10.1016/j.foodcont.2020.107714).
PbCrO4 is 64.1% lead by mass, so that is about 3,200 ug/g (ppm) lead.

Outputs: lead_recalls.csv (all lead recalls), spice_lead_recalls.csv,
summary.json, summary.md. The level parser reads FDA's free text, so every
parsed level is written next to the text it came from, for checking.

0.1.1: fixes from the hand spot check of 0.1.0 (galangal, supplements and
salted-plum candy, packaging words, levels written like ".012 ppm").

Made by MV2 of Munim, Inc. with AI agents working in his name. Apache-2.0.
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
import urllib.request
import zipfile

__version__ = "0.1.1"

DATA_URL = "https://download.open.fda.gov/food/enforcement/food-enforcement-0001-of-0001.json.zip"
USER_AGENT = "spice-lead-recalls (MV2 of Munim, Inc.; munimversion2@gmail.com)"

# Pb mass fraction of PbCrO4: 207.2 / (207.2 + 51.996 + 4 * 15.999) = 0.6411.
PB_IN_PBCRO4 = 207.2 / (207.2 + 51.996 + 4 * 15.999)
# 0.5% w/w lead chromate (Erasmus et al. 2021) expressed as ug/g lead.
RAMAN_LIMIT_PPM = round(0.005 * PB_IN_PBCRO4 * 1e6)

# Spice categories, checked in order against the product description.
# Phrases, not single words, where a word has another meaning ("chile" is
# also a country, "pepper" also a vegetable).
SPICES = [
    ("cinnamon", ["cinnamon", "canela", "cassia"]),
    ("turmeric", ["turmeric", "curcuma", "haldi"]),
    ("chili/paprika", ["chili", "chilli", "paprika", "cayenne", "red pepper", "chile powder",
                       "chile pepper", "chiles", "chile de arbol", "guajillo", "ancho", "kashmiri mirch"]),
    ("curry/masala", ["curry", "masala"]),
    ("cumin", ["cumin", "jeera"]),
    ("coriander", ["coriander", "dhania"]),
    ("ginger", ["ginger"]),
    ("garlic/onion powder", ["garlic powder", "onion powder", "granulated garlic", "granulated onion"]),
    ("black/white pepper", ["black pepper", "white pepper", "peppercorn"]),
    ("other single spice", ["clove", "nutmeg", "mace", "cardamom", "fenugreek", "allspice", "saffron",
                            "anise", "fennel seed", "bay leaf", "bay leaves", "oregano", "thyme",
                            "sumac", "mustard seed", "mustard powder", "asafoetida", "hing", "amchur",
                            "galanga", "galangal"]),
    ("mixed spice/seasoning", ["seasoning", "spice blend", "spice mix", "spices", "spice", "sazon",
                               "adobo", "za'atar", "zaatar", "garam", "five spice", "5 spice"]),
]

# Products that name a spice word but are not spices or spiced foods.
NOT_SPICE = ["licorice", "liquorice"]

# Words that mark a food that contains a spice rather than a spice itself.
# Not "pouch" or "beverage": spices are sold in pouches, and firms' names say "beverage".
FOOD_WORDS = ["puree", "purée", "applesauce", "apple sauce", "candy", "candies", "lollipop",
              "chocolate", "tea", "juice", "cereal", "cookie", "cracker", "chips", "snack", "noodle",
              "bread", "cake", "drink", "gum", "jelly", "tamarind", "pulparindo", "sauce",
              "paste", "pickle", "oil", "soup", "ramen", "biscuit", "nut", "seed mix",
              "plum", "plums", "prune", "prunes", "saladitos"]

SUPPLEMENT_WORDS = ["capsule", "capsules", "caps", "tablet", "tablets", "softgel", "softgels",
                    "supplement", "dietary supplement", "extract", "cleanse", "cleansing", "detox", "toxin"]

METALS = ["lead", "pb", "arsenic", "cadmium", "mercury", "chromium", "aluminum", "aluminium",
          "nickel", "copper", "zinc", "thallium", "antimony", "uranium"]

# Two-word country names whose first word alone would be cut short.
_COUNTRY_FIRST = {"united", "sri", "south", "north", "el", "costa", "dominican", "hong", "new", "saudi",
                  "ivory", "burkina", "sierra", "puerto"}

_LEAD = re.compile(r"\b(lead|pb)\b", re.I)
_NOT_METAL = re.compile(r"\b(lead|leads|leading)\s+(to|consumers|customers|people)\b"
                        r"|\b(could|may|might|would|will)\s+lead\b", re.I)
_METAL = re.compile(r"\b(%s)\b" % "|".join(METALS), re.I)
_NUM = r"(?<![\d.,])(\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?|\.\d+)"
_UNIT = (r"(ppm|ppb|parts\s+per\s+million|parts\s+per\s+billion|mg\s*/\s*kg|mg\s*/\s*g"
         r"|(?:µg|μg|ug|mcg)\s*/\s*g|(?:µg|μg|ug|mcg)\s*/\s*kg)")
_LEVEL = re.compile(_NUM + r"\s*\(?\s*" + _UNIT + r"(?![a-z])", re.I)
_RANGE = re.compile(_NUM + r"\s*(?:-|–|—|to)\s*" + _NUM + r"\s*" + _UNIT + r"(?![a-z])", re.I)
_ORIGIN = re.compile(r"\b(?:product\s+of|made\s+in|imported\s+from|country\s+of\s+origin:?|origin:)\s+"
                     r"([A-Za-z]+)(?:\s+([A-Za-z]+))?", re.I)

TO_PPM = {"ppm": 1.0, "parts per million": 1.0, "mg/kg": 1.0, "ug/g": 1.0,
          "ppb": 0.001, "parts per billion": 0.001, "ug/kg": 0.001, "mg/g": 1000.0}

BINS = [(0, 1, "<1"), (1, 2, "1-2"), (2, 5, "2-5"), (5, 10, "5-10"), (10, 100, "10-100"),
        (100, 1000, "100-1,000"), (1000, RAMAN_LIMIT_PPM, "1,000-%s" % format(RAMAN_LIMIT_PPM, ",")),
        (RAMAN_LIMIT_PPM, float("inf"), ">=%s" % format(RAMAN_LIMIT_PPM, ","))]


def _is_metal_word(m):
    """'Pb' only in its chemical spelling ('PB' is often peanut butter)."""
    word = m.group(1)
    return word.lower() != "pb" or word == "Pb"


def is_lead_recall(reason):
    """True if the recall reason names lead (the metal) as the problem."""
    text = reason or ""
    for m in _LEAD.finditer(text):
        if not _is_metal_word(m):
            continue
        if m.group(1).lower() == "lead" and _NOT_METAL.search(text[max(0, m.start() - 12):m.end() + 12]):
            continue
        return True
    return False


def _unit_key(unit):
    u = re.sub(r"\s+", " ", unit.lower()).replace(" / ", "/").replace(" /", "/").replace("/ ", "/")
    u = u.replace("µg", "ug").replace("μg", "ug").replace("mcg", "ug")
    return u


def _to_float(num):
    return float(num.replace(",", ""))


def parse_levels(text):
    """Lead levels (ug/g = ppm) stated in a recall text, with the snippet each
    came from. A number is kept only if the nearest metal word to it is lead."""
    text = text or ""
    metals = [(m.start(), m.end(), m.group(1).lower()) for m in _METAL.finditer(text) if _is_metal_word(m)]

    def gap(metal, start, end):
        if metal[1] <= start:
            return start - metal[1]
        if metal[0] >= end:
            return metal[0] - end
        return 0

    found = []
    spans = []
    for m in _RANGE.finditer(text):
        factor = TO_PPM.get(_unit_key(m.group(3)))
        if factor is None:
            continue
        spans.append((m.start(), m.end()))
        for num in (m.group(1), m.group(2)):
            found.append((m.start(), m.end(), _to_float(num) * factor))
    for m in _LEVEL.finditer(text):
        if any(a <= m.start() < b for a, b in spans):
            continue
        factor = TO_PPM.get(_unit_key(m.group(2)))
        if factor is None:
            continue
        found.append((m.start(), m.end(), _to_float(m.group(1)) * factor))
    out = []
    for start, end, ppm in found:
        if not metals:
            continue
        nearest = min(metals, key=lambda mm: gap(mm, start, end))
        if nearest[2] in ("lead", "pb"):
            out.append({"ppm": round(ppm, 6), "text": text[max(0, start - 30):end + 5].strip()})
    return out


def _has_word(text, word):
    return re.search(r"(?<![a-z])%s(?![a-z])" % re.escape(word), text) is not None


def classify(description):
    """(spice category, form) for a product description, or (None, None).
    form is 'spice', 'food containing spice' or 'supplement'."""
    d = (description or "").lower()
    if any(_has_word(d, w) for w in NOT_SPICE):
        return None, None
    for name, words in SPICES:
        if any(_has_word(d, w) for w in words):
            if any(_has_word(d, w) for w in SUPPLEMENT_WORDS):
                return name, "supplement"
            if any(_has_word(d, w) for w in FOOD_WORDS):
                return name, "food containing spice"
            return name, "spice"
    return None, None


def origin_of(*texts):
    """Country named after 'Product of', 'Made in' and the like, if any."""
    for t in texts:
        m = _ORIGIN.search(t or "")
        if m:
            name = m.group(1)
            if name.lower() in _COUNTRY_FIRST and m.group(2):
                name += " " + m.group(2)
            return name.title()
    return ""


def level_bin(ppm):
    for lo, hi, label in BINS:
        if lo <= ppm < hi:
            return label
    return ""


def build_rows(records):
    rows = []
    for r in records:
        reason = r.get("reason_for_recall", "") or ""
        if not is_lead_recall(reason):
            continue
        desc = r.get("product_description", "") or ""
        category, form = classify(desc)
        levels = parse_levels(reason) or parse_levels(desc)
        ppms = [lv["ppm"] for lv in levels]
        date = r.get("recall_initiation_date", "") or ""
        rows.append({
            "recall_number": r.get("recall_number", ""),
            "event_id": r.get("event_id", ""),
            "recall_initiation_date": date,
            "year": date[:4],
            "report_date": r.get("report_date", ""),
            "classification": r.get("classification", ""),
            "status": r.get("status", ""),
            "recalling_firm": " ".join((r.get("recalling_firm", "") or "").split()),
            "state": r.get("state", ""),
            "country": r.get("country", ""),
            "voluntary_mandated": r.get("voluntary_mandated", ""),
            "spice_category": category or "",
            "form": form or "",
            "origin_stated": origin_of(desc, reason),
            "lead_ppm_max": max(ppms) if ppms else "",
            "lead_ppm_min": min(ppms) if ppms else "",
            "level_bin": level_bin(max(ppms)) if ppms else "",
            "level_text": " | ".join(lv["text"] for lv in levels),
            "mentions_chromate": bool(re.search(r"chromate|chromium", reason, re.I)),
            "product_description": " ".join(desc.split())[:400],
            "reason_for_recall": " ".join(reason.split())[:400],
            "distribution_pattern": " ".join((r.get("distribution_pattern", "") or "").split())[:200],
        })
    rows.sort(key=lambda x: (x["recall_initiation_date"], x["recall_number"]))
    return rows


def _count(items, key):
    out = {}
    for it in items:
        k = key(it)
        out[k] = out.get(k, 0) + 1
    return dict(sorted(out.items(), key=lambda kv: (-kv[1], str(kv[0]))))


def summarize(rows, total_records, meta):
    spice = [r for r in rows if r["spice_category"]]
    pure = [r for r in spice if r["form"] == "spice"]
    with_level = [r for r in spice if r["lead_ppm_max"] != ""]
    above = [r for r in with_level if r["lead_ppm_max"] >= RAMAN_LIMIT_PPM]
    levels = sorted(r["lead_ppm_max"] for r in with_level)

    def median(v):
        if not v:
            return None
        n = len(v)
        return v[n // 2] if n % 2 else (v[n // 2 - 1] + v[n // 2]) / 2.0

    return {
        "version": __version__,
        "source": DATA_URL, "openfda_last_updated": meta.get("last_updated", ""),
        "sha256": meta.get("sha256", ""),
        "food_enforcement_records": total_records,
        "lead_recalls": len(rows),
        "lead_recall_events": len({r["event_id"] for r in rows}),
        "spice_lead_recalls": len(spice),
        "spice_lead_events": len({r["event_id"] for r in spice}),
        "spice_products_only": len(pure),
        "spice_by_category": _count(spice, lambda r: r["spice_category"]),
        "spice_by_form": _count(spice, lambda r: r["form"]),
        "spice_by_year": dict(sorted(_count(spice, lambda r: r["year"]).items())),
        "all_lead_by_year": dict(sorted(_count(rows, lambda r: r["year"]).items())),
        "spice_by_classification": _count(spice, lambda r: r["classification"]),
        "spice_by_firm_state": _count(spice, lambda r: r["state"] or r["country"]),
        "spice_top_firms": dict(list(_count(spice, lambda r: r["recalling_firm"]).items())[:15]),
        "spice_origin_stated": _count([r for r in spice if r["origin_stated"]], lambda r: r["origin_stated"]),
        "spice_with_level": len(with_level),
        "spice_level_bins": {label: sum(r["level_bin"] == label for r in with_level) for _, _, label in BINS},
        "spice_level_median_ppm": median(levels),
        "spice_level_max_ppm": levels[-1] if levels else None,
        "raman_limit_ppm_pb": RAMAN_LIMIT_PPM,
        "spice_at_or_above_raman_limit": len(above),
        "spice_above_limit_rows": [{k: r[k] for k in ("recall_number", "recall_initiation_date", "recalling_firm",
                                                       "spice_category", "form", "lead_ppm_max", "level_text")}
                                   for r in above],
        "spice_mentions_chromate": sum(r["mentions_chromate"] for r in spice),
    }


def write_markdown(s, path):
    def table(d, head):
        lines = ["| %s | recalls |" % head, "|---|---|"]
        lines += ["| %s | %d |" % (k or "(none)", v) for k, v in d.items()]
        return lines

    lines = ["# U.S. FDA food recalls for lead in spices (openFDA)", "",
             "spice-lead-recalls %s. Source: openFDA food enforcement bulk file, last updated %s (sha256 %s). "
             "%d enforcement records read." % (s["version"], s["openfda_last_updated"], s["sha256"][:12],
                                               s["food_enforcement_records"]),
             "", "- Recalls naming lead: %d (%d recall events)." % (s["lead_recalls"], s["lead_recall_events"]),
             "- Of these, spices or foods containing a named spice: %d (%d events); spice products themselves: %d." % (
                 s["spice_lead_recalls"], s["spice_lead_events"], s["spice_products_only"]),
             "- Spice recalls with a lead level stated by FDA: %d; median %s ppm, highest %s ppm." % (
                 s["spice_with_level"], s["spice_level_median_ppm"], s["spice_level_max_ppm"]),
             "- At or above about %s ppm lead (0.5%% w/w lead chromate, the reported Raman limit): %d." % (
                 format(s["raman_limit_ppm_pb"], ","), s["spice_at_or_above_raman_limit"]),
             "- Recall reasons that name chromate or chromium: %d." % s["spice_mentions_chromate"], ""]
    lines += ["## By spice", ""] + table(s["spice_by_category"], "spice") + [""]
    lines += ["## By form", ""] + table(s["spice_by_form"], "form") + [""]
    lines += ["## By year recall began", ""] + table(s["spice_by_year"], "year") + [""]
    lines += ["## Stated lead level (ppm = ug/g)", ""] + table(s["spice_level_bins"], "level") + [""]
    lines += ["## By FDA class", ""] + table(s["spice_by_classification"], "class") + [""]
    lines += ["## By recalling firm's state", ""] + table(s["spice_by_firm_state"], "state") + [""]
    lines += ["## Recalls at or above the Raman limit", "", "| recall | began | firm | spice | form | ppm | FDA text |",
              "|---|---|---|---|---|---|---|"]
    for r in s["spice_above_limit_rows"]:
        lines.append("| %s | %s | %s | %s | %s | %s | %s |" % (
            r["recall_number"], r["recall_initiation_date"], r["recalling_firm"], r["spice_category"], r["form"],
            r["lead_ppm_max"], r["level_text"].replace("|", "/")))
    lines += ["", "Levels are parsed from FDA's free text; check each against level_text in the CSV. "
              "openFDA covers recalls FDA classified; state-run actions that FDA did not classify are not in it."]
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


FIELDS = ["recall_number", "event_id", "recall_initiation_date", "year", "report_date", "classification", "status",
          "recalling_firm", "state", "country", "voluntary_mandated", "spice_category", "form", "origin_stated",
          "lead_ppm_max", "lead_ppm_min", "level_bin", "level_text", "mentions_chromate", "product_description",
          "reason_for_recall", "distribution_pattern"]


def load_records(data_dir):
    os.makedirs(data_dir, exist_ok=True)
    path = os.path.join(data_dir, os.path.basename(DATA_URL))
    if not os.path.exists(path):
        req = urllib.request.Request(DATA_URL, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=300) as resp, open(path + ".part", "wb") as fh:
            fh.write(resp.read())
        os.replace(path + ".part", path)
    with open(path, "rb") as fh:
        blob = fh.read()
    with zipfile.ZipFile(io.BytesIO(blob)) as zf:
        name = next(n for n in zf.namelist() if n.endswith(".json"))
        doc = json.loads(zf.read(name).decode("utf-8"))
    meta = {"last_updated": doc.get("meta", {}).get("last_updated", ""), "sha256": hashlib.sha256(blob).hexdigest()}
    return doc.get("results", []), meta


def write_csv(rows, path):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="/out")
    args = ap.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)
    records, meta = load_records(args.data_dir)
    rows = build_rows(records)
    write_csv(rows, os.path.join(args.out_dir, "lead_recalls.csv"))
    write_csv([r for r in rows if r["spice_category"]], os.path.join(args.out_dir, "spice_lead_recalls.csv"))
    s = summarize(rows, len(records), meta)
    with open(os.path.join(args.out_dir, "summary.json"), "w", encoding="utf-8") as fh:
        json.dump(s, fh, indent=1, ensure_ascii=False)
    write_markdown(s, os.path.join(args.out_dir, "summary.md"))
    print(json.dumps({k: s[k] for k in ("food_enforcement_records", "lead_recalls", "spice_lead_recalls",
                                        "spice_with_level", "spice_level_median_ppm",
                                        "spice_at_or_above_raman_limit")}))
    print("by spice:", json.dumps(s["spice_by_category"]))
    print("by form:", json.dumps(s["spice_by_form"]))
    print("level bins:", json.dumps(s["spice_level_bins"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
