<!-- PREREG-MARKER: coumarin-tdi-0.1.0 -->
# coumarin-tdi 0.1.0 — pre-registration

**How small a serving of Canadian retail cinnamon reaches the EFSA tolerable daily intake (TDI) for coumarin?**

By MV2 of Munim, Inc. Written and committed **before any row of the grading data was read**.
Made with AI agents working in MV2's name. Code Apache-2.0; this note and derived data CC BY 4.0.

## Question

The Canadian Food Inspection Agency (CFIA) measured coumarin in retail cinnamon and
cinnamon-containing products (2011–2016) and published the per-sample concentrations in
parts per million (ppm = mg coumarin per kg of product) as open data. Its reports state
that the levels were "not expected to pose a concern" but **deliberately do not translate
the measured concentrations into a dietary-exposure figure** — i.e. they never say how much
cinnamon a person could eat before reaching a health-based guidance value.

The European Food Safety Authority set a **tolerable daily intake (TDI) for coumarin of
0.1 mg per kg body weight per day** (EFSA 2004, reaffirmed 2008; the basis for EU flavouring
Regulation (EC) No 1334/2008). This study does the arithmetic CFIA left out, reproducibly:
for each CFIA cinnamon sample it computes the serving, in grams, that delivers one TDI to a
60 kg adult and a 15 kg child, and summarises the per-sample distribution.

This is an **information/research tool, not individual dietary or medical advice.** The TDI
is a population guidance value for chronic intake, not an acute-hazard threshold; EFSA itself
notes that intake up to three times the TDI for one–two weeks is not of safety concern.

## Prior art (why this is a new artifact, not a new toxicological claim)

Coumarin-in-cinnamon dietary-exposure work exists in Europe: the Norwegian Scientific
Committee for Food Safety used a benchmark-dose approach and found young children eating
cinnamon oatmeal porridge regularly could exceed the TDI several-fold, and a Danish market
study reported exceedances. Those used European market samples. A short search found **no
open, reproducible per-sample serving-to-TDI translation of CFIA's open Canadian retail
coumarin data (2011–2016)**, and CFIA's own reports do not compute it. The contribution here
is the **open reproducible tool and derived dataset** applied to these specific public
measurements — not a new exposure concept and not a new toxicological finding. The companion
study `coumarin_cinnamon.py` (this repo) classifies the same samples as *verum* (Ceylon) vs
*cassia* by coumarin level; it makes **no** exposure or TDI statement, so there is no overlap.

## Data

The same four CFIA open.canada.ca CSV files the companion study downloads, reused through
that module (`coumarin_cinnamon.fetch` + `coumarin_cinnamon.parse`), pinned to tag `v0.4.34`:

- 2011–12 coumarin in cinnamon (dataset `327a6726-a515-4cf6-b106-0cdb13dd94ba`)
- 2012–13 coumarin in cinnamon (dataset `ca2411af-18da-44be-ada1-1592dd7b94b5`)
- 2014–15 coumarin in cinnamon-containing products (dataset `ecb615ff-504c-4e38-899e-3aeab317fadf`)
- 2015–16 coumarin in cinnamon / cinnamon-containing (dataset `afa33f86-435b-490c-b7c1-31b7ed66c569`)

Contains information licensed under the Open Government Licence – Canada. The parser, unit
rules (ppm default; ppb/µg·kg⁻¹ → ÷1000; "<", "ND", blanks → 0; the 2015–16 ppb→ppm override),
and the cinnamon/vanilla/form/claim flags are exactly those of `coumarin_cinnamon.py`; this
study adds **only** the exposure arithmetic on top of the already-published `ppm` field.

**Sample set graded:** all records across the four files with `cinnamon == True` and a numeric
`ppm > 0` (pooled; the companion study's "primary" vs "replication" split is not used here,
because chronic-exposure interpretation does not depend on it).

## Method

For a product at concentration `ppm` (mg/kg), the coumarin in `g` grams is `g·ppm/1000` mg.
The serving that delivers exactly one TDI to a person of body weight `bw` kg is

```
serving_to_tdi_g(ppm, bw) = (0.1 · bw) / (ppm / 1000) = 100 · bw / ppm   grams
```

Constants (fixed now): `TDI = 0.1` mg/kg·day; `ADULT_KG = 60`; `CHILD_KG = 15`;
reference serving `TEASPOON_G = 2.6` g (one level teaspoon of ground cinnamon; sources give
~2.3–2.8 g, so the teaspoon-based thresholds below scale inversely with this value).
A teaspoon puts a 15 kg child over the TDI when `ppm > 1.5 / (2.6/1000) = 577 ppm`.

The grader reports, over the graded sample set: n samples; pooled min/median/max `ppm`;
median and distribution of adult and child serving-to-TDI; and the fractions used below.
Outputs: `out/coumarin_tdi_samples.csv`, `out/summary.json`, `out/grades.json`.

## Predictions

**G0 — parse/reproduction gate** (confirms the reused pipeline, not a scientific claim):
at least **120** graded cinnamon samples, and the pooled maximum `ppm` falls in **[7000, 8200]**
(the companion study reported a pooled maximum of 7816.3 ppm).

**P1 — primary, genuinely untested:** the **median** adult (60 kg) serving-to-TDI across the
graded cinnamon samples is **below 3.0 g** (less than about 1.2 level teaspoons). *Falsified if
the median is ≥ 3.0 g.*

**P2 — genuinely untested:** at least **25%** of graded cinnamon samples reach an adult TDI in
**under 2.0 g** (equivalently `ppm > 3000`). *Falsified if < 25%.*

**P3 — public-health framing, anticipated:** for a 15 kg child, **more than 80%** of graded
cinnamon samples put the child over the TDI at a single level teaspoon (2.6 g), i.e. `ppm > 577`.
This is largely implied by the companion study's finding that ~95% of these samples are
cassia-type (≥ 1000 ppm), so it is reported as a confirmation, not a discovery. *Falsified if ≤ 80%.*

I will report every prediction's observed value and pass/fail honestly, including G0 and P3,
and will not change a threshold after grading.

## Limits

Population guidance value, not individual advice. Averages/medians use detected positives as
parsed; single-food assumption (does not sum coumarin across a day's whole diet, which would
lower the serving-to-TDI); teaspoon mass and body weights are illustrative point values (a
70 kg adult raises adult servings by ~17%); CFIA product names are generic, so these are
retail-level population figures, not brand or lot statements.

<!-- PREREG-MARKER: coumarin-tdi-0.1.0 -->
