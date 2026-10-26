# Pre-registration: CFIA's open livestock-feed mycotoxin file against its own report (feed-myco 0.1.0)

PREREG-MARKER: feed-myco-0.1.0-prereg

By MV2 of Munim, Inc. Prepared with AI agents working in his name. Text CC BY 4.0; code Apache-2.0.

This note is written and published **before** any test result in CFIA's open livestock-feed
mycotoxin file is read by the grading code. A names-only census (job `feed-myco-census-v1`,
2026-10-25; output committed here as `data/feed_myco_census.json`) recorded the file's SHA-256, its
headers, row and sample counts, the label counts of the descriptive columns, and a **format**
census of the result column (how many cells are `<` censored and how many are numbers). It
reported no detection rate, no value and no censoring limit. Nothing else in the file has been
read. The public commit timestamp of this note fixes every check and prediction below before the
sealed job `feed-myco-v1` reads a single result.

A reference comparison, not a compliance finding about any feed, mill, farm or brand, and not
veterinary advice. Action levels in CFIA's report apply to the **total diet** of a species, and
most samples here are single ingredients labelled "Multiple species", so the comparison against
a level is the report's own convention, not a judgement on any lot.

## Data

CFIA, "Mycotoxin Monitoring Program for Livestock Feeds – Results from April 1, 2000 – March 31,
2018", Open Government Licence – Canada. Dataset `2d636f59-5f04-4725-afae-376850bc71d4`, English
CSV resource `b8cad53e-0a93-4366-a764-246fbc980c1f`, SHA-256
`6de28d69d6d2fe0552aae55720b2b481b6673efafbcccf90dc87f7002a2c1491` (5,872,784 bytes, UTF-8 with
BOM). The supplemental dictionary says `<` marks a result "less than the limit of quantification
(LOQ)", that the LOQ "is specific for each mycotoxin and sample matrix", and that methods are those
of the CFIA Ottawa Laboratory (Carling).

Census facts used below: 40,862 rows; 3,258 distinct System IDs; 10 columns (Fiscal Year, System
ID, Target Species, Feed Type, Ingredient Type, Ingredient Common Name, Sampled at – Province,
Mycotoxin, Test Result, Unit); units mg/kg (32,019 rows) and µg/kg (8,843); result format 35,368
censored `<` cells and 5,494 numbers (no blank, zero or token); 18 mycotoxin labels for 17
analytes, because 3-acetyl-DON is spelled two ways (`3-Acetyldeoxynivalenol` 3,063 rows,
`3-AcetyldeoxyNivalenol` 184). Rows per sample are mostly 11 (1,423 samples), 12 (1,094), 16 (163)
and 17 (530), consistent with an 11-toxin Fusarium/OTA panel plus fumonisins and/or the five
aflatoxin rows. 10 provinces; 19 fiscal-year labels (2000-2001 … 2017-2018, plus one blank).

**The report.** CFIA, "National feed inspection program: results for Program-15B (April 1, 1990 –
March 31, 2018)" (inspection.canada.ca, page dated 2019-04-05). Its Table 1 prints, for each
fiscal year and for seven mycotoxins, the percentage of samples below the "lowest action level"
(AL) and, in parentheses, the number of samples: DON < 1 ppm, HT-2 < 0.1 ppm, T-2 < 1 ppm, DAS < 1
ppm, FUM < 1 ppm, OTA < 0.2 ppm, ZEA < 1 ppm. All 18 rows from 2000-2001 to 2017-2018 are
transcribed in `feed_myco.py` (`_T1`); a unit test checks that every printed percentage equals k/n
for some whole k (all 126 cells pass), and that the column sums equal the census counts below.

## Findings already established by the report and the census (no file value involved)

- **R1 — the open file is the report's last 18 of 28 years.** The report covers April 1990 – March
  2018; the file starts in April 2000. Of the report's 5,449 DON samples, 2,211 (40.6%) are from
  1990-2000 and have no open per-sample record.
- **R2 — six of seven Table 1 columns sum exactly to the file.** Summed over 2000-2001 … 2017-2018,
  Table 1's sample counts equal the file's row counts for DON (3,238), T-2 (3,243), DAS (3,247),
  FUM (1,673), OTA (3,240) and ZEA (3,240).
- **R3 — HT-2 does not: 3,202 in the report, 3,243 in the file.** The gap of 41 equals, year by
  year, the report's own T-2 count minus its HT-2 count: 2010-11 (211 − 209 = 2), 2011-12 (209 −
  194 = 15), 2012-13 (198 − 187 = 11), 2013-14 (159 − 146 = 13); in every other year the two
  counts are equal. So the file appears to hold HT-2 results the report left out (C2, C5 test
  where and why).
- **R4 — the report's text misquotes its Table 1.** The text says Table 1's below-AL share is
  "lowest for DON (81.3%)", but Table 1's DON total is **82.22%**. 81.3% is the single-ingredient
  row of Table 3 (81.30) and the multiple-species row of Table 5a (81.32). The text's "17.7% of the
  samples for DON were above the lowest AL of 1ppm" fits neither exactly (100 − 82.22 = 17.78;
  100 − 81.30 = 18.70). These are 1990-2018 totals, so the open file cannot grade them.

## Registered rules

- **Result:** `<x` is a non-detect with censoring limit x (in the row's unit); a number above 0 is
  a detection; `0` would be a non-detect without a limit; anything else is unparseable.
- **Units:** values are converted to mg/kg (= ppm) by an explicit table: mg/kg ÷ 1, µg/kg ÷ 1000.
- **Analytes:** labels are matched case-insensitively, so both 3-acetyl-DON spellings are 3-ADON.
- **Below the AL (Table 1 convention):** a non-detect counts as below; a detection is below if its
  ppm value is strictly less than the AL (the "at or below" count is reported too).
  **Indeterminate:** a non-detect whose censoring limit is above the AL.
- **Sample count** for a Table 1 cell = the number of rows for that analyte in that fiscal year.
- **Co-occurrence:** per System ID, an analyte is "detected" if any of its rows is a detection;
  the 2×2 table counts samples tested for both analytes; odds ratio with a Haldane 0.5 correction
  only if a cell is zero; two-sided Fisher exact p.
- **Regions:** West = Alberta, British Columbia, Manitoba, Saskatchewan; East = the six other
  provinces in the file. **Periods:** early = 2000-01 … 2008-09, late = 2009-10 … 2017-18.
- **Corn:** an ingredient common name containing "corn" (any case). "Other named" = a non-blank
  name without "corn".

## Gate (only census facts)

SHA-256; the 10 headers in order; 40,862 rows; 3,258 samples; units exactly {mg/kg 32,019, µg/kg
8,843}; the 18 mycotoxin labels with their census row counts; result format exactly {censored
35,368, numeric 5,494}. If any gate check fails, the checks and predictions are reported but not
graded, and an amendment follows.

## Consistency checks against the report (graded)

- **C1** File sample counts equal Table 1's n in **at least 107 of the 108** year × {DON, T-2, DAS,
  FUM, OTA, ZEA} cells. *Why:* R2 makes the column sums equal already; one cell of slack for the
  single blank-fiscal-year row.
- **C2** In **at least 17 of 18** years the file's HT-2 count equals Table 1's **T-2** n, so the 41
  extra HT-2 rows sit in 2010-11 to 2013-14 (R3).
- **C3** DON: the file reproduces Table 1's n **and** "% below 1 ppm" (to the printed two
  decimals) in **at least 16 of 18** years.
- **C4** T-2, DAS, FUM, OTA and ZEA: n and % below the lowest AL reproduced in **at least 85 of
  90** year cells.
- **C5 (mechanism)** HT-2: in **every** year, the rows the report leaves out (file n − printed n)
  equal the HT-2 non-detects whose censoring limit is **above 0.1 ppm** — results that cannot be
  called "below 0.1 ppm". *Why:* the report says the HT-2 method's quantification limit "was 0.1
  ppm until recently" and uses 0.1 ppm as the HT-2 AL; a matrix with a higher limit makes a
  non-detect indeterminate against it. This is the registered explanation of R3; it may well fail.
- **C6** HT-2: with those indeterminate rows dropped, n and "% below 0.1 ppm" match Table 1 in
  **at least 16 of 18** years.
- **C7** **No** aflatoxin result (B1, B2, G1, G2 or total) exceeds 20 ppb. *Why:* the report says
  "aflatoxins, above the feed regulatory level of 20ppb, have not been detected".

## Blind predictions (graded)

- **S1** Every `<` cell carries a numeric censoring limit (no bare "<LOQ").
- **P1** DON is the most frequently detected of the 17 analytes (share of results detected).
- **P2** DON is detected in **35–75%** of its results. *Why:* Table 1 implies about 22% of
  2000-2018 DON samples at or above 1 ppm; with a quantification limit near 0.1 ppm and a
  right-skewed distribution, roughly half should quantify.
- **P3** Within-sample DON × zearalenone detection: odds ratio **≥ 3**, Fisher p < 0.001. *Why:*
  both are made by *Fusarium graminearum* in the field.
- **P4** Within-sample DON × 15-acetyl-DON: odds ratio **≥ 10**, Fisher p < 0.001. *Why:* 15-ADON
  is co-produced with DON by the 15-ADON chemotype.
- **P5** OTA × DON: odds ratio **> 1** with Fisher p < 0.05 — an out-of-sample replication in feed
  of the association found in CFIA's retail foods (myco-don 0.1.0 P11 missed: OR 8.54). Gradable
  only if OTA is detected in at least 10 samples tested for both.
- **P6** 15-ADON is detected in **more** samples than 3-ADON. *Why:* most samples are corn and
  mixed grains from Quebec and Ontario, where the 15-ADON chemotype has dominated.
- **P7 (chemotype map)** Among samples with any acetyl-DON detected, the share with 3-ADON detected
  is **higher in the West** than in the East, Fisher p < 0.05; gradable if each region has at
  least 10 such samples. *Why:* field surveys (e.g. Ward et al. 2008, *Fungal Genetics and
  Biology* 45:473) documented a rapid rise of the 3-ADON chemotype in western Canadian wheat from
  the late 1990s, while eastern populations stayed mostly 15-ADON.
- **P8 (chemotype trend)** The same 3-ADON share is **higher in 2009-10 … 2017-18** than in 2000-01
  … 2008-09 (point estimate; gradable if each period has at least 10 such samples).
- **P9** Fumonisins are detected **at least 3×** as often in corn-named ingredients as in other
  named ingredients (gradable if each group has at least 30 fumonisin results). *Why:* fumonisins
  come from *Fusarium verticillioides* / *proliferatum*, chiefly in corn.
- **P10 (limit drift)** The most common DON censoring limit in 2014-15 … 2017-18 is **lower** than in
  2000-01 … 2003-04 (gradable if each period has at least 10 censored DON results). Roughly a coin
  flip; registered because the drift is itself unmeasured.
- **P11** The most common HT-2 censoring limit is **0.1 ppm in every year 2000-01 … 2012-13**, and
  **below 0.1 ppm** in at least one year 2013-14 … 2017-18. *Why:* the report's "0.1 ppm until
  recently".
- **P12** Aflatoxin B1 is detected in **at most 5%** of its results.

As far as searches on 2026-10-25 and 2026-10-26 found, no published analysis uses this per-sample
file, and no one has rebuilt CFIA's Program-15B tables from it. The acetyl-DON split (P6–P8) would
be, to our knowledge, the first 3-ADON/15-ADON chemotype-proxy map from a regulator's feed
monitoring data. Caveat stated up front: detecting 3-ADON in a feed sample is a chemical proxy,
not a genotype; it depends on the censoring limit and on the grain's origin, which "Sampled at –
Province" does not record (the dictionary says so).

## Not graded, but reported

Every Table 1 cell rebuilt (`feed_myco_table1.csv`: printed and file n and %, the at-or-below
variant, indeterminate counts); per-analyte, per-year detection counts; the full censoring-limit
table by analyte and year (`feed_myco_limits.csv`, the first open LOQ history of this program as
far as we know); units by analyte and year; DON results at or above 1, 2, 5 and 10 ppm (the
Feeds Regulations, 2024 total-diet maximums range from 1 ppm for starter swine to 10 ppm for beef
cattle; single ingredients are not total diets, so these counts are context, not compliance);
where the 184 `3-AcetyldeoxyNivalenol` rows and the blank-year row sit; and a per-sample table
(`feed_myco_samples.csv`: descriptors, DON ppm and a detection flag per analyte) so every
co-occurrence and chemotype figure can be recomputed. The report's Tables 2–5 (by CFIA area, feed
type, ingredient and species) pool 1990-2018 and are **not gradable** from a 2000-2018 file.

Grading code `feed_myco.py` and offline tests `test_feed_myco.py` are committed with this note.
The sealed job `feed-myco-v1` runs `check_prereg.py` (which waits for this note to be public, then
makes the bundled modules equal the published copies), then the tests, then the grader.
