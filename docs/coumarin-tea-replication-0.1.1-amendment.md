<!-- AMENDMENT-MARKER: coumarin-tea-replication-0.1.1-amendment -->
# coumarin-tea-replication 0.1.1: amendment after a failed parse gate

By MV2 of Munim, Inc. Made with AI agents working in MV2's name. Code Apache-2.0; this note
CC BY 4.0. Data: CFIA coumarin targeted surveys (Open Government Licence - Canada).

This amends the [0.1.0 pre-registration](coumarin-tea-replication-0.1.0-prereg.md). It is
published **before** any re-grade. It is written **after** the 0.1.0 job printed every observed
value, so the re-grade it sets up is a **verification, not a blind test**.

## What happened

The sealed 0.1.0 job (`coumarin-tea-rep-v1`, 2026-10-24 05:15 UTC) ran as registered. It confirmed
the pre-registration was public, matched both bundled modules to the published copies, passed
its offline tests and verified both files' SHA-256 digests. Gate G0 then failed, so under the
pre-registered rule **P1-P10 were not graded**.

G0 had 14 checks, 7 per survey. 13 passed:

| check | 2014-15 | 2015-16 |
|---|---|---|
| measured rows | 739 (pass) | 747 (pass) |
| tea rows, six-type census | 210, exact (pass) | 297, exact (pass) |
| tea unit census | all ug/g (pass) | all ug/g (pass) |
| tea max | 1,920 (pass) | 2,230 (pass) |
| detected | 178 (pass) | 245 (pass) |
| mean of detected values | **356.2: FAIL** (registered [285, 320] around CFIA's 302) | 441.6 (pass; CFIA 442) |

The 2013-14 reproduction check also passed exactly (115 teas; 0 / 7 / 33 / 45 over the TDI).

## Why the one check failed

CFIA's 2014-15 report (Table 2) prints the tea average as **302 ppm**, under a note that reads
"Only positive results were used to calculate the average (hazard) levels." The pre-registration
took that note at face value. In CFIA's own open file, though:

- the mean of the **178 detected** teas is **356.2** mg/kg;
- the mean of **all 210** teas, with the 32 non-detects counted as 0, is **301.9** mg/kg, which
  rounds to CFIA's 302.

So CFIA's printed 2014-15 tea average is the all-sample mean, not the positives-only mean its
note describes. The 2015-16 tea average (442) does match the positives mean (441.6), as that
report's note says. So does the 2013-14 tea average of 500 that CFIA reprints in the 2014-15
report's Table 3 (positives mean 500.0; all-sample mean 495.7).

The parser was not at fault. Every count, the unit census, the maximum and the detection count
match CFIA exactly, and the 2013-14 result reproduces. The gate did its job: it caught a mismatch
between a published headline and the file, and stopped the grading.

## The amendment

One check changes. Nothing else does.

- **G0, 2014-15 mean check:** compare CFIA's printed 302 with the **mean of all 210 teas**
  (non-detects as 0), bounds unchanged at [285, 320]. The 2015-16 check is unchanged (positives
  mean in [420, 465]).
- **P1-P10:** unchanged, word for word and threshold for threshold. The code is
  `coumarin_tea_replication.py` 0.1.1. Its offline tests pin the 0.1.0 thresholds.
- **Status:** every graded prediction is labelled `"blind": false`. The result note will call the
  outcome a verification, because the 0.1.0 job output already showed every value. That output
  will be published with the result note.

## What the misreading changed in the 0.1.0 reasoning

The 0.1.0 reasoning scaled the 2013-14 distribution by the ratio of positives means, and it used
302 as 2014-15's positives mean (0.60x of 2013-14's 500). The true ratio is 356 / 500 = 0.71x.
With the correct figure, the 2014-15 band predictions (P3, P5, P7) would have been centred
somewhat higher. They are **not** re-centred here, because that would mean tuning the predictions
after seeing the data. The result note reports them as registered.

## A wider question this raises

If one row of CFIA's 2014-15 Table 2 is an all-sample mean, are the others? The 2014-15 grand
total (149) can only be reproduced from CFIA's own row figures if **every** row is an all-sample
mean: sum(n x average) / 739 = 148.9. Under the footnoted positives-only reading, the grand
positives mean would be 186.5. That question is pre-registered separately, before any non-tea
value is read, in [coumarin-cfia-table-audit 0.1.0](coumarin-cfia-table-audit-0.1.0-prereg.md).
The same sealed job grades both.

<!-- AMENDMENT-MARKER: coumarin-tea-replication-0.1.1-amendment -->
