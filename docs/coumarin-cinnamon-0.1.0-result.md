# coumarin-cinnamon 0.1.0 — result

Graded result for the pre-registration in
[`coumarin-cinnamon-0.1.0-prereg.md`](coumarin-cinnamon-0.1.0-prereg.md). The classes,
predictions and code were fixed before the primary files were read. Nothing has been changed.

- **Sources:** CFIA coumarin surveys on open.canada.ca (Open Government Licence – Canada).
  Primary: 2012-13 (sha256 `6c155d79…`, 93 samples), 2014-15 (`e418443d…`, 739), 2015-16
  (`45208635…`, 747). Replication, reported but not graded: 2011-12 (`10d2a339…`, 193).
  Full hashes are in the grader's `summary.md`. No unparseable numbers; every row is coumarin;
  no unit override was needed.
- **Sealed per-sample table:** [`../data/coumarin_samples.csv`](../data/coumarin_samples.csv)
  (176 pure-cinnamon samples; no vanilla product was found).
  [`../test_coumarin_cinnamon_result.py`](../test_coumarin_cinnamon_result.py) recomputes every
  count below with the Python standard library only.

Classes: **verum-type** (true or Ceylon cinnamon) below 300 ppm; **cassia-type** at 1,000 ppm
or more; **intermediate** in between.

## Pre-registered predictions (4 of 4 gradable met; 5 not gradable)

| | prediction | value | status |
|---|---|---|---|
| P1 | >= 50 primary cinnamon samples, 26-32 in 2015-16 (gate) | 69; 29 in 2015-16 | met |
| P2 | primary maximum 7,621 ppm in 2012-13; 2015-16 maximum 5,040 (consistency) | 7,621.1; 5,040.0 | met |
| P3 | >= 80% of primary cinnamon is cassia-type | 68 of 69 (98.6%) | met |
| P4 | < 10% of primary cinnamon is intermediate | 0 of 69 | met |
| P5 | nothing named Ceylon is cassia-type | no product name makes any claim | not gradable |
| P6 | everything named cassia/Saigon/etc. is cassia-type | no product name makes any claim | not gradable |
| P7 | nothing declaring Indonesia, China or Vietnam is verum-type (needs >= 5) | 3, all cassia-type | not gradable |
| P8 | > half of Sri Lanka-declared cinnamon is verum-type (needs >= 3) | 1 (verum-type) | not gradable |
| P9 | Mexico leads 2014-15 vanilla products with coumarin | no vanilla product in the file | not gradable |

- **P5/P6.** As the pre-registration warned, CFIA records generic names ("Ground cinnamon",
  "Cinnamon"), so the open files cannot answer the label-fraud question by claim.
- **P9 and the 2014-15 file.** The file published as 2014-15 (dataset `ecb615ff…`) holds 739
  samples of products that include teas, spice mixes, sauces and dried mixes. A case-insensitive search of the raw
  file finds no product named cinnamon, vanilla, extract, oil, flavour or essence. The
  pre-registration's description of a 2014-15 report with 200 vanilla extracts therefore does
  not match this file. We have not found where those samples are published.
- **A units question settled.** The 2015-16 HTML report prints ppb. The open file gives µg/g
  (= ppm), as the pre-registration assumed. Its 10 samples marked "Import" match the
  report's 10 imported, but 8 of the 10 carry no country.

## What the files show

| set | n | verum-type | intermediate | cassia-type | max ppm |
|---|---|---|---|---|---|
| primary 2012-13 | 40 | 0 | 0 | 40 | 7,621.1 (Indonesia) |
| primary 2015-16 | 29 | 1 | 0 | 28 | 5,040 (Vietnam) |
| replication 2011-12 | 107 | 4 | 3 | 100 | 7,816.3 (Vietnam) |
| **all three** | **176** | **5 (2.8%)** | **3** | **168 (95.5%)** | |

**Cinnamon sold at Canadian retail is almost all cassia.** 168 of 176 samples sit at cassia
levels (1,268-7,816 ppm), and only 5 look like true cinnamon. Every sample declaring a
cassia-growing country is cassia-type: Indonesia 10, Vietnam 5, China 2 (17 of 17 across all
three files). So P7 holds on the pooled data, though it was not gradable on the primary set
alone.

**Sri Lanka-declared cinnamon is mostly, not always, true cinnamon.** Six samples declared
Sri Lanka:

| file | sample | form | coumarin ppm | class |
|---|---|---|---|---|
| 2011-12 | 2011COU0073 | sticks | 6.2 | verum-type |
| 2011-12 | 2011COU0016 | ground | 16.2 | verum-type |
| 2011-12 | 2011COU0012 | ground | 17.5 | verum-type |
| 2015-16 | C2015COUM00513 | ground | 6.8 | verum-type |
| 2011-12 | 2011COU0084 | ground | 859.7 | intermediate |
| 2011-12 | **2011COU0024** | ground | **4,717.4** | **cassia-type** |

Four of six are verum-type, so P8's direction holds on the pooled data. One ground cinnamon
declaring Sri Lanka carried 4,717 ppm, a cassia level about 50 times the highest true-cinnamon
value in the literature we used (90 ppm). Another, at 860 ppm, looks like a blend. This fits
the EU Joint Research Centre's 2025 finding that up to 9% of "Ceylon"-labelled cinnamon was
wholly or partly cassia. It cannot show fraud: the declared origin may be a packer or
re-exporter, and the product name makes no Ceylon claim. Of the 5 verum-type samples, 4
declared Sri Lanka and 1 declared Canada (2011COU0090, 20.5 ppm, presumably packed in Canada).

## Limits

- Coumarin types a sample; it does not prove species. Only DNA or a full chemical profile does.
- The Sri Lanka findings are mostly from the 2011-12 replication file, whose header and one row
  an earlier run had seen. Read them as exploratory, not as a graded result.
- Targeted retail sampling, not market shares. Most samples (118 of 176) declare no country.
- CFIA and Health Canada found no health concern in these surveys, and nothing here says
  otherwise. No brand appears in CFIA's open files or here.

---

Made by MV2 of Munim, Inc. with AI agents. Code Apache-2.0; text and derived data
CC BY 4.0. Contains information licensed under the Open Government Licence – Canada.
