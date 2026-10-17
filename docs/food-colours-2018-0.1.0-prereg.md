# Pre-registration: which product carried the one non-permitted colour in Canada's 2018-19 food colours survey? (food-colours-2018 0.1.0)

**Author:** MV2, Munim, Inc. (mv2@munimtech.com). Work made with AI agents.
**License:** text CC BY 4.0; code Apache-2.0.
**Written:** 2026-10-17, before any row of the data file was read.

## What was already known when this was written

Everything below comes from CFIA's final report page, "Food Colours in Essences/Flavourings, Oils, Sweets
and Processed Vegetables - April 1, 2018 to March 31, 2019" (inspection.canada.ca), and the dataset page
on open.canada.ca (dataset 1b0c4141-7a22-4c93-8679-63eb49f7be24, one CSV, Open Government Licence - Canada).
We have not opened the CSV or seen any per-sample row, product name or column layout.

- 399 retail samples from six cities: 50 essences/flavourings, 99 oils, 50 processed vegetables, 200 sweets.
  56 domestic, 184 imported, 159 with no origin determinable from the label (40%).
- Tested for up to 43 colours: 10 permitted water-soluble, 17 non-permitted water-soluble and 18 non-permitted
  fat-soluble (the Sudan dyes, Para Red, Metanil Yellow, Rhodamine B and others).
- 181 samples (45%) had at least one colour. Allura Red (101 samples, max 539 ppm), Tartrazine (100),
  Brilliant Blue FCF (61) and Sunset Yellow FCF (44) made up 91% of detections. Highest levels were in
  soft and hard candy.
- Non-permitted colours in Table 3: Rhodamine B in 1 sample at 10.8 ppm; Orange II in 2 samples, max
  0.221 ppm (CFIA marks Orange II as a possible subsidiary colour of a permitted dye).
- Five non-compliant samples (98.7% compliance): "Food colours at levels exceeding the maximum level of use
  were detected in 3 of the samples", "A non-permitted food colour was found in 1 sample", and 1 sample
  held permitted colours not declared on the label. Table 2 places them as 2 processed vegetables and
  3 sweets. The report does NOT say which product, origin or colour each non-compliant sample involved.
- Health Canada judged none a health concern; no recalls.

So the one fact this study adds is the one the report withholds: what product, from where, carried the
Rhodamine B (and, descriptively, what the two Orange II samples and the high-level permitted-colour samples
were). Rhodamine B is a textile dye that is genotoxic in animal studies and turns up in brightly coloured
sweets and chilli products in South and Southeast Asian markets; Yellow Flag's SERS dye panel includes it.

## Predictions (graded by `food_colours_2018.py`, unchanged after this commit)

Gradable only if at least 380 base samples parse and the file reports Rhodamine B as a component (P1).

| | prediction |
|---|---|
| P1 | at least 380 samples parse and the file reports Rhodamine B (parse gate) |
| P2 | exactly one sample carries Rhodamine B above zero (CFIA's Table 3; a consistency check, not a prediction) |
| P3 | the Rhodamine B sample is a sweet (not a processed vegetable, oil or essence) |
| P4 | the Rhodamine B sample declares an Asian origin (South, Southeast, East or West Asia; not unspecified) |
| P5 | every sample with Orange II above zero is a sweet |
| P6 | under 5% of oil samples declare a West or Central African origin |

Reasoning. P3: 3 of the 5 non-compliant samples were sweets, sweets were 200 of 399 samples, and the
published Rhodamine B food cases are mostly confectionery. P4: Rhodamine B food cases are reported from
India, Pakistan, Bangladesh, Indonesia and China; a bright imported sweet usually carries an origin. The
risk is the 40% unspecified-origin share, which would make P4 fail. P5: Orange II is a subsidiary colour of
Sunset Yellow FCF, and Sunset Yellow was found mostly in sweets. P6: CFIA ran separate red palm oil surveys
in 2017-18 and 2018-19 (v0.4.10 line); this survey's oils are more likely olive, sesame, chilli and flavoured
oils, so West African red palm oil should be rare here. This matters for the where-you-look line: it tests
whether the only frame that reached the fat-soluble Sudan dyes in "oils" sampled the origin where CFIA's
own red palm oil files found Sudan IV (Nigeria).

Over-maximum-level samples are reported descriptively (any permitted colour above 300 ppm in one sample),
not graded, because Canada's maximum levels differ by food and the report gives no per-sample detail.

## Method

`food_colours_2018.py` downloads the one CSV, records its sha256, and merges rows into one record per base
sample number (a trailing "D" duplicate merges into its base). Each sample is assigned a category from the
Commodity and Product text by keyword rules, in this order: oils (the word "oil"), processed vegetables
(pickle, vegetable, relish, olive and similar), sweets (candy, confection, jelly, chocolate and similar),
essences/flavourings (essence, flavour, extract, colour). A sample no rule matches is "unclassified", and a
prediction about an unclassified sample is "not gradable", not "met". A blank, "unspecified" or
"not stated" origin is UNKNOWN; a "<" value reads as zero. A colour is non-permitted if it is not one of
the 10 permitted colours in CFIA's Appendix A (Erythrosin Yellowish is not Erythrosin B). The script writes
`grades.json`, `summary.md` and a per-sample table. `test_food_colours_2018.py` checks the parser, the
classifier and the grader on synthetic files in CFIA's open-data layout. If the real file's columns differ
from what the parser expects, the job fails loudly; any fix is recorded as a deviation, and none of the
predictions change.

## Limits

One survey year, 399 samples chosen because they were likely to contain colours; CFIA says detection rates
are not representative of retail food. Origin is what the label declares. One Rhodamine B sample proves
nothing about any origin or product class; the study names a case the report left anonymous and tests
whether a frame-coverage guess made in advance was right.

Contains information licensed under the Open Government Licence - Canada.
