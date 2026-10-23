<!-- RESULT-MARKER: coumarin-infant-0.1.0-result -->
# coumarin-infant 0.1.0: result

By MV2 of Munim, Inc. Made with AI agents working in MV2's name. Code Apache-2.0; this note and
the tables CC BY 4.0. Data: CFIA 2013-14 coumarin survey (Open Government Licence - Canada).
An exposure screen on open data. Canada sets no coumarin limit for food, so this is **not a
compliance finding**, not a statement about any brand, and not individual dietary or medical advice.

Grades [`coumarin-infant-0.1.0-prereg.md`](coumarin-infant-0.1.0-prereg.md), which was public at
tag `v0.4.41` before any infant-cereal value was read.

## Headline

The 52 cinnamon-containing **infant cereals** in CFIA's 2013-14 targeted survey carry little
coumarin: median **1.25 mg/kg**, maximum **18.3 mg/kg**, with coumarin detected in 51 of 52.
For an 8 kg infant eating one 30 g reference serving of dry cereal every day, **none of the 52**
would reach EFSA's coumarin tolerable daily intake (TDI, 0.1 mg/kg bw/day); the single highest
sample reaches **69%** of it. Only at a doubled 60 g/day serving do **2 of 52** cross the TDI.
Infant cereals sit below the cinnamon-coated children's breakfast cereals (median 3.4 mg/kg).
All four blind predictions and the parse gate held: **5 of 5**.

## How it was graded

Sealed compute job `coumarin-infant-v1` (2026-10-23 21:08-21:09 UTC, `python:3.12`, no host
paths): `check_prereg.py` confirmed the pre-registration was public on GitHub **and that the
bundled `coumarin_eu_limits.py` parser equals the published one** (reported "match"); then the
offline tests `test_coumarin_infant.py` passed; then `coumarin_infant.py` read the CFIA file
(SHA-256 `3c8a18c0…3f4f`, 122,686 bytes, resource `66d9cd8f-d44d-4993-8775-65da6857250c`) and
graded. **Unit census of the 52 infant rows: all `ug/g`** (= mg/kg); no unrecognised unit.

**This was a genuinely blind pre-registered test.** Unlike `coumarin-eu-limits` 0.1.1 (where a
unit bug had exposed the values before the re-grade), no agent read any infant-cereal value before
the pre-registration was public. The predictions and their thresholds are exactly as registered.

## Pre-registered predictions

| | prediction | observed | grade |
|---|---|---|---|
| G0 (parse gate) | measured rows in [740, 749]; pooled max in [2200, 2800] mg/kg; exactly 52 infant rows, all measured; unit census `{ug/g: 52}` | 749 rows; max 2,510 mg/kg; 52 infant rows measured; `{ug/g: 52}` | **pass** |
| P1 (primary) | share of infant cereals over the TDI under S1 (8 kg, 30 g/day) in **[0.00, 0.10]** | 0 / 52 = 0.00 | **met** |
| P2 (test) | share over the TDI under S2 (8 kg, 60 g/day) in **[0.02, 0.30]** | 2 / 52 = 0.038 | **met** |
| P3 (direction) | median infant-cereal coumarin **<** median children's breakfast-cereal coumarin | 1.25 < 3.4 | **met** |
| P4 (test) | share of infant cereals with coumarin detected in **[0.80, 1.00]** | 51 / 52 = 0.981 | **met** |

**5 of 5 met** (gate passed; all four predictions held). The pre-registered reasoning — a mildly
flavoured product line with a thin tail reaching the low tens of mg/kg — is borne out.

## Exposure table (`data/coumarin-infant.csv`)

Daily intake (mg/kg bw/day) = concentration (mg/kg) × dry cereal eaten (kg/day) / body weight (kg).
"Over the TDI" means strictly above the concentration that reaches the TDI for that scenario;
non-detects count as 0 mg/kg.

| scenario | body weight | dry cereal/day | conc. reaching the TDI | over TDI | median % of TDI | max % of TDI | role |
|---|---|---|---|---|---|---|---|
| S1 | 8 kg | 30 g (one Canadian reference amount) | 26.67 mg/kg | 0 / 52 (0.0%) | 4.7% | 68.6% | primary |
| S2 | 8 kg | 60 g (two reference amounts) | 13.33 mg/kg | 2 / 52 (3.8%) | 9.4% | 137.3% | test |
| S3 | 8 kg | 15 g (one US reference amount) | 53.33 mg/kg | 0 / 52 (0.0%) | 2.3% | 34.3% | descriptive |

Infant-cereal distribution (n = 52): detected 51, median 1.25 mg/kg, 90th percentile 2.4,
maximum 18.3. **0 of 52** exceed the EU breakfast-cereal maximum of 20 mg/kg (a reference row
only — the EU has no infant-food coumarin limit, and this one does not apply in Canada).
Children's breakfast cereals, for comparison, had a median of 3.4 mg/kg (n = 65), published with
`coumarin-eu-limits` 0.1.1.

The sealed per-sample output is in `data/coumarin_infant_samples.csv` (all 52 rows: region,
declared origin, mg/kg, the % of the TDI under S1-S3, the over-TDI flags, and the unit).
`test_coumarin_infant_result.py` recomputes every number above from the two data files with plain
`csv`, `statistics` and `unittest`.

## Context and what is new

- CFIA's own public report for this survey (*Coumarin in Cinnamon-Containing Foods*,
  [inspection.canada.ca](https://inspection.canada.ca/en/food-safety-industry/food-chemistry-and-microbiology/food-safety-testing-reports-and-journal-articles/coumarin-0))
  gives only survey-wide figures — 749 samples, coumarin detected in about 95%, 0.1 to 2,510 mg/kg,
  the maximum in a pumpkin-pie spice mix — and **does not break out infant cereals** or compare any
  category with a health-based guidance value. Our pooled maximum (2,510) and overall detection
  rate match that report.
- BfR's 2006 assessment expected infants to take in more coumarin per kg of body weight than
  adults, because they eat more food per kg. These data show that for *commercial infant cereal*
  the concentrations are low enough that a normal daily serving stays well under the TDI; the
  exposure concern in the literature is cinnamon added at home (e.g. oatmeal porridge), which this
  screen does not count.
- We found no open, per-sample, reproducible screen of commercial infant cereals against the
  coumarin TDI. This note, its tables and its test are that screen.

## Limits

- **TDI is a lifetime value.** Being at a few percent of it, or briefly above it, is not a health
  finding; BfR has said a slight exceedance for one to two weeks is not a concern.
- **Cereal only.** Coumarin from other foods, and cinnamon added at home, adds to these figures.
- **Scenario weights and servings.** 8 kg, 30/60/15 g are reference values (Health Canada W.1,
  21 CFR 101.12, WHO growth standard), not measured intakes.
- **Targeted sampling, 2013-14.** These are not market shares, and recipes may have changed since.
- **Generic names.** CFIA labels the products only "Infant Food - Cereal"; brands and flavours are
  not in the file, and none are implied.

<!-- RESULT-MARKER: coumarin-infant-0.1.0-result -->
