# multimyco-2018 0.1.0: CFIA's open 2018-19 multi-mycotoxin file against its own report — result

RESULT-MARKER: multimyco-2018-0.1.0-result

By MV2 of Munim, Inc. Prepared with AI agents working in his name. Text CC BY 4.0; code Apache-2.0.

This grades the pre-registration [multimyco-2018-0.1.0-prereg.md](multimyco-2018-0.1.0-prereg.md).
It was public first, at tag `v0.4.61`, after the
[report-check note](multimyco-2018-report-check-0.1.0.md) (`v0.4.60`). The sealed job
`multimyco-2018-v1` ran on 2026-10-27 at 11:47 UTC (python:3.12, 1 GB, no host paths). It waited
for the note to be public, checked that its bundled `multimyco_2018.py` and
`test_multimyco_2018.py` were byte-identical to the published copies, ran the 16 offline tests,
and only then read the SHA-256-pinned file. **The gate passed. 4 of 10 graded items held (G, C1,
P5, P6); 6 missed (P1, P2, P3, P4, P7, P8).** Most of the misses are the finding: the open file
does not reproduce several figures CFIA printed for it.

This is a reference comparison, not a compliance finding. Canada sets no mycotoxin maximum level
for these foods. It is not about any brand, and it is not dietary or medical advice. Health
Canada judged the levels found "not expected to pose a concern to human health".

## Headlines

1. **The file gives a third answer to "388 or 386".** The report's text says 388 samples had a
   mycotoxin, and Table 2's total says 386. The file says **387**.
2. **The printed DON average does not come from the file.** The file reproduces Table 3's DON
   count (306 of 750) and maximum (2,570 ppb) exactly. But the average of its 306 positives is
   **181 ppb**, against the printed 282. A 282 average would need about 31,000 ppb more DON
   across those samples than the file holds.
3. **Three of Table 3's toxin-group counts are off.** The file has fumonisins in 106 samples
   (printed 105), zearalenone in 38 (printed 34 for the zearalenone/zearalenol group) and
   aflatoxins in 10 (printed 11). Ergot alkaloids, OTA, cyclopiazonic acid, sterigmatocystin,
   HT-2/T-2 and nivalenol match exactly, and so do every printed maximum and average for the
   single-toxin groups (C1).
4. **The zearalenols are detected.** The report lists "alpha-/beta-zeranol" among the toxins never
   detected. Its "17 different mycotoxins" holds only if those are the file's α-/β-zearalenol
   rows (P3). They are not undetected: the file's `?-Zearalenol(ppb)` label has at least one
   detection, so the file shows **18** of its 24 labels detected (18 or 19 of 25 analytes,
   depending on whether one or both zearalenols are detected). The six never-detected labels are 3- and 15-acetyl-DON,
   aflatoxin G2, diacetoxyscirpenol, fusarenon-X and neosolaniol.
5. **DON and fumonisins co-occur *within* products. That is not composition.** For OTA × DON,
   [cooc-strata](cooc-strata-0.1.0-result.md) found that pooled co-occurrence in CFIA's mixed
   retail file is mostly a commodity effect. P7 predicted the same here and missed. Pooled, the
   DON × fumonisin odds ratio is 2.42. Within the 30 product labels, the Mantel-Haenszel odds
   ratio is **2.48** (CMH χ² 10.0, p 0.0016), no closer to 1.

## Data

CFIA, "Multi-Mycotoxins in Corn Products, Crackers, Other Grain Products, Pasta and Gluten-Free
Products – April 1, 2018 to March 31, 2019". Open Government Portal resource
`09a3c285-8552-4a38-b4be-cdf6d5fc3fd2`, SHA-256 `ba508494…3835` (3,484,399 bytes, cp1252), Open
Government Licence – Canada. It has 18,750 rows: 750 samples × 25 analyte rows. Every AMOUNT
cell passed the registered format rule. There are 722 positive cells and 18,028 literal zeros,
with no comma, `<` or text cell. All values are in ng/g (= ppb).

## Gate (passed)

The SHA-256 matched, as did 18,750 rows / 750 samples / 25 rows each, the 24 component labels and
30 product labels by count, the one plan code, the one unit, the origin split (CANADA 155,
UNKNOWN 291, 304 foreign over 30 distinct origins) and a clean AMOUNT format. All 13 checks held.

## Graded items: 4 of 10 held

| ID | Prediction | Observed | Met |
|---|---|---|---|
| G | gate (above) | all 13 checks | ✅ |
| P1 | exactly 386 of 750 samples carry ≥ 1 detected mycotoxin (Table 2), not 388 (text) | **387** | ❌ |
| P2 | DON in 306 samples, max 2,570, average of positives 282 ppb | 306, 2,570, average **181.3** | ❌ |
| P3 | exactly 17 of 24 labels detected; the zearalenols are never detected | **18**; `?-Zearalenol(ppb)` detected | ❌ |
| P4 | the nine non-DON groups reproduce Table 3's counts exactly | 6 of 9 exact; fumonisins **106** (105), zearalenone **38** (34), aflatoxins **10** (11) | ❌ |
| C1 | OTA, CPA, sterigmatocystin and nivalenol max and average match Table 3 | OTA 33.8 / 4.165; CPA 47.2 / 11.13; STE 11.8 / 2.67; NIV 86 / 21.86 (printed 34/4.2, 47/11, 12/2.7, 86/22) | ✅ |
| P5 | exactly 7 of 750 samples carry OTA above the proposed 3 ppb level (99.1% compliance) | **7** | ✅ |
| P6 | OTA detected in fewer than 25% of the 101 crackers (CFIA's OTA-only survey that year: 75%) | **2 of 101 (2.0%)** | ✅ |
| P7 | within product labels, the DON × fumonisin odds ratio is pulled toward 1 | pooled 2.42, MH **2.48** (p 0.0016) | ❌ |
| P8 | the most toxin groups in one sample is 9, in a corn product | **6**, in a corn flour | ❌ |

### P1–P4: what the file holds that the report does not

- **387 samples with a mycotoxin.** That is 750 − 363: 363 samples have no detection in any of
  the ten toxin groups, and every sample with a zearalenol detection also carries another group.
  Neither printed figure (386 or 388) is in the file. The report's per-category counts cannot be
  checked one by one, because its five categories do not follow the file's 30 product labels
  (see the report-check note).
- **The DON average.** The 306 DON positives sum to 55,480 ppb (mean 181.3; the all-sample mean is
  74.0). A 282 average needs 86,139–86,445 ppb. The count and maximum match exactly, so this is
  not a different sample set. We cannot tell from the file whether 282 is a transcription error
  (for example, of 182 or 181) or comes from another calculation.
- **Group counts.** The file has one more fumonisin-positive sample, four more zearalenone-positive
  samples and one fewer aflatoxin-positive sample than Table 3. The zearalenone gap cannot come
  from the zearalenols, because adding them could only raise the file's count. A follow-up job
  publishes every positive cell by label, so the exact samples behind these gaps can be checked.
- **The zearalenols.** The report's "zeranols" are either the file's zearalenols, which *are*
  detected at least once, or a pair of analytes the file does not hold. In both readings the
  report's "17 different mycotoxins" does not describe this file.

### P5, P6: the two OTA figures CFIA left uncounted

- **P5.** Exactly 7 of 750 samples carry OTA above the proposed 3 ppb level, which is 99.07%
  compliance and matches the printed 99.1% on an all-sample base. The report gives no count. The
  OTA maximum is 33.8 ppb.
- **P6.** OTA is detected in 2 of the 101 crackers. CFIA's separate OTA-only survey of the same
  year found it in 30 of 40 (75%, max 2.2 ppb). The gap points to a much higher effective
  detection limit in the multi-toxin method, not to cleaner crackers. Survey-to-survey
  comparisons of detection rates across CFIA methods are not like for like.

### P7: DON × fumonisin is not a commodity artefact

| | DON & fumonisin | DON only | fumonisin only | neither | odds ratio |
|---|---|---|---|---|---|
| All 750 samples | 63 | 243 | 43 | 401 | 2.42 |
| 5 corn labels (150) | 51 | 10 | 36 | 53 | 7.51 |
| the other 25 labels (600) | 12 | 233 | 7 | 348 | 2.56 |
| within the 30 labels (Mantel-Haenszel) | | | | | **2.48** (CMH p 0.0016) |

Fumonisins sit mostly in corn: 87 of the 106 fumonisin-positive samples carry a corn label. The
prediction was that stratifying by label would absorb the association, as it did for OTA × DON.
It does not. Inside the corn labels, a DON-positive sample is far more likely to be
fumonisin-positive than a DON-negative one. Corn starch is the exception: none of its 25 samples
carries either toxin. DON and fumonisins are both field-mould toxins, while OTA is mostly a
storage-mould toxin. That may be why the OTA × DON case behaved differently. It is a hypothesis
from two results, not a rule.

### P8

At most 6 of the 10 toxin groups occur in any one sample: a corn flour with DON, fumonisins,
zearalenone, cyclopiazonic acid, aflatoxins and nivalenol (sample C2018MUMY00663). The predicted
9 was too high.

## Limits

- Detection is binary at the method's own limits, which the report does not give. Low positives
  near the limit drive both the group counts and the co-occurrence table.
- The co-occurrence result is for one survey year and one method. Its strata are CFIA's product
  labels, some of which mix products (`Gluten-free Products`, `Corn Products`).
- This note does not say *why* the file and report differ: corrected data, a different extract
  or report errors are all possible. Only CFIA can say.

Prior art: a search on 2026-10-26 found no published analysis of this open file. We did not
finish a literature search on within-commodity DON × fumonisin co-occurrence for this note. So
the only novelty we claim for P7 is that it is the first such test on this file.

## Reproduce it

- `data/multimyco_2018_samples.csv`: one row per sample (sample, product, origin, number of toxin
  groups, and a 0/1 flag for each of the 10 groups), the sealed job's output.
- `data/multimyco_2018_summary.json`: the sealed grader record (gate, census, every prediction
  with its observed values, the analyte statistics, provenance).
- `test_multimyco_2018_result.py`: a pinned test. It recounts every group, the 387, the crackers,
  the corn and non-corn tables and the Mantel-Haenszel and CMH figures from the per-sample table
  with its own code, which does not import the grader. It also checks the DON arithmetic and the
  graded tally against the sealed record.

A sealed follow-up job (`multimyco-2018-result-v1`) fetches these published files from GitHub,
re-runs the pinned test on them, and lists every positive cell by label from the pinned raw file.
That listing is exploratory, for the P1/P4 gaps, and is not graded. The grading code
`multimyco_2018.py` and the pre-registration are at tag `v0.4.61`.
