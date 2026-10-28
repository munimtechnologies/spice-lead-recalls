# ota-grain-2018 0.1.0: CFIA's open 2018-19 ochratoxin A grain file against its two reports, and against the multi-mycotoxin method — result

RESULT-MARKER: ota-grain-2018-0.1.0-result

By MV2 of Munim, Inc. Prepared with AI agents working in his name. Text CC BY 4.0; code Apache-2.0.

This grades the pre-registration [ota-grain-2018-0.1.0-prereg.md](ota-grain-2018-0.1.0-prereg.md)
and its companion [report-check note](ota-grain-2018-report-check-0.1.0.md). Both were public first,
at tag `v0.4.67`. The sealed job `ota-grain-2018-v1` ran on 2026-10-28 at 00:56 UTC (python:3.12,
1 GB, no host paths). It waited for
both markers to be public and checked that its bundled `ota_grain_2018.py` and
`test_ota_grain_2018.py` were byte-identical to the published copies. It ran the 14 offline tests
and only then read the two SHA-256-pinned files. **The gate passed. 16 of 17 graded items held:
all ten consistency checks and five of six blind predictions. P5 missed.**

This is a reference comparison, not a compliance finding. Health Canada's OTA levels for these
foods are proposed, not in force. It is not about any brand, and it is not dietary or medical
advice. Health Canada judged the OTA levels found in the survey "unlikely to pose a health risk".

## Headlines

1. **Comparing CFIA's two 2018-19 methods at the same cut makes most of the gap go away.** On
   the seven product labels both files share, the OTA-only file detects OTA in 82 of 150 samples
   (54.7%) and the multi-mycotoxin file in 10 of 247 (4.0%). Within labels, that is a
   Mantel-Haenszel odds ratio of **26.0** (CMH p ≈ 6 × 10⁻³⁰). Count only results at or above
   0.8 ppb, the multi-mycotoxin method's smallest OTA result and its listed limit of detection,
   and the OTA-only file has 15 of 150 (10.0%). The odds ratio falls to **2.09** (CMH χ² 2.11,
   **p 0.146**), so P4 held. Most of the 75%-versus-2% cracker gap is a reporting-limit effect,
   not cleaner crackers in the second survey.
2. **But "no significant difference" is not "the same".** The 95% interval for that 2.09 (Robins-
   Breslow-Greenland, computed after grading) is **0.86–5.08**. The data allow anything from no
   gap to a five-fold one. Crackers alone still differ at the cut: **4 of 29** against **2 of 101**
   (Fisher two-sided p 0.022, exploratory), which is why P5 missed. Above its limit, the
   multi-mycotoxin method may still find OTA less often than the OTA-only method. The open data
   cannot settle that.
3. **The open file settles the report's contradictions.** It holds **496** samples, as CFIA's later
   "Ochratoxin A in Selected Foods" report says, not the survey report's 495. Rice has **14**
   positives (Table 5), not 13 (Table 2). The oat average is **0.26** ppb, not Table 4's 2.6, which
   is above the oat maximum of 1.65. **220 of 496** samples (44.4%) carry OTA, so the report's
   headline "45%" does not come from any count.
4. **Every row of both reports that the labels identify rebuilds from the file** (C1–C10): rye,
   baking mixes, infant cereal, pasta, the overall range of 0.042–11 ppb, and all five 2018 rows of
   the later report.

## Data

- **OG:** CFIA, "Ochratoxin A in Wheat Products, Oat Products, Rice Products and Other Grain
  Products – April 1, 2018 to March 31, 2019". Open Government Portal resource
  `d9d79110-e472-4aec-89ee-e51861f4d88d`, SHA-256 `36dde7d7…7d47403` (139,876 bytes, UTF-8 with
  BOM), Open Government Licence – Canada. It has 496 rows, one OTA result per sample.
- **MM:** CFIA's 2018-19 multi-mycotoxin file, resource `09a3c285-8552-4a38-b4be-cdf6d5fc3fd2`,
  SHA-256 `ba508494…3835`. Only its 750 OTA rows are used.
- **Non-detects:** OG writes them as the text `Not Detected/ Non-détecté` (276 cells, one token),
  where earlier CFIA mycotoxin files used a literal 0. The registered value rule read them
  correctly. All values in both files are in ng/g (= ppb).

## Gate (passed)

All 17 checks held. For OG: the SHA-256, 496 rows and samples with one OTA row each, all 21
product-label counts, CANADA 92 and UNKNOWN 232, one known unit, 220 positive and 276 token cells,
and one token. For MM: the SHA-256, 18,750 rows, 750 OTA rows, 20 OTA positives with a minimum of
0.8, known units, and exactly the seven registered shared labels.

## Graded items: 16 of 17 held

| ID | Registered (printed figures) | Observed in the file | Met |
|---|---|---|---|
| G | gate (above) | 17 of 17 checks | ✅ |
| C1 | R20 rye: 25, 15 positive, 0.050–1.9, avg 0.24 | 25, 15, 0.050–1.87, 0.237 | ✅ |
| C2 | R20 baking mixes: 28, 9, 0.051–0.46, 0.16 | 28, 9, 0.051–0.455, 0.162 | ✅ |
| C3 | R20 infant cereal (wheat): 28, 5, 0.050–0.17, 0.077 | 28, 5, 0.050–0.172, 0.0766 | ✅ |
| C4 | R20 pasta: 28, 21, 0.049–0.34, 0.18 | 28, 21, 0.049–0.342, 0.177 | ✅ |
| C5 | R20 whole survey: 0.042–11 | 0.042–11.1 | ✅ |
| C6 | R22 less commonly consumed grains: 100, 44%, 0.05–7.6, 1.0 | 100, 44 (44%), 0.05–7.62, 1.035 | ✅ |
| C7 | R22 oat: 97, 54%, 0.05–1.6, 0.26 | 97, 52 (54%), 0.05–1.65, 0.262 | ✅ |
| C8 | R22 rice: 99, 14%, 0.049–11, 1.1 | 99, 14 (14%), 0.049–11.1, 1.127 | ✅ |
| C9 | R22 wheat: 29, 62%, 0.06–1.5, 0.4 | 29, 18 (62%), 0.06–1.48, 0.403 | ✅ |
| C10 | R22 grain-based foods: 171, 54%, 0.042–2.2, 0.24 | 171, 92 (54%), 0.042–2.21, 0.244 | ✅ |
| P1 | `Buckwheat Products` max 7.6 with 9–11 positives; `Quinoa Products` max 5.8 with 7–8 | buckwheat 7.62, 9; quinoa 5.75, 8 | ✅ |
| P2 | the 25 kamut samples: 9–10 positives, max ≤ 1.25 | 10, 1.24 | ✅ |
| P3 | exactly one sample outside buckwheat and quinoa above 3 ppb, a `Grain - Rice` | one: a rice at 11.1 ppb | ✅ |
| P4 | 7 shared labels at 0.8 ppb: CMH p ≥ 0.05 | MH OR 2.09, χ² 2.11, **p 0.146** | ✅ |
| P5 | `Crackers`: ≥ 20 positive and ≤ 3 at or above 0.8 ppb | 21 positive, **4** at or above 0.8 | ❌ |
| P6 | 10–39 of 496 at or above 0.8 ppb | 27 (5.4%) | ✅ |

(R20 = the survey's own 2020 report; R22 = CFIA's later "Ochratoxin A in Selected Foods" report,
whose Table 7 reprints this survey as five 2018 rows. "Positive" = above 0.)

## P4 and P5: two CFIA methods, one year

| shared label | OTA-only: n | detected | ≥ 0.8 ppb | multi-mycotoxin: n | detected (all ≥ 0.8) |
|---|---|---|---|---|---|
| `Buckwheat Products` | 23 | 9 | 6 | 15 | 2 |
| `Crackers` | 29 | 21 | 4 | 101 | 2 |
| `Grain - Kamut` | 1 | 0 | 0 | 13 | 1 |
| `Kamut Products` | 24 | 10 | 2 | 15 | 1 |
| `Pasta - Dry` | 28 | 21 | 0 | 62 | 2 |
| `Quinoa Products` | 24 | 8 | 2 | 15 | 0 |
| `Rye Products` | 21 | 13 | 1 | 26 | 2 |
| **pooled** | **150** | **82 (54.7%)** | **15 (10.0%)** | **247** | **10 (4.0%)** |

- **At each method's own limits** the two surveys look like different worlds: Mantel-Haenszel
  odds ratio 26.0, CMH χ² 129.2. Of the 82 OTA-only detections on these labels, 67 are below
  0.8 ppb. The multi-mycotoxin method would not have reported them.
- **At the common 0.8 ppb cut** the odds ratio is 2.09 (crude 2.63), and the registered test
  does not reject (p 0.146). Pasta reverses: 0 of 28 OTA-only pasta samples reach 0.8 ppb (the
  maximum is 0.342), while the multi-mycotoxin file has 2 of 62.
- **Crackers, P5's miss.** Four OTA-only crackers reach 0.8 ppb (0.84, 0.855, 1.59 and 2.21),
  where the prediction allowed three. Two of the four sit within 0.06 ppb of the cut, and a fifth
  is at 0.74, so the miss depends on exactly where the cut falls. Against the multi-mycotoxin
  file's 2 of 101, four is a cracker-only odds ratio of 7.9 (Fisher p 0.022). This test was
  chosen after seeing the table, and it is one of seven labels, so it is a lead, not a finding.
- **What this means for reading CFIA's surveys.** A detection rate from the OTA-only method
  (smallest result 0.042 ppb) and one from the multi-mycotoxin method (0.8 ppb) are not
  comparable. Cutting both at 0.8 ppb removes most of the gap, but this test cannot rule out a
  real difference of up to about five-fold. Neither CFIA report gives a detection limit for its
  own method. The 0.8 ppb figure comes from the multi-mycotoxin file's smallest result and from
  CFIA's 2015–2018 multi-mycotoxin report.

## Exploratory: how the survey report's grain rows relate to the file

These counts were reconciled after grading. The arithmetic is exact, but the explanation is
inferred, not stated by CFIA.

| R20 Table 2 grain row | R20 n / positive | file family n / positive | R20 − file |
|---|---|---|---|
| buckwheat | 25 / 11 | 23 / 9 | +2 / +2 |
| kamut | 26 / 10 | 25 / 10 | +1 / 0 |
| oat | 100 / 55 | 97 / 52 | +3 / +3 |
| quinoa | 25 / 8 | 24 / 8 | +1 / 0 |
| rice | 98 / 13 (Table 5: 14) | 99 / 14 | −1 / 0 with Table 5 |
| rye | 25 / 15 | 25 / 15 | 0 / 0 |
| wheat (the ten other labels) | 196 / 107 | 203 / 112 | −7 / −5 |
| **total** | **495 / 219 (220 with Table 5)** | **496 / 220** | **−1 / 0** |

The four grain rows gain exactly the 7 samples and 5 positives the wheat row lacks. That fits
the report moving seven products with generic labels (a cookie, a cracker, a cereal) into their
grain's row. The 496 − 495 gap is one rice sample with no OTA. Once Table 2's rice "13" is read as
Table 5's 14, every positive in the report is in the file.

## Also reported (not graded)

- **Above 3 ppb:** 7 samples. One rice (11.1 ppb, P3) and six with no proposed level: four
  `Buckwheat Products` (7.62, 5.68, 5.35, 3.41) and two `Quinoa Products` (5.75, 4.34).
- **Infant cereals:** none of the 28 is above 0.5 ppb (maximum 0.172). **Oat bran:** none of the
  25 is above 7 ppb (maximum 1.65).
- **Crackers + crispbread:** the file's 31 samples (23 positive, 0.047–2.21, average 0.388) against
  R20 Table 3's crackers/crispbreads row (40, 30 positive, 0.047–2.2, 0.41). The minimum and maximum
  match. Nine samples, seven of them positive, carry other labels in the file.
- **Whole file at the cut:** 27 of 496 (5.4%) at or above 0.8 ppb, against the multi-mycotoxin
  file's 20 of 750 (2.7%). The product mixes differ, so this is not a like-for-like comparison.

## Limits

- Detection is binary at each method's own limits, and neither report gives its method's limit.
  The 0.8 ppb cut is the best figure available, from the multi-mycotoxin file's smallest result
  and CFIA's 2015–2018 report. It is not a stated limit for the 2018-19 method.
- The seven shared labels hold different products in the two surveys, bought by different
  samplers. Stratifying by label removes label-level differences, not within-label ones.
- A non-significant CMH test with an interval of 0.86–5.08 does not show the methods agree. It
  only shows the open data cannot tell them apart at this cut.
- This note does not say why the reports and the file differ. Only CFIA can say that.

Prior art: on 2026-10-27, searches for analyses of this open file, and for a comparison of CFIA's
OTA-only and multi-mycotoxin results, found none. As far as we know, this is the first
per-label comparison of the two methods' OTA detection at a common cut.

## Reproduce it

- `data/ota_grain_2018_samples.csv`: one row per sample (sample, product, family, origin,
  detected, OTA in ng/g), the sealed job's output.
- `data/ota_grain_2018_crossmethod.csv`: per shared label, n, detected and at or above 0.8 ppb
  in OG, and n and detected in MM.
- `data/ota_grain_2018_summary.json`: the sealed grader record (gate, census, every check and
  prediction with its observed values, the cross-method tables, provenance).
- `test_ota_grain_2018_result.py`: a pinned test. It does not import the grader. With its own
  code it rebuilds every C-row, P1–P6, the R20 reconciliation and the cross-method tables from
  the two CSVs, along with the Mantel-Haenszel, CMH, Robins-Breslow-Greenland and cracker Fisher
  figures. It also checks them against the sealed record.

A sealed follow-up job (`ota-grain-2018-result-v1`) fetches these published files from GitHub and
re-runs the pinned test on them. The grading code `ota_grain_2018.py` and the pre-registration are
at tag `v0.4.67`.
