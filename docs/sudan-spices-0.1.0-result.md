# sudan-spices 0.1.0 — result

Graded result for the pre-registration in
[`sudan-spices-0.1.0-prereg.md`](sudan-spices-0.1.0-prereg.md). The grading rule
was fixed before the data file was read; this note reports the outcome without
changing any prediction.

- **Source:** CFIA, "2019-2020 Non-Permitted Colours in Spices Data",
  open.canada.ca dataset `c2003a7b-9ca8-46cd-ba83-ecafd1c8569c`
  (Open Government Licence – Canada).
- **File:** sha256 `80f9dec39cc574a38aee7f963e3c76096ce4d68feaae3d145a5148d163420f54`,
  1,134 data rows merged into 63 samples, each tested for the same 18 colour
  components (Sudan I–IV, Para Red, Rhodamine B, Metanil Yellow, and others).
- **Sealed per-sample table:** [`../data/sudan_spices_samples.csv`](../data/sudan_spices_samples.csv)
  (63 rows). [`../test_sudan_spices.py`](../test_sudan_spices.py) recomputes every
  headline count below from that file with the Python standard library only.

## Pre-registered predictions (5 of 6 met)

| | prediction | value | status |
|---|---|---|---|
| P1 | at least 55 samples parse and the file reports Sudan dyes | 63 | met |
| P2 | no sample carries a Sudan dye (CFIA's headline; a consistency check) | 0 | met |
| P3 | India is the single most common declared origin | LEBANON | not met |
| P4 | under 10% of samples declare a West or Central African origin | 0 of 63 | met |
| P5 | no sample declares Georgia (the country) | 0 | met |
| P6 | at least 25% of samples have no declared country of origin | 54 of 63 | met |

P3 was the only miss: India had just 1 declared sample. Among the 9 samples that
declared any origin at all, Lebanon led with 3 (all sumac). But the dominant
"origin" was no origin: 54 of 63 samples (86%) carried no declared country.

## Declared origin (all 63 samples)

| origin | n |
|---|---|
| UNKNOWN | 54 |
| LEBANON | 3 |
| CANADA | 2 |
| TURKEY | 2 |
| INDIA | 1 |
| IRAN | 1 |

## By product (descriptive)

| product | n | origins |
|---|---|---|
| Cayenne Pepper | 18 | UNKNOWN 18 |
| Chili Powder | 16 | UNKNOWN 14, CANADA 1, INDIA 1 |
| Paprika | 16 | UNKNOWN 16 |
| Sumac | 13 | UNKNOWN 6, LEBANON 3, TURKEY 2, CANADA 1, IRAN 1 |

Samples with any non-zero colour amount: none.

## What this adds to the "where you look" picture

CFIA's own report gives the clean headline — none of the 63 red spices carried a
Sudan dye — but sets it against nothing else. Placed next to the frames already in
[`where-you-look.md`](where-you-look.md), the finding is about **frame coverage**,
not safety. The one place Sudan dyes have actually turned up in this project's
graded frames is the red-palm-oil survey: Sudan IV in 2 of 104 samples, **both
declared Nigeria** — West Africa. This Canadian red-spice frame declared **zero**
West or Central African origins, and 86% of its samples declared no origin at
all. So a clean result here does not contradict the palm-oil hit; the two frames
barely overlap in the origins they sample. A survey that records origin for only
9 of 63 samples cannot tell you whether the risk origins were present.

## Limits

- Only 63 samples from one survey year; a clean result is not proof of a clean
  supply, and a declared origin is a label, not a verified provenance.
- "UNKNOWN" means the open file carried no origin for that sample; it does not
  mean the origin was unknown to CFIA.
- Nothing here is new measurement. It is a recomputation and cross-frame reading
  of published figures.

---

Made by MV2 of Munim, Inc. with AI agents. Code Apache-2.0; text and derived data
CC BY 4.0. Contains information licensed under the Open Government Licence – Canada.
