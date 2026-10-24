<!-- PREREG-MARKER: coumarin-tea-replication-0.1.0-prereg -->
# coumarin-tea-replication 0.1.0: pre-registration

By MV2 of Munim, Inc. Made with AI agents working in MV2's name. Code Apache-2.0; this note
CC BY 4.0. Data: CFIA 2013-14, 2014-15 and 2015-16 coumarin targeted surveys (Open Government
Licence - Canada).
A bounded exposure screen on open data. It is not a compliance finding (Canada sets no coumarin
limit), not a statement about any brand, and not individual dietary or medical advice.

## Question

[`coumarin-tea` 0.1.0](coumarin-tea-0.1.0-result.md) screened the 115 teas in CFIA's 2013-14
survey per brewed cup against EFSA's tolerable daily intake (TDI) for coumarin, 0.1 mg per kg body
weight per day, at a 100% leaf-to-cup transfer upper bound. All five of its predictions held. A
60 kg adult's standard 2 g cup put none of the 115 over the whole-day TDI, a strong 4 g adult cup
put 7 over (6.1%), a 15 kg child's 2 g cup 33 (28.7%) and a child's 4 g cup 45 (39.1%). A
post-publish job re-ran its result test on the published files and all 12 tests passed.

**Does that result replicate in CFIA's two later tea surveys?** These are 210 teas bought from
August 2014 to March 2015 and 297 teas bought from August 2015 to March 2016, by the same agency
and in the same six cities, with the same lab unit. Two things differ. Each survey drew new
products in a new year. And the 2015-16 survey also targeted **licorice-flavoured** products:
175 of its 747 samples contained licorice flavouring, and CFIA reports that teas with licorice
but no cinnamon carried less coumarin than cinnamon teas. So this is an out-of-sample test of
the published method on 507 new teas, plus a pooled three-survey per-cup table (622 teas). We
found no such table published anywhere.

## Method (unchanged from coumarin-tea 0.1.0)

The same scenarios, thresholds and functions are imported from the published `coumarin_tea.py`
(`SCENARIOS`, `threshold_ppm`, `pct_budget`). The same parser is imported from
`coumarin_eu_limits.py` 0.1.1. The sealed job checks both against the live repository before it
runs. Coumarin in one cup (mg) = concentration (mg/kg) x dry tea per cup (kg) x transfer, with
transfer fixed at 1.0. A tea is "over the TDI" when a **single cup** delivers more than the
drinker's **whole-day** budget. Non-detects count as 0.

| id | drinker | dry tea per cup | one cup exceeds the day's TDI above |
|---|---|---|---|
| A1 | 60 kg adult | 2 g | 3,000 mg/kg |
| A2 | 60 kg adult | 4 g | 1,500 mg/kg |
| C1 | 15 kg child | 2 g | 750 mg/kg |
| C2 | 15 kg child | 4 g | 375 mg/kg |

**Tea selection.** A row is a tea when its Product cell is exactly one of CFIA's six labels:
`Tea - Black`, `Tea - Green`, `Tea - Herbal`, `Tea - Oolong`, `Tea - White` or `Tea - Other`. This
is an exact match, not a substring test, so a product such as a steak sauce could not leak in
the way a "tea" substring rule would let it. The same rule re-selects the 2013-14 teas, and the job reports whether it
reproduces the published 115 / 0 / 7 / 33 / 45 counts. That is a reproduction check, not a
prediction.

## Data and status of the values (read this first)

- 2014-15: resource `85372927-17ac-4958-a66f-fdd278f13f26`, SHA-256
  `e418443deb56f7c1269e8c3527ad707788c53d6543c4f6da19d74cca95beec1e` (739 data rows).
- 2015-16: resource `3a9481c9-cf6e-4dd0-8b25-29dd8975aa5e`, SHA-256
  `4520863554e06b60092074d91eceff12123f39f4bcc2ce75eea2cdacedc0d30c` (747 data rows).
- 2013-14: the file used by `coumarin-tea` 0.1.0 (resource `66d9cd8f-...`, SHA-256
  `3c8a18c0...3f4f`).
- Both later files were downloaded on 2026-10-18 by the `coumarin-cinnamon` 0.1.0 job, which
  recorded their digests, headers and unit census (every row `µg/g`, which equals mg/kg). That
  study published **only the pure-cinnamon rows**. No tea value from either file has been
  published by this repository or read by any agent.
- Before writing this note, an agent ran a **names-only census** of the two files. It counted
  Product labels and counted Result cells equal to the non-detect token `0`. It never displayed
  any other value. The results:
  - 2014-15: Black 77, Green 30, Herbal 60, Oolong 7, White 15, Other 21 (210 teas). 32 tea
    results are `0`.
  - 2015-16: Black 81, Green 31, Herbal 86, Oolong 32, White 42, Other 25 (297 teas). 52 tea
    results are `0`.
  - No tea row has a blank result.
  - The zero counts equal CFIA's own published detection figures (178 of 210 and 245 of 297
    detected), so they add nothing beyond the headline.
- CFIA's published tea headlines, the only figures the predictions rest on:
  - **2014-15:** 210 samples, detected in 178 (85%), range 0.2-1,920, average of the positives
    302 mg/kg. The report also says herbal tea "contained the highest levels of coumarin in
    comparison to other dried teas".
  - **2015-16:** 297 samples, detected in 245 (82%), range 0.2-2,230, average of the positives
    442. The HTML report prints "ppb", but the file's unit is µg/g. Earlier work already found
    the HTML unit is a typo: cinnamon at 5,040 only makes sense as mg/kg.
  - The report gives no breakdown by tea type.
- CFIA's 2011-12 survey had only 11 teas, so it is left out.

## Gate and predictions

| id | kind | prediction |
|---|---|---|
| G0 | parse gate | **both** files: measured rows in [730, 739] (2014-15) and [740, 747] (2015-16); exactly 210 / 297 tea rows, all measured; the six-type census exactly as above; tea unit census exactly `{"ug/g": 210}` / `{"ug/g": 297}`; tea max in [1,910, 1,930] (CFIA 1,920) / [2,220, 2,240] (CFIA 2,230); detected exactly 178 / 245; mean of detected values in [285, 320] (CFIA 302) / [420, 465] (CFIA 442) |
| P1 | check | no tea in either survey exceeds an adult's whole-day TDI in one standard 2 g cup (A1 = 0) |
| P2 | **primary** | child 2 g cup (C1): the share over the TDI is **lower than 2013-14's 33/115 (0.287) in each** later survey |
| P3 | test | 2014-15 C1 share in **[0.04, 0.22]** |
| P4 | test | 2015-16 C1 share in **[0.10, 0.32]** |
| P5 | test | 2014-15 child 4 g cup (C2) share in **[0.12, 0.40]** |
| P6 | test | 2015-16 C2 share in **[0.18, 0.45]** |
| P7 | test | 2014-15 adult 4 g cup (A2): **1 to 12** teas over the TDI |
| P8 | test | 2015-16 A2: **2 to 30** teas over the TDI |
| P9 | direction | the C1 share is **higher in 2015-16 than in 2014-15** |
| P10 | test | in 2015-16, `Tea - Herbal` has the **strictly highest median** coumarin of the six tea types |

If G0 fails, P1-P10 are not graded. An amendment would be published first, as with
`coumarin-eu-limits` 0.1.1.

### Reasoning (written before any per-sample value was seen)

- **P1 is implied by the headlines.** Both published maxima (1,920 and 2,230) are below 3,000.
  It is graded only because it is the study's main public statement. The same goes for the lower
  ends of P7 and P8 in part: a max above 1,500 guarantees at least one A2 tea in each survey. P8
  asks for at least 2.
- **P2.** The 2013-14 teas had a positives-average of about 500 mg/kg, with almost all detected
  (114 of 115). The later positives-averages are lower: 302 is 0.60x and 442 is 0.88x. The later
  surveys also have many more non-detects (15% and 18% against 1%). The 2015-16 non-detects are
  plausibly licorice teas without cinnamon. A smaller share of the later teas should therefore
  sit above 750 mg/kg.
- **P3-P8.** These scale the 2013-14 shape: 61% under 375, 10% from 375 to 750, 23% from 750 to
  1,500 and 6% above 1,500. Each threshold is moved by the ratio of positive means and the
  result is multiplied by the detected share. That gives about 10% (C1) and 27% (C2) for
  2014-15, and about 22% (C1) and 31% (C2) for 2015-16, with wide bands. The shape of the later
  distributions is not published, so these are genuinely uncertain.
- **P9.** 2015-16's positives-average is 46% higher than 2014-15's, and the two detected shares
  are similar.
- **P10.** Cinnamon herbal blends are often mostly cinnamon bark. CFIA says chamomile, a common
  herbal ingredient, also contains coumarin. Flavoured green, white and oolong teas usually carry
  cinnamon or licorice as a minor note. CFIA said herbal tea was highest in 2014-15, but that
  statement is not used as evidence for 2015-16. It is the hypothesis being tested on the new
  survey. Black chai is a real rival, so this could fail.

## Grading

A sealed compute job (`python:3.12`, no host paths) does the grading:

1. `check_prereg.py` waits until this file is public on GitHub. It then makes the bundled
   `coumarin_eu_limits.py` and `coumarin_tea.py` equal the published copies.
2. The offline tests `test_coumarin_tea_replication.py` run. They use a cp1252 fixture with this
   header, the micro sign, a `0` non-detect and a "Sauce - Steak" decoy.
3. `coumarin_tea_replication.py` verifies each file's SHA-256 before parsing. It then writes:
   - `summary.json` and `grades.json`;
   - `coumarin_tea_replication_samples.csv`: every tea from the three surveys, with mg/kg,
     % of the day's budget under A1-C2 and the four over-TDI flags;
   - `coumarin_tea_replication_by_type.csv`: n, detected, median, mean, max and over-TDI counts
     per survey and tea type.

The result note follows in a later run, with a result test that recomputes every number from
those tables.

Descriptive, not graded:
- the pooled three-survey and two-survey per-cup tables;
- the per-type tables for all three surveys;
- each survey's median, mean and 90th percentile;
- the 2013-14 reproduction check.

## Limits (stated in advance)

- **100% transfer is an upper bound.** A real cup delivers only the share of coumarin that steeps
  out. The counts are ceilings.
- **The TDI is a lifetime value.** Going over it in one cup on one day is not a health finding.
- **Children rarely drink these teas.** The child scenarios are a reference bound.
- **Generic labels only.** The files name a tea only by type. Whether a tea contains cinnamon,
  licorice or both is not in the open data, so the cinnamon-versus-licorice contrast CFIA
  describes cannot be rebuilt here.
- **Targeted retail sampling, not market shares.** The three surveys are separate draws, not a
  panel, so differences between years are not trends in the products people buy.

## Prior art (searched 2026-10-24)

- CFIA's 2014-15 and 2015-16 reports give tea headlines (and a herbal-highest remark for
  2014-15). They give no per-cup exposure, no transfer model and no per-type table for 2015-16.
- BfR and EFSA give the TDI and cinnamon examples, but no per-cup screen of a national tea
  survey.
- `coumarin-tea` 0.1.0 (this repository) did it for one survey. As far as we found, no open,
  per-sample, reproducible per-cup screen of commercial teas against the coumarin TDI has been
  done **across several national surveys**, and no pre-registered replication of one exists.

<!-- PREREG-MARKER: coumarin-tea-replication-0.1.0-prereg -->
