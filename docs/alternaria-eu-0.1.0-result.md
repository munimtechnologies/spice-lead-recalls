# alternaria-eu 0.1.0: result

This is the graded result for the pre-registration in
[`alternaria-eu-0.1.0-prereg.md`](alternaria-eu-0.1.0-prereg.md). The grader `alternaria_eu.py` and its
predictions were committed (v0.4.19) before any row or header of the data file was read, and they have not
been changed. One rule defect found after grading is reported below as a labelled deviation. The
graded numbers are given both as frozen and as corrected.

- **Source:** CFIA, *Alternaria in selected foods 2014-2018 and 2019-2022*, open.canada.ca dataset
  `8888649b-c059-4f76-ae0f-30ab6c1159c5` (Open Government Licence - Canada). sha256
  `9b79ec399c2d7e016ee52aef0279767b68e9d09f8fbda3316e772bf1cca3722a`, 5,190 data rows. Every
  result is in ng/g (= ppb), and the grader found no unreadable numbers. Each row is either alternariol (AOH) or
  alternariol monomethyl ether (AME), with no totals. The file has no product-type column.
- **Records:** 2,596. Of these, 2,594 have AOH and AME. Sample `C2020ALTN00315` carries a different
  product name on each toxin row (a hot pepper), so it parses as two one-toxin records. That leaves
  2,595 sample numbers, against the 2,597 samples in CFIA's report.
- **Sealed per-sample table:** [`../data/alternaria_eu_samples.csv`](../data/alternaria_eu_samples.csv).
  [`../test_alternaria_eu_result.py`](../test_alternaria_eu_result.py) recomputes every count below
  using only the Python standard library.

The EU indicative levels (Recommendation (EU) 2022/553) are **triggers for investigation, not food safety
limits**. Canada sets no limit for these toxins. Health Canada found no health concern in these surveys,
and nothing here says otherwise.

## Pre-registered predictions

| | prediction | value | as frozen | corrected (deviation D1) |
|---|---|---|---|---|
| P1 | 2,500-2,700 samples parse (gate) | 2,596 | met | met |
| P2 | top AOH + AME total is 860-890 ppb **and a processed tomato** (consistency) | 871 ppb, a pomegranate juice | not met | not met |
| P3 | 2-4 processed tomato samples above a tomato level (AOH 10, AME 5) | 0 of 200 | not met | not met |
| P4 | no sesame or sunflower seed above its level | 0 of 34 sunflower seeds (no sesame in the file) | met | met |
| P5 | 1-5 sunflower oils above its level (AOH 10, AME 10) | 3 of 41 | met | met |
| P6 | >= 20% of cereal-based infant foods above the infant level (AOH 2, AME 2) | as frozen 4 of 92; corrected **0 such foods** | not met | **not gradable** |
| P7 | Turkey leads country-declaring pomegranate products at >= 100 ppb | United States 11, Canada 1, Turkey 0 | not met | not met |
| P8 | foreign-declared pomegranate median > Canada-declared median | 0.21 (n 121) vs 46.75 (n 8) | not met | not met |
| P9 | > half of country-declaring above-level samples are foreign | as frozen 1 of 4; corrected 0 of 3 | not met | not met |

**3 of 9 gradable met as frozen; 3 of 8 gradable met as corrected.** The two consistency checks and
three of the four origin or count guesses failed.

### Deviation D1: the infant cereal rule matched "non-cereal"

The pre-registered rule put a sample in *infant cereal* if its text named an infant food **and** a cereal
word. CFIA labels 92 toddler and baby meals `Infant Food (non-cereal)`, and the word "cereal" in
"non-cereal" satisfied the rule. So all 92 records in the frozen class are foods that CFIA itself marks as
*not* cereal-based. The file holds **no** cereal-based infant food at all. Its other infant product is
`Infant Food - Puree`, and its `Cereal - Corn/Rice/Mixed Grains` products are adult foods from the 2020
survey. The EU's infant level applies only to cereal-based foods, so the 4 frozen "above" infant samples
(2.5-11.9 ppb) are not above any EU indicative level. Corrected, P6 has 0 samples (it needed 10) and is
not gradable. P9 drops the one Chile-declared infant meal and becomes 0 of 3. No other rule or number
changes. We did not swap the rule quietly: the frozen grades stay in the table, and the test checks both readings.

## What the file shows

**Only 3 of 2,596 records sit above an applicable EU indicative level. All 3 are sunflower oils declared
Canada** (2017: AOH 11.4 / 11.9 / 10.2 ppb, AME 8.9 / 50.4 / 43.0). That is 3 of the 4 Canada-declared
sunflower oils, against 0 of 16 foreign-declared and 0 of 21 with no country. The groups are tiny, and a
declared origin is a label (often the packer's country), so read this as a pointer, not a finding about
Canadian oil.

| EU food (AOH/AME level, ug/kg) | n | above | max AOH | max AME |
|---|---|---|---|---|
| processed tomato (10/5) | 200 | 0 | 6.22 | 0.90 |
| sunflower seeds (30/30) | 34 | 0 | 13.2 | 8.78 |
| sunflower oil (10/10) | 41 | 3 | 11.9 | 50.4 |
| sesame seeds (30/30) | 0 | - | - | - |
| cereal-based infant food (2/2) | 0 | - | - | - |

**The high levels are in foods the EU sets no AOH/AME level for.** These are pomegranate juice (up to 871 ppb), other
juices and blends (up to 619), barley (237.6), sorghum products (163.6), figs (146.3; the EU sets only a
tenuazonic-acid level for figs, and CFIA did not measure tenuazonic acid) and fruit purees for infants (up to 37.1). AME
exceeds AOH in 189 of the 1,551 detected records.

**Pomegranate: the high tail mostly declares no country.** 184 records name pomegranate. Of the 50 at
100 ppb or more, **38 (76%) declare no country**, 11 declare the United States and 1 declares Canada.
Records declaring the classic pomegranate-growing origins stay low: Turkey 7 (max 46.3) and Azerbaijan 11 (max
72.2). The 55 no-country records have a median of 308 ppb. P7 (Turkey) was a weak guess and failed outright. This
repeats the "where you look" pattern from this repository's earlier frames: most of the signal sits in
samples whose label names no origin, so the open file cannot say where the contamination came from.

## The open file does not contain the tomato results CFIA's report describes

CFIA's report (inspection.canada.ca, *Alternaria in selected foods*, Appendix A and Table 9) gives tomato
maxima of **880 ppb** (whole tomato, 2015) and **350 ppb** (diced tomato, 2016). Its text says the survey's
levels "ranged from 0.046 ... to 880 ppb", while its own Table 2 prints 871. The open per-sample
file has **no tomato row with either toxin at 10 ppb or more** (checked on the raw CSV as well as the
parsed table). Its highest tomato record totals **6.72 ppb**, an Italian tomato sauce from 2016. The
counts match the report closely everywhere except at these two values:

| year | report: samples / positive / min / max / mean of positives | open file: samples / positive / min / max / mean of positives |
|---|---|---|
| 2015 | 101 / 36 / 0.080 / **880** / 25 | 100 / 36 / 0.08 / **3.91** / 0.73 |
| 2016 | 100 / 41 / 0.060 / **350** / 9.4 | 100 / 40 / 0.06 / **6.72** / 1.02 |

In 2015 the positive count and the minimum match, but the report's mean (36 x 25, about 900 ppb in
total) needs one value near 880 that the file does not have. In 2016 the report has one more positive
sample, and its mean (41 x 9.4, about 385) needs one extra value near 345. The file's overall maximum,
871 ppb (a 2019 pomegranate juice), equals the report's Table 2 figure, not the "880" in its text. The file's
infant puree maximum (37.1 ppb, 2016) matches the report's Table 5, not its Table 2 (26). **Either the
report's two tomato maxima are wrong, or the open file is missing (or zeroes) those two samples.** We
cannot tell which from public material. It matters because, if real, those two would be the survey's only
processed tomato results above the EU tomato levels, and far above them (AOH 10, AME 5). As far as we can find,
this mismatch has not been reported before. It would need CFIA to resolve, and no human has yet
checked our reading.

The file's tomato products are named only `Tomato`, `Tomato Sauce` and `Tomato - Organic`. The
report's subtypes (whole, diced, crushed, paste, stewed, strained) cannot be matched to records.

## Limits

- Targeted retail sampling, not market shares. Many records declare no country.
- CFIA measured only AOH and AME. Tenuazonic acid, which has the most EU indicative levels (paprika,
  nuts, figs, tomato), was not measured, so most EU levels cannot be compared at all.
- The food classes are text rules on CFIA's product names. D1 shows how one can misfire. The test
  re-derives the corrected reading.
- No brand appears in CFIA's open file or here.

---

Made by MV2 of Munim, Inc. with AI agents. Code Apache-2.0; text and derived data CC BY 4.0. Contains
information licensed under the Open Government Licence - Canada.
