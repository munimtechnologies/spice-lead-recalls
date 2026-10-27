# multimyco-2018 detail 0.1.0: how CFIA built Table 3's group rows, and the aflatoxin result the open file lacks

DETAIL-MARKER: multimyco-2018-detail-0.1.0

By MV2 of Munim, Inc. Prepared with AI agents working in his name. Text CC BY 4.0; code Apache-2.0.

**Exploratory, not pre-registered.** This note follows the graded
[multimyco-2018 0.1.0 result](multimyco-2018-0.1.0-result.md) (tag `v0.4.65`). That result left
three of Table 3's toxin-group counts unexplained (fumonisins 106 vs 105, zearalenone 38 vs 34,
aflatoxins 10 vs 11), as well as the DON average (181 vs 282). A sealed follow-up job
(`multimyco-2018-result-v1`, 2026-10-27 18:00 UTC) did two things. First, it re-ran the pinned
result test on the published files from GitHub, and 10 of 10 passed. Second, it listed every
positive cell of the SHA-256-pinned file: 722 cells, now in `data/multimyco_2018_positives.csv`.
Everything below was worked out from that listing after the results were seen. It is a
reading of the data, not a blind test.

This is a reference comparison, not a compliance finding. It is not about any brand, and it is
not dietary or medical advice. Health Canada judged the levels found in the survey "not expected
to pose a concern to human health".

## 1. Table 3's group rows sum each group's analytes per sample

Table 3 reports six toxin groups that cover more than one analyte. The question is how CFIA
turned several analyte rows into one figure per sample. Three groups answer it exactly: CFIA
**summed the group's analytes within each sample**.

| group (printed n / max / avg) | file: samples | per-sample maximum | average of per-sample sums |
|---|---|---|---|
| fumonisins B1+B2+B3 (105 / 3,503 / 280) | 106 | **3,503** = 2,370 + 780 + 353 (one corn flour) | 277.2 over 106; 279.8 over 105 |
| ergot alkaloids (46 / 664 / 79) | 46 | **664** = 507 + 70 + 87 (one rye product) | **79.1** |
| HT-2 + T-2 (8 / 98 / 37) | 8 | **98** = 54 + 44 (one millet product) | **37.0** |

No single cell in the file is 3,503, 664 or 98. Each of those printed maxima is the sum of all
three or both analytes in one sample. The ergot and HT-2/T-2 rows reproduce exactly, in count,
maximum and average.

The fumonisin average fits either way. Read "280" at two significant figures and the 106-sample
mean (277.2) matches. Read it at three, the way Table 3 prints its other three-digit figures,
and only the file's total over **105** samples matches (279.8). A 105-sample row with the file's
total would mean the report counted one fewer fumonisin-positive sample while keeping nearly all
of the fumonisin mass. That fits the report leaving out one sample with a very small fumonisin
result. We cannot tell which sample.

## 2. The aflatoxin row needs a result the file does not hold

Under the same per-sample-sum rule, the file's aflatoxin group has **10** samples. Their
per-sample sums total **18.4 ppb**, with a maximum of **10.0 ppb** (B1 9.3 + B2 0.7, in a corn
flour) and an average of 1.84 ppb. Table 3 prints **11**, **30** and **4.4**.

One missing sample explains all three printed figures. Add one aflatoxin result of x ppb to the
file's ten. The printed average of 4.4 needs (18.4 + x) / 11 in [4.35, 4.45), so x is between
29.45 and 30.55. The printed maximum of 30 needs x between 29.5 and 30.5. **A single result of
29.5–30.5 ppb, absent from the open file, reproduces the count, the maximum and the average.**
No other reading of the file comes close:

- Counting cells instead of samples gives 11 positives (B1 in 7 samples, B2 in 1, G1 in 3). But
  the largest cell is 9.3, and 18.4 / 11 = 1.67, not 4.4.
- No cell or per-sample sum in the file is above 10.0 ppb.

The same thing happened in the [Alternaria result](alternaria-0.1.0-result.md). There, CFIA's
printed tomato maxima (880 and about 345 ppb) were not in its open file either. Here, a printed
aflatoxin maximum about three times the file's largest value is missing. The file cannot say
which product the missing result came from.

## 3. What stays unexplained

- **Zearalenone (printed 34 / 450 / 44).** The file has zearalenone in 38 samples (sum 1,632 ppb,
  maximum 450, mean 42.9). One more sample (a fresh pasta) has α-zearalenol (11 ppb) and no
  zearalenone. The maximum matches. A 34-sample row averaging 44 needs a total of 1,479–1,513
  ppb, so four of the 38 samples carrying 119–153 ppb between them would have to be left out. No
  reporting threshold produces 34: counting values at or above 8, 9 or 10 ppb gives 37, 36 or
  32, and no other cut lands on 34.
- **DON (printed 306 / 2,570 / 282).** Count and maximum match. The file's average is 181.3, and
  nothing in the listing explains 282.
- **387 vs 386/388** samples with a mycotoxin: also unexplained. If the report did hold an
  aflatoxin sample the file lacks, its total would rise, not fall.

## Limits

- This is exploratory and was found after seeing the data. The per-sample-sum rule is
  inferred from three exact matches, not stated anywhere in the report.
- "Missing from the file" means missing from the open CSV as published (SHA-256 `ba508494…3835`).
  The value may have been corrected, withdrawn or mistyped. Only CFIA can say which.
- Canada sets no aflatoxin maximum level for these grain products, and this note makes no
  compliance claim about the missing result.

## Reproduce it

- `data/multimyco_2018_positives.csv`: every positive cell (sample, product, English and French
  component label, ppb). It was written by the sealed job from the pinned file, using the same
  parse rule as the grader.
- `test_multimyco_2018_detail.py`: a pinned test. From the listing it rebuilds every figure
  above: the per-sample group sums, maxima and averages, the 29.5–30.5 ppb interval, and the
  zearalenone thresholds. It also checks that the listing's samples equal the group flags in
  the committed `data/multimyco_2018_samples.csv`. It does not import any grader.
