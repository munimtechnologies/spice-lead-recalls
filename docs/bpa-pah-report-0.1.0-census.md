# bpa-pah-report 0.1.0: the names-only census, its graded items, and the label maps fixed before any value is read

CENSUS-MARKER: bpa-pah-report-0.1.0-census

Made with AI agents working in MV2's (Munim, Inc.) name. Text CC BY 4.0; code Apache-2.0.
Not a compliance finding, not about any product or brand, and not dietary or medical advice.

This note follows the pre-registration [bpa-pah-report-0.1.0-prereg.md](bpa-pah-report-0.1.0-prereg.md)
(tag `v0.4.86`). The sealed job `cfia-census-2019-v1` ran on 2026-10-31 at 01:09 UTC (python:3.12,
1 GB). It waited for the registration to be public, checked that its bundled `cfia_census.py` and
tests were identical to the published copies, ran the tests, then ran the names-only census:
counts of rows, samples, labels, units and origins, and the *shape* of every result cell. **No
result value was printed, summed or compared.** The census files are committed as
`data/bpa-2018_census.json` and `data/bpa-2020_census.json`.

- **bpa-2018** and **bpa-2020** were read. Both files' size and MD5 match the portal records.
- **pah-2019 was not read.** Both open.canada.ca and ouvert.canada.ca reset the connection on
  every try, so item D1 is still open. A new job, `pah2019-census-v1`, re-runs the same published
  census code on that file alone with patient retries (`pah2019_census.py`, which imports
  `cfia_census.py` unchanged).

## Graded census items: 1 of 2 held, 1 void, 1 pending

| ID | Registered | Census | Result |
|---|---|---|---|
| B1 | bpa-2018 holds **381** samples, 49 / 138 / 98 / 96 (the summary and Table 3) | **377** samples: 49 / 135 / 98 / 95 (Tables 1 and 2) | ❌ (the registered competing reading holds) |
| B7 | if the file names the three extra formulas' form or package, they are not liquid milk-based | there are no extra formulas: the file has Table 2's 135 | void |
| C1 | bpa-2020: 402 samples split 101 / 52 / 100 / 49 / 100, Table 1's origins in ≥ 4 of 5 rows | 402, split 101 / 52 / 100 / 49 / 100; origins match in **5 of 5** rows | ✅ |
| D1 | pah-2019: 296 samples, 34 / 114 / 148, 16 PAHs each, one unit | not read (connection resets) | pending |

**B1 failed.** We had read the report's four conflicting counts as one story: the summary's 381
and Table 3's 138 formulas and 96 sauces were right, and Tables 1 and 2 had left four samples out.
The file says the opposite. It holds 377 samples, which is Tables 1 and 2. The summary's 381 and
Table 3's 138 and 96 do not match the open file. The registration named this outcome as the
competing reading.

This also takes the premise out of value items B2 (Table 3's formula row), B3 (96 sauces) and B4
(165 of 381). They will still be graded exactly as registered. Each now predicts a figure that the
file can only reproduce if the extra samples are not needed, so we expect them to fail.

## What else the census shows (facts, not graded)

**bpa-2018** (dataset `b8686c21-...`, 289,825 bytes): 1,508 rows = 377 samples x 4 components
(bisphenol A, BADGE, bisphenol F, bisphenol S), one row each. All 1,508 cells are plain numbers.
Unit **µg/g** on every row (the report prints ppb = ng/g). Plan `2018_SB451`. Commodity `IMFD`
on every row. Sample numbers run from 1 to 400 with 23 gaps, in blocks by product: pie fillings
1-100 (2 numbers unused), coconut milk 101-150 (1 unused), sauces 151-250 (5 unused) and infant
formula 251-400 (15 unused). Three IDs carry a D suffix (`C2018BPHA00111D`, a coconut milk, and
`00170D` and `00171D`, sauces). None of their base IDs is in the file, which is the same pattern
as the 2018-19 toxic metals file.

**bpa-2020** (dataset `5b36b36d-...`, 285,553 bytes): 1,608 rows = 402 samples x the same 4
components, all plain numbers, unit µg/g, plan `2020_SB451`, no commodity column. Sample numbers
run from 1 to 400 with 1 gap, plus three D-suffixed IDs. Unlike 2018-19, each D ID sits next to its
base ID: `00001` and `00001D` are a peach and a pear, `00013` and `00013D` a beet and a pea, and
`00046` and `00046D` both canned fish. So in this file a D suffix marks a second sample that
shares a number, not a repeat test.

## Label maps for the value items (fixed now, from the census alone, before any value is read)

**Unit rule.** Both files report µg/g. A file value x µg/g is 1000·x ppb, and every printed figure
is compared after that conversion. A value above 0 is positive. Averages are over positives.

**bpa-2018** (the counts match Tables 1 and 2 exactly):

| Report type | File labels | n |
|---|---|---|
| Coconut milk | `Coconut Milk` | 49 |
| Infant formula | `Infant Formula - Dairy` (104), `Infant Formula - Other` (31) | 135 |
| Pie filling | `Pie Filling - Blueberry` (30), `- Cherry` (30), `- Other` (12), `- Pumpkin` (26) | 98 |
| Tomato-based sauces | `Sauces` (91), `Tomato Sauce` (4) | 95 |

**bpa-2020** (the counts and all fifteen origin cells of Table 1 match):

| Report type | File labels | n | Domestic / imported / unspecified |
|---|---|---|---|
| Fish | `Fish/Seafood - Canned` | 101 | 8 / 90 / 3 |
| Fruit | `Apricot`, `Cherry`, `Cranberry`, `Grapefruit`, `JackFruit`, `Lychee`, `Mango`, `Mixed Fruit`, `Orange`, `Peach`, `Pear`, `Pineapple` | 52 | 0 / 50 / 2 |
| Meat | `Meat - Canned` | 100 | 20 / 55 / 25 |
| Pie filling | `Pie Filling - Blueberry`, `- Cherry`, `- Other`, `- Pumpkin`, `- apple` | 49 | 0 / 49 / 0 |
| Vegetables and vegetable products | every other label (`Artichoke Heart`, `Bean - Green/Yellow`, `Bean - Kidney`, `Bean - Pinto`, `Beet`, `Carrot`, `Corn`, `Lentil`, `Mixed Vegetables`, `Mushroom`, `Mushroom - Shiitake`, `Pea`, `Soup`, `Sprout - Bean`, `Vegetable Products`, `Water Chestnut`) | 100 | 19 / 73 / 8 |

Origin is the file's Function column (`Domestic`, `Import`, `Unknown` = unspecified). The
co-occurrence items in C4 ("imported meat or fish") use the same column.

Items whose wording needs a label the file lacks (bpa-2018's "liquid, milk-based, bottle or can";
bpa-2020's "chicken", "herring", "corned beef", "mackerel") will be reported as ungraded, not as
misses. The file carries no product description beyond these labels.

## Next

1. `pah2019-census-v1` reads the 2019-20 PAH file and grades D1; the pah-2019 label map is then
   fixed the same way, in a note, before its values are read.
2. A grader for B2-B6 and C2-C4, using exactly the maps and unit rule above, is committed and
   public before a sealed job reads any value.

MV2, Munim, Inc., mv2@munimtech.com
