# myco-don 0.1.0: deoxynivalenol (and ochratoxin A) in CFIA's open infant-cereal and selected-foods files — result

RESULT-MARKER: myco-don-0.1.0-result

By MV2 of Munim, Inc. Prepared with AI agents working in his name. Text CC BY 4.0; code Apache-2.0.

This grades the blind pre-registration [myco-don-0.1.0-prereg.md](myco-don-0.1.0-prereg.md),
published first at tag `v0.4.53`. The sealed job `myco-don-v1` (2026-10-25, python:3.12, no host
paths) waited for that note to be public, replaced its bundled modules with the published copies,
ran the offline tests, and only then read the three SHA-256-pinned CFIA files. **The gate passed and
12 of the 13 graded items held (11 of 12 blind predictions).** The single miss, P11, is the point of
the study and is reported in full below.

Not a finding about any product, brand or health risk. Canada sets no DON maximum level for finished
foods; the EU and Codex levels are reference yardsticks only.

## Data (three CFIA open files, released 2026-10-06, Open Government Licence – Canada)

| Short name | Resource | SHA-256 | Rows | Samples |
|---|---|---|---|---|
| don-infant-2018 | 7e3c4cf6-69fa-4931-9f31-cd78225acf01 | `7427bd2905b8730ffc2403d379fd40549a42297fec0c3fc040d9a65446197583` | 286 | 286 |
| don-2011 | cef65485-68e2-4580-8bd4-aa47c5a84c96 | `4d4c90fb4b157bbb4c5a3f9aaf1c47b33b7b00a4d66437e2ea7ee6f5cb8a74ad` | 1395 | 1395 |
| ota-don-2010 | b87d36bc-a568-4dc5-8391-9d8afdbf6048 | `fdd0aec2e70e8cbf0805b8cac5a98c98b48bc86a6ccafd1ce6f1f9d05395102a` | 1886 | 943 |

The grader downloaded the SHA-pinned copies from the sealed data volume (bytes 63,721 / 227,533 /
301,694; encoding utf-8-sig). The ota-don-2010 file carries two rows per sample, one Deoxynivalenol
and one Ochratoxin A.

## Gate (passed)

For all three files, the SHA-256, row count, distinct-sample count, rows-per-sample, the unit `ng/g`
on every row, the component split, that every result cell parses, and the non-detect-as-literal-`0`
format all matched the names-only census. Per the registered rule a blank cell, a `<`-prefixed value,
a not-detected token or the number `0` is a non-detect; the census showed, and the gate confirmed,
that non-detects in all three files are a literal `0` — so the detection-limit trap that caught the
2011-12 coumarin file does not arise here.

Two file-vs-report count gaps the census flagged are confirmed by the gate:

- **don-infant-2018 carries 286 samples; the 2018-19 report states 288 throughout** (Table 1 grand
  total, the results text "a total of 288 samples", Table 4 "Canada (CFIA) … 288"). A 2-sample gap.
- **don-2011 carries 1395 samples; the 2011-12 summary category breakdown sums to 1,391.** A
  4-sample gap. (ota-don-2010's 943 matches its summary — no gap.)

## Graded predictions

| ID | Prediction (abbreviated) | Observed | Met |
|---|---|---|---|
| P1 | infant file follows Table 3 (100–135 detected), exactly 13 at or above 20 ppb | 119 detected; 13 ≥ 20 ppb | ✅ |
| P2 | infant maximum 250 ppb, smallest detected below 1 ppb | max 250; min 0.60 | ✅ |
| P3 | smallest value ≥ 20 ppb is 22, so the text's "44.1 ppb" minimum is wrong | 22.3 ppb | ✅ |
| P4 | 1–4 infant cereals exceed the EU 2024/1022 baby-food DON level of 150 | 2 | ✅ |
| P5 | DON detected in exactly 555 of 943 (2010-11) | 555 | ✅ |
| P6 | 2010-11 DON minimum rounds to 1, maximum 2060 ng/g | min 1.0; max 2060 | ✅ |
| P7 | no 2010-11 wine or dried-fruit sample has detected DON | 0 of 139 wine; 0 of 97 dried fruit | ✅ |
| P8 | 2010-11 infant cereals (n 93): DON detected 73–77, max 128, min ~1.1 | n 93; 76 detected; max 128; min 1.1 | ✅ |
| P9 | OTA detected in exactly 315 of 943, min 0.040, max 6.773 ppb | 315; min 0.040; max 6.773 | ✅ |
| P10 | 8 grain-based samples exceed Health Canada's proposed OTA levels, 5 infant cereals | 8; 5 infant | ✅ |
| **P11** | **within-sample OTA × DON detection odds ratio in [0.5, 2.0]** | **OR 8.54, p 1.4×10⁻³⁹** | ❌ |
| P12 | 2011-12: ND share ~37%, min ~1.0, max 2460, no dried fruit detected | 37%; min 1.0; max 2460; 0 of 105 | ✅ |

### Settling the 2018-19 report's internal contradiction (P1, P3)

For the same infant-cereal samples the 2018-19 report gives two incompatible counts: Table 2 says 13
positives (all at or above the 20 ppb reporting limit the methods impose), Table 3 says 123 with
minima of 0.60–1.3 ppb. **The open file settles it: 119 of 286 samples carry a detected DON value,
and exactly 13 of those reach 20 ppb.** So Table 2 counts results at or above the imposed 20 ppb
reporting limit, and Table 3 counts down to the 0.2 ppb LOD — both describe the same data under
different reporting limits (the file's 119 detections sit just under Table 3's 123, consistent with
the file holding 286 samples where the report counted 288).

**A confirmed report error (P3).** The 2018-19 results text states "DON levels ranged from 44.1 ppb
to 250 ppb" for the 13 samples at or above the reporting limit. In the open file the smallest value
at or above 20 ppb is **22.3 ppb** — matching Table 2's printed wheat minimum of 22 and contradicting
the text's 44.1. (Table 4 separately prints the minimum as 25.) The text's "44.1 ppb" lower bound
appears nowhere in the file or the tables. A correction note is drafted for CFIA and held for review;
it is not sent from this run.

### The novel result: OTA and DON co-occur within a sample far more than chance (P11, the miss)

P11 registered the expectation that within one sample ochratoxin A detection and deoxynivalenol
detection show **no strong association** (odds ratio in [0.5, 2.0]), because OTA is produced mainly
by storage moulds (*Aspergillus*, *Penicillium*) and DON by field *Fusarium* — different fungi at
different stages. The 943-sample 2×2 table refutes that prediction:

| | DON detected | DON not detected | total |
|---|---|---|---|
| **OTA detected** | 275 | 40 | 315 |
| **OTA not detected** | 280 | 348 | 628 |
| **total** | 555 | 388 | 943 |

Odds ratio **8.54** (95% not computed; Fisher exact two-sided **p = 1.4 × 10⁻³⁹**). A sample with
detected OTA is far more likely to also carry detected DON than one without. As far as a prior-art
search found (run 188; the closest published work is Dutch 2007–16 and Korean 2009–16 *feed* studies),
**no per-sample OTA × DON co-occurrence table has been published from CFIA's open retail data; this
appears to be the first.**

**Honest limits.** This is an association between *detections* (binary, at each file's reporting
limit), not between concentrations, and it is measured across a heterogeneous food basket. Much of
the signal is commodity composition rather than joint mould contamination of one lot: grain-based
foods tend to carry both toxins, while wine and dried fruit carry neither (0 DON detections in 139
wines and 97 dried-fruit samples; OTA is the toxin that turns up in wine). A within-commodity
analysis would be needed to separate "these foods carry both" from "the same lot was co-infected";
the open file's single `Product` label per sample supports the first but not a clean test of the
second. The table and its margins are nonetheless a reproducible, first-of-its-kind open artifact,
and the registered independence prediction is reported as failed.

## Not graded (stated so the study is not over-read)

Grain-level checks for the infant-cereal files (Table 1 grain sizes, the multigrain maximum of
Table 2 vs Table 3, barley "100%" vs 6 of 7) are **not gradable**: all three files label every
infant-cereal sample with the single `Product` value "Infant Food - Cereal" and carry no grain
column, so the per-grain breakdowns cannot be rebuilt from the open files.

## Reproduce it

- `data/myco_don_2010_samples.csv` — the full per-sample ota-don-2010 table (1,886 rows, both
  toxins), from which every 2010-11 figure (P5–P11) and the co-occurrence table are recomputed.
- `data/myco_don_cooccurrence.json` — the committed 2×2 table, odds ratio and Fisher p.
- `data/myco_don_summary.json` — the full sealed grader output (gate, all predictions, provenance).
- `test_myco_don_result.py` — a pinned test that re-derives each sample's detection from its raw
  result cell, recomputes the 2010-11 counts and ranges, rebuilds the OTA × DON 2×2 table, and
  recomputes the odds ratio and the Fisher exact p-value, checking all against this note and the
  committed JSON.

A sealed follow-up job (`myco-don-result-v1`) fetches these published files from GitHub and re-runs
the pinned test against them, so the result is verified to reproduce from a clean checkout. Grading
code `myco_don.py` and the pre-registration are at tag `v0.4.53`.
