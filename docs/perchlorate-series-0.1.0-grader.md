# perchlorate-series 0.1.0: grader note — the 2013-14 food-group map, fixed from label counts and printed shares, and the grader

GRADER-MARKER: perchlorate-series-0.1.0-grader

By MV2 of Munim, Inc. Prepared with AI agents working in his name. Text CC BY 4.0; code Apache-2.0.

This follows the [pre-registration](perchlorate-series-0.1.0-prereg.md) (`v0.4.106`) and the
[census note](perchlorate-series-0.1.0-census.md) (`v0.4.108`). Written on 2026-11-04. **No
result value of any of the three files has been read.** Everything below uses only the label
counts in `data/perchlorate_p13_census.json` and figures printed on CFIA's 2013-14 summary page.
It fixes the last open label map (2013-14), states what that map implies before any value is
read, and publishes the grader `perchlorate_series.py` with its offline tests
`test_perchlorate_series.py`. This is a reproducibility check of open government data. It is not
a compliance finding (Health Canada has set no maximum level for perchlorate in food), not about
any brand, and not dietary or medical advice.

## The 2013-14 map

The 2013-14 summary names six groups (fresh vegetables, processed fruit and vegetable products,
dairy products, infant formula, grain products, assorted foods). It gives a detect share for each
and averages for four, but no group sizes. The file has 88 product labels. The census note
fixed dairy (50: the cheese and yogurt labels) and infant formula (all 39). The other 77 labels
are placed as follows.

**Fixed by what the label says:**

- **Fresh vegetables (131):** arugula 9, dandelion 1, endive 2 + broadleaf endive 2, kale 6, the
  three lettuce labels 6, `Misc Vegetables` 2, rapini 1, spinach 2; the 13 fresh-potato labels
  (46); the eight `Herb - ... - Fresh` labels (14); and the eleven plain herb labels (basil,
  bay leaves, chive, cilantro, dill, mint, oregano, parsley, rosemary, sage, thyme; 40). The
  plain herbs count as fresh because this file marks dried products as dried (`Cranberry -
  dried`, `Dried Fruit`, `Dried Vegetables`), and no plain herb label says dried.
- **Processed fruit and vegetable products (73 before the open blocks):** the six dried-fruit
  labels (cranberry, date, dried fruit, fig, prune, raisin; 45), `Dried Vegetables` 17,
  `Mixed Vegetables` 10, `Potato Products` 1.
- **Grain products (60):** couscous 10, rice flour 9, wheat flour 15, rice grain 14, wheat
  grain 1, rice products 2, wheat products 9.
- **Assorted foods (50 before the open blocks):** meat alternatives 10, tofu 10, frozen desserts
  (dairy 9, non-dairy 1), pizza products 20.

**Four blocks whose group the labels do not settle:** the 47 juices, nectars and fruit drinks
(nine `Juice`/`Nectar` labels and `Beverage - Fruit`), soup 15, salsa 9 and `Beverage - Other`
3. Each could be a processed fruit or vegetable product or an assorted food. They are placed by
the only rule that uses no value: the printed shares must be reachable. The summary says 205 of
477 samples had no perchlorate, so 272 had some. A group of n samples with a printed share of p%
needs a whole number of detects k with k/n rounding to p%. Of the 16 placements of the four
blocks, **exactly one** lets every printed share be met while the six groups sum to 272:

| Group | Samples | Printed share | Detects that round to it |
|---|---|---|---|
| Fresh vegetables | 131 | 71% | 93 only |
| Processed fruit/vegetable products (with soup and salsa) | 97 | 40% | 39 only |
| Dairy products | 50 | 80% | 40 only |
| Infant formula | 39 | 54% | 21 only |
| Grain products | 60 | 30% | 18 only |
| Assorted foods (with the juices and `Beverage - Other`) | 100 | 61% | 61 only |
| Total | 477 | | 272 = 477 - 205 |

So the grading map puts **the juices and fruit drinks in assorted foods**, and soup and salsa
in processed products. The natural first guess (juices as processed fruit products) fails: it
leaves 53 assorted foods, and no count of 53 rounds to 61% (32 is 60.4%, 33 is 62.3%).

**What this pins in advance.** Under this map every printed share allows exactly one detect
count, so V8's five shares hold together only if the file has exactly 93, 39, 40, 18 and 61
detects in those groups (and 21 formulas, which V8 does not grade; see S6). One wrong placement
of a single sample can fail a share.

**Other placements the arithmetic allows.** If the blocks fixed above by their labels are also
moved, at least five more placements pass the same test. Each one needs the plain herbs to be
assorted foods, or the dried vegetables to be assorted foods and pizza a grain product. Those
placements are not used for grading. Before grading anything, the grade job prints every
passing placement over all eight blocks: plain herbs, mixed vegetables, dried vegetables, pizza
and the four open blocks. If the grading map fails V8 and another placement would pass, the
result will say so as a description, never as a regrade.

## How each item is graded (`perchlorate_series.py`)

Coding as registered: a detect is a result above zero. Averages are of detects only. A printed
figure matches within half a unit of its last digit. A share matches when it rounds half up to
the printed whole number. Bands are inclusive. Survey years run April to March and come from each
file's date column (`DateSample` in 2011-13).

| ID | Population (fixed maps) | What must hold |
|---|---|---|
| V1 | 2010-11: 433 fruit and vegetables / 89 dairy / 89 formulas | detects 280-283 / 77 / 56; smallest detect rounds to 2; largest 539.5-540.5 |
| V2 | 2010-11 commodities (base label; organic and greenhouse merged; three lettuce labels pooled) | cucumber 48.6 and tomato 44.9, and they are the two highest commodity averages; cheese rounds to 5, yogurt 4.9, milk below both; `Infant Formula - Soy` 16.7 |
| V3 | 2010-11 cheese 23, milk 42, yogurt 24 | counts; maxima 24 / 9 / 12; each minimum rounds to 2; at most one of the three averages is 5.05-5.15; the 89-sample dairy average is 5.05-5.15 |
| V4 | 2010-11 `Infant Formula - Dairy` (74) | minimum 2, maximum 22, average 10.35-10.45 |
| V5 | 2011-13 groups of the census note | 637 without; detects juice 51-52, dairy-based 139-140, formula 49; fruit 44% of 356, vegetables 74% of 525; minimum 2, maximum 2400 |
| V6 | 2011-13 `Cream` (15) by survey year; the 68 formulas not labelled soy | creams 2011-12: 3 / 6 / 4.25-4.35; 2012-13: 3 / 7 / 3.95-4.05; formulas 2 / 33 / 11.75-11.85 |
| V7 | 2011-13 cucumber, tomato, the six leafy commodities pooled (342), and each of the seven fruits | cucumber 106, leafy 65, tomato 57, and these three are the highest averages |
| V8 | 2013-14 six groups as mapped above | 205 without; shares 71 / 40 / 80 / 30 / 61; averages fresh 130, processed 23, grain 5, dairy 6; smallest detect rounds to 2; largest 3299.5-3300.5 and its label names arugula |
| V9 | 2013-14 cheeses (20), yogurts (30), formulas not labelled soy (30) | cheese 3 / 42 / 8.95-9.05; formula 2 / 64 / 16.45-16.55; yogurt 2 / 11 / 4.85-4.95; dairy has 40 detects and 10-16 of them are cheeses |

The census already settles some of this. S4's 8 + 9 creams cannot both hold with 15, but V6
still grades the cream rows by year. V8 leaves out the formula share, as registered.

**Gate (per file):** portal size and MD5, every role column found, every result a number, every
unit `ng/g`, no short rows, the registered sample count, one row per sample, and every label
mapped. If a file's gate fails, its items are reported as ungraded.

**Also reported, before or beside the grades (descriptive, not graded):**

- the 2013-14 placement search above, from label counts;
- for each file, the number of results that are exactly zero, the five smallest above zero, and
  the stored minimum and maximum detect per group and region, so a scale slip (as in the 2018-19
  ethyl carbamate file) or a non-detect coded as a small number is visible;
- each group's split by survey year, including 2011-13's 663 / 763 date split and the year split
  of the 68 non-soy formulas (Table 3 labels them "2011");
- all 89 formulas of 2010-11 and all 39 of 2013-14, for comparison with Table 3's subsets;
- the 2013-14 groups under the juices-as-processed placement.

## Tests

`test_perchlorate_series.py` (offline, standard library) checks, among other things:

- the label maps against the published census counts: 2010-11 433 / 89 / 89; 2011-13
  356 / 525 / 225 / 233 / 87 with 342 leafy; 2013-14 131 / 97 / 50 / 39 / 60 / 100 with all 88
  labels mapped;
- the share arithmetic: one passing placement of the four open blocks, and none with the juices
  in processed products;
- that the 2011-13 `DateSample` dates (month/day/year) land in the right survey year;
- the gate, and three graders on synthetic values.

## The next step

The sealed job `perchlorate-grade-v1` waits until this note is public and makes its modules
equal the published copies. It then runs the tests, and only then reads the values. Its result
note will report every item as met, failed or ungraded, with an independent test.

MV2, Munim, Inc., mv2@munimtech.com
