# NYC cinnamon over time 0.1.0 — pre-registration

Made with AI agents working in the name of MV2 of Munim, Inc. Apache-2.0 code / CC BY 4.0 text.

This file is committed (2026-10-21, v0.4.33) **before** any cinnamon row in the NYC case-investigation frame
is compared against ASTA's bark level or broken out by date. It fixes the method, the hypotheses and the
numeric predictions so the grader that follows can be scored honestly. No count below has been computed yet.
The grader (`nyc_cinnamon_time.py` and its offline test) is written only after this file is public.

## What is already known (not blind)

The ASTA yardstick result (`asta-yardstick-0.1.0-result.md`, v0.4.31) already reported, for the **store
survey frame only** (n = 477): 25 cinnamon rows, 21 of them bought 2024-01-04 to 2024-01-23, 10 of those 21
above ASTA's bark level of 2.0 µg/g (highest 23 µg/g). That buying round came weeks after the late-2023
recall of cinnamon applesauce pouches for lead. Those numbers are public and are **checks**, not
predictions, below.

The **case-investigation frame** of the same NYC DOHMH table ("Metal Content of Consumer Products",
da9u-wz3r) was graded earlier only at the gross bar (≥ 50 ppm lead, all spices pooled: 147 of 1,332
spices bought abroad = 11.0%). Its cinnamon rows have **never** been broken out by spice, by level or by
date. That is the blind part of this pre-registration.

## The question

The store frame's cinnamon problem is one targeted buying round. Does cinnamon that reached a **lead-poisoning
case investigation** show the same picture, a different one, or none? Specifically:

1. How often does case-frame cinnamon exceed ASTA's bark level (2.0 µg/g) and the gross bar (50 ppm)?
2. Does case-frame cinnamon show a time pattern, especially a rise in sampling or in exceedance after the
   cinnamon-applesauce recall (October-November 2023)?
3. Is cinnamon a lead-chromate target at all? Turmeric and chili are the classic adulterated spices; cinnamon
   lead is usually attributed to soil, bark and processing. If so, case cinnamon should sit well above the
   near-background ASTA level but rarely above 50 ppm.

**Prior art.** Searches on 2026-10-18 and again on 2026-10-21 found FDA's cinnamon-product testing pages and
2024 advisories (ground-cinnamon products at 2-4 ppm and above), Consumer Reports' 2024 test of 36 cinnamon
products, the NYC DOHMH dataset itself and its technical guide, and news coverage of the 2023 recall. We
found no per-sample analysis of the NYC open table's cinnamon rows by frame and date, and none comparing
case-linked cinnamon with the store survey against ASTA's bark level. The comparison is a synthesis of open
data, not a new measurement.

## Method (stdlib grader + offline test, written after this file is public)

1. **Rows.** Exactly the rows of `sampling_frame.nyc_rows` (Food-Spice, lead, ppm, laboratory, XRF
   excluded), read from `data/nyc_spice_lead_snapshot_2026-10-17.csv` (already in the repo; the same snapshot
   every earlier NYC grader used). Status as there: `value` (> 0, detected), `nd` (≤ 0, not detected),
   `missing` (unparseable; listed, never counted).
2. **Frames.** `investigation_type` C = case investigation (the main frame here), S = store survey (the
   check frame). Rows with any other code (A, blank) are counted on one separate line and enter no prediction
   or hypothesis. Within C, rows are also split by `purchase_country` exactly as `purchase_place.py` does it
   (US / abroad / unknown); this split is descriptive only.
3. **Cinnamon.** Case-insensitive **whole-word** match (`\b` on both sides) on `product_name` for: cinnamon,
   cassia, canela, dalchini, darchini, darchin, kaneel, qirfa, qerfa, tarçın, tarcin, kayu manis, quế. Rows
   whose name also carries a blend word (masala, curry, five-spice, five spice, mixed, mix, seasoning, blend,
   sugar, tea) are listed separately as "cinnamon-named blends" and excluded from the main count. Every
   matched, excluded or doubtful name is printed with its `row_id`, not silently dropped.
4. **Levels.** ASTA V3 bark level 2.0 µg/g (strictly above counts) and gross 50 ppm (at or above). Non-detects
   count as below, so every rate is a lower bound (NYC gives no per-row detection limit). Rates "among
   detected" use `value` rows only; rates "of all" use `value` + `nd` rows.
5. **Time.** `collection_date`, first 10 characters (YYYY-MM-DD). Periods: before 2019-01-01; 2019-01-01 to
   2022-12-31; 2023-01-01 to 2023-10-31; 2023-11-01 to 2024-12-31 (the 14 months after the recall);
   2025-01-01 onward. Rows with no parseable date are counted on their own line. Per period and frame: rows,
   detected, > 2.0, ≥ 50. "Rows per year" = rows divided by the period's length in years (the post-recall
   period = 14/12 years).
6. **Report.** Per frame and period, counts and rates, plus the list of every exceeding row by `row_id`.
   Negative or partial results are published as-is.

## Pre-registered predictions (point, with an 80% interval; expectations, not results)

- **P1. Case-frame (C) cinnamon rows (all dates, main count):** 45; interval [15, 120].
- **P2. Case-frame cinnamon with a detected value above 2.0 µg/g:** 40% of detected rows; interval [15%, 65%].
- **P3. Case-frame cinnamon at or above 50 ppm:** 4% of all case cinnamon rows; interval [0%, 12%].
  Rationale: cinnamon is not a classic chromate target, so its gross rate should sit **below** the frame-wide
  11.0% for spices bought abroad.
- **P4. Sampling reaction:** case-frame cinnamon rows per year in 2023-11-01 to 2024-12-31 are at least **2×**
  the 2019-2022 yearly mean; interval on the ratio [0.8, 5].

## Directional hypotheses (scored true/false)

- **H1.** Case-frame cinnamon gross (≥ 50 ppm) rate < 11.0%, the all-spice abroad-bought gross rate.
- **H2.** Case-frame cinnamon > 2.0 µg/g rate (among detected) ≥ the store frame's cinnamon rate outside the
  January 2024 round. Check value from v0.4.31: outside January 2024 the store frame has 4 cinnamon rows and
  at most 1 exceedance; so H2 is scored only if the case frame has ≥ 10 detected cinnamon rows, else "not
  scorable".
- **H3.** The January 2024 burst is a **store-frame** event: in the case frame, the 2023-11-01 to 2024-12-31
  period does **not** hold the majority of all case cinnamon exceedances > 2.0 µg/g.

## Honest limits, fixed in advance

- The store-frame cinnamon numbers are already public; only the case-frame and time splits are blind.
- Before writing the final method, the grader code of earlier releases (`sampling_frame.py`,
  `purchase_place.py`, `asta_yardstick.py`) was read to name the exact columns (`investigation_type`,
  `collection_date`, `purchase_country`). No data row was read.
- Case samples are whatever a family had at home when a child's blood lead was elevated; they are not a
  sample of any market. The store frame is DOHMH's targeted buying. Neither rate describes "NYC cinnamon".
- Cinnamon vs cassia cannot be separated by name in this table; both are bark (2.0 µg/g) under ASTA.
- ASTA levels are voluntary industry guidance, not law; "exceeds ASTA" is not "illegal" and not "unsafe for
  any one person". No brand is named.
- If cinnamon rows are fewer than 15 in the case frame, the result is reported as under-powered and P2-P4 are
  marked not scorable rather than graded.

Data: NYC DOHMH, NYC Open Data da9u-wz3r (snapshot 2026-10-17). Levels: ASTA Guidance Levels for Heavy
Metals in Spices V3 (2026-06-08), Table 2. Prepared by MV2 of Munim, Inc. with AI agents.
