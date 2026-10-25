# CFIA's 2018-19 DON in infant cereals report: what its own tables say (don-infant-report-check 0.1.0)

<!-- MARKER: don-infant-report-check-0.1.0 -->

By MV2 of Munim, Inc. Prepared with AI agents. Text CC BY 4.0; code Apache-2.0.
Written 2026-10-25. A record of the report alone, made **before any value in CFIA's open
per-sample file for this survey was read**. It is not a finding about any product, brand or
health risk.

## Why this note exists

On 2026-10-06 the Canadian Food Inspection Agency (CFIA) put the per-sample file for its
targeted survey *Deoxynivalenol in Infant Cereals, April 1, 2018 to March 31, 2019* on the Open
Government Portal (dataset `d17f8fe4-1d8b-4d78-8937-5f4f85812e02`, resource
`7e3c4cf6-69fa-4931-9f31-cd78225acf01`, Open Government Licence - Canada). The survey's final
report disagrees with itself in several places. This note puts those disagreements on record
from the report alone, so that a later pre-registered check of the open file
(myco-don 0.1.0, to follow) is graded against figures that were public before the data was read.

Source: the report PDF,
`https://inspection.canada.ca/DAM/DAM-food-aliments/STAGING/text-texte/deoxynivalenol_infant_cereal_1671718288841_eng.pdf`
(9 pages, 849,127 bytes, SHA-256
`05ab2204592091a88c3fb3ba834aaaaa1db6673d5b1034dabc153fa77a705d85`, fetched 2026-10-25). Its
text was extracted with `pdf_text.py` (pypdf 5.1.0) inside a sealed job; every figure below
was read from that text, not from a paraphrase.

## What the report says

**Methods (page 4).** Two laboratories tested the samples. "One laboratory method had a limit of
detection (LOD) of 0.2 ppb and the other had an LOD of 20 ppb. To ensure that the two datasets
could be combined, a reporting limit for DON of 20 ppb (parts per billion) for all matrices was
imposed."

**Summary and results text (pages 2 and 4).** 288 samples. "DON was found in 4.5% of the
samples." "DON was not detected in 275 (95.5%) samples. In the remaining 13 samples, DON levels
ranged from 44.1 ppb to 250 ppb." "DON was not detected in any of the buckwheat or rice infant
cereals and most of the barley cereals. The average DON level was lowest in oat and highest in
barley."

**Table 1** (samples by grain and origin; internally consistent, rows and columns add up):
barley 7, buckwheat 4, multigrain 74, oat 115, rice 44, wheat 44; total 288 (34 domestic, 100
imported, 154 unspecified; all 44 wheat cereals are of unspecified origin).

**Table 2** (page 5; positives / minimum / maximum / average, ppb):

| Grain | n | Positives | Min | Max | Avg |
|---|---:|---:|---:|---:|---:|
| Barley | 7 | 6 | 25 | 250 | 102 |
| Buckwheat | 4 | 0 | - | - | - |
| Multigrain | 74 | 4 | 30 | 150 | 81 |
| Oat | 115 | 2 | 36 | 64 | 50 |
| Rice | 44 | 0 | - | - | - |
| Wheat | 44 | 1 | - | 22 | - |

Sum of positives: 13, matching the text and the summary's 4.5% (13 / 288 = 4.51%).

**Table 3** (page 6; the 2018-19 rows; positives (%) / minimum / maximum / average, ppb):

| Grain | n | Positives (%) | Min | Max | Avg |
|---|---:|---|---:|---:|---:|
| Barley | 7 | 6 (86) | 25 | 250 | 102 |
| Buckwheat | 4 | 4 (0) | - | - | - |
| Multigrain | 74 | 39 (53) | 0.80 | 110 | 13 |
| Oat | 115 | 49 (43) | 0.70 | 64 | 7.2 |
| Rice | 44 | 7 (16) | 0.60 | 13 | 4.2 |
| Wheat | 44 | 22 (50) | 1.3 | 22 | 6.0 |

Each printed percentage matches its count (39 / 74 = 52.7%, 49 / 115 = 42.6%, 7 / 44 = 15.9%,
22 / 44 = 50%, 6 / 7 = 85.7%). Positives: 123, or 127 if buckwheat's "4" is a count.

**Table 4** (page 7; comparison with other jurisdictions) gives Canada 2018-2019 as 288 samples,
13 (4.5%) detected, minimum 25, maximum 250, average 82 ppb.

## Where the report disagrees with itself

1. **How many samples had DON: 13 or 123.** Table 2, the text, the summary and Table 4 say 13
   (all at or above 20 ppb). Table 3 says 123 for the same 288 samples, with minima of 0.60 to
   1.3 ppb, below the 20 ppb reporting limit the methods section says was imposed on all
   matrices. The low values can only come from the laboratory with the 0.2 ppb LOD; Table 3
   appears to report them without the reporting limit.
2. **Multigrain maximum: 150 or 110 ppb.** Censoring at 20 ppb can remove low values, not
   lower a maximum. If Table 3 were simply the uncensored version of Table 2, its multigrain
   maximum would be at least 150. One of the two figures is wrong. (Barley 250, oat 64 and
   wheat 22 agree between the tables.)
3. **Lowest positive: 44.1, 22 or 25 ppb.** The text says the 13 positives ranged from 44.1 to
   250 ppb. Table 2's own minima are 25 (barley), 30 (multigrain), 36 (oat) and a single wheat
   value of 22, all below 44.1. Table 4 gives 25, which is Table 2's minimum without the wheat
   value.
4. **Barley: 100%, 86% or "most not detected".** The discussion says "100% of barley infant
   cereal samples contained a quantifiable amount of DON vs. 50% in the three previous
   surveys." Tables 2 and 3 say 6 of 7 (86%). The results text says DON was not detected in
   "most of the barley cereals".
5. **Buckwheat "4 (0)".** Table 3 prints 4 positives at 0%; Table 2 says 0 positives.
6. **Which grain has the lowest average.** "Lowest in oat" holds for Table 2 (oat 50,
   multigrain 81, barley 102). Under Table 3 rice (4.2) and wheat (6.0) are lower than oat (7.2).

Table 4's average of 82 ppb is consistent with Table 2 within rounding (81.4 from the rounded
rows), so it is not listed as a disagreement.

## Two cross-report counts to check

Table 3 also reprints infant-cereal rows from CFIA's 2010-11 and 2011-12 surveys, whose per-sample
files were released on the same day. CFIA's summary pages for those surveys list 93 and 59
infant cereals. Table 3's grain rows add up to 91 (2010-11: barley 2, multigrain 22, oat 23,
rice 34, wheat 10) and 54 (2011-12: barley 4, multigrain 14, oat 13, rice 12, wheat 11). This
is not necessarily an error: the missing 2 and 5 may be cereals of a grain Table 3 does not list.
The open files can tell.

## What the open file can settle, and what it cannot

The per-sample file can show which reading of the survey CFIA published as data: values down to
about 0.6 ppb (Table 3) or only values of at least 20 ppb (Table 2), the true multigrain
maximum, the lowest positive, and the barley count. It cannot show which laboratory tested
which sample unless the file says so. The predictions, the gate and the grading code will be
registered in `docs/myco-don-0.1.0-prereg.md` before any value is read. Until then this note
makes no claim about which table is right.

For scale only, not as a compliance finding: Canada sets no maximum level for DON in infant
cereals. The EU's level for processed cereal-based food for infants and young children is
150 ug/kg (Regulation (EU) 2024/1022), and Codex's is 200 ug/kg (CXS 193). Under both of
CFIA's tables, the 250 ppb barley sample is the highest value in the survey.
