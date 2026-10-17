# Pre-registration: does the Pb:Cr chromate screen stay quiet on spices a regulator called clean? (cfia-chromate-2018 0.1.0)

**Author:** MV2, Munim, Inc. (mv2@munimtech.com). Work made with AI agents.
**License:** text CC BY 4.0; code Apache-2.0.
**Status:** pre-registered. Written and committed together with the grading code
(`cfia_chromate_2018.py`, `test_cfia_chromate_2018.py`) **before any lead, chromium or
chromate value in the data file was read**. The result will be a separate, later commit,
graded against the predictions below.

## Why this exists

Two published parts of this repository judge whether a lead/chromium pair looks like lead
chromate (PbCrO4):

- `nyc_spice_lead.py` calls a pair **chromate-like** when lead is at least 18 ppm and the
  molar Pb:Cr ratio lies in 0.7-2.0 (PbCrO4 = 1).
- `cr_baseline.py` calls a chromate-like pair **robust** when its chromium is higher than
  every published natural-chromium ceiling for that spice (`data/natural_cr_ceilings.csv`).
  32 of the 34 chromate-like NYC pairs are robust, and the stress test showed 30 of them
  survive a 2-fold inflation of every ceiling.

Both were built on contaminated samples. Neither has been tested on spices **known to be
clean**. If ordinary retail spices often carry more chromium than those ceilings, the
ceilings are too low and "robust" means less than claimed. If clean spices often land in
the molar band, the band is only specific because of its lead floor.

The Canadian Food Inspection Agency (CFIA) bought 131 yellow and red spices at retail in
six Canadian cities in 2018-19 and measured lead, total chromium and a colorimetric
chromate spot test on each one. Its report found none adulterated with lead chromate. The
per-sample file is open: "2018-2019 Lead Chromates in Spices Data", open.canada.ca dataset
06033736-6095-4b85-8760-95dd8c209576 (Open Government Licence - Canada). That makes it a
labelled negative set for both tools. We found no published per-sample analysis of this
file, and no test of a natural-chromium ceiling table against a regulator's clean samples.

## What was seen before registering (blinding record)

- The dataset page and the file's **structure**: 393 rows in long format (lead, chromium
  and a chromate spot-test row for each of 131 sample numbers, some ending in "R"),
  columns, regions (Atlantic, Quebec, Ontario, West), function (Import / Domestic /
  Unknown), declared origins (Canada, India, Sri Lanka, China, Bangladesh, United States,
  Jamaica, Hungary, South Africa, Unknown), products (spice blend, thyme, turmeric,
  cayenne pepper, chili powder, coriander, cinnamon, cumin, paprika, star anise, anise),
  units ug/g, and that some metal amounts are a bare 0 (no detection limits are given).
- The CFIA report's methods, and its headline from a search snippet: 131 samples, **none
  found to contain elevated levels of lead or chromium** and none adulterated by CFIA's
  three-part rule (lead and chromium both present, a ratio consistent with lead chromate
  and a positive spot test). CFIA gives no numeric ratio.
- From the same search: CFIA's 2019-2021 survey (132 samples, no per-sample open file
  found) reported two ground-ginger samples consistent with lead chromate.
- No lead, chromium or spot-test value of any sample was seen.

Because CFIA's headline was seen, P4 is close to a sanity check, and it is labelled as one.
P1, P2, P3 and P5 depend on per-sample values that were not seen.

## Method (fixed in advance)

- Unit: one sample number with both a lead and a chromium amount. A bare 0 counts as 0
  (not detected). Amounts are in ug/g = ppm.
- Matrix: the English product name maps to a ceiling matrix: turmeric; cinnamon;
  chili/paprika (cayenne pepper, chili powder, paprika); cumin; coriander. Everything else
  (spice blends, thyme, star anise, anise) is "generic".
- Ceiling: the **highest** ceiling for that matrix, any method, in
  `data/natural_cr_ceilings.csv` on `main` now (natural_cr_ceilings 0.1.2), frozen in the
  code: turmeric 2.88, cinnamon 4.0, chili/paprika 3.17, cumin 8.59, coriander 18.93,
  generic 8.59 ppm. This is the ceiling that decides "robust" in `cr_baseline.py`.
- Molar Pb:Cr = (Pb / 207.2) / (Cr / 51.996), defined only when both are above 0.
  The band is 0.7-2.0 inclusive and the lead floor 18 ppm, as in `nyc_spice_lead.py`.
- The parse is gradable only if at least 120 samples have both lead and chromium.

## Predictions (falsifiable)

- **P1 (main).** Among samples of a spice with its own ceiling (not generic), **at most
  5%** carry more chromium than that spice's highest published natural ceiling.
- **P2.** **At most 2** samples of any kind carry more than 8.59 ppm chromium (the
  generic ceiling).
- **P3.** With **no** lead floor, **no** sample's molar Pb:Cr lies in 0.7-2.0. (Natural
  spices should carry far more chromium than lead, mole for mole.)
- **P4 (sanity, see above).** The published screen (lead >= 18 ppm and molar Pb:Cr in
  0.7-2.0) flags **no** sample, agreeing with CFIA.
- **P5.** **Fewer than 8.3%** of samples carry lead >= 2 ppm, the share among NYC
  store-survey spices in 2016-2025 (purchase-place 0.1.0).

A failure of P1 or P2 means the natural-chromium ceilings behind the "robust" verdicts are
too low for retail spices, and the result note will say which of the 32 robust NYC pairs
the observed clean-spice chromium could flip. A failure of P3 means the band is not
specific without its lead floor. Failures will be reported as failures.

## Descriptive (not graded)

Lead and chromium medians and maxima by product, matrix, function (import / domestic) and
declared origin; the spot-test values; the largest molar ratio; how many coriander
samples exceed coriander's highest ICP-MS ceiling (0.912 ppm), since the 18.93 ppm
ceiling comes from FAAS on market seed.

## Outputs (next commit)

- `data/cfia_lead_chromates_2018-2019.csv` (the CFIA file, frozen, Open Government
  Licence - Canada) and `data/cfia_chromate_2018_samples.csv` (one row per sample).
- `docs/cfia-chromate-2018-0.1.0-result.md`, graded against P1-P5, with a test that
  recomputes every graded number from the committed file.

Contains information licensed under the Open Government Licence - Canada.
