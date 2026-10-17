# Pre-registration: which declared origins carry the Canadian retail spices that would fail the EU's ochratoxin A limits? (ota-spices 0.1.0)

**Author:** MV2, Munim, Inc. (mv2@munimtech.com). Work made with AI agents.
**License:** text CC BY 4.0; code Apache-2.0.
**Written:** 2026-10-17, before any row of the data file was read.

## Why this question

Ochratoxin A (OTA) is a mould toxin that IARC classes as a possible human carcinogen (group 2B) and that
damages the kidney in animals. Spices are among the most contaminated foods. The EU sets limits for
spices (Regulation (EU) 2023/915: 20 ug/kg for Capsicum spices such as paprika and chili, 15 ug/kg for
pepper, nutmeg, ginger, turmeric and spice mixtures). Canada has none: CFIA's report lists Health Canada's
2009 proposed OTA limits (still proposals) for cereal products and dried vine fruit, and none for spices.

Nobody has been able to say where Canada's high-OTA spices come from. Health Canada's peer-reviewed study
of the same retail programme (J. Food Prot., "Ochratoxin A Concentrations in a Variety of Grain-Based and
Non-Grain-Based Foods on the Canadian Retail Market from 2009 to 2014") found 21 spice samples over EU
limits (7 chili powder, 5 nutmeg, 6 paprika, 2 pepper, 1 curry powder) and wrote: "The country of origin
of these products is rarely known, so it is not possible to correlate country of origin and OTA
concentrations". CFIA's report on 2012-2022 gives origin only as domestic / imported / unspecified.
On 2026-10-06 CFIA published the per-sample file on open.canada.ca. This study is, as far as we can find,
the first origin-level reading of it.

## What was already known when this was written

From CFIA's final report, "Ochratoxin A in Selected Foods - April 1, 2012 to March 31, 2018 and April 1,
2019 to March 31, 2022" (inspection.canada.ca), the dataset page (open.canada.ca dataset
37300d06-0887-4353-bc9b-4f030f1089a2, one bilingual CSV, Open Government Licence - Canada, released
2026-10-06) and the J. Food Prot. abstract above. We have not opened the CSV or seen any row, product name,
origin or column header of it. We read only the header of a different CFIA file (2011-12 coumarin in
cinnamon) to learn CFIA's usual layout (Sample No., Region, Function, Origin, Product, Date, Component,
Result, Unit, in English/French pairs).

- 8,384 retail samples from six cities; OTA detected in 4,056 (48%). Conventional max 1,770 ppb; organic max 65.
- Spices: 778 samples (41 domestic, 533 imported, 204 unspecified); 517 positive (66%); max 1,770 ppb, "observed
  in a sample of paprika"; mean of positives 22 ppb. By year: 2013 n 99 max 631; 2014 n 262 max 1,770;
  2015 n 273 max 152; 2019 n 144 max 124.
- Detection and mean of positives by spice: paprika 92% / 62 ppb, chili powder 88% / 18, hot/cayenne pepper 83% /
  6.4, mixed spices 83% / 3.0, nutmeg 82% / 38, curry powder 79% / 1.5, turmeric 71% / 2.2, black pepper 67% /
  0.93, ginger 50% / 6.0. Not detected in anise, cinnamon, cumin, fennel, fenugreek, marjoram, vanilla and others.
  Per-spice counts and maxima (except paprika) are not given.
- Dried fruit: 695 samples, max 116 ppb; 6 raisin samples were non-compliant with the proposed Canadian limit
  of 10 ppb for dried vine fruit. Their origins are not given.
- Grain-based foods: 119 non-compliant (max 65 ppb, frozen waffles). Health Canada: unlikely to pose a health
  risk; no recalls.

## Predictions (graded by `ota_spices.py`, unchanged after this commit)

| | prediction |
|---|---|
| P1 | at least 8,000 samples parse and 700-860 of them are spices (parse gate) |
| P2 | the highest spice result is 1,700-1,850 ppb in a paprika (CFIA's report; a consistency check, not a prediction) |
| P3 | 5-15% of spice samples exceed the EU limit for their type (a spice with no EU limit never counts as over) |
| P4 | the highest-OTA paprika declares Spain or Hungary (unspecified counts as not met) |
| P5 | India is strictly the most frequent declared country among spices over the EU limit (gradable if at least 5 such samples have a country) |
| P6 | Canada-declared spices exceed EU limits less often than foreign-declared spices (gradable if each group has at least 10) |
| P7 | no raisin, sultana or currant sample above 10 ppb declares the United States (gradable if at least one has a country) |
| P8 | Indonesia is strictly the most frequent declared country among nutmeg over 15 ppb (gradable if at least 3 have a country) |

Reasoning. P3: the J. Food Prot. study counted 21 exceedances among 2009-2014 spices; CFIA's high means for
paprika, nutmeg and chili come from a skewed tail, so we expect a minority of a few percent to about one in
ten; the band is 5-15%. P4: our recollection (not re-checked before writing) is that EU alerts on OTA in
paprika most often name Spain or Hungary; the risk is a blank or "Product of Canada" label. P5: India is
the largest spice supplier we know of for chili, turmeric, ginger and mixtures sold in Canada; the risk is
that paprika or nutmeg exceedances from other countries outnumber them. P6: "Canada" on a spice label
usually means packed in Canada from imported spice, so the gap may be small, but we predict a gap in this
direction. P7: we expect sun-dried raisins from a dry climate (California) to carry less OTA than those
from Turkey, Iran or Central Asia. P8: Indonesia is, to our knowledge, the largest nutmeg exporter. All of
these are expectations written down to be tested, not checked facts.

## Method

`ota_spices.py` downloads the one CSV, records its sha256, keeps rows whose component names ochratoxin
(all rows if there is no component column), and merges rows into one record per (base sample number,
product) (a trailing "D" duplicate merges into its base; the highest result is kept). Results are converted
to ppb (ppm and mg/kg x 1000); "<" values, "ND" and blanks read as zero. A sample is a spice if its
product-type column names spices; if the file has no such column, product-name keyword rules decide (and
exclude baked goods, cereals, teas and similar). Spice type comes from the English product name, in this
order: paprika (20), chili/cayenne/red or hot pepper (20), nutmeg or mace (15), ginger (15), turmeric (15),
mixtures (curry, masala, mix, blend, seasoning and similar; 15), pepper (15); anything else has no EU
limit. "Chili powder" is graded as a Capsicum spice (20) even though US-style chili powder is a blend.
Origins are upper-cased and normalised (USA -> UNITED STATES); blank, unknown and "imported" without a
country do not count as a declared country. The script writes `grades.json`, `summary.md` (with tables by
spice type and by origin, the 25 highest spice results and every vine fruit above 10 ppb) and
`ota_samples.csv`. `test_ota_spices.py` checks the parser, the rules and the grader offline on synthetic
files in CFIA's layout. If the real file's columns differ from what the parser expects, the job fails
loudly; any fix is recorded as a deviation, and none of the predictions change.

## Limits

Targeted retail sampling, not a representative diet survey. Origin is what the label declares (often the
packer's country, not where the spice grew), and about a quarter of spices declare none. EU limits are a
yardstick, not Canadian law: no Canadian rule is broken by any spice result here. Spice types come from
keyword rules on product names. Counts per origin will be small; this is a description with pre-registered
guesses, not a causal claim about any country's growers.

Contains information licensed under the Open Government Licence - Canada.
