# Census: CFIA's open 2011-12 and 2012-2018 fumonisin files, names and counts only (fumonisin-series 0.1.0)

CENSUS-MARKER: fumonisin-series-0.1.0-census

Made with AI agents working in MV2's (Munim, Inc.) name. Text CC BY 4.0; code Apache-2.0.
Not a compliance finding and not dietary or medical advice.

This note grades the census items of the [pre-registration](fumonisin-series-0.1.0-prereg.md) and
fixes the label maps and grading rules for its value items. It was written from the sealed
names-only census (job `fumonisin-series-census-v1`, run 2026-11-07 09:16 UTC, after the
pre-registration and the census module were public as v0.4.120 and v0.4.121). That job read
labels, counts and cell shapes; **no result value of either file has been read**. Its records are
published as [data/fumonisin_fum11_census.json](../data/fumonisin_fum11_census.json) and
[data/fumonisin_fum1218_census.json](../data/fumonisin_fum1218_census.json), and
`test_fumonisin_census_notes.py` checks every count below against them.

## Both files at a glance

Both gates hold: each MD5 is the portal's, each size is inside its KiB band read as rounded up
(158,076 bytes for 155 KiB; 1,402,889 bytes for 1371 KiB), and the key columns are found by name.
Both have the same 15 columns as the 2010-11 file, two rows per sample (Fumonisin B1 and B2, every
result a number, every unit ng/g) and no stored total, so a sample's total is B1 + B2. Neither has
a region, grain or organic field.

**Both files hold more samples than their reports: 498 against 454 (2011-12) and 4,320 against
4,261 (2012-2018).** With the 2010-11 file's 277 against 276
([its census](fumonisin-2010-0.1.0-census.md)), all three newly opened fumonisin files are larger
than the reports they belong to.

## File A, 2011-12

| Item | Registered | File | Grade |
|---|---|---|---|
| A-C1 | 454 samples | **498** | **fails** |
| A-C2 | 274 corn-based, 180 soy-based | corn-named 262, soy-named 191, 45 neither | **fails** |
| A-C3 | analytes a subset of {B1, B2, total}, no B3 | B1, B2 | holds |
| A-C4 | ppb-scale units | ng/g | holds |

Label map. Corn-named (262): Cereal - Corn 35, Chips - Corn 36, Corn 25, Corn - Sweet - Organic 2,
Corn Products 108, Cornmeal 44, Flour - Corn 12. Soy-named (191): Bean - Soy 38, Beverage - Soy 36,
Flour - Soy 4, Infant Formula - Soy 29, Misc - Soy 43, Soy Products 41. Neither (45): Cereal - Other
43, Misc 1, Protein Powder 1. No split of these labels gives 274 and 180, and the soy-named labels
alone are 11 over the page's soy count. Sampling dates run 2011-02-09 to 2012-03-28; one cornmeal is
dated inside the 2010-11 survey year, the other 497 samples inside 2011-12. Sample numbers run
2011FUM0001 onward.

## File B, 2012-2018

| Item | Registered | File | Grade |
|---|---|---|---|
| B-C1 | 4,261 samples | **4,320** | **fails** |
| B-C2 | 3,650 grain, 185 soy, 426 tea | 3,713 / 182 / 425 | **fails** |
| B-C3 | analytes a subset of {B1, B2, total}, no B3 | B1, B2 | holds |
| B-C4 | ppb-scale units | ng/g | holds |
| B-C5 | Table 1's origin split, nine cells | 2 of 9 cells match | **fails** |
| B-C6 | **77 teff** (13 / 8 / 14 / 42 by year) | **59** labelled teff (7 / 7 / 10 / 35) | **fails** |
| B-C7 | rice 189, 19 in 2012-13 | rice-named 108, 9 in 2012-13 | **fails** |
| B-C8 | soy 94 / 91; teas all 2016-17 (426); corn 328 / 307 / 320 / 0 / 1 / 732 | soy 91 / 91; teas all 2016-17 (425); corn-named 272 / 264 / 201 / 0 / 0 / 493 | **fails** |
| B-C9 | organic 1,322, conventional 2,939 | no label or column marks organic | not gradable |

Two of nine hold, six fail and one cannot be graded.

**Group map.** Tea = the six "Tea - ..." labels and "Beverage - Tea" (425). Soy = Bean - Soy 40,
Beverage - Soy 40, Flour - Soy 29, Infant Formula - Soy 20, Tofu 30, Meat Alternative 9 and Soy
Products 14 (182). Grain = the other 52 labels (3,713). The soy labels match Table A2 row by row
(soybeans 40, soy beverages 40, soy flour 29, soy infant formula 20, tofu 30, meat alternatives 9;
Soy Products 14 = miso 5 + soy protein 1 + soybean paste 3 + soy nuts 1 + tempeh 4). The one A2 row
with no soy label is "infant cereal" (3), which the file most likely files under Infant Food -
Cereal: that label has 4 samples in 2012-13, the year the soy labels are 3 short. That reading is
from names only and is not used in grading. The one missing tea is a white tea: the file has 24
"Tea - White" against the text's 25.

**Origin (B-C5).** The function column (Domestic / Import / Unknown) gives grain 734 / 1,849 /
1,130, soy 61 / 83 / 38 and tea 62 / 207 / 156, against Table 1's 721 / 1,770 / 1,159, 64 / 83 / 38
and 61 / 171 / 194. Only soy's imported and unspecified cells match; soy's domestic cell is 3 short,
as the three soy infant cereals would make it.

**Grains.** No label names wheat, and 1,262 grain-group samples (14 labels) name no grain at all:
Cereal - Adult 333, Cereal - Children 300, Bakery Product - Bread 151, Infant Food - Cereal 109,
Grain - Other 72, Bakery Product - Bread - Other 67, Bakery Product - Tortilla/Wrap/Pita 66,
Bakery Product - Bagel 50, Bakery Product - English Muffin 50, Infant Food (non-cereal) 50, Bread -
Other 9, Bakery Product - Cookie 3, Baking Mixes 1 and Crispbread/Crouton 1. The other 2,451 name
one grain. Against Table 3 (samples):

| Grain | Table 3 | Labels naming it | | Grain | Table 3 | Labels naming it |
|---|---|---|---|---|---|---|
| amaranth | 88 | 55 | | oat | 124 | 30 |
| arrowroot | 66 | 65 | | quinoa | 141 | 136 |
| barley | 134 | 130 | | rice | 189 | 108 |
| buckwheat | 131 | 128 | | rye | 136 | 121 |
| corn | 1,688 | 1,230 | | spelt | 129 | 121 |
| kamut | 148 | 132 | | teff | 11 (77 needed) | 59 |
| millet | 137 | 135 | | triticale | 1 | 1 |
| wheat | 456 | 0 | | mixed grains | 5 | - |

So the report's per-grain tables (Tables 3 to 16, Appendices A and B) cannot be rebuilt from the
open file's labels: most grains are a few samples short, and the rest sit in labels such as
Grain - Other, the cereals and the bakery products. Four Appendix B corn rows do match a label one
to one (corn flour 276, corn starch 251, popcorn 25, corn bran 2), cornmeal is 337 against 336, and
Infant Food (non-cereal) has the same count (50) as Appendix B's creamed corn.

**Teff (B-C6), the headline item.** The pre-registration showed from the report's own arithmetic
that Table 3's 11 teff samples cannot be right and that the teff table's year rows (77) close every
gap. The file's teff label holds **59**, by year 7 / 7 / 10 / 35, neither 11 nor 77. Grain - Other
(72; 16 / 7 / 15 / 34 by year) is large enough to hold the other 18 in every year, but the names
cannot show it. The registered item fails; that Table 3's 11 is wrong stands either way.

**Years.** By sampling date the file has 605 / 715 / 750 / 750 / 750 / 750 samples in 2012-13 to
2017-18; the plan codes agree year by year. Rice-named labels (Grain - Rice, Rice Products, Flour -
Rice) appear only in 2012-13 (9) and 2015-16 (99); oat-named labels only in 2013-14 and 2014-15.
Sixteen sample numbers end in "D" (for example C2013FUMN00303D); the grader reports whether each has
a partner without the D.

## How the value items are graded (fixed now, before any value is read)

A sample is positive when B1 + B2 is above zero; averages are of positives; a printed figure
matches in its half-unit band [printed - half a unit, printed + half a unit).

File A, on the map above (corn = the seven corn-named labels):
- A-V1. 162 positives in all; exactly one soy-named positive, labelled Flour - Soy, total at least
  22.35 and below 22.45; and 161 positives among the corn-named and neither labels.
- A-V2. The smallest corn-named positive is at least 20.75 and below 20.85 (the 2011-12 page). The
  23.1 reading of Table 7 is reported beside it.
- A-V3. The largest total is at least 4442.45 and below 4442.55 and is labelled Cornmeal.
- A-V4. The corn-named positives average at least 253.15 and below 253.25. The corn-plus-neither
  reading is reported beside it.

File B, on the group map above:
- B-V1. 1,076 positives: 1,073 grain, 2 soy, 1 tea.
- B-V2. Smallest positive in [19.5, 20.5); largest in [7789.5, 7790.5) and labelled Cornmeal.
- B-V3. Exactly two soy positives: a Tofu sampled in 2012-13 in [26.5, 27.5) and a Flour - Soy
  sampled in 2013-14 in [44.5, 45.5).
- B-V4. Exactly one tea positive, labelled Tea - Black, in [42.5, 43.5).
- B-V11. Averages: grain in [364.5, 365.5), soy in [35.5, 36.5), all in [363.5, 364.5).
- **Not gradable from the labels**, reported only: B-V5 (Table 3 cell by cell needs a grain for
  1,262 samples whose labels name none), B-V6 (no label names wheat) and B-V9 (Cereal - Children
  does not say which cereals contain corn).
- **Failed on the label map, decided now from names alone**: B-V7 (the registered rice positives
  are in 2013-14, 2014-15 and 2017-18, years with no rice-named sample), B-V8 (no oat-named sample in
  2017-18) and B-V10 (the corn-named counts differ from all four registered corn rows).

Reported, not graded: each label's and each named grain's figures by year, the "D" sample numbers
and their partners, the totals with the "D" samples left out, non-detect coding, and, as
**exploratory, not registered**, every positive whose total matches a printed figure the labels
cannot place (wheat 2012's 28.8 and 393; rice's 33, 47, 249 and 42; oat 2017's 53; 7711 and 7710).

## What the census decides

Of seventeen census items across the three files, six hold, ten fail and one cannot be graded.
All three files are larger than their reports; the 2012-2018 file's labels cannot rebuild its
report's grain tables; and teff, the pre-registration's headline, is neither of the report's two
figures. The grader is in [fumonisin-0.1.0-grader.md](fumonisin-0.1.0-grader.md).

MV2, Munim, Inc., mv2@munimtech.com
