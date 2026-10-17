# ia9942-lead-spice 0.1.1: did FDA's border listings for lead in spices fall after 2020?

By MV2 of Munim, Inc. Prepared with AI agents. Text CC BY 4.0; code Apache-2.0.

This grades the [pre-registration](ia9942-lead-spice-0.1.0-prereg.md) under the
[declared deviation](ia9942-lead-spice-0.1.1-deviation.md). Both were written and
committed before any lead-spice firm was counted. The counts come from a sealed
compute job (`ia9942-lead-spice-v2`, 2026-10-17) that froze the live FDA page and
Wayback copies, parsed every Red List line, and graded the five predictions. Every
number here is recomputed from the committed firm table
([`data/ia9942_lead_spice_firms.csv`](../data/ia9942_lead_spice_firms.csv)) by
[`test_ia9942_result.py`](../test_ia9942_result.py).

## Headline grade (deviation, E_D): 2 of 5 predictions held

The registered early count — lead-spice firms on the 2021 copy of Import Alert 99-42 —
is **zero by construction**, because that copy says spices containing lead then fell under
Import Alert 28-13 and lists no spice line at all (the deviation note explains this, and
the parse check confirms it: 0 industry-28 lines in the 2021 99-42 copy). So the headline
grade counts the early period on the **2021 copy of Import Alert 28-13** instead, merged
with the same-year 99-42 copy (which adds nothing), exactly as declared.

- **E** (lead-spice firms listed 2016–2020, on the 2021 copy of 28-13): **19**.
- **L** (lead-spice firms listed 2021–2025, on the current 99-42 page, Oct 2026): **14**.
- **L′** (robustness: L firms whose country+name appears on no 28-13 copy): **12**.

| Prediction | Result | Met? |
|---|---|---|
| **P1** L > E (listings did **not** fall) | 14 < 19 | **No** |
| **P2** L ≥ 2E | 14 < 38 | **No** |
| **P3** cinnamon is the top spice tag among L firms | cinnamon 10, other 4, ginger 1 | **Yes** |
| **P4** turmeric is the top spice tag among E firms | cinnamon 14, turmeric 2, cumin 1, other 2 | **No** |
| **P5** no E firm under the Georgia heading | 0 Georgia firms in E | **Yes** |

**2 of 5 held.** The registered grade (E from 99-42 alone = 0, which would make P1, P2 and
P5 "met" whatever FDA did) is reported in `grades.json` under `grades_as_registered` and is
**flagged invalid by scope**; it is not counted as support for any prediction.

## What this says

1. **Contrary to the prediction, the border record fell too.** We predicted FDA's
   lead-in-spice firm listings would **not** fall after 2020 (P1/P2), so that the border
   record would *diverge* from NYC's falling case data. Instead the stock of lead-spice
   firms went from 19 (2016–2020) to 14 (2021–2025), and 12 after the robustness cut — a
   fall, not a rise. The two independent records point the same way. This weakens the
   "the border can't see what NYC saw, so the records diverge" framing of the prereg.

2. **But the border list is still blind to Georgia, NYC's largest gross-contamination
   source.** P5 held: **no** 2016–2020 lead-spice firm is under the Georgia heading (the
   only Georgian firm, GEO LTD., was listed 2026-01-08, outside both periods). NYC's
   open case data put Georgia (the country) first for results ≥ 50 ppm (49 of the abroad
   total), yet those spices never appear on the US import record — consistent with their
   being carried home in luggage, not commercially imported. The two records agreeing on
   the *trend* does not mean the border sees the same *sources*.

3. **Cinnamon/cassia — not turmeric — dominates the border listings, in both periods.**
   P3 held (cinnamon tops L, 10 of 14) and P4 failed (cinnamon, not turmeric, tops E, 14
   of 19). This is the opposite of NYC's home cases, where turmeric and masala blends
   carry the gross lead. The border and the home tell different spice stories: the import
   record is mostly cassia cinnamon from Vietnam, India, China and Sri Lanka; the home
   record is mostly South-Asian turmeric and mixed masalas.

4. **The most reusable finding is methodological (from the deviation):** lead-in-spice
   listings moved from Import Alert 28-13 into 99-42 around October 2022 (many current
   spice lines carry a 10/13/2022 publication date over much older detention dates). The
   old 28-13 page now 404s and the live 99-42 page no longer cross-references it. Anyone
   trending lead-in-spice border listings from 99-42 alone will see an artificial jump
   around 2022. A correct before/after count must join the two alerts, as this grade does.

## By country

- **E (2016–2020):** India 9, Lebanon 2, Vietnam 2, Canada 1, China 1, Indonesia 1,
  Syrian Arab Republic 1, Thailand 1, Yemen 1.
- **L (2021–2025):** Vietnam 6, India 4, China 1, Ecuador 1, Indonesia 1,
  Trinidad & Tobago 1.

Vietnam rose from 2 to 6 firms; India fell from 9 to 4. None of NYC's top-five abroad
purchase countries other than India (Georgia, Bangladesh, Pakistan, Russian Federation)
appears among E or L lead-spice firms at all.

## Parse checks (all consistent)

| Page | Problems lines (text / parsed) | Firm blocks (text / parsed) | industry-28 lines | mentions 28-13 |
|---|---|---|---|---|
| 99-42 current (Oct 2026) | 606 / 606 | 210 / 210 | 92 | no |
| 99-42 Wayback 2021-12-05 | 156 / 156 | 17 / 17 | **0** | yes |
| 28-13 Wayback 2021-12-08 | 30 / 30 | 26 / 26 | 57 | yes |

The 2021 99-42 copy has no spice line and still names 28-13; the 2021 28-13 copy carries
the 57 lead-spice lines. This is the scope move, frozen in the committed data.

## Honest limits

- **Listings are enforcement actions, not contamination.** A firm count reflects what FDA
  sampled, which firms shipped to the US, and policy (Closer to Zero 2021; the 2023
  cinnamon-applesauce response), not how much lead is in the world's spice supply.
- **This is a stock comparison, with survivorship.** E is counted on a capture near the
  end of its period (Dec 2021); L on a page up to five years after its period opened.
  Firms removed before a capture are unseen, and the two periods are exposed to removal
  differently, so the 19→14 fall should not be read as a precise rate.
- **One likely duplicate in E.** `ABHAYA EXPORTS (PVT) LTD.` and
  `M/S. ABHAYA EXPORTS PVT. LTD.` (both India, both 2020-03-23, both cinnamon) are
  probably one firm under two name forms; the exact (country, firm) dedup keeps them
  apart. Merging them gives E = 18, which does not change any verdict (still L < E,
  cinnamon still tops E).
- **Firms are not products or shipments.** One listing can cover many entries, and the
  country is the Red List heading, not necessarily where the spice was grown.
- **Wayback rate limits.** The 2022–2026 captures of both alerts returned HTTP 429 during
  the job, so the stock-by-year series beyond the 2021 anchors is from the current page
  only (`current_lead_spice_firms_by_listing_year` in `grades.json`), not from
  period-matched captures.

## Files

- [`data/ia9942_lead_spice_firms.csv`](../data/ia9942_lead_spice_firms.csv) — every
  lead-spice firm on the current 99-42 page and the 2021 copy of 28-13, with country,
  name, listing date, spice tags and line count (frozen; FDA data is US government work).
- [`data/ia2813_wayback_20211208151355.txt`](../data/ia2813_wayback_20211208151355.txt) —
  text of the 2021-12-08 Wayback copy of Import Alert 28-13, the early-period source.
- [`data/ia9942_wayback_20211205053251.txt`](../data/ia9942_wayback_20211205053251.txt) —
  text of the 2021-12-05 Wayback copy of 99-42 (committed in v0.4.4), showing the scope
  sentence and no spice line.
- [`ia9942_lead_spice.py`](../ia9942_lead_spice.py) 0.1.1 — fetch, parse and grade.
- [`test_ia9942_result.py`](../test_ia9942_result.py) — recomputes E, L, the spice-tag
  counts and all five predictions from the committed firm table.
