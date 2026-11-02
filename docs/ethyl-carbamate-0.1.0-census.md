# ethyl-carbamate 0.1.0: names-only census of CFIA's 2018-19 and 2019-20 ethyl carbamate files, label maps and grader

CENSUS-MARKER: ethyl-carbamate-0.1.0-census

By MV2 of Munim, Inc. Prepared with AI agents working in his name. Text CC BY 4.0; code Apache-2.0.

This follows the [ethyl-carbamate 0.1.0 pre-registration](ethyl-carbamate-0.1.0-prereg.md)
(`v0.4.104`). The sealed job `ethyl-carbamate-census-v1` ran on 2026-11-02 from 06:27 to 06:29 UTC
(python:3.12, 1 GB, no host paths). It waited until the pre-registration was public, checked its
modules against the published copies and ran the 5 offline tests (all passed). Only then did it
open the two files, and it read labels, units, cell shapes and sample counts only. **No result
value has been read.**

This note grades the five census items, fixes the label maps and coding before any value is read,
says which value items the census already settles, and publishes the grader
(`ethyl_carbamate.py`, with offline tests in `test_ethyl_carbamate.py`) that a sealed job will
run. This is a reproducibility check of open government data. It is not a compliance finding, not
about any brand, and not dietary or medical advice.

## Census items: 4 of 5 held

| ID | Registered | Observed | Met |
|---|---|---|---|
| G18 | 2018-19: portal size and MD5; 390 sample IDs; one analyte; one unit | all hold (71,629 bytes; ng/g) | ✅ (gate) |
| G19 | 2019-20 is not the 58-byte record: 300 sample IDs, one analyte, one unit | the file served is 58,972 bytes and matches the portal MD5; 300 IDs; ng/g | ✅ (gate) |
| S1 | 125 beer / 17 sake / 117 spirits / 125 vinegar / 6 wine; 200 vegetables / 100 soy | every total holds under the map below; the file has one label for sake, spirits and wine (140 = 17 + 117 + 6), so that split cannot be checked | ✅ (totals) |
| S2 | the 21 origin cells of the two Table 1s | the 12 cells that can be checked one by one all match; the 9 sake / spirits / wine cells match as three sums (37 / 85 / 18) | ✅ |
| S2p | the earlier pattern: totals match, at least one origin cell is off, none by more than 2 | no checkable cell is off | ❌ |

**G19 and the 58-byte record.** The pre-registration flagged that the portal lists the 2019-20
file at 58 bytes. The file served is complete: 58,972 bytes, 300 samples, and its MD5 equals the
portal's. The record's size field is off by a factor of about 1,000 (it most likely holds
kilobytes). This is a metadata slip, not a missing file.

**S2p failed.** In the earlier CFIA files (PAH 2019-20, food colours 2018-19, BPA 2017-18) the
origin split was off by one or two samples somewhere. Here every cell that can be checked matches.
This is the first pair in the series where it does.

## What the files look like

**2018-19 (ec18).**
- 390 rows, one per sample, 18 bilingual columns. Every result cell (`MaxOfAMOUNT`) is a number;
  no cell holds `<`, `ND`, a limit or any text. Every row is in ng/g (ppb). Plan code 2018_SB428.
- Regions: Atlantic 27, Ontario 154, Quebec 87, West 122.
- The product field has four labels: **Beer 124, Beef 1, Beverage - Alcohol 140, Vinegar 125.**
  Sake, spirits and liqueurs, and wine all carry "Beverage - Alcohol" (French "Boisson - Alcool").
- **One sample is labelled "Beef" (French "Boeuf"), imported from Iceland.** Its ID, 251, sits
  inside the beer block (beer IDs run 151-250 and 252-275). With it, the beer count is the
  report's 125 and the beer origin row is the report's 54 / 49 / 22; without it, 124 and
  54 / 48 / 22. It is most likely an Icelandic beer coded with the wrong product.
- The IDs run from 1 to 400 with 10 numbers missing (15, 16, 19, 23, 34, 37, 39, 42, 44 and 45), all
  in the alcohol block (IDs 1-150). The alcohol block is followed by beer (151-275) and vinegar
  (276-400). No ID has a suffix.
- **Sampling dates run from 3 April 2018 to 6 March 2019** (119 distinct dates, all
  `D-Mon-YY`). The report's text says sampling ran from 1 April 2018 to 21 March 2019, and its
  title says 31 March. The file has no sample dated after 6 March.
- Origins use the Function column (Domestic 103, Import 198, Unknown 89), as registered. The
  Origin column has 97 UNKNOWN. In each product the Domestic count equals the CANADA count, so the
  8 extra UNKNOWNs (2 beers, 2 alcohol, 4 vinegars) are most likely imports with no country.

**2019-20 (ec19).**
- 300 rows, one per sample, 15 columns; no region or commodity column. Every result cell is a
  number, every row is in ng/g, plan code 2019_SB428. Dates are ISO (`2019-04-09` onward).
- IDs run from 1 to 300 with no gap. One ID, `C2019ETCA00152D` (a sauerkraut), carries a `D`
  suffix and has no plain `00152` partner, the same pattern as `C2018FCOL00008D` in the food-colour
  file and the `AD` IDs in the 2019-20 PAH file.
- Products: soy is IDs 1-100 (**Soy Products 97, Tofu 3**); fermented vegetables are IDs 101-300
  (**Pickled Vegetable - Misc 118, Sauerkraut 55, Cucumber - Pickled 21, Cabbage 4, Gherkin -
  Pickled 1, Fish/Seafood - Frozen/Refrigerated 1**).
- **One sample in the vegetable block is labelled "Fish/Seafood - Frozen/Refrigerated"** (ID 272,
  imported from Korea). With it, the vegetable count is the report's 200 and the origin row is
  the report's 49 / 143 / 8. It may be a kimchi made with seafood; the file does not say.
- Going by the counts, the English label "Cucumber - Pickled" (21) pairs with the French
  "Cornichon" (21), and "Gherkin - Pickled" (1) with "Marinades (concombre)" (1). *Cornichon* is
  French for gherkin, so the two French labels look swapped.
- None of the labels names a kimchi, a bean curd or a miso, which the report's text names.

## Label maps and coding (fixed before any value is read)

**2018-19 product types.**
- Beer (125): `Beer` and the single `Beef` row (ID 251, by its position in the beer block). S1's
  beer total and S2's beer import cell therefore depend on this choice; the vinegar row and the
  alcohol sums do not.
- Sake + spirits and liqueurs + wine (140, "pooled"): `Beverage - Alcohol`.
- Vinegar (125): `Vinegar`.

**2019-20 product types.**
- Soy (100): `Soy Products`, `Tofu`.
- Fermented vegetables (200): `Cabbage`, `Cucumber - Pickled`,
  `Fish/Seafood - Frozen/Refrigerated` (ID 272, by its position in the vegetable block),
  `Gherkin - Pickled`, `Pickled Vegetable - Misc`, `Sauerkraut`.

**Coding.**
- One result per sample (every sample has exactly one row). A sample is a *detect* when its
  result is above zero, as registered. Both files code every result as a number, so if they write
  non-detects as a small positive number instead of zero, the detect counts will come out far
  above the printed ones. The result will report that; it will not be patched. The grader also
  reports how many results are exactly zero and the five smallest above zero.
- A printed figure matches when the file's value is within half a unit of its last printed digit
  (Table 2 prints wine's average as "40", so it carries half a unit). A band derived from several
  printed figures is inclusive.
- The 2019-20 gate uses the measured size (58,972 bytes) and the portal MD5.

## What the census already settles

- **V4 cannot be graded.** No label names the wine, so the 86 ppb wine cannot be identified as
  fortified, sweet or 20 years old. The report's sentence that all wines met Health Canada's
  limits stays unchecked.
- **V1 and V2 lose their sake, spirits and wine parts.** V1 is graded on four rows: beer, vinegar,
  the grand total, and a pooled sake + spirits + wine row derived now from Table 2 alone: 140
  samples, 29 detects, minimum 4, maximum 86, average between (3 x 15.65 + 23 x 12.25 + 3 x 39.5)
  / 29 = 15.42 and (3 x 15.75 + 23 x 12.35 + 3 x 40.5) / 29 = 15.61 (band 15.42-15.62). V2 is
  graded on its beer and vinegar parts; the hidden sake (7, 7, 33) and wine (17, 17, 86) values
  stay unchecked.
- **V6 loses its bean-curd and miso part.** It is graded on 94 of 100 soy samples without EC and
  on the vegetable detects being two `Sauerkraut` rows plus one `Cabbage`,
  `Pickled Vegetable - Misc` or `Fish/Seafood` row (the kimchi has no label of its own).
- **V3, V5 and V7 can be graded in full.**
- **R4 is now settled by labels alone:** the file's last sampling date is 6 March 2019, neither
  the text's 21 March nor the title's 31 March.

## The grader and the next step

`ethyl_carbamate.py` (Apache-2.0, standard library only) uses the published `cfia_census.py` only to
download and decode the two files. It:
- re-checks both gates (size, MD5, the columns found, numeric values of zero or more, the unit,
  390 and 300 samples with one row each);
- re-derives the product totals and origin splits from the labels;
- grades V1, V2, V3, V5, V6 and V7 with the maps and coding above, and writes V4 as ungraded.

It also writes descriptive results: zeros and the smallest detects, the ID range, gaps and the
`D` ID, the date range, the `Beef` and `Fish/Seafood` rows, and the five highest pooled
sake/spirits/wine detects. Its outputs are `ethyl_carbamate_summary.json` and a per-sample table
for both files, `ethyl_carbamate_samples.csv`.

`test_ethyl_carbamate.py` holds 11 offline tests on synthetic rows: both real headers, value and
unit parsing, half-unit matching, the product maps against the census counts, the pooled band,
a synthetic 390-sample file and a synthetic 300-sample file built to meet every printed figure,
and two altered versions that must fail (a vinegar at 14 ppb fails V1 and V2 only; a cabbage at
10 ppb fails V5 and V7 but not V6).

The sealed job `ethyl-carbamate-grade-v1` waits until this note is public, checks that its modules
match the published copies, runs the tests, and then grades.

The census records are committed as `data/ethyl_carbamate_ec18_census.json` and
`data/ethyl_carbamate_ec19_census.json` (labels and counts only).

MV2, Munim, Inc., mv2@munimtech.com
