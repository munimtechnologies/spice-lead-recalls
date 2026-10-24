<!-- RESULT-MARKER: coumarin-tea-0.1.0-result -->
# coumarin-tea 0.1.0: result

By MV2 of Munim, Inc. Made with AI agents working in MV2's name. Code Apache-2.0; this note and
the tables CC BY 4.0. Data: CFIA 2013-14 coumarin survey (Open Government Licence - Canada).
A bounded per-cup exposure screen on open data. Canada sets no coumarin limit for food, so this is
**not a compliance finding**, not a statement about any brand, and not individual dietary or
medical advice.

Grades [`coumarin-tea-0.1.0-prereg.md`](coumarin-tea-0.1.0-prereg.md), which was public at tag
`v0.4.43` before any per-sample tea value was read.

## Headline

The 115 cinnamon-containing **teas** in CFIA's 2013-14 targeted survey carry a wide range of
coumarin: median **240 mg/kg**, mean **496 mg/kg**, 90th percentile **1,420 mg/kg**, maximum
**2,430 mg/kg**, with coumarin detected in 114 of 115. Screened per cup under a deliberately
conservative **100% leaf-to-cup transfer** ("even if every bit of the coumarin steeped out"):

- **A 60 kg adult's standard 2 g cup: none of the 115 teas** delivers more than the adult's
  **whole-day** coumarin tolerable daily intake (TDI, 6 mg). The single most coumarin-rich tea
  reaches **81%** of that whole-day budget in one standard cup, at 100% transfer.
- A 60 kg adult's strong 4 g cup: **7 of 115** (6.1%) cross the adult whole-day TDI.
- A 15 kg child's standard 2 g cup: **33 of 115** (28.7%) cross the child whole-day TDI.
- A 15 kg child's strong 4 g cup: **45 of 115** (39.1%) cross the child whole-day TDI.

All four pre-registered predictions and the parse gate held: **5 of 5**.

## How it was graded

Sealed compute job `coumarin-tea-v1` (2026-10-24 00:52-00:53 UTC, `python:3.12`, no host paths):
`check_prereg.py` confirmed the pre-registration was public on GitHub **and that the bundled
`coumarin_eu_limits.py` parser equals the published one** (reported "match"); then the offline
tests `test_coumarin_tea.py` passed; then `coumarin_tea.py` read the CFIA file (SHA-256
`3c8a18c0…3f4f`, 122,686 bytes, resource `66d9cd8f-d44d-4993-8775-65da6857250c`) and graded.
**Unit census of the 115 tea rows: all `ug/g`** (= mg/kg); no unrecognised unit.

**Blindness, stated honestly.** No agent read any per-sample tea value before the pre-registration
was public. Unlike the fully untouched infant-cereal rows, the tea values *did* already exist in a
file this repository had published — the 749-row per-sample table shipped with `coumarin-eu-limits`
0.1.1 lists every row, including the out-of-scope tea rows — but earlier work read only the bakery,
breakfast-cereal and infant-cereal rows, never the tea rows. We cannot prove a negative, so the
public commit times of the pre-registration and of the grading job are the record. The predictions
and their thresholds are exactly as registered.

## Pre-registered predictions

| | prediction | observed | grade |
|---|---|---|---|
| G0 (parse gate) | measured rows in [740, 749]; pooled max in [2200, 2800] mg/kg (CFIA's 2,510); exactly 115 "tea" rows, all measured; tea max in [2300, 2500] (CFIA's 2,430); tea detected in [112, 115] (CFIA's 99%); unit census `{ug/g: 115}` | 749 rows; pooled max 2,510; 115 tea rows all measured; tea max 2,430; tea detected 114; `{ug/g: 115}` | **pass** |
| P1 (primary) | **no** tea exceeds an adult's whole-day TDI in one standard 2 g cup (A1 count = 0) | 0 / 115 | **met** |
| P2 (test) | share of teas over the TDI in an adult's strong 4 g cup in **[0.005, 0.12]** | 7 / 115 = 0.061 | **met** |
| P3 (test) | share of teas over the TDI in a child's standard 2 g cup in **[0.07, 0.40]** | 33 / 115 = 0.287 | **met** |
| P4 (test) | share of teas over the TDI in a child's strong 4 g cup in **[0.25, 0.70]** | 45 / 115 = 0.391 | **met** |

**5 of 5 met.** The pre-registered reasoning — CFIA's published tea maximum (2,430 mg/kg) sits just
below the adult standard-cup threshold (3,000 mg/kg), so even the most coumarin-rich tea at 100%
transfer stays under an adult's day budget, while the long right tail above the ~500 mg/kg mean is
caught progressively by the stronger and the child scenarios — is borne out.

## Per-cup exposure table (`data/coumarin-tea.csv`)

Coumarin in one cup (mg) = concentration (mg/kg) × dry tea per cup (kg) × transfer (fixed 1.0).
"Over the TDI" means strictly above the concentration at which one cup delivers the drinker's
**whole-day** budget; non-detects count as 0 mg/kg. The TDI is EFSA's 0.1 mg/kg bw/day: 6 mg/day
for a 60 kg adult, 1.5 mg/day for a 15 kg child.

| id | drinker | dry tea/cup | conc. putting one cup over the day's TDI | over TDI | median % of budget | max % of budget | role |
|---|---|---|---|---|---|---|---|
| A1 | 60 kg adult | 2 g (standard cup/bag) | 3,000 mg/kg | 0 / 115 (0.0%) | 8.0% | 81.0% | primary |
| A2 | 60 kg adult | 4 g (strong / double cup) | 1,500 mg/kg | 7 / 115 (6.1%) | 16.0% | 162.0% | test |
| C1 | 15 kg child | 2 g (standard cup/bag) | 750 mg/kg | 33 / 115 (28.7%) | 32.0% | 324.0% | test |
| C2 | 15 kg child | 4 g (strong / double cup) | 375 mg/kg | 45 / 115 (39.1%) | 64.0% | 648.0% | test |

Tea distribution (n = 115): detected 114, minimum 0.0, median 240, mean 496, 90th percentile 1,420,
maximum 2,430 mg/kg. In absolute terms, one standard 2 g adult cup of the most coumarin-rich tea
carries **4.86 mg** of coumarin at 100% transfer (median cup 0.48 mg); a strong 4 g cup doubles
these to 9.72 and 0.96 mg.

The sealed per-sample output is in `data/coumarin_tea_samples.csv` (all 115 rows: CFIA tea
sub-type, region, declared origin, mg/kg, the % of each drinker's day budget under A1-C2, the four
over-TDI flags, and the unit). `test_coumarin_tea_result.py` recomputes every number above from the
per-sample table, the exposure table and the published 749-row `coumarin-eu-limits` table (for the
G0 gate) with plain `csv`, `math`, `statistics` and `unittest`.

## Context and what is new

- CFIA's own public report for this survey (*Coumarin in Cinnamon-Containing Foods*,
  [inspection.canada.ca](https://inspection.canada.ca/en/food-safety-industry/food-chemistry-and-microbiology/food-safety-testing-reports-and-journal-articles/coumarin-0))
  gives a tea-category headline (115 samples, 0.3-2,430, average 500 mg/kg, coumarin detected in
  99%) but **no per-cup exposure and no transfer model**; our n, maximum, mean and detection rate
  match that report. The companion `coumarin-eu-limits` study put tea out of scope, because a
  beverage carries no EU bakery/cereal maximum level; this note covers it on a per-cup basis.
- BfR's and EFSA's coumarin assessments discuss cinnamon in food and the TDI; published studies of
  coumarin extraction from cinnamon bark into hot-water infusions report only **partial** transfer,
  so the real cup is always below these ceilings. We found no open, per-sample, reproducible per-cup
  screen of commercial cinnamon teas against the coumarin TDI. This note, its tables and its test
  are that screen, with an explicit 100%-transfer upper bound.

## Limits

- **100% transfer is an upper bound, not reality.** A real cup delivers only the fraction of
  coumarin that steeps out of the leaf; every count here is a deliberate ceiling. The bound is used
  because it needs no contested extraction figure.
- **TDI is a lifetime value.** Going over it on a single day is not a health finding; BfR has said
  a slight exceedance for one to two weeks is not a concern. This screen counts single cups against
  a whole-day budget as a bounded reference, not a daily-habit estimate.
- **Children rarely drink cinnamon tea.** The child scenarios are a reference bound, not a claim
  that children commonly drink these teas.
- **One cup only.** Coumarin from food and other drinks adds to these figures; this screen does not
  count it.
- **Generic names, targeted sampling.** CFIA labels the products only "Tea - Herbal/Black/Green/
  Other/White"; brands, blends and whether cinnamon is a main or trace ingredient are not in the
  file, and none are implied. 2013-14 targeted sampling, not market shares.

<!-- RESULT-MARKER: coumarin-tea-0.1.0-result -->
