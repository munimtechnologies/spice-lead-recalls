# ethyl-carbamate 0.1.0: pre-registration — CFIA's open ethyl carbamate files (2018-19 alcoholic beverages and vinegars; 2019-20 fermented vegetables and soy) against their reports

PREREG-MARKER: ethyl-carbamate-0.1.0-prereg

By MV2 of Munim, Inc. Prepared with AI agents working in his name. Text CC BY 4.0; code Apache-2.0.
Written on 2026-11-02, before either open file was opened. Everything below comes from the two
printed reports, a later CFIA report and the portal records (size and hash only).

This is a reproducibility check of open government data. It is not a compliance finding, it is
not about any brand, and it is not dietary or medical advice. Ethyl carbamate (EC) forms naturally
during fermentation. All values are ppb.

## Sources

- **ec18:** "Ethyl Carbamate in Alcoholic Beverages and Vinegars - April 1, 2018 to March 31, 2019"
  (CFIA report page; open dataset `303903b7-91ba-4a79-ad37-7bcd9f0dc8a1`, series CFIA-ACIA-1149,
  resource `0a30e00b-9c4b-4402-b329-51565119d767`, portal size 71,629 bytes, MD5
  `d7d7bf62a3bb275ccec657fb27501fd8`).
- **ec19:** "Ethyl Carbamate in Fermented Vegetables and Soy Products - April 1, 2019 to March 31,
  2020" (CFIA report page; open dataset `920d97a1-b98d-4def-b386-dd234a45f457`, series
  CFIA-ACIA-1313, published on the portal 2026-07-22, resource
  `985e3d90-ecbb-4a34-b299-8032627c3c3d`). **The portal record gives this file's size as 58
  bytes** (hash `e5aab1da6e57c1afa0536e9d92455a6e`, marked "ignore_hash"). 58 bytes is too small
  for 300 samples.
- **Later report:** CFIA's combined ethyl carbamate report for April 2016 to March 2018 and April
  2020 to March 2022, whose Table 3 restates both surveys as "previous CFIA surveys".
- Health Canada's List of Contaminants, ethyl carbamate (read 2026-11-02): 30 ppb for wines;
  100 ppb for fortified wines, wines aged 20 years or more and wines with more than 60 g/L residual
  sugar; 150 ppb for distilled spirits; 200 ppb for alcoholic beverages from rice (sake); 400 ppb for
  fruit spirits and fortified wines aged 20 years or more.

## What the printed reports already show (no file needed)

- **R1.** ec19 soy: 6 of 100 samples had EC, so 94 had none, but the text says "93%" had none.
- **R2.** The later report's row for the 2019 soy survey reads 100 samples, 6 detects, minimum
  **4.0**, maximum 217, average **74.1**. The 2019-20 report's soy row is minimum **7**, average
  **108**. Its all-products Total row is minimum 4, average 74, and (3 x 6.3 + 6 x 108) / 9 =
  74.1. The later report appears to have taken the soy row's minimum and average from the Total row.
- **R3.** ec18's arithmetic holds: detects 2 + 3 + 23 + 6 + 3 = 37 of 390 (9.49%; Table 2 prints
  9, the text 9.5). The average over all detects, (2 x 4 + 3 x 15.7 + 23 x 12.3 + 6 x 29.5 + 3 x
  40) / 37 = 17.16, matches the printed 17.2. The later report's alcoholic-beverage subtotal
  (265 samples, 31 detects, 4.0 to 86.0, average 14.8) is beer + sake + spirits + wine, and 458 / 31
  = 14.77.
- **R4.** ec18 says sampling ran to 21 March 2019; its title says 31 March.
- **R5.** ec18's highest wine result is 86 ppb, and the text says all wine results met Health
  Canada's limits. The limit for wine is 30 ppb unless the wine is fortified, aged 20 years or more,
  or has more than 60 g/L residual sugar (100 ppb). So that wine must be one of those for the
  statement to hold.
- **R6.** Averages pin down hidden values. With 3 detects, a minimum, a maximum and an average fix
  the middle value: sake 7 / 33 / 15.7 gives a middle of about 7, wine 17 / 86 / 40.0 gives about
  17, and 2019-20 vegetables 4 / 9 / 6.3 give about 6. Vinegar's six detects average 29.5 with a
  maximum of 135, so the other five sum to about 42; the text says they are all 13 ppb or less.

## Census predictions (labels, counts and cell shapes only; no value read)

| ID | Prediction |
|---|---|
| G18 | ec18 matches its portal size and MD5; 390 distinct sample IDs; one analyte label; one unit |
| G19 | ec19 is not the 58-byte record: the file served holds 300 distinct sample IDs, one analyte label and one unit. If it holds no samples, every ec19 item below is ungradable and that is the finding. |
| S1 | ec18 product types 125 beer / 17 sake / 117 spirits and liqueurs / 125 vinegar / 6 wine; ec19 200 fermented vegetables / 100 soy (label maps fixed in the census note before any value is read) |
| S2 | the 21 origin cells of the two Table 1s (Function or origin column): ec18 beer 54 / 49 / 22, sake 0 / 17 / 0, spirits 36 / 63 / 18, vinegar 12 / 64 / 49, wine 1 / 5 / 0; ec19 vegetables 49 / 143 / 8, soy 16 / 69 / 15 (domestic / imported / unspecified) |
| S2p | the pattern in the earlier CFIA files: every product total matches, at least one of the 21 origin cells differs, and none differs by more than 2 samples |

## Value predictions (graded by a sealed job after the census note fixes maps and coding)

| ID | Prediction |
|---|---|
| V1 | ec18 Table 2 in full: detects 2 / 3 / 23 / 6 / 3 (37); minimum and maximum per type 4-4, 7-33, 4-42, 6-135, 17-86; averages 4, 15.7, 12.3, 29.5, 40; overall 4-135, average 17.2 (each within half a unit of its last printed digit) |
| V2 | ec18 hidden values: both beer detects round to 4; the sake detects round to 7, 7 and 33; the wine detects round to 17, 17 and 86; one vinegar is 135 and the other five each round to 6-13 and sum to 41-43 |
| V3 | the later report's alcoholic subtotal: 31 detects among the 265 beers, sakes, spirits and wines, 4 to 86, average 14.75-14.85 |
| V4 | the 86 ppb wine's product label names a fortified, sweet (ice, dessert, late harvest) or 20-year wine. Not met if its label names a table wine (for example red, white, rose or sparkling with no such term). Ungraded if the label says only "wine". |
| V5 | ec19 Table 2 in full: vegetables 3 detects rounding to 4, 6 and 9 (average 6.25-6.35); soy 6 detects, minimum 7, maximum 217, average 107.5-108.5; total 9 detects, 4-217, average 73.5-74.5 |
| V6 | ec19 text: 94 of 100 soy samples have no EC (not 93); the soy detects are 5 bean curds and 1 miso, and the highest is a bean curd; the vegetable detects are 2 sauerkrauts and 1 kimchi |
| V7 | R2 settled by the file: the soy minimum is 7 and the soy average is 107.5-108.5, while the all-products average is 74.05-74.15, so the later report's 4.0 / 74.1 belong to the Total row |

## Coding (fixed now; the census note may only add label maps)

- A sample is a *detect* when its EC result is above zero or is a number where non-detects are
  written as text (`ND`, `<LOD` and the like). If the file codes non-detects as a number at or below
  some limit, the census note will say so before any value is read, and that rule applies.
- One result per sample. If a sample has more than one EC row, its largest value counts and the
  census note will report it.
- Origins use the file's Function column (Domestic / Import / other) when it exists, otherwise the
  origin column (CANADA = domestic, UNKNOWN or blank = unspecified).

## Limits

- Neither report prints a limit of detection.
- The Health Canada list was read in 2026. It may have changed since 2018-19.
- V4 depends on how specific the product labels are; it may end up ungraded.
- If ec19 is a stub, half of this study cannot be graded. The 58-byte portal record is reported
  either way.

## The next step

A sealed job (`ethyl-carbamate-census-v1`) waits until this note is public, checks that its modules
match the published copies, runs the offline tests in `test_ethyl_carbamate_census.py`, and only
then runs `ethyl_carbamate_census.py`: labels, units, cell shapes and sample counts, never a value.
The census note then grades G18, G19, S1, S2 and S2p and fixes the label maps and the grader before
any value is read.

Prior art: searches on 2026-11-02 found the CFIA report pages and the open dataset records, but no
analysis of either per-sample file.

MV2, Munim, Inc., mv2@munimtech.com
