# Pre-registration: CFIA's open 2015-16 deoxynivalenol file for grains, pseudo-cereals and pulses, and a second look at two CFIA methods (don-grains-2015 0.1.0)

PREREG-MARKER: don-grains-2015-0.1.0-prereg

By MV2 of Munim, Inc. Prepared with AI agents working in his name. Text CC BY 4.0; code
Apache-2.0.

**Written before any result value in the 2015-16 file was read.** The figures below come from
CFIA's summary page, a names-only census of the open file, and figures already published in
this repository. The census records labels, counts and the format of each result cell, never a
value. The 2018-19 multi-mycotoxin file (MM) was already read and graded in
[multimyco-2018 0.1.0](multimyco-2018-0.1.0-result.md). This registration uses only its
published DON facts (306 positives; the smallest is 10 ppb) and the published listing
`data/multimyco_2018_positives.csv`.

The grading code is `don_grains_2015.py`, and its offline tests are `test_don_grains_2015.py`. A
sealed compute job grades this registration only after it is public on GitHub. The job checks
out the published code and then reads the two SHA-256-pinned files.

Nothing here is a finding about any product, brand or health risk. Canada sets no DON maximum
level for these finished foods. CFIA reports that the levels found "were considered safe for
consumption by Canadians and no product recalls were required".

## What CFIA printed

- **R15:** CFIA, "2015-2016 Deoxynivalenol in Selected Grains and Pulses", summary page
  (modified 2018-10-03, read 2026-10-28). It says "997 products were sampled" and "Detectable
  levels of DON were found in 46% of samples tested". The survey covered grain products,
  pseudo-cereals such as quinoa, and pulses. The full report is "available upon request", so no
  table, range or average is public.
- **R18:** CFIA, "Multi-Mycotoxins in Milled Grain Products and Grain-based Foods – April 1, 2015
  to March 31, 2018". Its Appendix Table A1 lists the multi-mycotoxin method's DON limit of
  detection as **10 ppb** (LOQ 50). Its Table 5 compares earlier CFIA DON surveys and has no row
  for this survey.

We found no CFIA document that reprints this survey's results by product.

## What the census shows (names only)

- **DG:** Open Government Portal dataset `debeebfe-8e35-4914-8ad5-8432340e1e5a`, resource
  `90b59896-d874-4da5-9c03-580d7ee6c584`, 201,445 bytes, UTF-8 with BOM, SHA-256
  `b662d980…4912d7`, Open Government Licence – Canada.
- 997 rows, 997 distinct samples, one row each, all `Deoxynivalenol`, all in `ng/g`. Sampled
  2015-05-02 to 2016-03-14.
- Every result cell is a number. Literal zeros are present. 326 distinct non-zero strings,
  with at most 7 rows sharing one. Unlike MM, whose DON results are whole multiples of 10 ppb,
  this suggests a finer reporting step.
- 44 product labels: 19 grain and pseudo-grain labels (26–52 samples each), 23 pulse and soy
  labels (8 each, except `Bean - Other` 12 and `Tofu` 9), `Flour - rye` 6 and
  `Meat Alternative` 6.
- `Origin`: UNKNOWN 407, CANADA 254, UNITED STATES 217, others 119 over 21 countries.
  `Function`: Import 425, Unknown 318, Domestic 254.
- **18 product labels are shared with MM.** On those labels the published MM listing has DON in
  75 of 297 samples. This was counted from published data and is reported, not gated.

## Data and rules

- **Values (registered rule):** a number above 0 is a positive, and a literal 0 is a non-detect.
  Any blank, text, negative or non-finite cell fails the gate.
- **Units:** units go through an explicit table, and an unknown unit fails the gate.
- **MM:** resource `09a3c285-8552-4a38-b4be-cdf6d5fc3fd2`, SHA-256 `ba508494…3835`. Only its 750
  DON rows are used.
- **Common cut: 10 ppb.** This is MM's smallest DON result and the DON limit of detection R18
  lists for the multi-mycotoxin method. A result is "at or above the cut" if it is ≥ 10 ppb.

### Label groups (registered; each label in exactly one)

| group | labels | n |
|---|---|---|
| **SG** small-grain cereals | `Grain - Barley`, `Barley Products`, `Grain - Rye`, `Rye Products`, `Flour - rye`, `Grain - Kamut`, `Kamut Products`, `Spelt`, `Spelt Products` | 353 |
| **PS** pseudo-cereals and arrowroot | `Grain - Buckwheat`, `Buckwheat Products`, `Grain - Quinoa`, `Quinoa Products`, `Amaranth Products`, `Arrowroot Products` | 252 |
| **OG** other grains | `Millet`, `Millet Products`, `Teff Products`, `Grain - Other`, `Flour - Other` | 197 |
| **PU** pulses and soy | the 23 bean, chickpea, lentil, pea and soy labels, including `Tofu`, `Beverage - Soy` and `Infant Formula - Soy` | 189 |
| **MA** | `Meat Alternative` (may contain wheat gluten; reported alone) | 6 |

SG + PS + OG = 802 "grain-type" samples.

## Gate (G)

The gate has two parts. If it fails, nothing below is graded.

- **DG:** the SHA-256 matches, along with 997 rows and samples, one row each, all
  `Deoxynivalenol`, all 44 product-label counts, CANADA 254 and UNKNOWN 407, one unit in the
  table, and every cell a positive number or a literal 0 (both present).
- **MM:** the SHA-256 matches, along with 18,750 rows, 750 DON rows (one per sample), only
  positive or literal-0 DON cells with 306 positives, a smallest positive of 10, and units in
  the table. The two files share exactly the 18 registered labels.

## Consistency check (C1)

- **C1.** 997 samples, with DON detected in 46%. Rounded half up, that means **454–463**
  positives.

## Blind predictions (P1–P7)

**Where DON sits (R15 gives no breakdown):**

- **P1.** In pulses and soy (PU, 189), DON is detected in at most **15%** (≤ 28), and no PU
  result is at or above **100 ppb**. DON comes from Fusarium head blight of cereals, so it
  should reach pulses mostly by cross-contact.
- **P2.** Small-grain cereals (SG) are DON-positive at least **twice** as often as pseudo-cereals
  and arrowroot (PS). In MM's published listing, the SG labels had DON in 65 of 136 samples and
  the PS labels in 5 of 101.
- **P3.** At least **60%** of the 353 SG samples are DON-positive.
- **P4.** The file's highest DON result is in an SG label and is below **2,000 ppb**.

**Against the EU's 2024 maximum levels (a reference comparison only):**

- **P5.** Of the 802 grain-type samples, at most **16** (2%) are at or above **750 ppb**. That is
  the EU level for cereals placed on the market for the final consumer (Regulation (EU)
  2023/915 as amended by 2024/1022, row 1.4.4). At most **40** (5%) are at or above **400 ppb**,
  the EU level for bakery wares, cereal snacks and breakfast cereals (row 1.4.7). The product
  labels do not say which EU row applies to each sample, so these are threshold counts, not
  compliance verdicts. The EU levels did not apply in Canada, or anywhere, in 2015-16.

**Two CFIA methods, three crop years apart (the new part):**

The [ota-grain-2018 result](ota-grain-2018-0.1.0-result.md) found that most of the gap between
CFIA's OTA-only and multi-mycotoxin surveys disappears at a common cut. These predictions ask
the same of DON. The surveys here are three years apart, so crop-year weather is a confounder:
in R18, CFIA's own DON detection at 10 ppb moved from 27% (2015) to 59% (2017).

- **P6.** On the 18 shared labels, at each method's own limit, DG detects DON more often than MM.
  The Mantel-Haenszel odds ratio (DG vs MM, labels as strata) is **≥ 2**, and the
  continuity-corrected CMH two-sided p is **< 0.05**. In addition, at least **25%** of DG's
  positives on those labels are below 10 ppb.
- **P7.** At a common 10 ppb cut on the same 18 labels, the Mantel-Haenszel odds ratio is
  between **0.5 and 2.0**. If P7 holds, the methods agree once read at the same limit, as for
  OTA. If it fails, a crop-year difference or a method difference above 10 ppb remains, and
  this design cannot tell which.

## Also reported (not graded)

- Statistics for every label and group: n, positives, minimum, maximum, average and median of
  positives, and counts below 10 ppb and at or above 10, 400 and 750 ppb.
- The ten highest results, and every positive pulse or soy result.
- Grain groups by `Function` (Domestic, Import, Unknown).
- `Meat Alternative` (6) alone.
- At both cuts: the per-label 2×2 tables, the pooled table, the MH odds ratio and the CMH
  figures.

## Outputs

The job writes three files:

- `don_grains_2015_samples.csv`: one row per sample (sample, product, group, origin, function,
  detected, DON in ng/g).
- `don_grains_2015_crossmethod.csv`: per shared label, n, detected and the count at or above
  10 ppb in DG, and n and detected in MM.
- `don_grains_2015_summary.json`: the gate, every check and prediction with its observed
  values, the census and provenance.

The next run publishes these with a result note and a pinned recompute test that does not
import the grader.

## Prior art

On 2026-10-28, a search for analyses of this open file found none. CFIA's own summary gives two
figures.
