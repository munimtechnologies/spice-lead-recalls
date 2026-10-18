# food-colours-2018 0.1.0 — result

Graded result for the pre-registration in
[`food-colours-2018-0.1.0-prereg.md`](food-colours-2018-0.1.0-prereg.md). The grading rule
was fixed before the data file was read; this note reports the outcome without
changing any prediction.

- **Source:** CFIA, "Food Colours in Essences/Flavourings, Oils, Sweets and Processed
  Vegetables - April 1, 2018 to March 31, 2019", open.canada.ca dataset
  `1b0c4141-7a22-4c93-8679-63eb49f7be24` (Open Government Licence – Canada).
- **File:** sha256 `327fd0b6484ce00f9550742c316f603f9b870f78a5e674c79b0cec59e1d24d9d`,
  18,354 data rows merged into 399 samples, each tested for the same 43 colours.
  No unparseable numbers and no origin conflicts.
- **Sealed per-sample table:** [`../data/food_colours_2018_samples.csv`](../data/food_colours_2018_samples.csv)
  (399 rows). [`../test_food_colours_2018_result.py`](../test_food_colours_2018_result.py)
  recomputes every headline count below from that file with the Python standard library only.

## The answer the report left out

CFIA's report says one sample carried the non-permitted dye Rhodamine B (10.8 ppm)
but not what it was or where it came from. The open file says:

| sample | product | declared origin | where / when sampled | colours found |
|---|---|---|---|---|
| C2018FCOL00263 | Pickled Vegetable - Misc | LEBANON (import) | Quebec, 27 Nov 2018 | Rhodamine B 10.8 ppm; Erythrosin B 13.3 ppm |

The other two Lebanese pickled vegetables in the survey (C2018FCOL00309, C2018FCOL00392)
carried no colour at all.

**Context (not part of the grade).** That same autumn Lebanon itself was dealing with
Rhodamine B in pickled turnips. The EU's rapid alert system had flagged "unauthorised
colour Rhodamine B in pickled turnips from Lebanon" (RASFF 2018.2883, as cited by Tlais
et al. 2020, *Turkish J. Agriculture – Food Science and Technology*). Lebanon's Consumer
Protection Directorate warned about it in November 2018, and in December 2018 the
Ministry of Public Health reported Rhodamine B in 25% of factory turnip samples and
sent seven factories to the prosecutor. CFIA's file does not say "turnip": it says
"Pickled Vegetable - Misc", and pink pickled turnip is only the most likely candidate.
The Canadian sample is an independent retail detection that fits that episode. CFIA's
report gave no link to it, and a brief search found nothing published that makes the link.

## Pre-registered predictions (3 of 5 gradable met)

| | prediction | value | status |
|---|---|---|---|
| P1 | at least 380 samples parse and the file reports Rhodamine B | 399 | met |
| P2 | exactly one sample carries Rhodamine B above zero (CFIA's Table 3; a consistency check) | 1 | met |
| P3 | the Rhodamine B sample is a sweet | processed vegetables | **not met** |
| P4 | the Rhodamine B sample declares an Asian origin (South, Southeast, East or West Asia) | LEBANON (West Asia) | met |
| P5 | every sample with Orange II above zero is a sweet | a soft candy and a pudding | not gradable |
| P6 | under 5% of oil samples declare a West or Central African origin | 5 of 74 (6.8%) | **not met** |

- **P3 missed.** We expected confectionery, which accounts for most published Rhodamine B
  food cases in South and Southeast Asia. The real case was a Levantine pickle.
- **P4 met, but only just.** Lebanon counts as West Asia under the wording we wrote down. The
  reasoning behind P4 (India, Pakistan, Bangladesh, Indonesia, China) was wrong.
- **P5 not gradable.** One Orange II sample was a soft candy (sweets). The other was a
  pudding, which the pre-registered keyword rules left "unclassified", and a prediction
  about an unclassified sample is not gradable under the pre-registered rule.
- **P6 missed, and the reasoning behind it was wrong.** We guessed this survey's "oils" would
  be olive, sesame and flavoured oils, with red palm oil rare. In fact 23 of the 74 oil
  samples were palm oil: Ecuador 13, Togo 3, Ghana 2, Colombia 2, Malaysia 2, unknown 1.
  **All 5 West African palm oils (Togo 3, Ghana 2) were clean across all 43 colours,
  including all the Sudan dyes.** So were all 23 palm oils.

## By category (pre-registered keyword rules)

| category | n | with any colour | top declared origins |
|---|---|---|---|
| essences/flavourings | 50 | 9 | UNKNOWN 26, UNITED STATES 12, CANADA 10 |
| oils | 74 | 0 | UNKNOWN 18, ECUADOR 13, CANADA 9, TUNISIA 8, ITALY 7 |
| processed vegetables | 50 | 28 | UNITED STATES 14, INDIA 9, CANADA 8, GERMANY 6 |
| sweets | 87 | 64 | UNKNOWN 44, GERMANY 10, UNITED STATES 10, CANADA 9 |
| unclassified | 138 | 80 | UNKNOWN 67, UNITED STATES 43, CANADA 20, MALAYSIA 5 |

Samples with any colour: 181 of 399, the same as CFIA's report (an independent check of
the merge). The keyword rules put only 87 samples in "sweets" against CFIA's 200 and 74
in "oils" against 99. The rest sit in "unclassified" (baked goods, puddings, dressings and
similar). That is a weakness of the rules, not of the file.

Non-permitted colours: Rhodamine B (above), and Orange II in C2018FCOL00293 (soft candy,
no origin, 0.221 ppm) and C2018FCOL00376 (pudding, United States, 0.042 ppm). CFIA marks
Orange II as a possible subsidiary colour of permitted Sunset Yellow FCF, and both samples
also carried Sunset Yellow. Permitted colours above 300 ppm (descriptive): Allura Red 539
and 475 ppm in two hard candies and 312 ppm in a baked good, none with a declared origin.

## What this adds to the "where you look" picture

- The project's graded frames now hold two non-permitted dye hits outside lead: Sudan IV
  in red palm oil declared **Nigeria** (2 of 104; v0.4.10 line) and Rhodamine B in a pickled
  vegetable declared **Lebanon** (1 of 399, here). Each fits a product-origin pairing
  that had earlier public alerts abroad, and neither came from a survey aimed at that origin.
- Lebanon also led the declared origins in CFIA's 2019-20 red-spice survey (3 sumac
  samples, all clean; v0.4.20). A frame that samples Levantine imports does reach them.
- This survey did sample West African palm oil (5 samples) and found it clean, so the
  Nigeria finding is not contradicted. It is still unreplicated.

## Limits

- One sample. Nothing here estimates how common Rhodamine B is in any product or origin.
- A declared origin is a label, not verified provenance. "UNKNOWN" means the open file
  carries no country for that sample.
- The link to the Lebanese 2018 episode is context, not proof: same product family, same
  declared country, same months. Nothing more is claimed.
- CFIA and Health Canada judged none of these results a health concern, and nothing here
  says otherwise. Nothing here is new measurement; it is a re-reading of published data.

---

Made by MV2 of Munim, Inc. with AI agents. Code Apache-2.0; text and derived data
CC BY 4.0. Contains information licensed under the Open Government Licence – Canada.
