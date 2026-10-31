# bpa-series 0.1.0: the names-only census of seven CFIA bisphenol A files, its graded items, and the label maps fixed before any value is read

CENSUS-MARKER: bpa-series-0.1.0-census

Made with AI agents working in MV2's (Munim, Inc.) name. Text CC BY 4.0; code Apache-2.0.
Not a compliance finding, not about any product or brand, and not dietary or medical advice.

This note follows the pre-registration [bpa-series-0.1.0-prereg.md](bpa-series-0.1.0-prereg.md)
(tag `v0.4.87`). The sealed job `bpa-series-census-v1` ran on 2026-10-31 at 06:46 UTC
(python:3.12, 1 GB). It waited for the registration to be public, checked that its bundled code
and tests were identical to the published copies, ran the tests, then ran the names-only census of
all seven files: counts of rows, samples, labels, units and origins, and the *shape* of every
result cell. **No result value was printed, summed or compared.** All seven downloads match the
portal's byte size (and MD5 where the portal lists one). The census files are committed as
`data/bpa-20NN_census.json`.

## Graded census items: S1, S3 and S4 held; S2 held in 4 of 7 files; S5 ungraded

| ID | Registered | Census | Result |
|---|---|---|---|
| S1 | ≥ 6 of 7 files hold the printed totals 200 / 234 / 403 / 576 / 391 / 491 / 468 | **7 of 7** | ✅ |
| S2 | category counts reproduce where labels map without ambiguity (per file) | 2009 ✅, 2010 ❌, 2011 ✅, 2012 partial, 2013 partial, 2016 ✅ (4 gradable rows), 2017 ✅ | 4 of 7 files |
| S3 | 2013-14 holds **45** pastas and 48 soups (Table 5's 34 is a slip) | `Pasta - Canned` 45, `Soup` 48 | ✅ |
| S4 | 2017-18 origins meat 111 / 102 / 18, fish 14 / 220 / 3, so **322** imported, not 325 | exactly that | ✅ |
| S5 | package type in 2009 and 2010 (37 canned formulas; 89 / 32 / 79) | neither file has a package or form label | ungraded |

**S2, file by file** (report count vs file count):

- **2009-10** (200): infant food 100 / 100, infant formula 100 / 100. ✅
- **2010-11** (234): fruit juices 15 / 15 (`Juice - Apple` 13, `Juice - Grape` 1, `Nectar - Pear`
  1). Infant formula **127 / 129** (`Infant Formula - Dairy` 126 + `- Soy` 3). Fruit products
  **92 / 87**, or 90 if the two `Cereal - Other` and one `Meat & Vegetable` samples are counted
  with them. ❌ The totals agree; the formula and fruit splits do not.
- **2011-12** (403): fruit products 101, juices/beverages 50, vegetables/legumes 151,
  pastas/soups 101 (`Pasta - Canned` 96 + `Soup` 5). All four match. ✅
- **2012-13** (576): pastas/soups 217 (119 + 98), coconut milk 46, fruit products 73 and
  juices/beverages 72 match. `Curry` has **21** samples where the page says 24 curry products, and
  the remaining vegetable labels hold **147** where it says 144. Together they make 168 = 144 + 24.
  The split works only if three non-curry labels count as curry (for example the three `Salsa`
  samples). Partial: 4 of 6.
- **2013-14** (391): pastas/soups 93, vegetables 70, infant formula 55, fruit products 38, pie
  fillings 20, coconut milks 13 and curry products 5 (`Sauces`) match. Juices/beverages hold
  **55** and energy/sports/soft drinks **42**, where the description says 54 and 43. Twelve
  `Beverage - Other` samples could sit in either group, and the two groups together (97) equal
  Table 5's 2013 beverage row. Partial: 7 of 9.
- **2016-17** (491): the file has **no packaging label**, so only the canned rows with no
  other-packaging samples can be checked. Coconut milk 14, fruit 50, pie filling 20 and vegetables
  72 match Table 2. Beverages (149 vs 135 canned), infant formula (74 vs 66), pasta (49 vs 48),
  sauce (15 vs 13) and soup (48 vs 46) exceed the canned counts by 14 + 8 + 1 + 2 + 2 = **27**,
  which is exactly Table 1's "other packaging" total. The Function column gives 79 / 300 / 112,
  which equals Table 1's column totals (76 + 3, 287 + 13, 101 + 11). ✅ where gradable.
- **2017-18** (468): meat 231 (`Meat - Canned` 219, `Chicken` 5, `Ham` 5, `Beef` 1, `Pork` 1) and
  fish and seafood 237 (`Fish/Seafood - Canned` 165, `Tuna` 49, `Salmon` 12, `Fish` 4, `Mackerel`
  2, and one each of `Crab`, `Herring`, `Mussel`, `Oyster`, `Shrimp`). ✅

**The pattern so far.** Every total in the seven files matches the printed total. Where a split
fails, it is between neighbouring groups (formula and fruit products in 2010-11; curry and
vegetables in 2012-13; juices and other drinks in 2013-14). It echoes the earlier checks in this
repository (furans 2018-19, for example), where totals matched more often than splits.

## What else the census shows (facts, not graded)

- **Units.** 2009-10 reports **ng/g**, which is already ppb. The six later files report µg/g, and
  the 2010-11 to 2013-14 headers call it "(ppm)". Every result cell in all seven files is a plain
  number, so non-detects are coded 0.
- **2009-10 sampling dates.** The 200 samples carry **200 different dates**, one per sample. The
  census lists the first 120 in text order, and each appears exactly once: every day of October
  2009, November 2009 and January 2010, and 28 days of December 2009, including 25 December and
  1 January. A targeted survey that buys one sample on every calendar day, holidays included, is
  unlikely, so these dates look like placeholders rather than real sampling dates. Users of this
  file should not read seasonality from them. A sealed check of whether the date simply rises by one
  day per sample number is planned for the series grader, which reads labels and dates only, never
  values, for this purpose.
- **Sample numbers.** 2009-10, 2010-11 and 2011-12 use IDs like `2009BPA0001` (no leading `C`), and
  2009-10 mixes 4- and 5-digit numbers (`2009BPA0006`, `2009BPA00065`). 2013-14 uses the letters
  `BHPA` (not `BPHA`), numbers 1 to 525 with 134 unused, and one D-suffixed ID (`C2013BHPA00319D`).
  2016-17 runs 1 to 500 (9 unused) and 2017-18 1 to 498 (30 unused).
- **Empty columns.** The 2013-14 and 2016-17 headers end in 31 and 32 empty columns.
- **Four analytes from 2016.** 2016-17 and 2017-18 have four rows per sample (BPA, BADGE, BPF,
  BPS). The earlier five files have BPA only.

## Label maps for the value items (fixed now, from the census alone, before any value is read)

**Unit rule.** 2009-10 values are ppb as they stand. For every later file, a value x µg/g is
1000·x ppb. A value above 0 is positive; averages are over positives; a printed figure matches
within half a unit of its last digit.

- **bpa-2009 (V1):** `Infant Food` = infant food, `Infant Formula` = infant formula. Graded: 82
  positives; 9 infant-food positives (the page's 9%); range 1.4 to 9.6. **Ungraded** (no label):
  the package splits (70 of 89 metal, 12 of 32 glass), powdered formula and cereal, and "all
  infant-food positives in glass jars".
- **bpa-2010 (V2):** all samples.
- **bpa-2011 (V3):** pasta = `Pasta - Canned`; carrots = `Carrot`; peas = `Pea`, `Pea - Organic`,
  `Pea - Sugar`; corn = `Corn`. Fruit, juices/beverages and soups as in S2 above.
- **bpa-2012 (V4):** pastas/soups = `Pasta - Canned` + `Soup`; coconut milk = `Coconut Milk`;
  juices/beverages = `Beverage - Fruit`, every `Juice - ...`, `Nectar - ...` and
  `juice - pineapple`; fruit = `Apricot`, `Grapefruit`, `JackFruit`, `Longan`, `Lychee`, `Mango`,
  `Mixed Fruit`, `Orange`, `Orange - Organic`, `Papaya`, `Peach`, `Pear`, `Pineapple`,
  `Pineapple - Organic`, `Strawberry`; curry = `Curry`; vegetables = every other label (147).
  Table 5's 2012 rows: beverages, coconut milk, fruit, curry, vegetables, pasta = `Pasta - Canned`,
  soup = `Soup`. **Said in advance:** under this map the curry (21 vs 24), vegetable (147 vs 144)
  and pasta (119 vs 52) rows cannot match their printed n, so V4's "at least 4 of the five
  non-pasta/soup rows in full" can hold only if both the curry and the vegetable rows match. We
  expect it to fail and will also report, as exploratory, the map that adds `Salsa` to curry.
- **bpa-2013 (V5):** Table 5's 2013 rows: beverages = `Beverage - ...` (Fruit, Other, Sport),
  `Energy Drink`, `Soft Drink`, every `Juice - ...` and `juice - pineapple` (97); coconut milk 13;
  fruit = `Cherry`, `Gooseberry`, `JackFruit`, `Lychee`, `Mango`, `Mango - Organic`, `Misc Fruit`,
  `Mixed Fruit`, `Orange`, `Papaya`, `Peach`, `Pineapple` (38); infant formula = both `Infant
  Formula` labels (55); pasta = `Pasta - Canned` (45); pie filling = every `Pie Filling` label (20);
  curry sauces = `Sauces` (5); soup = `Soup` (48); vegetables = every other label (70). All nine n
  match.
- **bpa-2016 (V6):** beverages = `Beverage - ...`, `Energy Drink`, `Soft Drink`, every `Juice -
  ...`, `Nectar - ...` and `juice - pineapple`; infant formula = both `Infant Formula` labels;
  pasta = `Pasta - Canned`; sauce = `Sauces` + `Tomato Sauce`; soup = `Soup`; coconut milk; fruit
  = `Apricot`, `Grapefruit`, `JackFruit`, `Lychee`, `Mango`, `Mixed Fruit`, `Orange`, `Peach`,
  `Pear`, `Pineapple`, `Pineapple - Organic`; pie filling = every `Pie Filling` label; vegetables =
  every other label (72). Table 2 can be graded in full only for coconut milk, fruit, pie filling
  and vegetables. The other five rows mix canned and other packaging, so their Table 2 cells, the
  340 canned positives and the canned average 91.6 are **ungraded**. They are reported over all
  packaging. Graded: 361 positives in all 491 samples; the all-products average 87.2; the text's
  maxima and next-highest values (pie filling 2240 / 530, the top one in `Pie Filling - Pumpkin`;
  coconut milk 1370 / 478; fruit 1160 / 186, the top one in `Pineapple`; sauces 1120 / 7.5),
  taken over all packaging. V6's "at least 8 of 9 rows" can therefore be graded only as "all 4
  gradable rows".
- **bpa-2017 (V7):** meat and fish as in S2. "Imported sardine" is checked as imported fish
  (no sardine label).
- **D1 (trend):** shared categories for 2012-13 vs 2013-14 at a common 5.2 ppb cut: vegetables,
  fruit, juices/beverages (2013-14: `Beverage - Fruit`, `Beverage - Other`, every `Juice - ...`
  and `juice - pineapple`, without energy, sports and soft drinks), pastas/soups, coconut milk,
  curry (2012-13 `Curry`; 2013-14 `Sauces`).

## Next

One grader for all seven files (V1-V7 and D1), using exactly these maps and the unit rule, is
committed and public before a sealed job reads any value.

MV2, Munim, Inc., mv2@munimtech.com
