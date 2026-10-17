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
- [Pre-registration: does the Pb:Cr chromate screen stay quiet on spices a regulator called clean? (cfia-chromate-2018 0.1.0)](cfia-chromate-2018-0.1.0-prereg.md) —
  written before any value in CFIA's open 2018-19 lead-chromate survey file (131 retail
  spices, lead, total chromium and a chromate spot test each; none adulterated per CFIA)
  was read: five predictions that at most 5% of these clean spices exceed the published
  natural-chromium ceilings, at most 2 exceed 8.59 ppm chromium, none falls in the
  0.7-2.0 molar band even without the 18 ppm lead floor, the screen flags none (a sanity
  check, since CFIA's headline was seen), and fewer than 8.3% reach 2 ppm lead. The first
  test of the ceiling table against a labelled clean set. Grading code
  `cfia_chromate_2018.py` is committed with it.

## The Cr(VI) speciation gate (cr_baseline 0.2.0)

- [Pre-registration: cr_baseline 0.2.0 — a Cr(VI) speciation flag](cr-baseline-0.2.0-prereg.md) —
  written before the code: a positive hexavalent-chromium test upgrades a chromate-like
  pair to "Cr(VI)-confirmed"; a negative test is treated as non-exculpatory.
- [cr_baseline 0.2.0: result of the pre-registered Cr(VI) speciation gate](cr-baseline-0.2.0-result.md) —
  34 chromate-like NYC pairs, 32 robust, 2 (both coriander) unresolved. No NYC pair
  carries a Cr(VI) result, so the counts are unchanged from 0.1.0, exactly as predicted;
  the gate fires on the Lopez worked example, which has a confirmed Cr(VI) reading.
- [Which chromate-like spices to confirm first: three Cr(VI) speciation candidates](speciation-candidates-0.1.0.md) —
  a practitioner sheet. Of the 32 robust pairs, the three with k = edge / highest
  natural-chromium ceiling below 5 are the only ones a five-fold ceiling error could
  overturn: Algerian turmeric (k 1.25), a Bangladeshi spice mix (k 1.94) and Algerian Raz
  El Hanout (k 3.95). These are the least certain pairs, not the most contaminated. The
  sheet lists their lab values and the confirmation assays to use (sodium rhodizonate for
  lead, diphenylcarbazide for Cr(VI), Raman near 840 cm⁻¹).

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
- [georgia-trend 0.1.0: result](georgia-trend-0.1.0-result.md) — 4 of 5 met; the control
  failed. Georgia-bought case results ≥ 50 ppm went from 49 of 141 (2016–2020) to 0 of 16
  (2021–2025), Fisher p ≈ 0.003. The fall survives a crude one-date-one-visit
  correction (30 of 44 dates vs 0 of 4, p ≈ 0.016). But Bangladesh-bought (7.5% → 1.9%),
  other abroad (6.9% → 2.4%) and US-bought (9 → 0) results fell too, and Bangladesh had
  its own 2019 enforcement campaign. NYC's open table alone cannot credit the fall to
  Georgia.
- [purchase-recording 0.1.0: since 2023, most records lack a purchase country](purchase-recording-0.1.0.md) —
  a descriptive check (not pre-registered). Purchase country is missing for 4.8% of case
  results in 2016–2020 but 38.9% in 2021–2025 (59.7% in 2023), and for 9 of the 18 gross
  (≥ 50 ppm) results since 2021 against 1 of 99 before. The citywide fall (8.5% → 1.4%
  ≥ 50 ppm) and the abroad fall survive any assignment of the missing countries.
  Georgia's per-result share fall (georgia-trend P1–P3) does not: as a count, Georgia
  gross results fell from 49 to between 0 and 9.

## For practitioners

- [On a home visit, ask where each spice was bought](ask-where-bought.md) — a one-page
  CC BY summary of the purchase-place, georgia-trend and purchase-recording results for
  lead-program staff: gross lead comes from spices bought abroad, low-level lead persists
  in US-bought spices, and the purchase field is going unrecorded.
- [Which chromate-like spices to confirm first](speciation-candidates-0.1.0.md) — the
  three Cr(VI) speciation candidates listed above, written for a lab or health department.

## A second source: FDA's border list

- [Pre-registration: did FDA's border listings for lead in spices fall after 2020? (ia9942-lead-spice 0.1.0)](ia9942-lead-spice-0.1.0-prereg.md) —
  written before any FDA Import Alert 99-42 Red List entry was counted: five predictions
  that FDA's lead-in-spice firm listings did **not** fall after 2020 (driven by
  cinnamon), and that Georgia, NYC's largest source of gross contamination, has no
  2016–2020 listing. The grading code `ia9942_lead_spice.py` is committed with it.
- [Deviation note: parser fix, and lead in spices lived on Import Alert 28-13 (ia9942-lead-spice 0.1.1)](ia9942-lead-spice-0.1.1-deviation.md) —
  written before any lead-spice firm was counted. The first job's parser left every
  Problems field empty, because the page prints the value on the next line. Separately, the
  December 2021 copy of 99-42 says lead in spices then fell under Import Alert 28-13, so
  the registered early count is zero by construction. The headline grade will add the
  2021 copy of 28-13. The registered grade is reported but flagged invalid.
  Anyone trending lead-in-spice listings from 99-42 alone will see an artificial jump.
- [ia9942-lead-spice 0.1.1: result](ia9942-lead-spice-0.1.1-result.md) — 2 of 5 met.
  Contrary to the prediction, the border record **fell** too: lead-spice firms went from
  19 (2016–2020, on the 2021 copy of 28-13) to 14 (2021–2025, on the current 99-42 page),
  12 after a robustness cut — P1 and P2 failed. But the border list is still blind to
  Georgia, NYC's largest gross-contamination source (P5 held, 0 Georgia firms in the early
  period), and cinnamon/cassia — not turmeric — dominates the listings in both periods
  (P3 held, P4 failed: cinnamon tops both). The reusable finding is that the listings
  moved from Import Alert 28-13 into 99-42 around October 2022, so a trend from 99-42
  alone shows an artificial jump. Recomputed from a committed firm table by a pinned test.

## A third source: Canada's spice authenticity surveillance

- [Pre-registration: lead chromate, dyes and fillers in Canada's spice surveillance (cfia-spice-auth 0.1.0)](cfia-spice-auth-0.1.0-prereg.md) —
  written before any assessment or note in CFIA's three open per-sample files (2020–2023)
  was read: five predictions that lead chromate still turns up but in at most 3% of
  samples, that fillers outnumber it among failures, and that it sits mostly in turmeric
  or ginger declared from South Asia. The grading code `cfia_spice_auth.py` is committed
  with it.

## The screen's second target: Sudan dyes

- [Pre-registration: where does Sudan-dyed red palm oil on Canadian shelves come from? (red-palm-dyes 0.1.0)](red-palm-dyes-0.1.0-prereg.md) —
  written before any amount in CFIA's open 2019-20 red palm oil colour file was read: six
  predictions that Sudan dyes turn up in at most 10% of imported retail samples (FDA Ghana
  measured 26.6% in its own 2019 market), only in oil declared from West or Central Africa
  or of unknown origin, mostly as Sudan IV and most often from Ghana, and that no other
  non-permitted colour appears. A destination-country check of a producing country's own
  surveillance, as georgia-trend was for spices. Grading code `red_palm_dyes.py` is
  committed with it.
- [red-palm-dyes 0.1.0: result (provisional)](red-palm-dyes-0.1.0-result.md) — 5 of 6 met.
  Two of 104 imported retail samples (2019–2021) carried a Sudan dye, both Sudan IV (47.5
  and 15.6 ppm), both declared from **Nigeria**. All 73 Malaysian and South American oils
  were clean, and no other non-permitted colour appeared. The Ghana prediction (P5)
  failed: 0 of 14 Ghana-declared samples were dyed (0 of 10 in 2019-20; if the dyed share
  were Ghana's 2019 market rate of 26.6%, that has about a 4.5% chance). Different sampling
  frames, small counts. Graded by the registered code on a committed transcription of both
  files, which CFIA's own headlines match. The sealed download run will confirm it later.

See the main [README](../README.md) for the FDA-recall, NYC-lab and detection-limit
analyses that frame these notes.
