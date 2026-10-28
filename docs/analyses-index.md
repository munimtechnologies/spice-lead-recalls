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
- [cfia-chromate-2018 0.1.0: result](cfia-chromate-2018-0.1.0-result.md) — 4 of 5 met.
  On 131 retail spices CFIA cleared, the published screen (lead ≥ 18 ppm *and* the molar
  band) flags **none**, agreeing exactly with CFIA, and the natural-Cr ceilings are quiet
  (1 of 81 over a ceiling; 1 over 8.59 ppm Cr). P3 failed, and that is the point: drop the
  lead floor and **21** clean samples fall in the molar band, each with lead under 5 ppm
  and a negative spot test — the lead floor is what makes the screen specific. The one
  over-ceiling sample (Indian cumin, Cr 16.9 ppm, positive spot test) carries only 0.52
  ppm lead, so it is not the lead-chromate signature. A low-level lead tail remains (6 of
  131 ≥ 2 ppm; top: thyme 6.57, a domestic Canadian blend 4.47). Computed by a sealed run.

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
- [Reading CFIA's mycotoxin detection rates: the reporting limit decides the number](reading-cfia-detection-rates-0.1.0.md) —
  a one-page CC BY note for anyone comparing "percent detected" across CFIA surveys. Five
  cases from CFIA's own files (infant-cereal DON 123 vs 13 under two limits; OTA odds ratio
  26.0 → 2.09 and DON 6.44 → 1.28 at a common cut; feed detection jumps that coincide with
  limit changes; a non-detect written as the bare limit) and a seven-point checklist: find
  each limit, re-cut at the higher one, compare within product labels, give an interval,
  check non-detect coding, check which mean an average is, and look for limit changes before
  reading a trend.

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
- [cfia-spice-auth 0.1.0: result](cfia-spice-auth-0.1.0-result.md) — 2 of 3 gradable met,
  computed by a sealed compute run (it supersedes an earlier provisional transcription).
  No note in 823 samples names lead or chromate (P1 failed; P4 and P5 not gradable), and
  allergen-protein "filler" notes — peanut in cumin, gluten in pepper and coriander, up to
  19,000 ppm gluten in a Vietnamese white pepper — outnumber it among the 57 failures
  (53 to 0). Five samples drew an undeclared-colour failure: four turmerics (declared from
  the United States ×2, Iran and Madagascar) and one Iranian cinnamon (Sunset Yellow FCF
  486.8 ppm); none of the colour-failed turmerics was declared from South Asia. Because
  CFIA tests a turmeric "for colours" by both dye HPLC and metals ICP-MS, the open note
  cannot separate a banned dye from lead chromate — the gap a point-of-use screen closes.
  No sample declares Georgia.

## A different adulterant: coumarin in Canadian retail cinnamon

- [Pre-registration: is Canadian retail cinnamon mostly cassia? (coumarin-cinnamon 0.1.0)](coumarin-cinnamon-0.1.0-prereg.md) —
  written before any CFIA coumarin value was read: predictions that most cinnamon sold at
  Canadian retail is cassia-type (high-coumarin) rather than verum/Ceylon, inferred from
  coumarin content in CFIA's open 2011–2016 coumarin survey files. Grading code
  `coumarin_cinnamon.py` is committed with it.
- [coumarin-cinnamon 0.1.0: Canadian retail cinnamon is almost all cassia](coumarin-cinnamon-0.1.0-result.md) —
  4 of 4 gradable predictions met (5 not gradable). Of 176 CFIA retail samples (2011–2016),
  168 (95.5%) sit at cassia coumarin levels (1,268–7,816 ppm) and only 5 look like true
  Ceylon cinnamon; the pooled maximum is 7,816.3 ppm (a 2011–12 Vietnamese ground cinnamon).
  Species is inferred from coumarin, not DNA, so borderline samples are left "intermediate".
- [Pre-registration: how small a serving of Canadian cinnamon reaches the coumarin TDI? (coumarin-tdi 0.1.0)](coumarin-tdi-0.1.0-prereg.md) —
  written before any row was graded (public at tag `v0.4.35` first): four predictions on the
  per-sample serving of cinnamon that reaches EFSA's tolerable daily intake (TDI) for coumarin,
  reusing the `coumarin_cinnamon.py` loader pinned at `v0.4.34`.
- [coumarin-tdi 0.1.0: a teaspoon of most Canadian retail cinnamon exceeds the coumarin TDI](coumarin-tdi-0.1.0-result.md) —
  4 of 4 met. Across the same 176 samples, the median sample reaches a 60 kg adult's TDI
  (6 mg/day) in 1.80 g of cinnamon and a 15 kg child's (1.5 mg/day) in 0.45 g; one level
  teaspoon (2.6 g) puts an adult over the TDI for 88% of samples (155 of 176) and a child
  over for 97% (170 of 176). The figures agree with BfR's illustrative 2 g adult / 0.5 g
  child at an assumed 3000 mg/kg; the novelty is the open per-sample Canadian table
  (`data/coumarin_tdi_samples.csv`). An information/research note, not individual dietary advice.
- [Pre-registration: Canadian cinnamon-containing foods against the EU's coumarin maximum levels (coumarin-eu-limits 0.1.0)](coumarin-eu-limits-0.1.0-prereg.md) —
  written before any value in CFIA's 2013-14 survey of cinnamon-containing foods (749
  samples) was read: a parse gate tied to CFIA's published 2,510 mg/kg maximum, and three
  predictions on how often bakery products and breakfast cereals exceed the EU's 15 and
  20 mg/kg levels.
- [Amendment: the parse gate caught a unit bug (coumarin-eu-limits 0.1.1)](coumarin-eu-limits-0.1.1-amendment.md) —
  the 0.1.0 grader read CFIA's µg/g (= mg/kg) as µg/kg and divided every value by 1000; the
  gate failed as designed. 0.1.1 converts units by an explicit table and reports a unit
  census, with every threshold unchanged. Because the 0.1.0 output exposed the values, the
  amendment states the implied outcome before the re-grade ran, so the re-grade is a check,
  not a blind test.
- [coumarin-eu-limits 0.1.1: result](coumarin-eu-limits-0.1.1-result.md) — 3 of 4 met
  (gate passed; the cereal prediction failed). 42 of 100 bakery samples exceed the EU's
  15 mg/kg fine-bakery level, almost all in CFIA's "Baked Goods" category (39 of 68), against
  2 of 31 cookies; even against the 50 mg/kg seasonal-bakery row, 11 of 100 exceed. Only 3 of
  136 breakfast cereals exceed 20 mg/kg (none of 65 children's cereals), plus 3 of 12
  flavoured oatmeals. A reference comparison (Canada sets no coumarin limit), recomputed
  from `data/coumarin-eu-limits.csv` and the sealed per-sample table by a pinned test.
- [Pre-registration: how much of the coumarin TDI do infant cereals give? (coumarin-infant 0.1.0)](coumarin-infant-0.1.0-prereg.md) —
  written before any infant-cereal value was read (public at tag `v0.4.41` first): a parse
  gate and four predictions on how much of EFSA's coumarin TDI the 52 cinnamon-containing
  infant cereals in CFIA's 2013-14 survey would give an 8 kg infant eating them daily, with
  the children's-cereal median as the direction comparator. Grading reuses the
  `coumarin_eu_limits.py` parser, checked against the published copy inside the sealed job.
- [coumarin-infant 0.1.0: result](coumarin-infant-0.1.0-result.md) — 5 of 5 met, a
  genuinely blind pre-registered test. The 52 infant cereals carry little coumarin (median
  1.25 mg/kg, max 18.3, detected in 51 of 52): for an 8 kg infant eating one 30 g dry
  serving a day, none reach the coumarin TDI (the highest sample reaches 69% of it), and
  only at a doubled 60 g/day serving do 2 of 52 cross it. Infant cereals sit below the
  children's breakfast cereals (median 3.4). CFIA's own report for this survey gives only
  survey-wide figures and does not break out infant cereals; this is, as far as we found,
  the first open per-sample screen of commercial infant cereals against the coumarin TDI.
  Recomputed from `data/coumarin_infant_samples.csv`, `data/coumarin-infant.csv` and the
  published children's-cereal rows by a pinned test.
- [Pre-registration: how much of the coumarin TDI could a cup of cinnamon tea give? (coumarin-tea 0.1.0)](coumarin-tea-0.1.0-prereg.md) —
  written before any per-sample tea value was read: a parse gate tied to CFIA's published
  tea headline (115 samples, max 2,430, avg 500 mg/kg, 99% detected) and four predictions
  on how much of EFSA's coumarin TDI a single brewed cup of the 115 cinnamon-containing
  teas in CFIA's 2013-14 survey could deliver, under a 100% leaf-to-cup transfer upper
  bound (2 g and 4 g dry per cup, 60 kg adult and 15 kg child). A names-only census first
  confirmed the bucket is five genuine dried teas (Herbal, Black, Green, Other, White).
  Grading reuses the `coumarin_eu_limits.py` parser, checked against the published copy
  inside the sealed job.
- [coumarin-tea 0.1.0: result](coumarin-tea-0.1.0-result.md) — 5 of 5 met. The 115
  cinnamon-containing teas in CFIA's 2013-14 survey carry a wide coumarin range (median
  240, mean 496, max 2,430 mg/kg, detected in 114 of 115). Screened per brewed cup at a
  100% leaf-to-cup transfer ceiling: a 60 kg adult's standard 2 g cup puts **none** of
  the 115 over the whole-day coumarin TDI (the top tea reaches 81% of it), a strong 4 g
  adult cup puts 7 over (6.1%), a 15 kg child's 2 g cup 33 (28.7%) and a child's 4 g cup
  45 (39.1%). CFIA's report gives a tea-category headline but no per-cup exposure; this is
  the first open, per-sample, reproducible per-cup screen of commercial cinnamon teas
  against the coumarin TDI, with an explicit transfer upper bound. A reference screen, not
  a compliance finding (Canada sets no coumarin limit). Recomputed from
  `data/coumarin_tea_samples.csv`, `data/coumarin-tea.csv` and the published 749-row table
  by a pinned test. A sealed job later fetched the published files from GitHub and re-ran
  that test on them: 12 of 12 passed (job `coumarin-tea-result-v1`, 2026-10-24).
- [Pre-registration: does the per-cup tea screen replicate in CFIA's 2014-15 and 2015-16 surveys? (coumarin-tea-replication 0.1.0)](coumarin-tea-replication-0.1.0-prereg.md) —
  written before any 2014-15 or 2015-16 tea value was read: the same per-cup scenarios and
  published code applied to 507 new teas (210 from 2014-15, 297 from 2015-16, a survey that
  also targeted licorice-flavoured teas). A parse gate is tied to CFIA's published tea
  headlines (max 1,920 and 2,230 mg/kg, detected 178 and 245) and to a names-only census of
  six tea types. Ten predictions; the primary one says a child's 2 g cup crosses the TDI
  less often in each later survey than 2013-14's 28.7%. Also a pooled three-survey per-cup
  table (622 teas) and per-type tables.
- [Amendment: the gate caught a mislabelled CFIA average (coumarin-tea-replication 0.1.1)](coumarin-tea-replication-0.1.1-amendment.md) —
  the sealed 0.1.0 job failed its gate on 1 of 14 checks, so P1–P10 were not graded. CFIA's
  2014-15 report prints the tea average as 302 under a note saying only positive results
  were used. In CFIA's own file the positives mean is 356.2, while the mean of all 210 teas
  (non-detects as 0) is 301.9. Every count, the unit census, the maximum and the 2013-14
  reproduction matched exactly. 0.1.1 changes only that one check. Because the 0.1.0
  output had already shown every value, the re-grade is a verification, not a blind test.
- [coumarin-tea-replication 0.1.1: result](coumarin-tea-replication-0.1.1-result.md) —
  10 of 10 met, labelled a verification (not blind). The per-cup screen replicates in 507
  new teas: across all three surveys (622 teas) no standard 2 g cup puts a 60 kg adult over
  the coumarin TDI even at 100% transfer, and a 15 kg child's 2 g cup crosses it less often
  in 2014-15 (13.3%) and 2015-16 (13.8%) than in 2013-14 (28.7%). Herbal teas carry the
  exceedances: 90 of the 102 pooled child standard-cup exceedances, 41.3% of 218 herbal
  teas against 3.0% of 404 others. Recomputed from
  `data/coumarin_tea_replication_samples.csv` and `data/coumarin_tea_replication_by_type.csv`
  by a pinned test. A sealed job later fetched the published files from GitHub and re-ran
  that test on them: 15 of 15 passed (job `coumarin-audit-result-v1`, 2026-10-24).
- [Pre-registration: do CFIA's coumarin summary tables match its open files? (coumarin-cfia-table-audit 0.1.0)](coumarin-cfia-table-audit-0.1.0-prereg.md) —
  written before any non-tea value in the 2014-15 or 2015-16 file was read: every Table 2
  row of both reports is rebuilt from the open files, and the audit asks whether each
  printed average is the footnoted positives-only mean or the all-sample mean. CFIA's own
  printed figures predict all-sample means throughout 2014-15 (its grand total of 149 is
  only reproduced that way: 148.9 against 186.5) and positives means throughout 2015-16
  (391.8, printed as 392). Eight graded verdicts, with a gate on the label mapping, row
  sizes and units.
- [coumarin-cfia-table-audit 0.1.0: result](coumarin-cfia-table-audit-0.1.0-result.md) —
  gate and 8 of 8 verdicts met. Every average in CFIA's 2014-15 coumarin Table 2 is an
  all-sample mean (non-detects as 0), although the table note says only positive results
  were used; the 2015-16 table follows its note. Every count, minimum and maximum matches.
  The gap is largest for 2014-15 oils and extracts: printed 46.2 ppm against a
  positives-only mean of 240.2. CFIA's 2016-2018 report reprints the 2014 tea (302) and
  spice-mix (329) averages under a positives-only note; like for like they are 356 and 385.
  Aggregate figures only, in `data/coumarin_cfia_table_audit.csv`, checked by a pinned test.
  Not a finding about any product or health risk. A sealed job later fetched the published
  files from GitHub and re-ran that test on them: 13 of 13 passed (job
  `coumarin-audit-result-v1`, 2026-10-24).
- [Pre-registration: CFIA's first two coumarin surveys beyond their cinnamon (coumarin-early-surveys 0.1.0)](coumarin-early-surveys-0.1.0-prereg.md) —
  written before any of the 139 non-cinnamon samples in CFIA's open 2011-12 and 2012-13
  files was read (tea, spice mixes, breakfast cereals, baked goods, baking mixes and baby
  food; the full reports are available only on request). A gate on SHA-256, a names-only
  label census and the already-published cinnamon values; three consistency checks against
  every figure CFIA printed for these surveys; three verdicts on which mean the averages
  reprinted in later reports' Table 3 equal (2011-12 tea 380 and spice mix 352: positives;
  2012-13 spice mix 568: both); and five blind replications of the EU-limit, per-cup tea
  and infant screens. Grading code `coumarin_early_surveys.py` is committed with it. CFIA's
  2016-2018 coumarin survey (1,497 samples) has no per-sample file on the Open Government
  Portal (checked 2026-10-24), so the five 2011-2016 files are the whole open record.
- [coumarin-early-surveys 0.1.0: result](coumarin-early-surveys-0.1.0-result.md) — gate
  passed, 8 of 12 met (7 of 11 predictions). All five blind replications held: 4 of 20
  baked goods over the EU's 15 mg/kg level and 2 over 50; 1 of 15 cereals over 20; a
  child's 2 g cup crosses the coumarin TDI for 2 of 11 teas and no adult 2 g cup does (now
  true across 633 teas in four surveys); baby food (median 5.2) sits below cereals (6.6).
  CFIA's six printed category maxima match at printed precision. C2, C3, V1 and V2 failed, all for one
  reason found after grading: the open 2011-12 file writes its four non-detects as the bare
  number `0.29` (the detection limit), so a naive reader counts 193 of 193 detected where
  CFIA says 98% (189). Read that way, the reprinted 2011-12 tea (380) and spice-mix (352)
  averages are all-sample means under a positives-only note (positives: 418 and 367), as in
  2014-15; the registered "positives" predictions fail either way. Recomputed from
  `data/coumarin_early_samples.csv` and `data/coumarin_early_surveys.csv` by a pinned test.
  A sealed job later fetched the published files from GitHub and re-ran that test on them:
  15 of 15 passed (job `coumarin-early-result-v1`, 2026-10-24).

## A mycotoxin: ochratoxin A in Canadian retail foods

- [Pre-registration: which declared origins carry the Canadian retail spices that would fail the EU's ochratoxin A limits? (ota-spices 0.1.0)](ota-spices-0.1.0-prereg.md) —
  written before any row of CFIA's open 2012–2022 ochratoxin A file (8,384 retail foods,
  released 2026-10-06) was read: eight predictions on the 778 spices against the EU's
  20 µg/kg (Capsicum) and 15 µg/kg (other spices and mixtures) levels, by declared origin.
- [ota-spices 0.1.0: result](ota-spices-0.1.0-result.md) — the registered gate failed (the
  keyword rule counted 1,024 "spices", catching baking mixes and fresh peppers), so formally
  nothing is graded. Under CFIA's own `Spice - …` labels (714 samples, chosen after seeing
  the data, exploratory), 6 of 8 hold: 106 spices (14.8%) exceed the EU level, led by
  paprika (53 of 122) and nutmeg (33 of 96); all four Hungarian paprikas exceed it,
  including the 1,770 ppb survey maximum; 67% of spices declare no country.
- [Pre-registration: ochratoxin A in Canada's retail foods beyond spices (ota-foods 0.1.0)](ota-foods-0.1.0-prereg.md) —
  written before any of the 7,606 non-spice samples in the same file was read (cereals and
  infant cereals, coffee, cocoa, dried fruit, licorice, nuts, seeds, pulses, soy, infant
  formula). A gate on SHA-256, label-derived category sizes and the published spice
  maximum; six consistency checks against CFIA's Tables 2 and 5 and Health Canada's
  proposed levels (CFIA: 119 grain-based foods over); two verdicts on which mean the printed
  averages are; and twelve blind predictions. P1 says the file follows CFIA's Table 8 for
  infant formula (about 60 detected, maximum 0.89 ppb), not Table 2 (13 detected, maximum
  11), and P3–P12 count samples over the EU maximum levels in force since 2023 (infant
  cereals 0.5, roasted coffee 3, cocoa powder 3, bakery 2 ppb and others), which CFIA's
  report does not use. Grading code `ota_foods.py` is committed with it.
- [ota-foods 0.1.0: result](ota-foods-0.1.0-result.md) — gate passed (blind), 20 of 21
  met; C5 the only miss. The headline is a confirmed CFIA report error: Table 2 prints
  infant formula as 13 positives, maximum 11 ppb, average 1.1, but the open file holds 60
  of 192 detected and a maximum of 0.886 ppb — matching the same report's Table 8 and
  Appendix B to the digit (2012: 148 samples, 52 detected = 35%, max 0.89; 2014: 44, 8 =
  18%, max 0.46; no dairy formula detected). For ochratoxin A the Table 2 averages really
  are positives-only means (V1, V2 held), unlike the coumarin tables under the same note.
  All twelve blind predictions held: counting against the EU levels in force since 2023,
  158 of 4,851 samples exceed their level, most of them infant cereals (95 of 409 over
  0.5 ppb, at a modest 4.85 ppb maximum). C5 failed and is reported honestly: the file
  flags 125 grain-based foods over Health Canada's proposed levels (126 at or above) where
  CFIA printed 119; reclassifying the twelve label-ambiguous pulse samples removes only
  one (a 2017 `Flour - Other` at 3.34 ppb). Non-detects in this file are a literal 0 (no
  `<`, no token), so the detection-limit trap that caught the 2011-12 coumarin file does
  not arise. Recomputed from `data/ota_foods_samples.csv`, `data/ota_foods_categories.csv`
  and `data/ota_foods_eu.csv` by a pinned test. A reference comparison, not a compliance
  finding (Canada has no OTA maximum level for these foods).

## A second mycotoxin: deoxynivalenol (DON) in infant cereals

- [CFIA's 2018-19 DON in infant cereals report: what its own tables say (don-infant-report-check 0.1.0)](don-infant-report-check-0.1.0.md) —
  a record of the report alone (PDF SHA-256 pinned), written before any value in CFIA's
  open per-sample file for the survey (released 2026-10-06) was read. The report disagrees
  with itself: Table 2, the text and the summary give 13 of 288 samples with DON (all at or
  above the 20 ppb reporting limit the methods impose), while Table 3 gives 123 for the same
  samples with minima of 0.60–1.3 ppb; the multigrain maximum is 150 ppb in Table 2 but 110
  in Table 3; the lowest positive is 44.1 (text), 22 (Table 2) or 25 ppb (Table 4); and
  barley is "100%" positive in the discussion, 6 of 7 in the tables and "mostly not
  detected" in the results text. The open file can settle which reading CFIA published
  as data; the pre-registered check (myco-don 0.1.0) follows. Not a finding about any
  product or health risk.
- [Pre-registration: deoxynivalenol in CFIA's open infant-cereal and selected-foods files (myco-don 0.1.0)](myco-don-0.1.0-prereg.md) —
  written before any DON or ochratoxin A value in CFIA's three open files (the 2018-19
  infant-cereal survey, 2011-12 DON in selected foods, and 2010-11 OTA-and-DON in selected
  foods, all released 2026-10-06) was read by the grader; a names-only census read the
  labels, counts and result format only. Twelve blind predictions plus a gate: whether the
  2018-19 file follows Table 3's 123 positives or Table 2's 13 (the difference is the
  imposed 20 ppb reporting limit), with exactly 13 at or above 20 ppb; that the lowest value
  at or above 20 ppb is 22, not the text's 44.1; the figures CFIA printed on the 2010-11 and
  2011-12 summary pages (DON detected 555 of 943 and OTA 315 of 943, ranges, no DON in wine
  or dried fruit, 8 grain-based samples over Health Canada's proposed OTA levels); and the
  first per-sample ochratoxin A × deoxynivalenol co-occurrence table from CFIA's open retail
  data (943 samples), predicted to show no strong within-sample association (odds ratio
  0.5–2.0). The census already shows the 2018-19 file carries 286 samples where the report
  says 288, and the 2011-12 file 1395 where the summary says 1,391; grain-level checks are
  not gradable because every infant-cereal sample carries the single label
  "Infant Food - Cereal". Grading code `myco_don.py` is committed with it. Not a finding
  about any product or health risk.
- [myco-don 0.1.0: result](myco-don-0.1.0-result.md) — gate passed, 12 of 13 met (11 of 12
  blind predictions). The open file settles the 2018-19 report's self-contradiction: 119 of
  286 infant-cereal samples carry detected DON and exactly 13 reach the 20 ppb reporting
  limit, so Table 2's 13 counts results ≥ 20 ppb while Table 3's 123 counts down to the
  0.2 ppb LOD — the same data under two reporting limits. A confirmed report error: the
  results text's stated minimum of 44.1 ppb is contradicted by the file's smallest ≥ 20 ppb
  value of 22.3 (Table 2 prints 22). Every CFIA 2010-11 and 2011-12 summary figure
  reproduces (DON detected 555 of 943, OTA 315 of 943, the ranges, no DON in wine or dried
  fruit, 8 grain-based over Health Canada's proposed OTA levels, 5 of them infant cereals).
  The one miss is the study's point: within a sample, OTA and DON detection are **not**
  independent (P11 registered an odds ratio in [0.5, 2.0]); the 943-sample 2×2 gives OR 8.54,
  Fisher exact p = 1.4×10⁻³⁹ — the first per-sample OTA × DON co-occurrence table from CFIA's
  open retail data, with the honest caveat that much of the signal is commodity composition
  (grain foods carry both toxins, wine and dried fruit neither). Recomputed from
  `data/myco_don_2010_samples.csv` and `data/myco_don_cooccurrence.json` by a pinned test. A
  sealed job later fetched the published files from GitHub and re-ran that test on them: 17 of
  17 passed (job `myco-don-result-v1`, 2026-10-25). Not a finding about any product or health risk.

## A feed mycotoxin monitoring program: CFIA livestock feeds 2000-2018

- [Pre-registration: CFIA's open livestock-feed mycotoxin file against its own report (feed-myco 0.1.0)](feed-myco-0.1.0-prereg.md) —
  written before any result in CFIA's open per-sample file from its Mycotoxin Monitoring
  Program for Livestock Feeds (April 2000 – March 2018; 40,862 results on 3,258 samples, 17
  analytes) was read; a names-only census read labels, counts and result format only. A gate
  on census facts, seven consistency checks against every 2000-2018 cell of Table 1 of CFIA's
  Program-15B report, a registered explanation of the one size gap (HT-2: 3,202 samples in
  the report, 3,243 rows in the file), and thirteen blind predictions on Fusarium toxin
  co-occurrence, an OTA × DON replication of myco-don in feed, a 3-acetyl-DON vs
  15-acetyl-DON chemotype-proxy split, fumonisins in corn and censoring-limit drift. From the
  report alone: the file holds its last 18 of 28 years, and its text quotes Table 1's DON
  figure as 81.3% where the table prints 82.22%.
- [feed-myco 0.1.0: result](feed-myco-0.1.0-result.md) — gate passed, 17 of 21 met (all 7
  consistency checks, 9 of 13 blind predictions). Every 2000-2018 cell of the report's Table
  1 rebuilds from the open file once two things are known: the 41 extra HT-2 rows are, year
  by year and exactly, non-detects with a 0.5 ppm quantification limit (above the 0.1 ppm
  action level, so indeterminate), which the report leaves out without saying so (the
  registered mechanism, C5); and one fumonisin row with a blank fiscal year belongs to
  2016-17, where it restores the printed 164 samples and 98.17%. The OTA × DON association
  found in retail foods does **not** replicate in feed. It reverses (OR 0.70, p 0.030; P5
  missed), which supports reading the retail OR of 8.54 as commodity composition. The 3-ADON
  share of acetyl-DON-positive samples is 38.9% in western provinces against 16.6% in the
  east (p 0.0024), with no change between the two nine-year periods. Also missed: DON detected in
  75.9% (band 35–75%), fumonisins 2.3× (not 3×) as often in corn, and no fall in the modal
  DON limit. Exploratory: the file's sharpest detection-rate changes (T-2 1.9% → 25.5% and
  HT-2 4.4% → 34.5% in 2014-15; OTA 7.0% → 2.4%; fumonisins 44.6% → 8.6% in 2016-17) fall in
  the same years as changes in the quantification limit, so they are method changes, not
  feed-supply trends. Recomputed from `data/feed_myco_table1.csv`,
  `data/feed_myco_samples.csv`, `data/feed_myco_limits.csv` and the sealed record by a
  pinned test. A sealed job later fetched the published files from GitHub and re-ran that
  test on them: 24 of 24 passed (job `feed-myco-result-v1`, 2026-10-26). A reference
  comparison, not a compliance finding about any feed, mill or farm.

## Is the ochratoxin A × DON co-occurrence a commodity effect?

- [Pre-registration: OTA × DON within commodities (cooc-strata 0.1.0)](cooc-strata-0.1.0-prereg.md) —
  written before any within-commodity table was computed. The two committed per-sample tables
  give opposite pooled answers (retail foods OR 8.54; livestock feeds OR 0.70). Four
  predictions on Mantel-Haenszel odds ratios and CMH tests within CFIA's retail product labels
  and feed ingredient names. Grading code `cooc_strata.py` and offline tests are committed with it.
- [cooc-strata 0.1.0: result](cooc-strata-0.1.0-result.md) — gate passed, 4 of 5 met. Both
  pooled figures are mostly composition. Within retail products the odds ratio falls from 8.54
  to **1.40** (CMH p 0.38; RBG 95% interval 0.72–2.70, computed after grading), so about 84% of
  the pooled log odds ratio lies between products: grain foods carry both toxins, while wine,
  dairy formula and dried fruit carry neither. M2 (a positive within-product association, p <
  0.05) missed. Within feed ingredient names the reversal shrinks from 0.70 to **0.90** (p 0.63;
  0.64–1.28). It is mostly corn against the small grains: corn has DON in 92.4% of samples and
  OTA in 1.0%, against 55–67% DON and 8–13% OTA in barley, wheat and oats. Sensitivity (not
  graded): CFIA's coarser `ingredient_type` keeps the reversal (MH 0.64, p 0.0066), because its
  `Cereals` type mixes corn with small grains. Recomputed from the two committed per-sample tables
  by an independent pinned test. A sealed job later fetched the published files from GitHub and
  re-ran that test on them: 10 of 10 passed (job `cooc-strata-result-v1`, 2026-10-27). Not a
  finding about any product, feed, mill or farm.

## Multi-mycotoxins in grain foods: CFIA 2018-19

- [CFIA's 2018-19 multi-mycotoxin survey: what its report and file labels say (multimyco-2018-report-check 0.1.0)](multimyco-2018-report-check-0.1.0.md) —
  a record of CFIA's report (750 corn products, crackers, other grain products, pasta and
  gluten-free products; 25 analytes per sample) and the names-only census of its open file. It
  was written before any value was read. The text says 388 samples had mycotoxins; Table 2's
  total says 386. The report's origin table is one sample off the file's `Origin` labels. Its
  five product categories (136/102/70/297/145) do not follow the file's 30 product labels
  (obvious grouping: 150/101/71/299/128). Its "17 different mycotoxins detected" holds only if
  the "alpha-/beta-zeranol" it lists as never detected are the file's α-/β-zearalenol rows,
  which the file stores under one garbled label. The report also gives an OTA compliance of 99.1%
  without a count (7 of 750 if the base is all samples). A pre-registered check follows.
- [Pre-registration: CFIA's open 2018-19 multi-mycotoxin file against its own report (multimyco-2018 0.1.0)](multimyco-2018-0.1.0-prereg.md) —
  written before any AMOUNT value was read (public at tag `v0.4.61`): a gate on census facts
  and a clean AMOUNT format, one consistency check and eight blind predictions on 388 vs 386,
  the DON row, the "17 mycotoxins", Table 3's group counts, the uncounted OTA figure, the
  crackers OTA gap, whether DON × fumonisin co-occurrence is a commodity effect, and the most
  toxin groups in one sample. Grading code `multimyco_2018.py` is committed with it.
- [multimyco-2018 0.1.0: result](multimyco-2018-0.1.0-result.md) — gate passed, 4 of 10 met;
  most misses are the finding. The file gives a third answer to "388 or 386": **387**. It
  reproduces Table 3's DON count (306) and maximum (2,570 ppb), but the average of its
  positives is **181 ppb**, not the printed 282. Three group counts are off (fumonisins 106 vs
  105, zearalenone 38 vs 34, aflatoxins 10 vs 11), and the zearalenol label the report lists as
  never detected has a detection, so 18 labels are detected, not 17. The two figures CFIA left
  uncounted hold: exactly 7 of 750 samples carry OTA above the proposed 3 ppb level, and OTA
  is found in only 2 of 101 crackers (75% in CFIA's OTA-only survey the same year). Unlike OTA ×
  DON, the DON × fumonisin association survives stratification by product label (pooled OR
  2.42, Mantel-Haenszel 2.48, CMH p 0.0016; within the corn labels 7.5). Recomputed from
  `data/multimyco_2018_samples.csv` and the sealed record by an independent pinned test. A
  sealed job later fetched the published files from GitHub and re-ran that test on them: 10 of
  10 passed (job `multimyco-2018-result-v1`, 2026-10-27). Not a finding about any product or
  health risk.
- [multimyco-2018 detail 0.1.0: how CFIA built Table 3's group rows, and the aflatoxin result the open file lacks](multimyco-2018-detail-0.1.0.md) —
  exploratory, not pre-registered, worked out from a sealed listing of all 722 positive cells.
  Table 3's multi-analyte rows are per-sample sums: the fumonisin maximum 3,503 = 2,370 + 780 +
  353 in one corn flour, ergot 664 and HT-2/T-2 98 likewise, and the ergot and HT-2/T-2 rows
  reproduce exactly. Under the same rule the file's aflatoxin group is 10 samples, total 18.4
  ppb, maximum 10.0, while Table 3 prints 11 / 30 / 4.4: one result of 29.5–30.5 ppb missing
  from the open file reproduces all three printed figures. The zearalenone (34 / 44) and DON
  (282) gaps stay unexplained. Rebuilt from `data/multimyco_2018_positives.csv` by a pinned
  test; a sealed job later fetched the published files from GitHub and re-ran it: 8 of 8 passed
  (job `multimyco-2018-detail-v1`, 2026-10-28).

## Ochratoxin A in grain foods: CFIA 2018-19, and two CFIA methods compared

- [CFIA's 2018-19 ochratoxin A grain survey: what its two reports and the file's labels say (ota-grain-2018-report-check 0.1.0)](ota-grain-2018-report-check-0.1.0.md) —
  written before any result value in the open file (496 samples) was read. The survey report
  says 495 samples and its Table 2 positives add up to 219; its own Table 5 gives rice 14
  positives where Table 2 gives 13; CFIA's later "Ochratoxin A in Selected Foods" report
  reprints the survey as five 2018 rows that add up to 496 and are exactly the file's product
  labels; Table 4 prints an oat average (2.6 ppb) above its maximum (1.6); and the headline
  "45%" follows from no count. CFIA's same-year multi-mycotoxin survey found OTA in 2 of 101
  crackers where this one found 75%, with a ~20-fold difference in the smallest result.
- [Pre-registration: CFIA's open 2018-19 ochratoxin A grain file against its two reports, and against the multi-mycotoxin survey at a common cut (ota-grain-2018 0.1.0)](ota-grain-2018-0.1.0-prereg.md) —
  public at tag `v0.4.67` before grading: a gate (including a new value rule, because this
  file writes non-detects as text), ten consistency checks against every report row the labels
  identify, and six blind predictions. The new part, P4: on the seven product labels both
  files share, read at the multi-mycotoxin method's 0.8 ppb limit, the two methods' OTA
  detection does not differ (CMH p ≥ 0.05). Grading code `ota_grain_2018.py` is committed with it.
- [ota-grain-2018 0.1.0: result](ota-grain-2018-0.1.0-result.md) — gate passed, 16 of 17 met
  (all ten consistency checks; five of six predictions). The file settles the report's
  contradictions: 496 samples, rice 14 positives, oat average 0.26, and 220 of 496 (44.4%)
  positive, so "45%" comes from no count. On the seven shared labels the OTA-only file detects
  OTA in 82 of 150 samples against the multi-mycotoxin file's 10 of 247 (Mantel-Haenszel OR
  26.0). At a common 0.8 ppb cut the OTA-only file has 15 of 150 and the OR falls to **2.09**
  (CMH p 0.146; P4 held), so most of the cracker gap is a reporting-limit effect. But the 95%
  interval is 0.86–5.08, and crackers alone still differ at the cut (4 of 29 against 2 of 101;
  P5 missed, with two of the four within 0.06 ppb of the cut). Exploratory: the report's grain
  rows gain exactly the 7 samples and 5 positives its wheat row lacks, and its 495 is the file
  minus one rice sample with no OTA. Recomputed from `data/ota_grain_2018_samples.csv` and
  `data/ota_grain_2018_crossmethod.csv` by an independent pinned test. A sealed job later
  fetched the published files from GitHub and re-ran that test on them: 19 of 19 passed (job
  `ota-grain-2018-result-v1`, 2026-10-28). Not a finding about any product or health risk;
  Health Canada's OTA levels for these foods are proposed, not in force.

## Deoxynivalenol in grains, pseudo-cereals and pulses: CFIA 2015-16

- [Pre-registration: CFIA's open 2015-16 deoxynivalenol file for grains, pseudo-cereals and pulses, and a second look at two CFIA methods (don-grains-2015 0.1.0)](don-grains-2015-0.1.0-prereg.md) —
  public at tag `v0.4.69` before any result value in the file (997 samples) was read. CFIA's
  only public report is a summary page (997 products, 46% detected); the full report is on
  request. A gate on census facts, one consistency check, four blind predictions on where DON
  sits (pulses and soy, small grains against pseudo-cereals, the maximum), one reference count
  against the EU's 2024 DON levels, and two on the 18 product labels shared with the 2018-19
  multi-mycotoxin file: the DON-only method detects more at its own limit, and at a common
  10 ppb cut the within-label odds ratio lies in [0.5, 2.0]. Grading code `don_grains_2015.py`
  is committed with it.
- [don-grains-2015 0.1.0: result](don-grains-2015-0.1.0-result.md) — gate passed, 7 of 9 met.
  The file reproduces the summary page (457 of 997 = 45.8%), but 243 of those positives are
  below 10 ppb (smallest 0.412), so at the multi-mycotoxin method's limit the survey detects
  DON in 214 of 997 (21%). On the 18 shared labels the within-label odds ratio is 6.44 at each
  method's own limit and **1.28** at 10 ppb (CMH p 0.237; RBG 95% interval 0.87–1.90): across
  three crop years, the two CFIA methods agree once read at the same limit (P6, P7 held).
  Small grains are positive in 86.1% against 15.1% for pseudo-cereals (P2, P3 held), and 9 of
  802 grain-type samples reach the EU's 750 ppb level and 30 its 400 ppb level, all small
  grains (P5 held). P1 missed by one sample (29 of 189 pulse and soy samples positive, at most
  33.8 ppb). P4 missed on its level: the maximum is a rye at 5,720 ppb, and all four results
  above 2,000 ppb are rye. Exploratory: every small-grain result at or above 400 ppb is
  Canadian (24) or of unknown origin (6); none of 119 imported small grains reaches 400 ppb.
  Recomputed from `data/don_grains_2015_samples.csv` and
  `data/don_grains_2015_crossmethod.csv` by an independent pinned test. A sealed job later
  fetched the published files from GitHub and re-ran that test on them: 14 of 14 passed (job
  `don-grains-2015-result-v1`, 2026-10-28). A reference comparison (Canada sets no DON maximum
  level for these foods), not a finding about any product or health risk.

## Aflatoxins in dried figs and dates: CFIA 2009-10

- [Pre-registration: CFIA's open 2009-10 aflatoxin file for dried figs and dried dates (aflatoxin-figs-2009 0.1.0)](aflatoxin-figs-2009-0.1.0-prereg.md) —
  public at tag `v0.4.71` before any result value in the file (100 samples, five rows each:
  B1, B2, G1, G2 and Total Aflatoxins) was read. CFIA's only public report is a summary page
  (49 dates, 51 figs; no date positive; four figs at 7.5–78.7 ppb). From the labels alone the
  file has 50 dates and 50 figs, and 10 named countries plus 5 `UNKNOWN` where the page says
  11 countries. A gate on census facts, two consistency checks and six blind predictions.
  Grading code `aflatoxin_figs_2009.py` is committed with it.
- [aflatoxin-figs-2009 0.1.0: result](aflatoxin-figs-2009-0.1.0-result.md) — gate passed, 8 of
  9 met. The file reproduces every result the summary page prints: no date positive (0 of 50),
  four figs positive, totals 7.46–78.66 ppb. The 49/51 against 50/50 product split stays open,
  because both print as "92%" of figs without aflatoxin. `Total Aflatoxins` is the per-sample
  sum of the four forms in all 100 samples (largest gap 0.01 ppb), the fourth CFIA file where a
  group row is a per-sample sum. Three positives, a Greek and two Turkish figs (71.5–78.7 ppb),
  exceed both of the EU's current dried-fig levels (B1 6.0, sum 10.0 µg/kg) at least seven-fold
  on the sum; a US fig (7.46 ppb) exceeds neither. P6 missed: G1 is in one positive only, the
  Greek fig, where it is 68% of the total. The note also corrects the pre-registration's
  sampling range: the file runs from 2 November 2009 to 10 March 2010, not to 27 January (the
  census had taken the text-order maximum of `DD-Mon-YY` strings). Recomputed from
  `data/aflatoxin_figs_2009_samples.csv` by an independent pinned test. A reference comparison
  (Canada sets no aflatoxin maximum level for dried fruit), not a finding about any product or
  health risk.

## Patulin in apple juice and concentrate: CFIA 2008-09

- [Pre-registration: CFIA's open 2008-09 patulin file for apple juice and apple juice concentrate (patulin-2008 0.1.0)](patulin-2008-0.1.0-prereg.md) —
  written before any result value in the file (104 samples, one patulin result each) was read.
  CFIA's only public report is a summary page (12 of 104 at or above the 10 ppb reporting
  limit; maxima 26.7 ppb in juice and 24.0 in concentrate; origin not linked to patulin). A gate
  on census facts and a registered rule for below-limit entries, four consistency checks
  (including Fisher tests of the page's origin claim), and five blind predictions on whether
  the open file is censored at the reporting limit, how the domestic label maps to origin, and
  where the quantified results sit. Grading code `patulin_2008.py` is committed with it.

## Alternaria toxins: CFIA 2014-2022, and the EU's indicative levels

- [CFIA's Alternaria toxin surveys 2014-2022: what the report and the file labels say (alternaria-report-check 0.1.0)](alternaria-report-check-0.1.0.md) —
  a record of CFIA's report (2,597 retail samples; alternariol (AOH) and alternariol monomethyl
  ether (AME), printed only as sums) and the names-only census of its two open per-sample files,
  written before any value was read. Seven points from the report's own arithmetic: Table 1
  swaps two rows; the total maximum (871) is below a row maximum (880); the infant row's
  maximum and average match 2019 alone; five positive samples move between juices and
  pomegranate; Table 9 omits 48 processed peppers; sorghum is in the total with no row; and
  cherry juice's average exceeds its maximum.
- [Pre-registration: CFIA's open Alternaria files against its report and the EU's indicative levels (alternaria 0.1.0)](alternaria-0.1.0-prereg.md) —
  written before any value was read (public at tag `v0.4.63`): a gate, 17 consistency checks
  (every report row the labels identify), six predictions on the report's open points and five
  on EU Recommendation 2022/553, the first per-toxin comparison of CFIA's open data with those
  levels. Grading code `alternaria.py` is committed with it.
- [alternaria 0.1.0: result](alternaria-0.1.0-result.md) — gate passed, 17 of 29 met (11 of
  17 consistency checks). The report's two largest tomato results (880 and about 345 ppb) are
  **not in the open file**: its tomato maximum is 6.72 ppb, and its only total above 700 ppb is
  the 871 ppb pomegranate juice that Table 2's Total prints. The whole 2-sample, 3-positive gap
  between report and file sits in four rows (2014–15 juices, 2015 and 2016 tomato products,
  2014 wine). Confirmed: the infant row's 26 and 5.2 are 2019-only (all years: 37.1 and 5.04),
  and Table 1's swap (13 of 187 2019 pomegranate samples are Canadian-origin). Table 6's 2018
  juice row counts F2's 5 pomegranate juices among its positives (125) and average (17) but not
  in its n (174). Against EU 2022/553: 3 of 51 sunflower oils and 2 of 3 sesame seeds exceed
  the indicative levels; no sunflower seed (0 of 51) and no tomato product (0 of 200) does.
  AME carries 61% of the toxin mass in sunflower products and AOH 75% in fruit products.
  Recomputed from `data/alternaria_samples.csv` and the sealed record by an independent pinned
  test. A sealed job later fetched the published files from GitHub and re-ran that test on
  them: 13 of 13 passed (job `alternaria-result-v1`, 2026-10-27). A reference comparison (EU
  indicative levels trigger investigation; Canada sets no limit), not a finding about any
  product or health risk.

## The screen's second target: Sudan dyes

- [Pre-registration: where does Sudan-dyed red palm oil on Canadian shelves come from? (red-palm-dyes 0.1.0)](red-palm-dyes-0.1.0-prereg.md) —
  written before any amount in CFIA's open 2019-20 red palm oil colour file was read: six
  predictions that Sudan dyes turn up in at most 10% of imported retail samples (FDA Ghana
  measured 26.6% in its own 2019 market), only in oil declared from West or Central Africa
  or of unknown origin, mostly as Sudan IV and most often from Ghana, and that no other
  non-permitted colour appears. A destination-country check of a producing country's own
  surveillance, as georgia-trend was for spices. Grading code `red_palm_dyes.py` is
  committed with it.
- [red-palm-dyes 0.1.0: result](red-palm-dyes-0.1.0-result.md) — 5 of 6 met, now confirmed
  by a sealed compute run (job red-palm-dyes-v1, 2026-10-17): same two positives, same
  grades. Two of 104 imported retail samples (2019–2021) carried a Sudan dye, both Sudan IV
  (47.5 and 15.6 ppm), both declared from **Nigeria**. All 73 Malaysian and South American
  oils were clean, and no other non-permitted colour appeared. The Ghana prediction (P5)
  failed: 0 of 14 Ghana-declared samples were dyed. Different sampling frames, small
  counts. The sealed per-sample table is in `data/red_palm_dyes_sealed_samples.csv`.

See the main [README](../README.md) for the FDA-recall, NYC-lab and detection-limit
analyses that frame these notes.
