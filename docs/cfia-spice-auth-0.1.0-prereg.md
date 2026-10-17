# Pre-registration: lead chromate, dyes and fillers in Canada's spice surveillance (cfia-spice-auth 0.1.0)

Written on 2026-10-17, before any assessment code or note in the three data files was
read or counted. The grading code `cfia_spice_auth.py` and its offline tests
(`test_cfia_spice_auth.py`, made-up fixtures only) are committed with this note. A
sealed job then downloads the files, freezes them and grades the five predictions below.

By MV2 of Munim, Inc. Prepared with AI agents. Text CC BY 4.0; code Apache-2.0.

## Why this question

The NYC and King County notes in this repository found that gross lead in spices turns
up in spices people buy abroad and bring home, not on store shelves (sampling-frame,
purchase-place). FDA's border list is the second source (ia9942-lead-spice, grading
pending). Canada gives a third view from a different frame: the Canadian Food Inspection
Agency (CFIA) samples single-ingredient spices "at various levels of trade" and checks them
for fillers and for undeclared colouring agents, lead chromate included. It publishes one
row per sample, with declared origin, product, assessment and notes:

- CFIA, *Spices Authenticity Summary Data*, Open Government Portal, dataset
  2d34ba67-f4a3-4c54-95f5-6073b59ad880 (Open Government Licence - Canada): CSV files for
  2020-2021, 2021-2022 and 2022-2023.

We found no published analysis of these files by product and declared origin. CFIA's own
Food Fraud annual reports give totals by spice. The EU's 2019-2021 coordinated plan
reported no trend by origin, but it covers EU samples, not Canada's.

## What was seen before this note (stated so no one has to trust us)

1. The dataset page: title, licence, nine resources (three CSVs, their supplemental files),
   last modified 2026-09-02.
2. The **structure only** of the 2022-2023 CSV, read through a fetch that was told not to
   report outcomes: nine bilingual columns (sample number; sampled from, a province;
   declared origin or dealer location, English and French; product name, English and
   French; sample assessment; notes, English and French), about 290-295 rows,
   assessment codes S, U-I and INV, and one note text quoted as an example: "Investigative
   for colours". No count of any code, and no other note, was seen. The 2020-2021 and
   2021-2022 CSVs were not opened.
3. The 2020-2021 supplemental text (methods only): S = satisfactory, U-I = unsatisfactory;
   a sample is unsatisfactory "if any testing shows the presence of adulterants"; sampling
   is "based on risk factors for non-compliance"; the results "are not representative of
   overall compliance in the Canadian marketplace".
4. Search snippets of CFIA's *Food Fraud Annual Report 2022 to 2023*: 294 spice samples
   (cinnamon, coriander, cumin, paprika, black and white pepper, turmeric), tests for
   fillers, dyes and "lead and chromate" by ICP-MS; 254 satisfactory, 25 unsatisfactory,
   15 investigative; black pepper 2 of 48 unsatisfactory (1 investigative), coriander 5 of
   34 (11), cumin 15 of 53 (2), turmeric 2 of 56 (1). The reason for each failure was not
   in the snippet.
5. Already in this repository's README: CFIA's lead chromate survey of 132 yellow and brown
   spices, 2019-2021, with two ginger samples chromate-positive.
6. Search snippets of the EU 2019-2021 herbs-and-spices plan (non-authorised dyes in 2% of
   samples, one sample with a high level of lead chromate) and of CFIA's 2023-24
   Departmental Results Report (CFIA evaluated AI models to identify lead chromate in
   turmeric).

Item 4 informs prediction P3 (cumin and coriander are classic filler targets and carry most
2022-2023 failures). It is said here so P3 is read as partly informed.

## Definitions (as coded in `cfia_spice_auth.py` 0.1.0)

- **Unit**: one row (sample) with a sample number or product name, pooled over the three
  files. Fiscal year = the file.
- **Assessment**: S; U (any code starting "U", or "insatisfaisant"); INV (starting "INV");
  anything else OTHER.
- **Lead-chromate sample**: the English and French notes, joined, match
  `\blead\b|chromat|chromium|\bpb\b|plomb` (case-insensitive), whatever the assessment.
- **Filler note**: the notes match the filler pattern in the code (filler, starch, wheat,
  gluten, shells, peanut, almond, nuts, foreign or other plant material, husk, sawdust,
  bran, flour, stems, cereal, rice, corn, barley, chickpea, soy, wood, substitution,
  dilution, and their French forms).
- **Spice**: the first pattern in `SPICES` that matches the English product name.
- **Declared origin**: split on `/ , ; & +` and the words and/or/et/ou. A sample has a
  single origin if exactly one name results.
- **South Asia**: India, Pakistan, Bangladesh, Sri Lanka, Nepal.

## Predictions

| | prediction | why we expect it |
|---|---|---|
| P1 | At least one sample's notes name lead chromate, over the three years. | CFIA tests for it and found two ginger samples in 2019-2021. |
| P2 | Lead-chromate samples are at most 3% of all samples. | Two of 132 in 2019-2021; single-ingredient trade samples are the store-shelf frame, where NYC found gross lead rare. |
| P3 | Among unsatisfactory samples, filler notes outnumber lead-chromate notes. | Cumin and coriander, classic filler targets, carry most 2022-2023 failures (item 4, seen). |
| P4 | At least half of lead-chromate samples are turmeric or ginger. | The two 2019-2021 positives were ginger; turmeric is the literature's main target. |
| P5 | At least half of lead-chromate samples with a single declared origin declare a South Asian origin. | Forsyth et al. 2019 and 2024 trace lead chromate in turmeric to South Asian polishing. |

## Grading rules, fixed now

- If fewer than half of the unsatisfactory samples carry any note, the notes cannot say why
  samples failed. P1-P5 are then **not gradable**, and the result reports assessment
  counts only.
- P4 is not gradable if there is no lead-chromate sample; P5 if none has a single origin.
- If one file cannot be downloaded or parsed, the grade uses the others and says so.
- The patterns above are final for this grade. Every flagged note is listed in the job's
  output and read by hand. Any note the patterns misread is reported as a disagreement next
  to the grade, which stays as computed.
- **Parse check before grading**: the 2022-2023 counts by spice should match item 4 (for
  example cumin 15 unsatisfactory of 53). A mismatch is investigated and explained before
  any prediction is read.

## Descriptive outputs (not predictions)

Counts by year, spice, declared origin and year x spice (n, S, U, INV, lead, dye, filler);
the number of samples declaring Georgia (the country); every lead-chromate row verbatim;
every unsatisfactory or investigative row with its notes. The supplemental files for each
year are saved with the data.

## Limits, known now

CFIA samples by risk, so no rate here describes the Canadian market, and a change between
years may reflect what CFIA chose to sample. "Declared origin or dealer location" can be
the Canadian importer's location rather than where the spice grew. A note may describe
a failure without naming its cause. The files report outcomes, not lead concentrations.
