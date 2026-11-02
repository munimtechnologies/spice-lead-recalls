# food-colours 0.1.0: names-only census of CFIA's 2009-10 and 2018-19 food-colour files, label maps and grader

CENSUS-MARKER: food-colours-0.1.0-census

By MV2 of Munim, Inc. Prepared with AI agents working in his name. Text CC BY 4.0; code Apache-2.0.

This follows the [food-colours 0.1.0 pre-registration](food-colours-0.1.0-prereg.md) (`v0.4.100`).
The sealed job `food-colours-census-v1` ran on 2026-11-01 from 19:25 to 19:26 UTC (python:3.12,
1 GB, no host paths). It waited until the pre-registration was public, checked its modules against
the published copies and ran the 4 offline tests (all passed). Only then did it open the two
files, and it read labels, units and cell shapes only. **No result value has been read.** Both
files match their portal records byte for byte (size and MD5).

This note grades the six census items and then fixes the label maps and coding rules before any
value is read. It also says which value items the census already settles, and it publishes the
grader (`food_colours.py`, with offline tests in `test_food_colours.py`) that a sealed job will
run. This is a reproducibility check of open government data. It is not a compliance finding, not
about any brand, and not dietary or medical advice.

## Census items: 4 of 6 held

| ID | Registered | Observed | Met |
|---|---|---|---|
| G18 | 2018-19: size and MD5; 399 sample IDs; every row names a colour and a unit; at most 43 colour labels | all hold; exactly 43 labels | ✅ (gate) |
| G09 | 2009-10: size and MD5; 100 sample IDs | both hold | ✅ (gate) |
| S1 | 2018-19 product types 50 / 99 / 50 / 200 | 50 / 99 / 50 / 200 under the map below | ✅ |
| S2 | origin totals 56 domestic / 184 imported / 159 unspecified | 56 / **183** / **160** | ❌ |
| S2b | all 12 cells of Table 1 | 11 of 12; sweets are 23 / **80** / **97**, printed 23 / 81 / 96 | ❌ |
| S3 | 2009-10 has fewer than 2,000 rows (not one row per sample per colour) | 176 rows | ✅ |

**S2 and S2b.** The origin split uses the file's Function column (Domestic / Import / Unknown).
Each sample has a single Function on all of its rows. Among the sweets, the file has one sample
fewer under Import and one more under Unknown than Table 1, so the imported and unspecified totals
each differ by one sample. The
essence, oil and processed-vegetable rows match exactly.

## What the files look like

**2018-19 (c18).**
- The file has 18,354 rows: 399 samples x 46 rows, with no exceptions. Every sample lists all 43
  colour labels. Three of them, Chrysoidine G, Orange II and Rhodamine B, appear twice: once
  under the water-soluble test and once under the fat-soluble test, giving 24 water rows and 22
  fat rows.
- Every result cell (`AMOUNT`) is a number. No cell holds `<`, `ND`, a limit or any text, so a
  non-detect must be coded as a number. Every row is in ug/g (the same as ppm). The plan code is
  2018_SB459 on every row.
- Samples come from four regions: Atlantic 23, Ontario 151, Quebec 95 and West 130. The
  product field has 24 labels.
- The IDs run from `C2018FCOL00001` to `C2018FCOL00400` with one number missing. One ID,
  `C2018FCOL00008D`, carries a `D` suffix, and the number arithmetic shows that there is no
  plain `00008`. This is the same pattern as the `AD` IDs in the 2019-20 PAH file.
- One sample, `C2018FCOL00400`, does not carry the same labels on all of its rows. Its product,
  Function and region are consistent. The date counts imply that 45 of its 46 rows are dated
  1 February 2019 and one row has a different date. The grader will report which.

**2009-10 (c09).**
- The file has 176 rows. Each of the 100 samples has one row for the fat-soluble test, labelled
  `Fat-Soluble Dyes` (a single entry, not one row per dye). 41 samples also have water-soluble
  rows: 76 rows in all, from one to five per sample, across seven colours: Tartrazine 18,
  Sunset Yellow 17, Brilliant Blue 16, Allura Red 15, Amaranth 8, Erythrosine 1 and Indigotine 1.
  The file therefore lists water-soluble colours only for some samples, most likely only where
  one was found. The 41 samples with water rows match the report's 41 samples with colours.
- Every result is a number, and every row is in ug/g.
- All 100 samples are from the Quebec region. There are 16 sampling dates, from 1 September
  2009 to 8 January 2010.
- The product field holds seven categories (Spices/flavours 27, Sauces/condiments 23, Sweets
  and jelly 16, Plant-based products 12, Beverage 9, Animal-based products 7, and
  "Miscalleneous" 6, spelled as in the file), not product names.

## Label maps and coding (fixed before any value is read)

**Product types (2018-19).** These are the four groups of Tables 1 and 2.
- Essences/flavourings (50): Essence/Flavour.
- **Oils (99): Oil - Blend, Olive, Other, Palm and Soybean (74), plus Salad Dressing (25).**
  The 74 oils alone cannot make 99. Adding cookies (25) or fruit snacks (25) would also give 99,
  but only salad dressings give Table 1's oil row (15 / 51 / 33). This choice therefore uses
  Table 1, and S2b's oil row is not independent of it. The sweets row, the one cell that fails,
  is independent.
- Processed vegetables (50): Beet, Cucumber, Cucumber Sweet, Gherkin, Onion, Pepper and Pepper Hot
  (all "Pickled"), and Pickled Vegetable - Misc.
- Sweets (200): Baked Goods, Bakery Product - Cookie, Candy - Hard, Candy - Soft, Fruit Snacks,
  Preserve - Jam/Jelly, Raspberry and Strawberry, and Pudding. "Candy" in V6 means Candy - Hard
  or Candy - Soft.

**Colours.** Table 3's names map to the file's labels: Allura Red, Tartrazine, Brilliant Blue FCF,
Sunset Yellow FCF, Erythrosin B (not "Erythrosin Yellowish", which is a separate label), Amaranth,
Indigo Carmine, Orange II and Rhodamine B. For 2009-10, V8's five colours are the labels
"Sunset, yellow", "Tartrazine, yellow", "Brilliant blue", "Allura, red" and "Amaranth". The
fat-soluble colours are the `Fat-Soluble Dyes` row.

**Coding.**
- A colour is *detected* in a sample when any of its rows in that sample is above zero. Its level
  is the largest of those rows. This matters for the three colours that have two rows.
- A *colour result* is one detected (sample, colour) pair. Table 2's "number of times colours
  detected" and Table 3's per-colour sample counts are both read this way.
- A printed figure matches when the file's value is within half a unit of its last printed
  digit. Orange II's average matches when it is below 0.13.
- If the file codes non-detects as a small positive number instead of zero, the counts will be
  far above the printed ones. The result will report that; it will not be patched.

## What the census already settles

- **V8's 93% clause is very unlikely to hold.** If every one of the 76 water-soluble rows is a
  detection, the five named colours make up 74 of 76 results, or 97.4%. 93% (92.5-93.5%) is
  possible only if both Erythrosine and Indigotine are detected and just 25-28 of the 74 rows for
  the five colours are above zero, or Erythrosine or Indigotine alone is detected and 13-14 of
  the 74 are. Either way, about half of the listed rows would have to be zeros. V8's other two
  clauses (41 samples with colour; no fat-soluble dye) remain open.
- **V9 cannot be graded.** The file has categories, not product names, and has no compliance
  column, so the seven named non-compliant products cannot be found in it. It stays ungraded.
- V1-V7 (2018-19) are all still open. The full panel per sample means every count in V1-V5 can be
  computed exactly.

## The grader and the next step

`food_colours.py` (Apache-2.0, standard library only) uses the published `cfia_census.py` only to
download and decode the two files. It:
- re-checks both gates (size, MD5, the columns found, numeric values of zero or more, the unit,
  399 x 46 rows and 43 labels for 2018-19, and 100 samples for 2009-10);
- re-derives S1 and S2b from the labels;
- grades V1-V8 with the maps and coding above, and writes V9 as ungraded.

It also writes descriptive results: how zeros and the smallest detected values look per colour,
whether the three double-row colours are detected in one row or both, a scan for samples with
identical multi-colour profiles, the mixed-label sample, the ID gap and the `D` ID, and the date
range together with a check of whether the dates follow the ID order. Its outputs are
`food_colours_summary.json`, a per-sample table and a per-detection table for 2018-19, and all
176 rows for 2009-10.

`test_food_colours.py` holds 17 offline tests on synthetic rows: both real headers, value
parsing, the product map against the census counts, the printed sums (181, 336, 337 and 56 / 184
/ 159), and each grading path. One of these is Orange II's below-LQ average, and one is a sample
whose Orange II is detected in both of its rows.

The sealed job `food-colours-grade-v1` waits until this note is public, checks that its modules
match the published copies, runs the tests, and then grades.

The census records are committed as `data/food_colours_c18_census.json` and
`data/food_colours_c09_census.json` (labels and counts only).

MV2, Munim, Inc., mv2@munimtech.com
