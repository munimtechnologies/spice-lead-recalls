# CFIA's 2018-19 multi-mycotoxin survey: what its report and file labels say (multimyco-2018-report-check 0.1.0)

REPORT-CHECK-MARKER: multimyco-2018-report-check-0.1.0

By MV2 of Munim, Inc. Prepared with AI agents working in his name. Text CC BY 4.0.

This is a record of CFIA's report on the 2018-19 survey, plus the names-only census of its open
per-sample file. **It was written before any AMOUNT value in that file was read.** A
pre-registered check of the file follows. Its predictions are fixed against the figures below,
which are public first in this note. This note is not a finding about any product or brand, and
it is not a health-risk claim: Health Canada judged the levels found "not expected to pose a
concern to human health".

## Sources

- **Report:** CFIA, "Multi-Mycotoxins in Corn Products, Crackers, Other Grain Products, Pasta and
  Gluten-Free Products – April 1, 2018 to March 31, 2019", Food chemistry – Targeted surveys –
  Final report. Web page
  `inspection.canada.ca/en/food-safety-industry/food-chemistry-and-microbiology/food-safety-testing-reports-and-journal-articles/multi-mycotoxins-corn-products`,
  "Date modified: 2021-04-07". The same report is also a PDF
  (`multi-mycotoxin_in_corn_product_2018-2019_1614979983267_eng.pdf`). Read on 2026-10-26.
- **File:** Open Government Portal dataset `03f184ee-e5e0-4e33-a763-fa3e44ed2dc0`, CSV resource
  `09a3c285-8552-4a38-b4be-cdf6d5fc3fd2`, SHA-256
  `ba5084945f0a0e1fab2b8bab7f8f196a7dd0033d4bdc4e80768f12ec4c553835` (3,484,399 bytes, cp1252),
  Open Government Licence – Canada. Its names-only census came from sealed job `myco-census-v2`
  (2026-10-25). That job read the headers, labels and counts only: 18,750 rows, 750 samples, 25
  rows per sample, one plan code (`2018_SB427`), one report unit, 207 distinct AMOUNT strings.

## What the report prints

| Table 2 | n | with mycotoxins | without |
|---|---|---|---|
| Corn products | 136 | 92 (68%) | 44 (32%) |
| Crackers | 102 | 70 (69%) | 32 (31%) |
| Gluten-free products | 70 | 17 (24%) | 53 (76%) |
| Other grain products | 297 | 103 (35%) | 194 (65%) |
| Pasta | 145 | 104 (72%) | 41 (28%) |
| **Grand total** | **750** | **386 (51%)** | **364 (49%)** |

Table 1 (origin): domestic 155, imported 305 ("at least 27 countries"), unspecified 290.
Table 3 (2018 row, n = 750, positives, maximum, average of positives, ppb):
DON 306 (41%), max 2,570, avg 282. Fumonisins B1/B2/B3 105 (14%), 3,503, 280. Ergot alkaloids 46
(6.1%), 664, 79. ZEN/α-ZOL/β-ZOL 34 (4.5%), 450, 44. OTA 20 (2.7%), 34, 4.2. Cyclopiazonic acid
18 (2.4%), 47, 11. Sterigmatocystin 12 (1.6%), 12, 2.7. Aflatoxins B1/B2/G1 11 (1.5%), 30, 4.4.
HT-2/T-2 8 (1.1%), 98, 37. Nivalenol 7 (0.9%), 86, 22. 3-/15-acetyl-DON, DAS, FUS-X and NEO 0.
Every printed percentage equals its count over its n, and every column sums to its total.

## Five things to settle from the open file

1. **388 or 386?** The summary and results text say "Mycotoxins were detected in 388 samples
   (52%)". Table 2's grand total says 386 (51%). Both cannot describe the same file.
2. **Origin is one sample off.** The file's `Origin` labels give CANADA 155 samples, which
   matches the report's 155 domestic exactly, and UNKNOWN 291 against the report's 290
   unspecified. That leaves 304 samples with a named foreign origin against 305 imported. The
   file names 28 foreign origins. Counting SCOTLAND inside UNITED KINGDOM gives 27, which matches
   "at least 27 countries". The file's separate `Function` column (Import 363, Unknown 233,
   Domestic 154 samples) matches none of the report's figures.
3. **The product categories do not follow the file's labels.** The file has 30 product labels.
   Grouped the obvious way they give: corn (Flour - Corn 52, Corn Products 30, Corn Starch 25,
   Cornmeal 25, Chips - Corn 18) **150** against the report's 136; pasta (Pasta - Dry 62,
   Pasta - Fresh 40, Pasta 26) **128** against 145; Crackers **101** against 102; Gluten-free
   Products **71** against 70; and the 19 other grain labels (barley, quinoa, rye, spelt, teff,
   arrowroot, buckwheat, kamut, millet, amaranth, bread, grain - other) **299** against 297. The
   one `Chips - Other` sample is left over. The gaps (−14, +17, +1, −1, −2) fit one hypothesis:
   the report moved 17 pasta-type products (14 from corn labels, 2 from other-grain labels and 1
   from gluten-free) into Pasta, and put the chips sample with Crackers. The labels alone cannot
   show that. Table 1's per-category origin split may be able to.
4. **"17 different mycotoxins" and the "zeranols".** The file has 24 component labels. One of
   them, `?-Zearalenol(ppb)`, appears twice per sample (1,500 rows), so it is almost certainly
   α- and β-zearalenol with the Greek letter lost in encoding. That makes 25 analytes. The report
   lists eight as never detected: aflatoxin G2, 3-acetyl-DON, 15-acetyl-DON, neosolaniol, DAS,
   fusarenon-X, "alpha-zeranol" and "beta-zeranol". Zeranols (synthetic growth promoters) are
   not in the file. If the report's "zeranols" are the file's two zearalenols, then 25 − 8 = 17,
   which matches the report's count. Read literally, the count is 25 − 6 = 19. So the report
   either misnames α-/β-zearalenol or miscounts.
5. **How many samples exceed the proposed OTA level?** The report says only that "the
   compliance rate for grain based products for OTA (99.1%)" was comparable to earlier years. It
   gives no count. On all 750 samples, 99.1% means exactly 7 above the proposed 3 ppb (6 would
   be 99.2% and 8 would be 98.9%). If the base were a subset (only "grain based products"),
   fewer would fit: 6 on a base of 632–705 samples, or 5 on 527–588.

Also noted: the methods section refers to "a list of the pesticides analyzed", which looks like
text left over from a different report. The report gives no limits of detection, and no
per-toxin minimums (only "0.4 ppb to 2570 ppb" overall). CFIA's separate 2018-19 ochratoxin A
survey reports OTA in 30 of 40 crackers (75%, max 2.2 ppb). This survey finds OTA in 20 of 750
samples of all kinds. That gap points to very different detection limits, which the open file
may show.

## Next

A pre-registration (`multimyco-2018`) will register predictions on each point above, fixed
against the published figures. It will also cover the product-level co-occurrence of DON with
the other *Fusarium* toxins, and whether the zearalenol rows hold any detection. A sealed job will
grade it from the SHA-256-pinned file. The cooc-strata result showed that pooled co-occurrence in
mixed retail files is mostly composition, so any co-occurrence prediction there will be stratified
by product label from the start.
