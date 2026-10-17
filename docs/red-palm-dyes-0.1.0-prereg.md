# Pre-registration: where does Sudan-dyed red palm oil on Canadian shelves come from? (red-palm-dyes 0.1.0)

**Author:** MV2, Munim, Inc. (mv2@munimtech.com). Work made with AI agents.
**License:** text CC BY 4.0; code Apache-2.0.
**Status:** pre-registered. Written and committed together with the grading code
(`red_palm_dyes.py`, `test_red_palm_dyes.py`) **before any AMOUNT value in the 2019-20 data
file was read**. The result will be a separate, later commit, graded against the
predictions below.

## Why this exists

Lead chromate is one target of this repository's screen. Industrial **Sudan dyes** are the
other (spice-screen's dye mode). They are banned in food everywhere, but some producers add
them to make poor oil or spice look redder. Red palm oil is the best-documented case:

- In Ghana, routine testing found Sudan IV in 96% of palm oil in August 2015 (FDA Ghana).
  FDA Ghana's own trend study (Osei Tutu, Amanfo, Mingle & Darko, 2018-2023) reports 7.3%
  of market samples contaminated in 2018, 26.6% in 2019, 22.9% in 2021, 26.1% in 2022 and
  8.1% in 2023, highest in Greater Accra. A 2023 national round failed 70 of 306 samples.
- Earlier studies in Accra (KNUST, 2016) and in major Ghanaian cities (Scientific African,
  2021) found the dye in most market oil, and an Eastern Region vendor survey (J Food Qual,
  2026) found 7% of 200 vendors admitting to using it.

All of that is measured inside the producing country. The Canadian Food Inspection Agency
(CFIA) measured the other end: imported red palm oil bought at Canadian retail, tested for
18 non-permitted colours, one row per sample and colour, with a declared origin for each
sample. Two years are open (Open Government Licence - Canada):

- "2019-2020 Non-Permitted Food Colours in Red Palm Oil Data", open.canada.ca dataset
  f0aa9c6f-984f-4cc8-a7d7-b679c6e64e10 (**the blind, primary file**);
- "2020-2021 Non-Permitted Food Colours in Red Palm Oil Data", open.canada.ca dataset
  5841c1a3-055e-489a-8766-1781a908903f.

This is the same question this repository asked of Georgian and Bangladeshi spices in New
York's case files: does a destination country's lab data see what the producing country's
regulator reports? We found no per-origin analysis of CFIA's red palm oil files, and no
comparison of them with FDA Ghana's market trend.

## What was seen before registering (blinding record)

- Both dataset pages and both files' **structure**: 15 columns (sample number, region,
  commodity, function, origin, product, date sampled, component, amount, report unit, with
  French twins); every row is imported red palm oil; units ug/g; a non-detect is a bare 0;
  18 components (Chlorophylline, Citrus Red 2, Metanil Yellow, Methyl Yellow, Orange II,
  Para Red, Rhodamine B, Solvent Blue 59, Sudan Black B, Sudan Blue II, Sudan I, II, III,
  IV, Sudan Orange G, Sudan Red 7B, Sudan Red G, Toluidine Red).
- 2019-20: about 72 sample numbers between C2019FFPO00001 and 00075 (00006, 00007 and 00018
  absent; 00019D and 00035D carry a "D" suffix), UTF-8 with a byte-order mark. Declared
  origins: Ecuador, Ghana, Senegal, Nigeria, Malaysia, Colombia, Togo, Unknown.
- 2020-21: 576 rows, 32 samples x 18 components, Windows-1252 text. Declared origins:
  Nigeria, Ghana, Unknown, Malaysia, Ivory Coast, Ecuador, Colombia, Togo, Cameroon.
- **2020-21 headline, from CFIA's report via a search snippet:** of 32 samples, 1 contained
  15.6 ppm Sudan IV and 31 had no detectable non-permitted colour. The origin of that
  sample was not seen.
- From the same search: an earlier CFIA survey, "Food Colours in Selected Foods", found
  non-permitted colours in 4 palm oil samples (3 products).
- The Ghanaian figures quoted above.
- **No AMOUNT value of the 2019-20 file and no 2019-20 headline were seen.** No 2019-20
  report text was opened.

Because the 2020-21 headline was seen, its one positive (Sudan IV) is known. P1 and P2 are
about the 2019-20 file alone. P3-P6 pool both years. P4 and P6 are partly settled for
2020-21 by the headline, and P3 and P5 depend on origins that were not seen.

## Method (fixed in advance)

- Unit: one base sample number. A trailing "D" after the digits marks a duplicate and is
  merged with its base sample; the sample counts as positive if either copy is.
- **Sudan-positive:** any of the nine Sudan dyes (Sudan I, II, III, IV, Black B, Blue II,
  Orange G, Red 7B, Red G) with AMOUNT > 0.
- **Other non-permitted colour:** Citrus Red 2, Metanil Yellow, Methyl Yellow, Orange II,
  Para Red, Rhodamine B, Solvent Blue 59 or Toluidine Red with AMOUNT > 0.
- Chlorophyllin is reported but never graded (it is a plant-derived green colour, not an
  industrial dye).
- Origin is the English "Origin" column, upper-cased. West or Central African =
  Ghana, Nigeria, Senegal, Togo, Ivory Coast, Cameroon. A blank counts as Unknown.
- The grade is gradable only if the 2019-20 file parses to at least 60 base samples and
  includes Sudan IV. If the 2020-21 file cannot be read, P3-P6 use 2019-20 alone and the
  result says so.

## Predictions (falsifiable)

- **P1.** In 2019-20, **at least one** sample carries a Sudan dye.
- **P2.** In 2019-20, **at most 10%** of samples carry a Sudan dye. (FDA Ghana measured
  26.6% in its own 2019 market; oil packed for export and sold at Canadian retail should be
  cleaner.)
- **P3.** Across both years, **every** Sudan-positive sample declares a West or Central
  African origin, or none. None comes from Malaysia, Ecuador or Colombia, where red palm oil
  is industrial.
- **P4.** Across both years, **Sudan IV** is found in at least as many positive samples as
  any other Sudan dye. (Gradable with at least 2 positives.)
- **P5.** Across both years, **Ghana** is the declared origin of at least as many
  Sudan-positive samples as any other single origin (ties count as met). (Gradable with at
  least 2 positives of known origin.)
- **P6.** **No** non-Sudan non-permitted colour is found in any sample of either year.

Failures will be reported as failures. If P3 fails, the dye is not only a West African
problem in the oil Canada imports. If P2 fails, Canadian retail looked like Ghana's own
market, not cleaner.

## Descriptive (not graded)

Samples, Sudan-positive samples and the highest Sudan amount by year and declared origin;
how often each colour was found; every sample with any non-permitted colour, with its
region and date; whether duplicate copies agree; chlorophyllin finds. The result note will
set the Ghana-origin rate next to FDA Ghana's market rate for the same year, with the
caveat that the two are different sampling frames.

## Outputs (next commit)

- `data/cfia_red_palm_oil_colours_2019-2020.csv` and `data/cfia_red_palm_oil_colours_2020-2021.csv`
  (the CFIA files, frozen, Open Government Licence - Canada) and
  `data/red_palm_dyes_samples.csv` (one row per sample).
- `docs/red-palm-dyes-0.1.0-result.md`, graded against P1-P6 from a sealed run of
  `red_palm_dyes.py`, with a test that recomputes every graded number from the committed
  files.

## Sources

- CFIA open data, as above. CFIA reports: "Non-Permitted Food Colours in Red Palm Oil",
  inspection.canada.ca.
- Osei Tutu B, Amanfo KK, Mingle CL, Darko D. Trend of Sudan dye adulteration on the
  Ghanaian market and the impact of regulatory intervention: 2018-2023. SSRN 4954945; also
  on fdaghana.gov.gh.
- Amoako-Mensah. Assessment of the prevalence of palm oil adulteration with Sudan IV dye in
  the Greater Accra Region. MSc thesis, KNUST (2016).
- Quality and safety evaluation of important parameters in palm oil from major cities in
  Ghana. Scientific African (2021). ScienceDirect PII S2468227621001642.
- Asante et al. Detection of Sudan dye adulteration in palm oil and assessment of vendors'
  knowledge and perceptions in the Eastern Region of Ghana. J Food Qual (2026).
  doi:10.1155/jfq/7180106

Contains information licensed under the Open Government Licence - Canada.
