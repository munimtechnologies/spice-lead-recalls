# Pre-registration: how often do foods sold in Canada sit above the EU's indicative levels for Alternaria toxins? (alternaria-eu 0.1.0)

**Author:** MV2, Munim, Inc. (mv2@munimtech.com). Work made with AI agents.
**License:** text CC BY 4.0; code Apache-2.0.
**Written:** 2026-10-18, before any row or header of the data file was read.

## Why this question

*Alternaria* moulds grow on tomatoes, oilseeds, cereals and fruit and make the toxins alternariol (AOH),
alternariol monomethyl ether (AME) and tenuazonic acid (TeA). No country sets a legal limit for them. In
2022 the European Commission set **indicative levels** (Commission Recommendation (EU) 2022/553 of 5 April
2022): values above which EU member states are asked to investigate how the toxins got there. They are not
food safety levels, and nothing here treats them as such. The AOH / AME levels, in ug/kg (= ppb), are:

| food | AOH | AME |
|---|---|---|
| processed tomato products | 10 | 5 |
| sesame seeds | 30 | 30 |
| sunflower seeds | 30 | 30 |
| sunflower oil | 10 | 10 |
| cereal-based foods for infants and young children | 2 | 2 |

(Paprika powder, tree nuts and dried figs have a TeA level only. Source: the Annex of 2022/553 as
reproduced by GALAB and cross-checked against other lab summaries; EUR-Lex itself did not load for us.)

The Canadian Food Inspection Agency (CFIA) tested 2,597 retail foods for AOH and AME in 2014-2018 and
2019-2022 and published the per-sample file in July 2026 (open.canada.ca dataset
8888649b-c059-4f76-ae0f-30ab6c1159c5, Open Government Licence - Canada). Its report gives only AOH + AME
combined, by product type, and compares with no level. We found no published comparison of Canadian retail
foods with the EU indicative levels (a 2026 review of tomato-product regulation notes that no level exists
outside Europe). This study makes that comparison sample by sample, and asks which declared origins carry
the highest levels in pomegranate products, CFIA's highest-level food.

## What was already known when this was written

We read the dataset page and CFIA's two report pages (selected foods 2014-2022; beer, juices, oils and
seeds 2018-19). We have not opened the CSV and do not know its columns, so we do not know whether it gives
AOH and AME separately. From the report (AOH + AME combined, ppb):

- 2,597 samples in 9 product types; 1,554 (60%) positive; range 0.046-880 (the summary table prints 871).
  ALT and TeA were not measured. Health Canada found no health concern; there were no recalls.
- Highest: a whole (canned) tomato at 880 (whole tomato: 47 samples, 10 positive, mean of positives 88).
  Diced tomato max 350 (85 samples, 28 positive, mean 13). Crushed max 5.2, sauce max 3.9, paste 0.50.
- Sunflower oil (2017): 41 samples, 31 positive, 0.10-62, mean 5.9.
- Sunflower seeds: 36 samples, max 20. Sesame: 6 samples, max 4.0.
- Infant purees max 26 (2019) and 37 (2016); toddler meals max 12. Infant cereals are not reported apart.
- Pomegranate: juice 99 samples, max 870, mean 220; blends with pomegranate 46, max 590. The report's
  origin table swaps the pomegranate and processed-fruit rows; read correctly, pomegranate products are
  24 domestic, 135 imported, 84 unspecified (243). No result is given by country.

Consequences we state now: two tomato samples (880 and 350 total) must exceed a tomato level, because a total
above the sum of the two levels (15) means at least one toxin is above its own level; the 62 ppb sunflower
oil must exceed (62 > 20); and no sesame or sunflower seed can exceed (all totals under 30). So P2 and P4
are consistency checks, and P3 and P5 have known lower bounds; their upper bounds are the predictions.

## Rules (fixed before reading)

- **Food classes** (from the product type and product name together): *infant cereal* if the text names an
  infant, baby, toddler or teething food and a cereal word (cereal, oat, rice, barley, wheat, grain,
  biscuit, cracker, puff, rusk, pasta); otherwise *processed tomato* if it names tomato and not fresh;
  *sesame seeds* if sesame and not oil; *sunflower oil* if sunflower and oil; *sunflower seeds* if
  sunflower and not oil or butter. *Pomegranate* is flagged separately. Full patterns are in the code.
- **Above / within / undetermined**: with AOH and AME separate, a sample is above if either exceeds its
  level (strictly greater). With only a total: above if the total exceeds the sum of the two levels,
  within if it is no more than the smaller level, otherwise undetermined. A prediction about a count is
  graded met or not met only if it holds or fails for every count the undetermined samples allow;
  otherwise it is "not gradable".
- Results in ppm or mg/kg are multiplied by 1,000; "<" values, "ND" and blanks read as zero; a blank unit
  means ppb. A trailing "D" (duplicate) merges into its sample, and values are averaged. "Domestic" counts
  as Canada; blank, unknown and "imported" without a country count as no declared country.

## Predictions (graded by `alternaria_eu.py`, unchanged after this commit)

| | prediction |
|---|---|
| P1 | 2,500-2,700 samples parse (parse gate; the report says 2,597) |
| P2 | the highest AOH + AME total is 860-890 ppb and is a processed tomato product (consistency check) |
| P3 | 2-4 processed tomato samples are above a tomato level (AOH 10, AME 5) (at least 2 are known) |
| P4 | no sesame or sunflower seed sample is above its level (consistency check) |
| P5 | 1-5 sunflower oil samples are above its level (AOH 10, AME 10) (at least 1 is known) |
| P6 | at least 20% of cereal-based infant foods are above the infant level (AOH 2, AME 2) (gradable if at least 10 such samples) |
| P7 | Turkey is strictly the most frequent declared country among pomegranate products with AOH + AME of 100 ppb or more (gradable if at least 5 have a country; a tie is not met) |
| P8 | pomegranate products declaring a foreign country have a higher median AOH + AME than those declaring Canada (gradable if at least 5 of each) |
| P9 | more than half of the above-level samples that declare a country declare one other than Canada (gradable if at least 3) |

P3-P6 need at least 10 samples in the class. Reasoning, all expectations rather than checked facts. P3: the
tomato means of positives are low apart from the two known high samples, so we expect few others above 5
AME. P5: the oil mean is 5.9, so most samples should sit under 10 for each toxin. P6: the infant level is
strict (2 ug/kg each) and grain foods average about 4 ppb combined among positives, so we expect a fair
share above it; this is the least certain call. P7: we believe (not checked) that Turkey is a leading
exporter of pomegranate juice concentrate; a weak guess, written down to be tested. P8: Canada-declared products are likely blends
packed in Canada with less pomegranate. P9: Canada imports most of these foods.

## Method

`alternaria_eu.py` downloads the CSV, records its sha256, keeps rows whose component is AOH, AME or a total
(every row is a total if there is no component column), merges rows into one record per (base sample
number, product), classifies each, and writes `grades.json`, `summary.md` (each EU food with counts above,
within and undetermined by origin group; every above-level and undetermined sample; the top 15; pomegranate
products by declared origin; every product type; the file's header, units and components) and
`alternaria_samples.csv` (every sample). `test_alternaria_eu.py` tests the parser, the classes, the
above/within/undetermined rule and the grader offline on synthetic files in CFIA's layout. If the real
file's columns differ from what the parser expects, the job fails loudly; any fix is recorded as a
deviation, and no prediction changes.

## Limits

Targeted retail sampling, not market shares. CFIA did not measure TeA, the toxin with the most EU levels, so
paprika, nuts and figs cannot be compared at all. Our food classes are text rules on CFIA's product names and
may misplace a product (for example a toddler pasta meal counts as cereal-based). Origin is what the label
declares, often the packer's country. Exceeding an indicative level is a trigger for investigation in the
EU, not a safety finding; Health Canada found no health concern in these surveys, and nothing here says
otherwise. No brand is named beyond what CFIA's own open file holds.

Contains information licensed under the Open Government Licence - Canada.
