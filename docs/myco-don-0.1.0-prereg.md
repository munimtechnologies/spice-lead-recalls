# Pre-registration: deoxynivalenol in CFIA's open infant-cereal and selected-foods files (myco-don 0.1.0)

PREREG-MARKER: myco-don-0.1.0-prereg

By MV2 of Munim, Inc. Prepared with AI agents working in his name. Text CC BY 4.0; code Apache-2.0.

This note is written and published **before** any deoxynivalenol (DON) or ochratoxin A (OTA)
concentration in CFIA's three open files below is read by the grading code. A names-only census
(job `myco-census-v2`, 2026-10-25) recorded each file's SHA-256, row and sample counts, the label
counts of the descriptive columns, and a **format** census of the result column that never reports
a value. Nothing else about the values has been read, with one disclosed exception (the 2010-11
file, below). The public commit timestamp of this note fixes the predictions before the sealed job
`myco-don-v1` reads a single value. A companion note, `don-infant-report-check-0.1.0.md`, already
recorded what CFIA's 2018-19 infant-cereal report says about itself from the report PDF alone.

Not a finding about any product, brand or health risk. Canada sets no DON maximum level for
finished foods; the EU and Codex levels below are used only as reference yardsticks.

## Data (three CFIA open files, all released 2026-10-06, Open Government Licence – Canada)

| Short name | Dataset | Resource | SHA-256 (first 16) | Rows | Samples | Rows/sample |
|---|---|---|---|---|---|---|
| don-infant-2018 | d17f8fe4-1d8b-4d78-8937-5f4f85812e02 | 7e3c4cf6-69fa-4931-9f31-cd78225acf01 | `7427b2905b8730f` | 286 | 286 | 1 |
| don-2011 | 30484e10-f94e-4580-999f-3dc54eb75106 | cef65485-68e2-4580-8bd4-aa47c5a84c96 | `4d4c90fb4b157bbb` | 1395 | 1395 | 1 |
| ota-don-2010 | 4c43a389-245b-4c6c-a28a-c88235064e1b | b87d36bc-a568-4dc5-8391-9d8afdbf6048 | `fdd0aec2e70e8cbf` | 1886 | 943 | 2 (OTA + DON) |

Full SHA-256 strings are pinned in the grading code. The ota-don-2010 file carries two rows per
sample, one for Deoxynivalenol and one for Ochratoxin A (census: Component = Deoxynivalenol 943,
Ochratoxin A 943). The other two files carry one DON row per sample.

## What was and was not seen (be exact)

- **don-infant-2018, don-2011:** no value read at all. The census is labels, counts and the result
  **format** only. For don-infant-2018 the census reports 286 numeric result cells, a literal `0`
  present, no `<` values, no not-detected tokens and no comma decimals, and **73 distinct non-zero
  result strings**. The 73 distinct non-zero strings already establish that at least 73 of the 286
  samples carry a detection, so the file cannot match CFIA's Table 2 count of 13 (this is known, not
  predicted). The exact detection count, the minimum, the maximum and every per-sample value remain
  unread.
- **ota-don-2010:** one WebFetch on 2026-10-25 (run 187) returned the header and the first 15 rows
  verbatim (e.g. sample 0002 Infant Food – Cereal DON 28.8 / OTA 0; 0003 Flour – Wheat DON 136 /
  OTA 0.791; 0006 Beer DON 51; 0007 Wine OTA 0.065) and a paraphrase of the first third. Blindness
  for this file is therefore "partly seen", stated plainly. No prediction below rests on any value
  from those rows.

Non-detect rule (registered): a blank cell, a `<`-prefixed value, a not-detected token or the
number `0` is a non-detect (0 ppb); any number above 0 is a detection. The census shows that in all
three files non-detects are written as a literal `0`, with no `<` and no token, so the detection-limit
trap that caught CFIA's 2011-12 coumarin file does not arise here.

## Findings already established by the names-only census (confirmed by the gate, not predictions)

These are documented up front because the census read them without reading any value. The sealed
job re-reads the SHA-pinned files and confirms them.

- **F1 — don-infant-2018 carries 286 samples, not 288.** The report states 288 samples throughout
  (Table 1 grand total; the results text "a total of 288 samples"; Table 4 "Canada (CFIA) … 288").
  The open file carries **286** distinct sample numbers (286 rows, one DON row each). A 2-sample gap
  between the published report and its own open file.
- **F2 — don-2011 carries 1395 samples, not 1,391.** The 2011-12 summary page's category breakdown
  sums to 1,391 (infant formula 98, infant cereals 59, other grain 126, wheat 102, corn 73, oat 32,
  breads/baked goods/crackers 193, breakfast cereals 255, beers 150, soy products 198, dried fruits
  105). The open file carries **1395** samples (one DON row each). A 4-sample gap.
- **F3 — ota-don-2010 carries 943 samples, matching the summary page.** 1886 rows = 943 samples × 2
  toxins; the summary's category breakdown sums to 943. No gap.

## Report figures (verified from the PDF text, re-checked for this note)

don-infant-2018 report (PDF SHA-256 `05ab2204592091a88c3fb3ba834aaaaa1db6673d5b1034dabc153fa77a705d85`;
text copy in `myco-census-v2/out/reports/don-infant-cereal-2018-19.txt`):

- Methods: one lab LOD 0.2 ppb, the other 20 ppb; "a reporting limit for DON of 20 ppb … for all
  matrices was imposed".
- Results text: "DON was not detected in 275 (95.5%) samples. In the remaining 13 samples, DON
  levels ranged from 44.1 ppb to 250 ppb."
- Table 2 (per grain; n / positives / min / max / avg): barley 7/6/25/250/102, buckwheat 4/0/–/–/–,
  multigrain 74/4/30/**150**/81, oat 115/2/36/64/50, rice 44/0/–/–/–, wheat 44/1/–/22/–. Positives
  sum 13; minima 22–36 ppb.
- Table 3 (2018-19 rows; n / positives(%) / min / max / avg): barley 7/6(86)/25/250/102, buckwheat
  4/4(0)/–/–/–, multigrain 74/39(53)/0.80/**110**/13, oat 115/49(43)/0.70/64/7.2, rice 44/7(16)/
  0.60/13/4.2, wheat 44/22(50)/1.3/22/6.0. Positives sum **123**; minima 0.60–1.3 ppb.
- Table 4: Canada (CFIA) 2018-2019, 288 samples, 13 (4.5%) detected, min 25, max 250, avg 82.
- Table 3, 2010-11 infant-cereal rows (cross-report): barley 2/1/–/128/–, multigrain 22/22/1.2/56/15,
  oat 23/21/1.1/14/4.4, rice 34/21/1.2/64/5.6, wheat 10/10/1.9/50/24. n sum **91**, positives sum 75,
  max 128, min 1.1. (The 2010-11 summary page gives 93 infant cereals.)

ota-don-2010 summary page: 943 samples tested for both OTA and DON; OTA 628/943 not detected, range
0.040–6.773 ppb, 8 above Health Canada's proposed levels (5 infant cereals, 1 breakfast cereal, 1
wheat flour, 1 wheat germ); DON 388/943 not detected, range 1–2060 ppb, no DON in any wine or dried
fruit. don-2011 summary page: 1,391 samples, 37% not detected, range 1.0–2460 ppb, every category
had detectable DON except dried fruits.

**The internal contradiction the file can settle.** For the same 286 infant-cereal samples, Table 2
reports 13 positives (all at or above the 20 ppb imposed reporting limit) and Table 3 reports 123
positives with minima of 0.60–1.3 ppb. Both can be true at once only if Table 2 counts results at or
above 20 ppb and Table 3 counts results down to the 0.2 ppb LOD. The open file holds the per-sample
values and settles it (P1).

## Yardsticks (DON; ng/g = ppb)

EU Reg. (EU) 2024/1022 (applies 1 July 2024): baby food / processed cereal-based food for infants
and young children **150** (dry matter, excl. rice); cereals to the final consumer 750; breakfast
cereals 400. Codex CXS 193: infant cereal-based foods 200. Health Canada OTA proposed levels (as in
ota-foods 0.1.0): infant cereal 0.5, wheat bran 7, other grain-based 3; dried vine fruit 10.

## Gate (only facts known from the names-only census; no value involved)

SHA-256 of all three files; row counts 286 / 1395 / 1886; distinct samples 286 / 1395 / 943;
rows-per-sample 1 / 1 / 2; unit `ng/g` on every row; Component = {Deoxynivalenol 286} / {Deoxynivalenol
1395} / {Deoxynivalenol 943, Ochratoxin A 943}; every result parses (no unparseable cell); and the
result format is non-detect-as-literal-0 only (no `<`, no token, no comma decimal) in all three files.
If any gate check fails, the predictions are reported but not graded, and an amendment follows.

## Blind predictions (graded by the sealed job)

**don-infant-2018 — resolving Table 2 vs Table 3.**
- **P1** The file follows Table 3's regime, not Table 2's: the number of detected samples is in
  **[100, 135]**, and **exactly 13** samples carry a value at or above 20 ppb. *Why:* Table 2's 13
  and Table 3's 123 differ only by the imposed 20 ppb reporting limit; the open file keeps the raw
  LOD-0.2 values; the census already shows ≥ 73 detections, so Table 2's 13 cannot be the detection
  count.
- **P2** The overall maximum is **250 ppb**, and the smallest detected value is **below 1 ppb**.
  *Why:* both tables and Table 4 give the maximum as 250; Table 3's minima reach 0.60 (rice).
- **P3** Among values at or above 20 ppb, the smallest is **22 ppb** (Table 2 wheat), so the results
  text's stated minimum of "44.1 ppb" is wrong. *Why:* Table 2 prints a wheat minimum of 22 and a
  barley minimum of 25; 44.1 appears nowhere in the tables.
- **P4** **1–4** samples exceed the EU 2024/1022 baby-food DON level of 150 ppb. *Why:* barley's six
  positives reach 250 (avg 102); multigrain's maximum is at most 150, which does not exceed 150.

**ota-don-2010 — DON side (summary and cross-report).**
- **P5** DON is detected in **exactly 555** of the 943 samples (summary: 388 not detected). *Why:*
  a direct count against the summary figure.
- **P6** The DON minimum detected value rounds to **1 ng/g** and the DON maximum is **2060 ng/g**
  (summary range 1–2060).
- **P7** **No** wine and **no** dried-fruit sample (Raisin, Fig, Date, Apricot, Prune) has a detected
  DON value. *Why:* the summary states no DON in any wine or dried fruit.
- **P8** The **Infant Food – Cereal** samples (census: 93) show DON detected in **73–77** of them,
  with maximum **128** ng/g and minimum rounding to **1.1** ng/g. *Why:* the 2018-19 report's Table 3
  2010-11 rows sum to 75 positives of 91, max 128, min 1.1 — and the file's 93 (vs Table 3's 91) is
  the second file-vs-report gap this study documents.

**ota-don-2010 — OTA side.**
- **P9** OTA is detected in **exactly 315** of the 943 samples (summary: 628 not detected), with
  minimum **0.040** and maximum **6.773** ppb.
- **P10** **Exactly 8** grain-based samples exceed Health Canada's proposed OTA levels (infant cereal
  0.5, wheat bran 7, other grain-based 3 ppb), of which **5** are Infant Food – Cereal. *Why:* the
  summary says 8, of which 5 are infant cereals. The file has no "wheat germ" label (its wheat-type
  labels are Flour – Wheat, Wheat Products, Bran – Wheat), so CFIA's per-label attribution of one
  "wheat germ" may land on a different label; the total and the infant-cereal count are the test.

**ota-don-2010 — the novel co-occurrence (discovery).**
- **P11** Within a sample, OTA and DON detection show **no strong association**: the odds ratio of
  the 943-sample 2×2 table (OTA detected × DON detected) is in **[0.5, 2.0]**. *Why:* OTA is produced
  mainly by storage moulds (Aspergillus, Penicillium) and DON by field Fusarium, different fungi at
  different stages, so a strong within-sample link is not expected. As far as a prior-art search
  found (run 188: Dutch 2007-16 and Korean 2009-16 feed studies are the closest), no per-sample
  OTA–DON co-occurrence analysis of CFIA's open retail data has been published; this is, to our
  knowledge, the first. Reported with the full 2×2 table and a Fisher exact p-value regardless of
  the band.

**don-2011.**
- **P12** The DON non-detect share rounds to **37%**, the minimum detected rounds to **1.0** and the
  maximum is **2460** ng/g (summary range 1.0–2460), and **no** dried-fruit sample (Date, Apricot,
  Raisin, Fig, Currant, Mango, Prune, Cherry, Cranberry, Mixed Fruit, Papaya, Blueberry, Banana,
  Apricot – Organic; census sum 105) has a detected DON value.

## Not graded, but reported

The result format census of each file; per-file detection counts and ranges; the full OTA×DON 2×2
table and odds ratio with its Fisher p-value; and a per-sample CSV of the ota-don-2010 file (both
toxins) so the co-occurrence is reproducible. Grain-level checks for the infant-cereal files (Table 1
grain sizes, the multigrain maximum of Table 2 vs Table 3, barley "100%" vs 6 of 7) are **not
gradable**: all three files label every infant-cereal sample with the single Product value
"Infant Food – Cereal" and carry no grain column, so the per-grain breakdowns in the reports cannot
be rebuilt from the open files. This is stated so the study is not read as settling them.

Grading code `myco_don.py` and offline tests `test_myco_don.py` are committed with this note; the
sealed job `myco-don-v1` runs `check_prereg.py` (which waits for this note to be public, then makes
the bundled modules equal the published copies) before reading any value.
