# aflatoxin-figs-2009 0.1.0: CFIA's open 2009-10 aflatoxin file for dried figs and dried dates — result

RESULT-MARKER: aflatoxin-figs-2009-0.1.0-result

By MV2 of Munim, Inc. Prepared with AI agents working in his name. Text CC BY 4.0; code Apache-2.0.

This grades the pre-registration [aflatoxin-figs-2009-0.1.0-prereg.md](aflatoxin-figs-2009-0.1.0-prereg.md),
which was public first, at tag `v0.4.71`. The sealed job `aflatoxin-figs-2009-v1` ran on 2026-10-28
at 16:09 UTC (python:3.12, 1 GB, no host paths). It waited for the registration's marker to be
public and checked that its bundled `aflatoxin_figs_2009.py` and `test_aflatoxin_figs_2009.py`
were byte-identical to the published copies. It ran the 12 offline tests and only then read the
SHA-256-pinned file. **The gate passed, and 8 of 9 graded items held: both consistency checks and
five of six blind predictions. P6 missed: aflatoxin G1 is in one positive sample, not two.**

This is a reference comparison, not a compliance finding. Canada sets no aflatoxin maximum level
for dried fruit, and the EU levels quoted below are today's, not those of 2009-10. It is not about
any brand, and it is not dietary or medical advice. CFIA referred all positive results to its
programs for follow-up.

## Headlines

1. **The file agrees with CFIA's summary page on every result it prints.** No dried date carries
   aflatoxin (0 of 50), four dried figs do, and their totals run from 7.46 to 78.66 ppb, printed as
   7.5 and 78.7 (C1, C2 held). The one disagreement is the product split recorded before grading
   (L1): the page says 49 dates and 51 figs, the file labels 50 of each. Both give the same printed
   "92%" of figs without aflatoxin (47 of 51 = 92.2%; 46 of 50 = 92.0%), so the page's own
   percentage cannot say which is right.
2. **`Total Aflatoxins` is the per-sample sum of the four forms.** In all 100 samples the total
   equals B1 + B2 + G1 + G2 to within 0.01 ppb (P1 held). The single 0.01 gap is a rounding step
   in one Turkish fig (57.87 + 13.67 = 71.54, printed total 71.53). This is the fourth CFIA file in
   which a group row is a per-sample sum, after the 2018-19 multi-mycotoxin fumonisin, ergot and
   HT-2/T-2 rows.
3. **Three of the four positive figs are above both EU levels in force today, by a wide margin.**
   A Greek fig (78.66 ppb total) and two Turkish figs (72.33 and 71.53) exceed the EU's dried-fig
   levels of 6.0 µg/kg aflatoxin B1 and 10.0 µg/kg for the sum, seven-fold or more on the sum
   (P5 held). The fourth, a US fig, has 5.18 B1 and 7.46 in total, under both. Against the figures
   CFIA's page quoted for the time (4 ppb in total for dried fruit eaten as is, 10 ppb for fruit
   to be processed further), all four exceed 4 and three exceed 10.
4. **One fig is G1-dominated.** B1 is the largest form in three positives and is detected in all
   four (P2, P3 held). The Greek fig is the exception: 53.83 ppb G1 against 22.0 B1, so G1 is 68%
   of its total. It is the only sample with any G1 or G2, so P6 (G1 in at least two positives)
   missed. G-type aflatoxins are usually linked to *Aspergillus parasiticus* rather than
   *A. flavus*; this file cannot test that, so it is noted, not claimed.

## Data

- **AF:** CFIA, "2009-2010 Aflatoxin in Dried Figs and Dried Dates". Open Government Portal dataset
  `bfac4a9d-ba2f-433a-8425-9b2fc7689d72`, resource `8339ffec-f854-430c-b3c8-4718e18ed4b2`,
  SHA-256 `5d3300b7…b055d` (60,259 bytes, Windows-1252), Open Government Licence – Canada.
  500 rows on 100 samples, five rows each (B1, B2, G1, G2, Total Aflatoxins), all in `ppb`, every
  `Function` `Import`. Non-detects are a literal 0 (486 cells); 14 cells are above 0.

## Gate (passed)

All 12 checks held: the SHA-256; 500 rows, 100 samples, five rows per sample with one row per
component; one product and one origin per sample; the product (250/250 rows) and origin row
counts; one known unit (`ppb`); only positive or literal-0 cells (both present); and exactly 14
non-zero cells.

## Graded items: 8 of 9 held

| ID | Registered | Observed in the file | Met |
|---|---|---|---|
| G | gate (above) | 12 of 12 checks | ✅ |
| C1 | no date positive, exactly 4 figs positive | 0 of 50 dates, 4 of 50 figs | ✅ |
| C2 | positive totals 7.5–78.7 ppb at printed precision | 7.46 – 78.66 | ✅ |
| P1 | Total = B1 + B2 + G1 + G2 within 0.25 ppb, every sample | largest gap 0.01 | ✅ |
| P2 | B1 detected in every positive | 4 of 4 | ✅ |
| P3 | B1 the largest form in ≥ 3 positives | 3 | ✅ |
| P4 | ≥ 2 positives declared from Turkey | 2 | ✅ |
| P5 | ≥ 3 positives above a current EU level for dried figs | 3 (all three above both) | ✅ |
| P6 | G1 detected in ≥ 2 positives | **1** | ❌ |

## The four positive samples

| sample | product | declared origin | B1 | B2 | G1 | G2 | total | above EU B1 6.0 | above EU sum 10.0 |
|---|---|---|---|---|---|---|---|---|---|
| 2009ATX0043 | fig | Greece | 22.0 | 1.64 | 53.83 | 1.19 | 78.66 | yes | yes |
| 2009ATX0012 | fig | Turkey | 65.7 | 6.63 | 0 | 0 | 72.33 | yes | yes |
| 2009ATX0027 | fig | Turkey | 57.87 | 13.67 | 0 | 0 | 71.53 | yes | yes |
| 2009ATX0003 | fig | United States | 5.18 | 2.28 | 0 | 0 | 7.46 | no | no |

All values in ppb (= µg/kg). The 14 non-zero cells are these four totals plus ten form results.

## By declared origin (exploratory)

| figs | n | positive | | dates | n | positive |
|---|---|---|---|---|---|---|
| Turkey | 20 | 2 | | Iran | 20 | 0 |
| Greece | 15 | 1 | | United States | 10 | 0 |
| United States | 10 | 1 | | China | 6 | 0 |
| France | 2 | 0 | | Tunisia | 5 | 0 |
| Italy | 2 | 0 | | Unknown | 4 | 0 |
| Unknown | 1 | 0 | | Saudi Arabia | 3 | 0 |
| | | | | Algeria | 2 | 0 |

Counts this small say nothing about any country's figs. They show only where the four positives
came from. 97 of the 100 samples give `BC` as region; 3 give `UNKNOWN`.

## A correction to the pre-registration

The pre-registration says the samples were taken "2009-11-02 to 2010-01-27". That is wrong. The
file's `Date Sampled` column runs from **2 November 2009 to 10 March 2010**. The census took the
smallest and largest of the `DD-Mon-YY` strings in text order, and "27-Jan-10" sorts last as
text, which matches the registered range exactly. The dates entered no graded item, so no grade
changes. The census tool's date ranges should be read as text ranges until it parses dates.

## Limits

- One survey, 100 samples, four positives. The figures describe this file, not dried figs in
  general.
- The file gives one result per sample. It carries no limit of detection, and CFIA's summary page
  gives none either.
- The EU levels are a reference only. They did not apply in Canada, and today's dried-fig levels
  (Regulation (EU) 2023/915, carried over from Regulation (EU) No 1058/2012) came after this survey.
- L1 (49/51 against 50/50) stays open: the labels and the printed percentage cannot settle it. Only
  CFIA's full report, which is available on request, can.
- This note does not say why any sample is contaminated. Only CFIA can say more about its samples.

Prior art: on 2026-10-28, searches for analyses of this open file found none. CFIA's summary page
gives the figures checked above, and its 2010-11 report (0 of 90 dried dates and figs positive)
compares the two surveys only by their headline. As far as we know, this is the first per-sample
reading of the file.

## Reproduce it

- `data/aflatoxin_figs_2009_samples.csv`: one row per sample (sample, product, origin, region,
  date sampled, B1, B2, G1, G2, total, in ppb), the sealed job's output.
- `data/aflatoxin_figs_2009_summary.json`: the sealed grader record (gate, census, every check and
  prediction with its observed values, the positive samples, provenance).
- `test_aflatoxin_figs_2009_result.py`: a pinned test. It does not import the grader. With its own
  code it rebuilds the product and origin counts, C1, C2, P1–P6, the EU counts and the date range
  from the CSV, and checks them against the sealed record.

A sealed follow-up job (`aflatoxin-figs-2009-result-v1`) fetches these published files from
GitHub and re-runs the pinned test on them. The grading code `aflatoxin_figs_2009.py` and the
pre-registration are at tag `v0.4.71`.
