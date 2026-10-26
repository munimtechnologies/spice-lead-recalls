# Pre-registration: CFIA's open 2018-19 multi-mycotoxin file against its own report (multimyco-2018 0.1.0)

PREREG-MARKER: multimyco-2018-0.1.0-prereg

By MV2 of Munim, Inc. Prepared with AI agents working in his name. Text CC BY 4.0; code Apache-2.0.

This registers, **before any AMOUNT value in the file has been read**, a gate and ten graded
checks of the Canadian Food Inspection Agency's open per-sample file for its 2018-19
"Multi-Mycotoxins in Corn Products, Crackers, Other Grain Products, Pasta and Gluten-Free
Products" targeted survey. The predictions are fixed against the figures CFIA printed in its
report and against a names-only census of the file; both are public first in the companion
[report-check note](multimyco-2018-report-check-0.1.0.md). A sealed job
(`multimyco-2018-v1`) grades it only after this note is public (its commit timestamp proves the
order), by downloading the SHA-256-pinned file and running the committed code. This is a
reference comparison, not a compliance finding (Canada sets no mycotoxin maximum level for these
foods), not about any brand, and not individual dietary or medical advice. Health Canada judged
the levels found "not expected to pose a concern to human health".

## Sources

- **Report:** CFIA, "Multi-Mycotoxins in Corn Products, Crackers, Other Grain Products, Pasta and
  Gluten-Free Products – April 1, 2018 to March 31, 2019", Food chemistry – Targeted surveys –
  Final report (web page and PDF `multi-mycotoxin_in_corn_product_2018-2019_1614979983267_eng.pdf`,
  "Date modified: 2021-04-07"). Every printed figure used below is transcribed in the report-check
  note.
- **File:** Open Government Portal dataset `03f184ee-e5e0-4e33-a763-fa3e44ed2dc0`, CSV resource
  `09a3c285-8552-4a38-b4be-cdf6d5fc3fd2`, SHA-256
  `ba5084945f0a0e1fab2b8bab7f8f196a7dd0033d4bdc4e80768f12ec4c553835` (3,484,399 bytes, cp1252),
  Open Government Licence – Canada. Names-only census: sealed job `myco-census-v2` (2026-10-25),
  which read headers, labels and counts only — 18,750 rows, 750 samples, 25 rows per sample, one
  plan code `2018_SB427`, one report unit, 207 distinct AMOUNT strings.

## What the census already fixes (names only, no value read)

- 24 distinct English `Component` labels. All carry 750 rows except `?-Zearalenol(ppb)`, which
  carries 1,500 (two rows per sample: α- and β-zearalenol, distinct in the French `Composant`
  column, which has 25 labels). So there are 25 analytes but 24 English labels.
- 30 `Product` labels (per-sample counts summing to 750), e.g. Crackers 101, Gluten-free Products
  71, Pasta-Dry 62, Flour-Corn 52, Corn Products 30, Corn Starch 25, Cornmeal 25, Chips-Corn 18.
- `Origin`: CANADA 155 samples, UNKNOWN 291, and 304 samples across 28 named foreign origins
  (30 distinct origins in all; folding SCOTLAND into the United Kingdom gives "at least 27
  countries", as the report says). The file is therefore one sample off the report's origin table
  (290 unspecified, 305 imported) — a gap noted, not graded here.

## The registered AMOUNT parse rule

A cell is a **non-detect** if it is blank, equal to `0`/`0.0`, begins with `<`, or is a
non-detect token (`nd`, `n.d.`, `n/d`, `not detected`, `non détecté`). Otherwise it is a
**positive** plain decimal (ppb). Any cell containing a comma, or otherwise not a number, is
treated as an unparseable format and **fails the gate** — so an unexpected numeric convention
(comma decimals, thousands separators, or a bare detection-limit coding like CFIA's 2011-12
coumarin file) is caught loudly rather than silently misread. The grader also reports the AMOUNT
census (kinds and distinct count) so any surprise is visible.

## Gate (G) — all from the census or the SHA; graded true only if every item holds

SHA-256 as above; 18,750 rows; 750 distinct samples; 25 rows per sample; the 24 component labels
with their exact counts; the 30 product labels with their exact per-sample counts; one plan code
`2018_SB427`; exactly one report unit; origin CANADA 155, UNKNOWN 291, 304 foreign over 30
origins; and a clean AMOUNT format (no comma or unparseable cell, at least one positive). If any
item fails, no prediction below is graded.

## Predictions (fixed now; each is met or missed, reported plainly)

- **P1 — 388 vs 386.** Exactly **386** of 750 samples carry at least one detected mycotoxin —
  the grand total of the report's Table 2, not the **388** its summary text prints. (Both appear
  in the report; only one can describe the file.)
- **P2 — DON.** Deoxynivalenol is detected in **306** of 750 samples (Table 3), with maximum
  **2570** ppb and average-of-positives **282** ppb.
- **P3 — the "17 mycotoxins" and the zeranols.** Exactly **17** of the 24 English component
  labels are detected in ≥1 sample. The 7 never detected are the `?-Zearalenol(ppb)` label (both
  zearalenols), 3- and 15-acetyl-deoxynivalenol, aflatoxin G2, diacetoxyscirpenol, fusarenon-X and
  neosolaniol. This is the only reading under which the report's "17 different mycotoxins
  detected" is literally correct: its "alpha-/beta-zeranol" (listed as never detected) are the
  file's zearalenols, and Zearalenone alone carries the 34 positives of the ZEN group.
- **P4 — Table 3 counts.** The nine non-DON groups reproduce Table 3's positive-sample counts
  exactly: fumonisins (any of B1/B2/B3) 105, ergot alkaloids (any of ergocristine/ergocryptine/
  ergosine) 46, Zearalenone 34, ochratoxin A 20, cyclopiazonic acid 18, sterigmatocystin 12,
  aflatoxins (any of B1/B2/G1) 11, HT-2/T-2 (either) 8, nivalenol 7.
- **C1 — single-analyte max and average.** For the four single-analyte groups, the file's maximum
  and average-of-positives match Table 3: OTA 34 / 4.2, cyclopiazonic acid 47 / 11,
  sterigmatocystin 12 / 2.7, nivalenol 86 / 22 ppb. (The grader also reports the all-sample mean,
  since CFIA's coumarin tables once used that under a positives-only note.)
- **P5 — the uncounted OTA figure.** CFIA reports only a 99.1% OTA compliance rate for grain-based
  products, with no count. On all 750 samples, 99.1% means exactly **7** samples carry OTA above
  the proposed 3 ppb level; P5 predicts 7.
- **P6 — the crackers OTA gap.** OTA is detected in **fewer than 25%** of the 101 crackers — far
  below the 75% (30 of 40) CFIA reported for the *same year's* dedicated OTA-only crackers survey.
  A large gap points to a higher effective detection limit in this multi-toxin method, not to
  cleaner crackers.
- **P7 — is the DON × fumonisin co-occurrence a commodity effect?** Pooled across all 750 samples,
  DON and fumonisin detection co-occur (odds ratio > 1). Within the finest product label, the
  Mantel-Haenszel odds ratio is pulled **toward 1** (|ln MH| < |ln pooled|), because fumonisins
  sit almost entirely in corn. This repeats, in a second CFIA file, what
  [cooc-strata](cooc-strata-0.1.0-result.md) found for OTA × DON: pooled multi-toxin co-occurrence
  in a mixed-commodity file is mostly composition. Stratified from the start, per that lesson.
- **P8 — most toxins in one sample.** The largest number of distinct toxin groups (of the 10)
  detected in any single sample is **9**, and that sample is a corn-type product.

Nineteen of the above are genuinely blind against the file's values (P1–P8, C1); the gate and the
census facts are already public. A miss is reported as a finding, not hidden — as in this
series' earlier mycotoxin notes, a blind prediction that misses has repeatedly been the headline
(the OTA × DON association, the OTA infant-formula report error). The grading code
(`multimyco_2018.py`) and its offline tests (`test_multimyco_2018.py`) are committed with this
note; the result note and a pinned recompute test follow once the sealed job reports.
