# cfp-lead 0.1.0: lead in six open CFIA Children's Food Project files (2017 to 2022) against every lead figure CFIA printed, and against the U.S. FDA's 2025 baby-food action levels — result

RESULT-MARKER: cfp-lead-0.1.0-result

By MV2 of Munim, Inc. Prepared with AI agents working in his name. Text CC BY 4.0; code Apache-2.0.

This grades the pre-registration [cfp-lead-0.1.0-prereg.md](cfp-lead-0.1.0-prereg.md), which was
public first, at tag `v0.4.79`. The sealed job `cfp-lead-v1` ran on 2026-10-30 at 02:06 UTC
(python:3.12, 2 GB, no host paths). It waited for the registration's marker to be public,
checked that its bundled `cfp_lead.py` and `test_cfp_lead.py` were byte-identical to the
published copies, ran the 12 offline tests and only then read the six SHA-256-pinned files.
**All six per-year gates passed, and 12 of 13 graded items held: the gate, five of six
consistency checks and all six blind predictions.**

This is a reproducibility check of open government data, not a compliance finding and not about
any brand. Health Canada reviewed every CFP lead result and found none a safety concern. Canada's
maximum levels for lead cover fruit juice (0.05 ppm) and infant formula (0.01 ppm as consumed);
the other products tested have none. The U.S. FDA levels below are non-binding U.S. guidance,
used only as a reference scale. Values are for products as sampled. It is not dietary or medical
advice.

## Headlines

1. **The 2021 report's 0.18 ppm meal maximum is a slipped decimal point (P1 and P2 held).** No
   2021 value is anywhere near 0.18 ppm. The three puree/meal positives in the file are 0.016,
   0.018 and 0.022 ppm. Reading the meal maximum as 0.018 makes every printed 2021 figure fit:
   meals 0.016 and 0.018 (mean over 53 = 0.00064, printed 0.001), puree 0.022 (printed maximum
   0.02). As printed, the table puts a toddler meal at 18 times the FDA's 10 ppb level; the file
   puts it at 1.8 times.
2. **The open files reproduce every printed lead table row in all six years** (tested,
   negative, positive and maximum, 979 samples), and every text figure but one. The one miss
   (C2021): the 2021 text says detected levels "ranged from 0.015 to 0.047 ppm", but the
   smallest 2021 value in the file is 0.016. Everything else in that sentence holds (285 of 291
   not detected; top value 0.047, a dry pasta).
3. **The printed means follow two conventions, as predicted (P5, 12 of 12 rows).** 2017, 2019,
   2020 and 2021 average over all samples; 2018-19 and 2022 over positives only. 2017's table
   note says "Average of positive results only", but its two positives (0.007 and 0.009) average
   0.008, not the printed 0.000; only the all-sample mean (0.0003) prints as 0.000. Anyone reading
   the means across years as one series would mix two different statistics.
4. **From 2018 to 2021 no value under 0.010 ppm was reported (P3 held).** The smallest detected
   value was 0.016 (2018), 0.015 (2019), 0.027 (2020) and 0.016 ppm (2021); in 2022 it was
   0.0050, and lead was found in 64 of 108 samples (59%) against 2-8% before. (2017's two juice
   positives, 0.007 and 0.009, show that juice was reported to a lower limit that year.) The rise in
   detections is a change in what the laboratory reported, not evidence of more lead.
5. **FDA dry-infant-cereal level (20 ppb; P4 held):** 6 of 48 infant cereals in 2019 were above
   it (12.5%, 95% interval 5.9-24.7%; 0.026 to 0.093 ppm), and 1 of 39 in 2022 (0.0211 ppm,
   just over; 0.5-13.2%).
6. **Infant cereal at a common 0.015 ppm cut fell from 11 of 48 (22.9%) in 2019 to 3 of 39
   (7.7%) in 2022 (P6 held; one-sided Fisher exact p = 0.049),** but see the exploratory note:
   the fall comes entirely from imported cereals, and the 2022 sample has no U.S.-declared
   cereal at all. Snacks at the same cut did not fall: 7 of 78 (9.0%) in 2019, 8 of 69 (11.6%)
   in 2022 (p = 0.40 for a rise).

## Gate (passed in all six years)

Per year: the SHA-256; all five columns found by header; lead rows and distinct samples (51,
143, 251, 135, 291, 108), the unit `µg/g` (= ppm) on every row and samples per product label
equal to the names-only census; every result a number above 0 (detected) or 0 (not detected).
No `<` values, tokens or blanks occurred, so no `bad_shapes` were recorded.

## Graded items: 12 of 13 held

| ID | Registered | Observed in the files | Met |
|---|---|---|---|
| G | per-year gate, all six years | 6 of 6 years pass | ✅ |
| C2017 | juice 51 / 49 / 2, max 0.009 | 51 / 49 / 2, max 0.009 | ✅ |
| C2018 | 5 table rows; formulas 3 of 59 at 0.016–0.019 | all rows; 3 of 59 at 0.016–0.019 | ✅ |
| C2019 | 5 table rows; 19 of 251 detected | all rows; 19 of 251 | ✅ |
| C2020 | 4 table rows; 130 of 135 not detected | all rows; 130 of 135 | ✅ |
| C2021 | 3 rows; 285 of 291 nd; range 0.015–0.047, top a pasta | rows, 285 of 291 and pasta 0.047 hold; **smallest is 0.016** | ❌ |
| C2022 | 2 rows; 44 of 108 nd; 0.0050–0.196, top a cracker; both minima 0.0050 | all hold | ✅ |
| P1 | 2021: no value rounds to 0.18; puree/meal max < 0.05 | max 0.022; none near 0.18 | ✅ |
| P2 | 2021: one puree/meal positive is 0.018 | 0.016, **0.018**, 0.022 | ✅ |
| P3 | smallest detected ≥ 0.010 ppm, 2018–2021 | 0.016, 0.015, 0.027, 0.016 | ✅ |
| P4 | 20 ppb cereal level: 2019 ≥ 6 of 48; 2022 1–3 of 39 | 6 of 48; 1 of 39 | ✅ |
| P5 | mean convention per year (12 rows) | 12 of 12 as predicted | ✅ |
| P6 | infant cereal ≥ 0.015 ppm: 2022 below 2019 | 7.7% vs 22.9% (p = 0.049) | ✅ |

## Per year (all product types)

| Year | Samples | Detected | Smallest detected (ppm) | Largest (ppm), product |
|---|---|---|---|---|
| 2017 | 51 | 2 | 0.007 | 0.009, toddler/infant juice |
| 2018 | 143 | 4 | 0.016 | 0.03, dry pasta |
| 2019 | 251 | 19 | 0.015 | 0.093, infant cereal |
| 2020 | 135 | 5 | 0.027 | 0.095, children's cereal |
| 2021 | 291 | 6 | 0.016 | 0.047, dry pasta |
| 2022 | 108 | 64 | 0.0050 | 0.196, cracker |

The 2022 maximum (0.196 ppm, a cracker the report calls gluten free) is about four times the
next-highest 2022 snack (0.0475). The FDA guidance sets no level for snacks.

## FDA reference table (reported, not graded)

Count above the FDA level that plausibly applies, with a Wilson 95% interval.

| Year | Product type | FDA level | Above / tested | 95% interval |
|---|---|---|---|---|
| 2018 | puree | 10 ppb | 0 / 38 | 0–9.2% |
| 2018 | toddler/baby meal | 10 ppb | 0 / 11 | 0–25.9% |
| 2019 | puree | 10 ppb | 1 / 98 (0.015) | 0.2–5.6% |
| 2019 | infant cereal | 20 ppb | 6 / 48 | 5.9–24.7% |
| 2019 | yogurt | 10 ppb | 0 / 16 | 0–19.4% |
| 2020 | pudding | 10 ppb | 0 / 36 | 0–9.6% |
| 2021 | puree and meals | 10 ppb | 3 / 177 (one above 20 ppb) | 0.6–4.9% |
| 2022 | infant cereal | 20 ppb | 1 / 39 | 0.5–13.2% |

**From 2018 to 2021, a "not detected" result cannot show that a puree, meal, yogurt or pudding
was under 10 ppb:** nothing below 15 ppb was reported in those years, so a food at 11-14 ppb would read as not
detected. These zero counts are therefore lower bounds. FDA's levels cover packaged food for
children under two; children's yogurts and puddings may fall outside them; snacks, formula and
juice have no FDA level and are left out.

## Exploratory, not registered: the infant-cereal fall is an import story

The pre-registration registered no origin comparison, so this was noticed after grading and is
reported as a hypothesis only. In 2019 the 48 infant cereals were declared as 9 United States,
12 Canada, 20 unknown and 7 European (Austria 2, Switzerland 5). The six above 20 ppb were 4 of
the 9 U.S.-declared cereals and 2 of the unknowns; none of the 19 Canadian or European ones.
The four U.S.-declared cereals carry consecutive sample numbers (CFP2019-0107 to -0110), so
they may be one product line sampled together and are better read as one cluster than as four
independent results.

In 2022 there is **no U.S.-declared infant cereal** among the 39 (8 Canada, 31 unknown). The
Canadian-declared cereals did not fall: at the 0.015 ppm cut, 4 of 12 in 2019 and 3 of 8 in
2022; the three 2022 cereals at or above 0.015 ppm are all Canadian-declared. The whole P6 fall
is in the imported and unknown cereals (7 of 36 in 2019 against 0 of 31 in 2022). So the
registered "2022 below 2019" holds as a count, but these files cannot tell a change in cereals
on the market from a change in which cereals were sampled.

## Limits

- "Detected" is each file's own coding (a number above 0). No page or file gives a lead
  reporting limit; the smallest values imply about 0.015 ppm in 2018-2021 (2017's juice went lower)
  and 0.0050 in 2022.
  Years are compared only at the common 0.015 ppm cut.
- The 2021 file labels only 5 of the report's 53 meals as meals, so 2021 purees and meals are
  checked as one row; the 0.018 reading of the meal maximum is the only one that fits all the
  printed 2021 figures, but the file cannot say which samples the report called meals.
- Origin is the product's declared country, not where its ingredients grew; "unknown" is common
  (most 2022 cereals).

Prior art: on 2026-10-29, searches found CFIA's yearly reports, the open datasets and reviews
of single report pages. They found no per-sample, multi-year analysis of the CFP lead data, no
check of the files against the printed lead tables, no note of the 2021 0.18 ppm slip or of the
mixed mean conventions, and no comparison of these samples with the FDA's 2025 levels.

## Reproduce it

- `data/cfp_lead_samples.csv`: one row per lead sample (year, sample, product, report type,
  origin, function, unit, rows, raw value, kind, value in ppm), the sealed job's output.
- `data/cfp_lead_summary.json`: the sealed grader record (gates, every check and prediction
  with observed values, the FDA table, the census and provenance).
- `test_cfp_lead_result.py`: a pinned test. It does not import the grader. With its own code it
  rebuilds the per-year counts, every printed table row, the text figures, P1–P6 (Wilson
  intervals and Fisher p from scratch), the FDA table and the exploratory origin counts from the
  CSV, and checks them against the sealed record.

A sealed follow-up job (`cfp-lead-result-v1`) fetches these published files from GitHub and
re-runs the pinned test on them. The grading code `cfp_lead.py` and the pre-registration are at
tag `v0.4.79`.
