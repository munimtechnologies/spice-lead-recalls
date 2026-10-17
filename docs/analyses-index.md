# Analyses index

A map of the standalone analysis notes in this repository, so the published work is
easy to find from one place. Each note is reproducible from the data and code cited
inside it; this index adds no new claims, it only points to work already published here.

By MV2 of Munim, Inc. Prepared with AI agents. Text CC BY 4.0; code Apache-2.0.

## The natural-chromium question (is a chromate-like Pb:Cr ratio really lead chromate?)

- [Natural chromium in coriander, and the lead-chromate ratio](coriander-chromium.md) —
  across the studies we found, coriander *whole seed* carries under ~1 ppm chromium by
  ICP-MS and neutron activation; the high outliers are FAAS/ICP-OES on extracts. A 2022
  Indian market study (Lopez et al.) found a Patna coriander *powder* with lead chromate
  confirmed by a hexavalent-chromium (DPC) test, yet its Pb:Cr sits inside the
  "unresolved" zone of the natural-chromium screen — so for coriander that verdict is
  conservative, not exculpatory.
- [Twelve coriander powders by ICP-MS: how much of their chromium is natural?](lopez2022-coriander-series.md) —
  OLS on the Lopez 2022 series gives Cr = 0.28 + 0.193·Pb ppm, and the clean reference
  sample reads 0.22 ppm Cr. This rules out a 10–19 ppm natural chromium background for
  South-Asian coriander powder measured by ICP-MS.
- [A direct turmeric ICP-MS ceiling, and the regrade it gives (natural_cr_ceilings 0.1.2)](natural-cr-ceilings-0.1.2-result.md) —
  adding two lead-free Lopez 2022 ICP-MS values raises the turmeric ceiling from 1.9 to
  2.88 ppm, yet every one of the 34 NYC verdicts holds (32 robust, 2 coriander
  unresolved); the Algerian turmeric pair stays robust with its margin tightened to
  0.71 ppm.
- [Pre-registration: a ceiling-inflation stress test (cr-ceiling-stress 0.1.0)](cr-ceiling-stress-0.1.0-prereg.md) —
  written before the analysis: how many of the 32 robust verdicts survive if every
  published natural-chromium ceiling is too low by 1.25x to 10x?
- [cr-ceiling-stress 0.1.0: how fragile is "32 of 34 robust"?](cr-ceiling-stress-0.1.0-result.md) —
  30 of 32 survive a 2-fold inflation of every ceiling and 24 survive 10-fold (median
  headroom about 56x). Only the Algerian turmeric (k 1.25) and a Bangladeshi spice mix
  (k 1.94) can be flipped by a 2-fold error. Three predictions met; the 10x bound
  (at most 8 survivors) failed: the screen is more robust than predicted. A separate
  sealed compute run of `cr_ceiling_stress.py` later reproduced the committed CSV
  exactly (same 32 rows, same k).
- [cr-band-sensitivity 0.1.0: band edge and rounding](cr-band-sensitivity-0.1.0.md) —
  a descriptive check (not pre-registered). Widening the molar Pb:Cr upper edge from 2.0
  to 3.0 changes no verdict and admits no new pair. Tightening it to 1.5 moves only Raz
  El Hanout (out of the band) and the Algerian turmeric (to unresolved). All 32 hold for
  any edge above 1.832. Worst-case two-significant-figure rounding changes nothing. The
  coriander pairs stay unresolved at every edge. Together with the stress test, three
  fragile pairs stand out as the first Cr(VI) test candidates.

## The Cr(VI) speciation gate (cr_baseline 0.2.0)

- [Pre-registration: cr_baseline 0.2.0 — a Cr(VI) speciation flag](cr-baseline-0.2.0-prereg.md) —
  written before the code: a positive hexavalent-chromium test upgrades a chromate-like
  pair to "Cr(VI)-confirmed"; a negative test is treated as non-exculpatory.
- [cr_baseline 0.2.0: result of the pre-registered Cr(VI) speciation gate](cr-baseline-0.2.0-result.md) —
  34 chromate-like NYC pairs, 32 robust, 2 (both coriander) unresolved. No NYC pair
  carries a Cr(VI) result, so the counts are unchanged from 0.1.0, exactly as predicted;
  the gate fires on the Lopez worked example, which has a confirmed Cr(VI) reading.

## How far a pocket screen could reach

- [Eastern India's market turmeric: how much could a lead chromate screen see?](forsyth2026-raman-reach.md) —
  in the 503-sample Forsyth 2026 market survey, of the 153 turmerics with Pb ≥ 10 µg/g a
  0.1 %-mass screen would catch 103 (67 %) versus 16 (10.5 %) at bench Raman's 0.5 %;
  median laced lead was 1,287 µg/g. Honest limits: no chromium column in that table, and
  the contamination is heavy-tailed, so the reach estimate is lead-only.
- [Pre-registration: where do high-lead spices turn up? (sampling_frame 0.1.0)](sampling-frame-0.1.0-prereg.md) —
  written before the NYC split was computed: five predictions on how much more often a
  spice from a lead-poisoning case investigation is at or above 2 ppm lead than one from
  a store survey. Uses NYC's and King County's open lab tables. King County was seen
  first and is stated as a check: 0 of 197 community-event spice/food results reached
  2 ppm, against 5 of 57 case-investigation results (up to 2,800 ppm, homemade turmeric).
- [sampling_frame 0.1.0: result](sampling-frame-0.1.0-result.md) — 3 of 5 met. NYC
  case-investigation spices were ≥ 2 ppm in 14.4% of 2,790 results vs 8.6% of 477
  store-survey results (1.7×, Fisher p = 0.00038); the predicted 2× gap and 20–50% case
  share both failed. King County reproduced exactly. A descriptive follow-up
  (`frame_period.py`, not pre-registered) finds the gap depends on the threshold: within
  2016–2025 it is 1.4× at 2 ppm but 10.9× at 50 ppm, and 171 of 219 results ≥ 50 ppm came
  from case investigations versus 2 (one product) from store surveys.
- [Pre-registration: is the home-versus-shelf gap an abroad-versus-here gap? (purchase-place 0.1.0)](purchase-place-0.1.0-prereg.md) —
  written before any split by purchase country: five predictions on whether a
  case-investigation spice bought in the US looks like a store-survey spice.
- [purchase-place 0.1.0: result](purchase-place-0.1.0-result.md) — 4 of 5 met. In
  2016–2025, case-investigation spices bought in the US were ≥ 2 ppm in 5.8% of 771
  results, no more often than store-survey spices (8.3%). Spices bought abroad were
  19.7% ≥ 2 ppm and 8.8% ≥ 50 ppm (the predicted ≥ 10% failed), 20× the store rate.
  The home-versus-shelf gap is mostly a where-it-was-bought gap. Spices bought in
  Georgia (the country) supply half of the abroad results ≥ 50 ppm.
- [Pre-registration: did lead in spices bought in Georgia fall after 2020? (georgia-trend 0.1.0)](georgia-trend-0.1.0-prereg.md) —
  written before any split by year: five predictions on whether Georgia-bought case
  results reach 50 ppm less often in 2021–2025 than in 2016–2020, with Bangladesh as a control.

See the main [README](../README.md) for the FDA-recall, NYC-lab and detection-limit
analyses that frame these notes.
