# CFIA's 2018-19 ochratoxin A grain survey: what its two reports and the file's labels say (ota-grain-2018-report-check 0.1.0)

REPORT-CHECK-MARKER: ota-grain-2018-report-check-0.1.0

By MV2 of Munim, Inc. Prepared with AI agents working in his name. Text CC BY 4.0.

**Written before any result value in the survey's open file was read.** This note records two
things: what CFIA printed about its survey "Ochratoxin A in Wheat Products, Oat Products, Rice
Products and Other Grain Products – April 1, 2018 to March 31, 2019", and what a names-only
census of the open per-sample file shows. It makes no product, brand or health-risk claim.
Health Canada judged the OTA levels in the survey "unlikely to pose a health risk", and no
recall was warranted. The pre-registered check follows in
[ota-grain-2018-0.1.0-prereg.md](ota-grain-2018-0.1.0-prereg.md).

## Sources

- **R20:** CFIA, the survey's own report (catalogue A104-242/2020E-PDF, modified August 2020),
  read from its HTML page on 2026-10-27. Tables 1–5.
- **R22:** CFIA, "Ochratoxin A in Selected Foods – April 1, 2012 to March 31, 2018 and April 1,
  2019 to March 31, 2022". Its Table 7 ("targeted survey data on OTA concentrations in
  grain-based foods") reprints this survey as five rows for the year 2018. It prints percent
  positive, not counts.
- **OG:** the open file, Open Government Portal dataset `7296b53e-56fc-41df-82c6-04656422b39e`,
  resource `d9d79110-e472-4aec-89ee-e51861f4d88d` (`1068.csv`, 139,876 bytes, UTF-8 with BOM),
  SHA-256 `36dde7d7…7d47403`, Open Government Licence – Canada.
- **Census:** the names-only job `myco-census-v2` (2026-10-25). It records labels, counts and the
  *format* of each result cell, never a value.

## What the census shows

- 496 rows, 496 distinct samples, one row each, all `Ochratoxin A`, one plan code, one unit.
- **The result column holds 220 cells that parse as numbers above 0 and 276 cells that do not
  parse as numbers.** None are blank, `0`, `<…` or a standard non-detect token, and none use a
  decimal comma. So non-detects are written as some other text, and this file needs its own
  value rule (the CFIA mycotoxin files read so far used a literal 0).
- 21 product labels: `Grain - Rice` 99; `Bakery Product - Cookie`, `Crackers`, `Wheat Products`
  29 each; `Baking Mixes`, `Infant Food - Cereal`, `Pasta - Dry` 28 each; `Cereal - Children`
  26; `Bran - Oat`, `Oatmeal` 25 each; `Kamut Products`, `Oat Products`, `Quinoa Products` 24
  each; `Buckwheat Products`, `Flour - Oat` 23 each; `Rye Products` 21; `Flour - rye` 4;
  `Flour - Other` 3; `Crispbread/Crouton` 2; `Cereal`, `Grain - Kamut` 1 each.
- `Origin`: CANADA 92, UNKNOWN 232, 172 foreign over 25 countries. `Function`: Import 282,
  Unknown 122, Domestic 92.

## Ten points from the reports and the labels

1. **495 or 496 samples.** R20 says 495 everywhere (summary, Table 1, Table 2). R22's five 2018
   rows add up to 100 + 97 + 99 + 29 + 171 = **496**, the file's count.
2. **R22's rows are the file's labels.** Each R22 row equals a set of file labels exactly:
   less commonly consumed grains 100 = rye (21 + 4) + kamut (24 + 1) + `Buckwheat Products` 23
   + `Quinoa Products` 24 + `Flour - Other` 3; oat 97 = the four oat labels; rice 99 =
   `Grain - Rice`; wheat 29 = `Wheat Products`; grain-based foods 171 = cookie, crackers,
   baking mixes, infant cereal, pasta, children's cereal, crispbread and cereal (29 + 29 + 28 +
   28 + 28 + 26 + 2 + 1). R20 instead classes products by grain, and only some of its rows
   follow labels (point 5).
3. **R20's positive count is one short of the file.** Table 2's positives add up to 11 + 10 + 55
   + 8 + 13 + 15 + 107 = **219**. The file has 220 numeric cells. R22's percentages pin four of
   its counts (44 of 100, 52 of 97, 14 of 99, 18 of 29 are the only counts that round to 44%,
   54%, 14% and 62%), and its grain-based 54% of 171 is 92 or 93. With 92 they add up to
   **220**. The difference is rice. Table 2 prints 13 positives of 98, while R20's own Table 5
   prints **14** of 98 for the same year, and R22 prints 14% of **99**, which is 14.
4. **"45%" does not follow from any count.** 219 / 495 = 44.2%, 220 / 495 = 44.4% and 220 / 496
   = 44.4%. All of them round to 44%, not R20's 45% (or its "55% not detected").
5. **Which R20 rows the labels identify.** Rye is 25 in Table 2, and `Rye Products` +
   `Flour - rye` is 25. Three Table 3 rows equal one label each: baking mixes, infant cereal
   (wheat) and pasta are 28 each. The other grain rows are off by a few: rice 98 (file 99),
   buckwheat 25 (23), quinoa 25 (24), kamut 26 (25), oat 100 (97). Wheat is 196, against 203
   in the ten generic labels. The pattern fits R20 moving seven products from generic labels
   (a cookie, a cracker, a cereal) into their grain's row, and putting rice at 98.
6. **Table 4's oat average is impossible.** It prints a 2018-19 oat average of **2.6** ppb with a
   maximum of 1.6. Table 2 (and R22) print 0.26.
7. **Table 5's other row** prints "1 (14)" for one rice sample in 2011-12: one positive of one
   is 100%, not 14%.
8. **Table 3 adds up.** Its eight 2018-19 wheat subrows sum to 196 samples and 107 positives,
   matching Table 2's wheat row. Their positive-weighted average is 29.36 / 107 = 0.274,
   matching 0.27. Their minimum (0.042) and maximum (2.2) are Table 2's. But
   crackers/crispbreads is **40** in Table 3, while the file has 29 `Crackers` and 2
   `Crispbread/Crouton`. So at least nine of R20's wheat crackers carry another label.
9. **Origins do not match.** R20's Table 1 has 93 domestic, 169 imported and 233 unspecified.
   The file's `Origin` has 92 CANADA, 172 foreign and 232 UNKNOWN. Its `Function` column
   (Domestic 92, Import 282, Unknown 122) matches neither.
10. **Compliance is internally consistent.** 99.8% of n = 420 is wheat + oat + rice + kamut (196
    + 100 + 98 + 26) with one non-compliant sample (the 11 ppb brown rice): 419 / 420 = 99.76%.
    Buckwheat (maximum 7.6) and quinoa (5.8) are above 3 ppb, but Health Canada has proposed
    no level for them, so R20 counts them as compliant.

## The same year, a second CFIA method

CFIA's 2018-19 multi-mycotoxin survey measured OTA in 750 other grain foods. Its open file, graded
in [multimyco-2018 0.1.0](multimyco-2018-0.1.0-result.md), found OTA in 2.7% of samples and in 2
of 101 crackers. This survey found it in about 44% of samples and in 30 of 40
crackers/crispbreads. Neither report states a detection limit. Two published figures suggest
the reason for the gap:

- The multi-mycotoxin file's smallest OTA result is **0.8 ppb** (all 20 OTA positives are
  0.8–33.8 ppb).
- CFIA's 2015–2018 multi-mycotoxin report (Appendix A, Table A1) lists the method's OTA limit of
  detection as **0.8 ppb** (LOQ 5 ppb).

This survey's smallest result is 0.042 ppb, about twenty times lower. The two files share
seven product labels: `Buckwheat Products`, `Crackers`, `Grain - Kamut`, `Kamut Products`,
`Pasta - Dry`, `Quinoa Products` and `Rye Products`. So the open data can test whether the
two surveys agree once both are read at the same 0.8 ppb cut, or whether the multi-mycotoxin
method also misses OTA above its limit. CFIA's reports do not make this comparison.

## Prior art

On 2026-10-27, searches for analyses of this open file, and for a comparison of CFIA's OTA-only
and multi-mycotoxin results on the same product types, found none. The file's metadata was
modified on 2026-03-31.
