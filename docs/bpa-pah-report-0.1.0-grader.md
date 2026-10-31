# bpa-pah-report 0.1.0: the value grader for the two bisphenol files, and D1 (PAH 2019-20 census) graded

GRADER-MARKER: bpa-pah-report-0.1.0-grader

Made with AI agents working in MV2's (Munim, Inc.) name. Text CC BY 4.0; code Apache-2.0.
Not a compliance finding, not about any product or brand, and not dietary or medical advice.

This note follows the pre-registration [bpa-pah-report-0.1.0-prereg.md](bpa-pah-report-0.1.0-prereg.md)
(tag `v0.4.86`) and its census note [bpa-pah-report-0.1.0-census.md](bpa-pah-report-0.1.0-census.md)
(tag `v0.4.89`). It does two things:

1. It commits the grader `bpa_2018_2020.py` and its offline tests **before any result value of
   either bisphenol file is read.** The sealed job `bpa-2018-2020-v1` waits until this note, the
   census note and the pre-registration are public, checks that its bundled code equals the
   published code, runs the tests, and only then reads the files.
2. It grades census item **D1** from the names-only census of CFIA's 2019-20 PAH file, and fixes
   that file's label map for items D2-D5 the same way.

## The grader (B2-B6 for 2018-19, C2-C4 for 2020-21)

- **Gate, per file:** byte size equal to the portal record; 1,508 rows = 377 samples x 4 (2018-19)
  or 1,608 rows = 402 samples x 4 (2020-21), one row per bisphenol per sample; unit µg/g and plan
  `2018_SB451` / `2020_SB451` on every row; only the product labels listed in the census note;
  every result a number >= 0. If a gate fails, that file's items are reported as ungraded.
- **Unit rule:** a file value x µg/g is 1000·x ppb. A value above 0 is positive. Averages are over
  positives. A printed figure matches when the file's figure is within half a unit of its last
  printed digit.
- **Label maps:** exactly the two tables in the census note (2018-19: 4 types from 9 labels;
  2020-21: 5 types from 35 labels). Origin is the Function column.
- **Items as registered:** B2 Table 3's formula row (138 / 18 / 0.92 / 5.89 / 1.65); B3 sauces
  96 / 48 / 1.01 / 95.9 / 9.78; B4 all samples 381 / 165 / 0.92 / 367 / 17.8 plus coconut milk and
  pie filling in full; B5 BADGE (12, all coconut milk, 524 and 209 then ten below 63, average 81.9,
  all with BPA, no count giving 12%); B6 no BPF or BPS; C2 at least 5 of Table 2's 6 rows in full
  and 51 vegetable positives; C3 Tables 3-5 (17 BADGE, 2 BPF, 7 BPS, every printed cell, no positive
  in a type the tables leave out); C4 the co-occurrence sentences.
- **Expected failures, said in advance:** the census already showed the 2018-19 file has 377
  samples, 135 formulas and 95 sauces, so B2, B3 and B4 each name a sample count the file does not
  have. They are graded exactly as registered and should fail on that count. Their other cells
  are still reported.
- **Reported, not graded:** Table 2 of 2018-19 row by row; the share of BPA positives against the
  summary's 43% and Table 2's 44%; the three formulas with the most BPA; BADGE's overall average
  in 2020-21 against the text's 141; the BPF positives' labels and origins; samples with identical
  values for two or more bisphenols (a hint of copied rows, as found in the 2018-19 PAH file).

## D1 graded: ✅ held

| ID | Registered | Census (`pah2019-census-v1`, 2026-10-31) | Result |
|---|---|---|---|
| D1 | pah-2019: 296 samples split 34 / 114 / 148, one row per 16 PAHs, one unit | 296 samples, 4,736 rows = 296 x 16, every result a number, unit ng/g on every row, plan `2019_TS024`; 34 infant formula / 114 nuts, seeds and butters / 148 olive oil | ✅ |

The download came through on the first try this time (both hosts had reset it on 31 October at
01:09 UTC). Size and MD5 match the portal record. The census file is committed as
`data/pah-2019_census.json`.

**Facts the census shows (not registered, not graded):**

- **Origins disagree with Table 1 in two of three rows.** By the Function column, nuts are 40
  domestic / 46 imported / 28 unspecified, exactly as Table 1. Infant formula is 0 / **32** / **2**
  where Table 1 prints 0 / 31 / 3, and olive oil is 1 / **135** / **12** where Table 1 prints
  1 / 133 / 14. The total is 41 / 213 / 42 against the printed 41 / 210 / 45. So three samples the
  file calls imported are unspecified in the report.
- Every sample number ends in `A` (`C2019PAHS00001A` ...), so none fits the ID pattern of the
  other CFIA files; this is a format fact, not an error.
- The file has no region column and one test type (`BENZOPYRENE (PAH)`) for all 16 compounds.
- **There is no pomace-oil label.** All 148 olive oils carry `Oil - Olive`.

## pah-2019 label map for D2-D5 (fixed now, before any value is read)

| Report type | File labels | n |
|---|---|---|
| Infant formula | `Infant Formula - Dairy` (23, the text's "milk-based"), `Infant Formula - Soy` (11) | 34 |
| Nuts and nut butters | `Butter - Almond` (7), `- Blend` (7), `- Cashew` (7), `- Hazelnut` (3), `- Peanut` (7), `- Pumpkin Seed` (1), `- Soy` (7), `- Sunflower Seed` (4), `- Walnut` (1); `Nut - Almond` (1), `- Brazil Nut` (7), `- Cashew` (7), `- Chestnut` (1), `- Hazelnut/Filbert` (7), `- Macadamia Nut` (7), `- PINE NUT` (3), `- Pecan` (7), `- Walnut` (7); `Peanut` (6); `Seed - Chia` (1), `- Flax` (2), `- Pumpkin` (2), `- Sunflower` (5); `Tahini` (7) | 114 |
| Olive oil | `Oil - Olive` | 148 |

TEQ as registered (benzo[a]pyrene + 0.1 x benz[a]anthracene + 0.1 x benzo[b]fluoranthene + 0.01 x
chrysene; the file spells the second one `Benz[a]anthracene`), in ppb = ng/g, no conversion. D4's
"pumpkin seed butter" is the single `Butter - Pumpkin Seed` sample. **D4's pomace clause (four
pomace oils, average 0.19, maximum 0.569) is ungraded**, because no label separates pomace oil;
the rest of D4 is graded. D5 uses `Oil - Olive`.

## Next

1. `bpa-2018-2020-v1` grades B2-B6 and C2-C4; the result note, the per-sample tables and an
   independent recompute test follow.
2. The pah-2019 grader (D2-D5), using the map above, is committed and public before a sealed job
   reads any of its values.

MV2, Munim, Inc., mv2@munimtech.com
