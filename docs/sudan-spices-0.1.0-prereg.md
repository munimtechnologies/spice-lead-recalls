# Pre-registration: which red spices did Canada's Sudan-dye survey sample, and from where? (sudan-spices 0.1.0)

**Author:** MV2, Munim, Inc. (mv2@munimtech.com). Work made with AI agents.
**License:** text CC BY 4.0; code Apache-2.0.
**Written:** 2026-10-17, before any row of the data file was read.

## What was already known when this was written

- CFIA's dataset page for "2019-2020 Non-Permitted Colours in Spices Data" (open.canada.ca
  dataset c2003a7b-9ca8-46cd-ba83-ecafd1c8569c) says the survey tested red spices sold at
  retail (paprika, sumac, chili powder and cayenne are named) for the Sudan dyes I-IV. CFIA's
  report page also lists Sudan Orange G and other non-permitted colours. **None of the 63
  samples** had a detectable amount. That headline is not a prediction here:
  P2 only checks that the parse agrees with it.
- We have not opened the CSV or seen any per-sample origin, product count or column layout.
  CFIA publishes no breakdown by declared origin.
- The same CFIA programme's red palm oil files found Sudan IV in 2 of 104 samples, both declared
  from Nigeria (release v0.4.10, confirmed v0.4.13). In our other frames, the country of Georgia
  supplies most gross-lead spice in New York City's poisoning cases but never appears in a CFIA
  sample file (docs/where-you-look.md).

## Why it matters

The synthesis note's finding is that the sampling frame decides what you find. A clean result
("0 of 63") means little until you know which origins were sampled. This asks one thing: did
Canada's Sudan-dye survey of red spices sample the origins where Sudan dyes in food have turned
up? It is a descriptive frame-coverage study, not a test of whether spices are adulterated.

## Predictions (graded by `sudan_spices.py`, unchanged after this commit)

Gradable only if at least 55 base samples parse and the file reports Sudan dyes (P1).

| | prediction |
|---|---|
| P1 | at least 55 samples parse and the file reports Sudan dyes (parse gate) |
| P2 | no sample carries a Sudan dye (CFIA's headline; a consistency check, not a prediction) |
| P3 | India is the single most common declared origin |
| P4 | under 10% of samples declare a West or Central African origin |
| P5 | no sample declares Georgia (the country) |
| P6 | at least 25% of samples have no declared country of origin |

Reasoning: P3 holds because India is the largest chili exporter, and Indian chili powder was the
source of the 2003 EU Sudan I crisis. P4 and P5 hold because CFIA's spice frames buy from
mainstream retail (see v0.4.11, v0.4.12). P6 holds because CFIA's 2019-21 lead chromate survey
could not assign an origin to 44 of 132 samples (33%).

## Method

`sudan_spices.py` downloads the one CSV, records its sha256, and merges the rows into one record
per base sample number. A trailing "D" duplicate merges into its base. A blank or "not stated"
origin counts as UNKNOWN, and a "<" value reads as zero. A sample is Sudan-positive if any
component whose name starts with "sudan" has an amount above zero. Any other non-zero colour
is reported, not graded. It writes `grades.json`,
`summary.md` and a per-sample table. `test_sudan_spices.py` checks the parser and grader on
synthetic files. If the real file's columns differ from those the parser expects, the job fails
loudly. Any fix will be recorded as a deviation, and none of the predictions will change.

## Limits

63 samples from one year. Origin is what the label declares. No origin is "proved" adulterated
or clean by a survey this small. The result describes the frame, not the spice supply.

Contains information licensed under the Open Government Licence - Canada.
