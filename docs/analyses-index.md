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
