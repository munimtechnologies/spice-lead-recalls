# raman-reach 0.1.1: result

This is the graded result for the pre-registration in
[`raman-reach-0.1.0-prereg.md`](raman-reach-0.1.0-prereg.md) (v0.4.21), run with the parser fix recorded in
[`raman-reach-0.1.1-deviation.md`](raman-reach-0.1.1-deviation.md) (v0.4.27). The nine predictions have not
changed. As the deviation says, the sealed table text was read before 0.1.1 was written, so every rule that
needed a choice is graded three ways: frozen, reading A and reading B.

**Author:** MV2, Munim, Inc. (mv2@munimtech.com). Work made with AI agents.
**License:** text and derived data CC BY 4.0; code Apache-2.0.

- **Source:** Forsyth J.E., Sinha M., Bandekar A., Mistree D., Luby S., "Systemic drivers of toxic food
  adulteration: lead chromate in turmeric across eastern India", *npj Science of Food* (2026),
  doi:10.1038/s41538-026-00867-8, Supplementary Table 8 (CC BY 4.0). Supplement sha256
  `f728f8c613ed9dafdc730f595049fd326affd29e9827e4f4a1e20b69079b9193`, Table 8 on pages 15-27.
- **Sealed per-sample table:** [`../data/raman_reach_samples.csv`](../data/raman_reach_samples.csv) (503 rows,
  both form readings). [`../test_raman_reach_result.py`](../test_raman_reach_result.py) recomputes every
  count below using only the Python standard library.
- **Job:** `raman-reach-v2`, 2026-10-18 10:43-10:47 UTC; the grader's own tests passed before it ran.

## Consistency with the article (all exact)

- 503 rows, the article's n. Type codes 1/2/3/4 = 162/30/235/76, matching Table S3. Cities mapped to states
  give Bihar 134, Jharkhand 77, Uttar Pradesh 200, West Bengal 60, Chhattisgarh 32, matching Table S2. The
  table's own Bihar flag (`sellstate_bin`) agrees with that map on all 503 rows.
- 152 samples are strictly above 10 ug/g and one is exactly 10 (`50_KD-1-2-5`, Ambikapur), so the article's
  153 counts 10 as exceeding. 340 rows read 2 ug/g (half the 4 ug/g detection limit: non-detects) and 350 are
  below 10.
- Ten sample IDs occur twice (listed in the test). Every one of the 20 rows reads 2 ug/g, so they change no
  count at or above 10 ug/g.

## Pre-registered predictions

| | prediction | value | frozen | A | B |
|---|---|---|---|---|---|
| P1 | 495-515 samples in S (gate) | 503 | met | met | met |
| P2 | 148-158 above 10 ug/g (consistency) | 152 | met | met | met |
| P3 | highest is 6,300-6,500 ug/g and from Bihar (consistency) | 6,416, Buxar, Bihar | not gradable | met | met |
| P4 | at most 10% of E at or above 3,200 ug/g | **16 of 152 (10.5%)** | not met | not met | not met |
| P5 | median lead in E below 320 ug/g | **1,294 ug/g** | not met | not met | not met |
| P6 | Bihar holds more than half of samples at or above 500 ug/g | 47 of 105 | not gradable | not met | not met |
| P7 | at or above 500 ug/g, roots outnumber powders | A: 75 roots, 30 powders; B: 1 root, 30 powders | not gradable | met | not met |
| P8 | no packaged powder above 100 ug/g | 2 of 30 (240 Deoghar, 130 Jamshedpur) | not gradable | not met | not met |
| P9 | median Pb:Cr in E is 2-8 | no chromium column | not gradable | not gradable | not gradable |

**Frozen: 2 of 4 gradable met. A: 4 of 8. B: 3 of 8.** Both consistency checks held wherever gradable. The
two predictions that matter most for MV2's own pitch, P4 and P5, failed in every reading, and they failed in
the direction that changes the pitch.

P4 missed narrowly (16 against a cap of 15.2). P5 missed by a factor of four: we expected a lognormal spread
with a median exceedance near the low hundreds of ug/g. The real exceedances are **gross**. Half of them are
at or above 1,301 ug/g, about 0.2% w/w lead chromate. Only 21 of 152 sit between 10 and 100 ug/g, and 105 of
152 (69%) are at or above 500 ug/g. Low-level lead from soil or equipment would sit in the tens of ug/g;
there is very little of it here.

P6 failed because adulteration is spread across states: Bihar has the most samples above 10 ug/g (72 of
152) but only 47 of the 105 at or above 500 ug/g. P7 depends on the codebook: under the count-matched codes (A)
double-polished roots dominate the gross tail (74 of 105); under the caption's literal codes (B) code 3 is
undefined and only one root is known.

## How much of the problem a screen reaches

Share of the 152 samples above India's 10 ug/g limit that a screen with a given lead detection limit would
flag (lead chromate is 64.1% lead by mass, so 0.1% w/w lead chromate is about 640 ug/g lead):

| screen detection limit (ug/g lead) | about % w/w lead chromate | samples at or above | share of E |
|---|---|---|---|
| 3,200 (bench FT-Raman, PLSR, *Food Control* 2021) | 0.5 | 16 | 10.5% |
| 2,000 | 0.31 | 51 | 33.6% |
| 1,000 | 0.16 | 91 | 59.9% |
| 640 | 0.1 | 103 | 67.8% |
| 500 | 0.08 | 105 | 69.1% |
| 320 | 0.05 | 112 | 73.7% |
| 100 | 0.016 | 131 | 86.2% |
| 50 | 0.008 | 139 | 91.4% |

At the 3,200 ug/g threshold, by state: Bihar 6 of 72, Uttar Pradesh 4 of 32, Jharkhand 3 of 32,
Chhattisgarh 3 of 8, West Bengal 0 of 8. By form (reading A): double-polished roots 13 of 83, loose powder 2
of 57, single-polished roots 1 of 9, packaged powder 0 of 3.

## What this means for Yellow Flag

1. **At today's best published bench sensitivity, a Raman screen sees about one adulterated sample in ten.**
   The pitch cannot claim to enforce the 10 ug/g limit with Raman, and it must not. Portable XRF (detection
   limit about 4 ug/g in this study) stays the enforcement tool.
2. **The sensitivity curve is steep, so a modest gain pays off.** Because the adulteration is gross, a screen
   five times more sensitive (0.1% w/w, about 640 ug/g) would reach about two thirds of exceedances, and one at
   about 100 ug/g would reach 86%. That is the design target this result sets: **about 0.1% w/w lead chromate
   or better**, plus the dye screen Raman already does well.
3. **Where to point it:** double-polished roots and loose powder. Packaged powders held 3 of 152 exceedances
   and none at or above 500 ug/g.

## Limits

- Lead was measured by handheld XRF calibrated to ICP-MS, not ICP-MS per sample. The article reports a mean
  error of 18% for roots. One sample per distinct type on sale, so these are not market shares.
- The 3,200 ug/g figure comes from one bench study on spiked powder. A pocket Raman device is usually less
  sensitive than bench FT-Raman, so 10.5% is a best case for powder. For polished roots the pigment sits on
  the surface; a surface measurement might see more than the whole-root average suggests. That is untested here.
- Lead is not lead chromate. The article says every sample above 10 ug/g also held chromium suggestive of lead
  chromate, but the open table has no chromium column, so P9 and any Pb:Cr check cannot be made from it.
- Reading A's form codes rest on matching counts to Table S3. The caption's codebook (double-polished = 4,
  single-polished = 5) does not fit a column holding only 1-4; we have not asked the authors.
- Nothing here is advice to any person about any food.

Data: Forsyth J.E. et al., npj Science of Food (2026), doi:10.1038/s41538-026-00867-8, Supplementary Table 8,
licensed CC BY 4.0. The derived table in `data/` is CC BY 4.0. Prepared by MV2 of Munim, Inc. with AI agents.
