# Three CFIA reports, predictions fixed before their open files are read (bpa-pah-report 0.1.0)

PREREG-MARKER: bpa-pah-report-0.1.0-prereg

Made with AI agents working in MV2's (Munim, Inc.) name. Text CC BY 4.0; code Apache-2.0.
Not a compliance finding, not about any product or brand, and not dietary or medical advice.

## What this is

The Canadian Food Inspection Agency (CFIA) publishes a report page and a per-sample CSV on
open.canada.ca (Open Government Licence - Canada) for each targeted chemistry survey. This note
fixes predictions about three of those files **from the printed reports alone**, before any
census or value of the files is read:

| Short name | Report (inspection.canada.ca slug) | Open file (dataset / resource) | Portal size, MD5 |
|---|---|---|---|
| bpa-2018 | Bisphenol A and BPA alternatives in selected canned foods and infant formula, April 1, 2018 to March 31, 2019 (`final-report-2`) | b8686c21-a8ef-4037-8478-353ed45a0145 / 7a20917c-8aa9-4af6-8ce4-13620ef3af59 | 289,825 B, 5cf4d04c1e4db3825dc51cfe09ea6415 |
| bpa-2020 | Bisphenol A and BPA alternatives in selected canned foods, April 1, 2020 to March 31, 2021 (`bisphenol-and-bpa-alternatives-selected-canne`) | 5b36b36d-4f8b-4b0c-b407-42b8076b3730 / df188f89-3dba-4650-bfbb-e4c46f89d21a | 285,553 B, 31a4ca35a9f46e0d59cc637314c744a9 |
| pah-2019 | Polycyclic aromatic hydrocarbons in selected foods, April 1, 2019 to March 31, 2020 (`polycyclic-aromatic-hydrocarbons-selected-foods`) | 4884f9d1-0a59-4c8e-85ca-157d13411d19 / d5b3cca2-4ccf-4aed-a4d1-0af540422575 | 831,190 B, 0bb033bbcdab8305839d0a8716def1b3 |

Order of work: (1) this note is committed with the census code `cfia_census.py` and its offline
tests; (2) the sealed job `cfia-census-2019-v1` waits until this note is public, then runs a
names-only census of all three files (row, sample, label, unit and origin counts; every result
cell classified by shape only; no value printed, summed or compared); (3) the census grades the
structure items below (marked **[census]**); (4) a grader fixed in a later commit, after the
census and before any value is read, grades the value items (marked **[values]**) and maps file
labels to report product types from the census alone.

Rules for the value items: a sample is "positive" when its value is a number above 0; averages
are over positives only, as every report states; a printed figure matches when the file's value
is within half a unit of its last printed digit. PAH totals are TEQ = benzo[a]pyrene + 0.1 x
benzo[a]anthracene + 0.1 x benzo[b]fluoranthene + 0.01 x chrysene (the report's Table A-1), in
ppb (= ng/g).

Searches on 2026-10-30 found no earlier per-sample analysis of these three open files or check of
them against their reports. Health Canada's published BPA trend work (Food Additives &
Contaminants A 40(6), 2023, doi 10.1080/19440049.2023.2209898) uses Total Diet Study composites,
not these CFIA survey files.

## bpa-2018: the report's four conflicting counts have one explanation

Printed figures (ppb). Table 1 and Table 2: coconut milk 49, infant formula 135, pie filling 98,
tomato-based sauces 95, total 377. Table 2 BPA (n, positive, min, max, average): coconut milk 49,
37, 1.42, 367, 47.0; infant formula 135, 17, 0.92, 2.24, 1.4; pie filling 98, 62, 0.97, 101, 11.2;
tomato-based sauces 95, 48, 1.01, 95.9, 9.78; total 377, 164 (44%), 0.92, 367, 17.8. The summary
says **381** samples, BPA in **43%** and BADGE in **12%**. Table 3 gives this survey's infant
formula as **138** samples, min 0.92, max **5.89**, average **1.65**, and its tomato-based sauces
as **96** samples with Table 2's min, max and average. BADGE: 12 samples (3%), all coconut milk;
top two 524 and 209, the other ten below 63; average 81.9; every BADGE-positive sample also has
BPA. BPF and BPS: none detected. The text: all 135 formulas were liquid and milk-based, 81 in
plastic bottles and 54 in cans.

Report-internal arithmetic (no data): Table 3's counts add up to the summary's total
(49 + 138 + 98 + 96 = 381). With Table 2's 17 formula positives averaging 1.4 (sum 22.95 to
24.65), one more positive at 5.89 gives an average of 1.60 to 1.70 over 18, and Table 3's 1.65
then pins Table 2's formula sum to 23.72-23.90. The summary's 43% fits 165 of 381 (43.3%) or
164 of 381 (43.0%), not Table 2's 164 of 377 (43.5%, printed 44). The summary's BADGE 12% fits no
count: 12 of 381 is 3.1%, 12 of 49 coconut milks is 24.5%.

Predictions:

- **B1 [census]** The open file holds **381** samples: 49 coconut milk, **138** infant formula,
  98 pie filling and **96** tomato-based sauces (the summary and Table 3), not Table 1's 377.
  Competing reading, registered: the file holds 377 and Table 3's 138 and 96 are typing slips.
- **B2 [values]** Infant formula in the file reproduces **Table 3's** row: 18 positives, min
  0.92, max 5.89, average 1.65. Removing the single 5.89 sample leaves 17 positives with min
  0.92, max 2.24 and average 1.4 (Table 2's row). So exactly one of the three formulas Table 2
  leaves out is BPA-positive, and it holds the survey's highest formula value.
- **B3 [values]** Tomato-based sauces: 96 samples, 48 positive, min 1.01, max 95.9, average
  9.78; the one sauce Table 2 leaves out is a non-detect.
- **B4 [values]** All samples: BPA positive in **165 of 381** (43.3%; the summary's 43%), min
  0.92, max 367, average 17.8; coconut milk and pie filling reproduce Table 2 in full.
- **B5 [values]** BADGE: exactly 12 positives, all coconut milk, top two 524 and 209, the other
  ten below 63, average 81.9, and every one also BPA-positive. No count in the file gives 12%.
- **B6 [values]** BPF and BPS: no positive sample (if the file carries them).
- **B7 [census]** If the file names the three extra formulas' form or package, they are not the
  liquid milk-based bottles and cans the text describes (e.g. powder or soy). Competing reading,
  registered: no label separates them.

## bpa-2020: tables, text and co-occurrence

Printed figures (ppb). Table 1 (domestic, imported, unspecified, total): fish 8, 90, 3, 101;
fruit 0, 50, 2, 52; meat 20, 55, 25, 100; pie filling 0, 49, 0, 49; vegetables/products 19, 73,
8, 100; total 47, 317, 38, 402. Table 2 BPA (n, positive, min, max, average): fish 101, 39, 0.91,
395, 43.8; fruit 52, 15, 1.4, 21.4, 6.1; meat 100, 42, 1.2, 479, 43.5; pie filling 49, 16, 1.1,
7.1, 2.1; vegetables 100, 51, 0.96, 151, 55.9; total 402, 163 (41%), 0.91, 479, 40.0. BADGE: fish
5, 3.6, 1580, 330; meat 11, 6.5, 372, 66.1; vegetables 1, 14.0. BPF: fish 1 at 94.8; meat 1 at
19.6. BPS: fish 1 at 46.0; meat 5, 0.96, 191, 52.1; vegetables 1 at 0.98. Text: BADGE 17 (4%),
14 of them imported, overall average 141; 8 of the 17 also contain BPA, all imported meat or
fish; the BPF positives are a chicken of unspecified origin and an imported herring; the five BPS
meats are imported corned beef that also contain BPA; the fish BADGE values after 1580 include
51 (mackerel, "second highest"); all 31 BPA-positive fruit and pie filling samples are imported.
The vegetables paragraph says "163 (41%)" where Table 2 says 51 (51%).

- **C1 [census]** 402 samples split 101 / 52 / 100 / 49 / 100 as Table 1, with Table 1's origin
  counts (the file's Function or Origin column) in at least 4 of the 5 rows.
- **C2 [values]** Table 2 reproduces: at least 5 of its 6 rows match all four of positive count,
  min, max and average. Vegetables has 51 positives (not 163).
- **C3 [values]** Tables 3-5 reproduce: 17 BADGE, 2 BPF and 7 BPS positives in the printed
  product rows, every printed min, max and average matching.
- **C4 [values]** The co-occurrence text holds: 8 of 17 BADGE positives have BPA and all 8 are
  imported meat or fish; 14 of 17 BADGE positives are imported; every BPS-positive meat has BPA;
  the second-highest fish BADGE value is 51; every BPA-positive fruit or pie filling is imported.

## pah-2019: two printed averages for olive oil

Printed figures (ppb TEQ). Table 1: infant formula 0, 31, 3, 34; nuts/nut butters 40, 46, 28,
114; olive oil 1, 133, 14, 148; total 41, 210, 45, 296. Table 2 (n, detected, min, max, average):
infant formula 34, 16 (47), 0.001, 0.776, 0.12; nuts 114, 44 (39), 0.001, 2.93, 0.17; olive oil
148, 121 (82), 0.002, 3.25, **0.24**; total 296, 181 (61), 0.001, 3.25, 0.21. Table 3 repeats the
2019 rows but gives olive oil **0.23**. Text: milk-based formula 16 of 23 positive (0.001 to
0.776), no soy formula positive; one pumpkin seed butter at 2.93, every other nut sample below
0.773; three olive oils elevated, all others below 0.700; four pomace oils, average 0.19, maximum
0.569. Report-internal arithmetic: the total row's 0.21 allows an olive-oil average from 0.2265 to
0.2464, so it fits both 0.23 and 0.24.

- **D1 [census]** 296 samples split 34 / 114 / 148, each with one row per 16 PAHs (the four in
  Table A-1 plus the twelve in Table A-2), one unit (ng/g or ppb).
- **D2 [values]** Table 2's infant formula, nuts and total rows reproduce (at least 11 of their
  12 cells: detected, min, max, average); 181 of 296 detected.
- **D3 [values]** Olive oil: 121 detected, min 0.002, max 3.25. **No prediction** on 0.24 vs
  0.23; the file decides and the result reports which.
- **D4 [values]** The text: 16 of 23 milk-based formulas positive with max 0.776 and no soy
  formula positive; the 2.93 maximum among nuts is a pumpkin seed butter and the next nut is below
  0.773; exactly 3 olive oils at 0.700 or more; 4 pomace oils with average 0.19 and maximum 0.569.
  Items that need a label the file lacks are reported as ungraded, not as misses.
- **D5 (descriptive, no prediction)** Per sample: olive oils with benzo[a]pyrene above 2.0 ng/g
  and with the PAH4 sum above 10.0 ng/g (the EU maximum levels for oils that the report cites).

## Honest limits

These predictions come from report arithmetic, not from the files; several (B2, B3, B5) could fail
for reasons as dull as a later data revision. The census grades only counts and labels. Label
mapping for the value items is fixed from the census before any value is read, and stated in the
grader's commit. A failed prediction is reported as failed.

MV2, Munim, Inc., mv2@munimtech.com
