# Where do high-lead spices turn up? Result of sampling_frame 0.1.0

By MV2 of Munim, Inc. Prepared with AI agents. Text CC BY 4.0; code Apache-2.0.

**Status:** graded against [the pre-registration](sampling-frame-0.1.0-prereg.md), which
was committed before the NYC data were split by frame. Every prediction is reported,
met or not. Section 4 is a descriptive follow-up added after grading. It was **not**
pre-registered and grades nothing.

## 1. What ran

`sampling_frame.py` 0.1.0 ran once in a sealed container on 2026-10-17 (03:25 UTC). It
fetched NYC DOHMH's *Metal Content of Consumer Products* (`da9u-wz3r`; Food-Spice, lead)
and Public Health – Seattle & King County's *Lead Content of Consumer Products*
(`i6sy-ckp7`; Seasoning and Food). Its 11 offline unit tests passed first. The exact rows
it read are committed as snapshots:

- `data/nyc_spice_lead_snapshot_2026-10-17.csv`: 3,580 records. 3,575 are laboratory
  results in ppm. The other 5 are 2 XRF readings and 3 results in mg/l, and they are excluded.
- `data/kc_seasoning_food_snapshot_2026-10-17.csv`: 260 records, all used.
- `data/frame_yield.csv`: the per-frame table below.

`test_sampling_frame_result.py` recomputes `frame_yield.csv`, the grades and every figure
in this note from those snapshots, with no network access.

## 2. NYC: the five predictions

Share of results at or above 2 ppm lead (non-detects count as below):

| Frame | Results | ≥ 2 ppm | Share | Wilson 95% | ≥ 50 ppm | Max (ppm) |
|---|---:|---:|---:|---|---:|---:|
| C, case investigation | 2,790 | 403 | 14.4% | 13.2–15.8% | 171 | 78,000 |
| S, store survey | 477 | 41 | 8.6% | 6.4–11.5% | 2 | 610 |
| A, undefined code | 308 | 93 | 30.2% | 25.3–35.5% | 46 | 27,000 |
| all | 3,575 | 537 | 15.0% | 13.9–16.2% | 219 | 78,000 |

| # | Prediction | Observed | Verdict |
|---|---|---|---|
| P1 | Case share ≥ 2 × store share | 14.4% vs 8.6%, ratio 1.68 | **failed** |
| P2 | Store share ≤ 15% | 8.6% | met |
| P3 | Case share between 20% and 50% | 14.4% | **failed** (too low) |
| P4 | Store surveys supply ≤ 10% of results ≥ 50 ppm | 2 of 219 (0.9%) | met |
| P5 | Fisher two-sided p < 0.001, case share higher | p = 0.00038 | met |

**3 of 5 met.** I overestimated how often a case-investigation spice is positive at
2 ppm (14%, not 20–50%) and how much more often than a store-shelf spice (1.7×, not 2×).
The store-survey side was predicted correctly.

**Strict cut check.** Five results read exactly 2 ppm (3 C, 1 S, 1 A). Using "> 2"
instead of "≥ 2" gives C 400, S 40, A 92 and changes no verdict (P5 stays below 0.001).

The A code is not defined in the dataset documentation we found. It has the highest
share (30%), and it is reported here without interpretation, as pre-registered.

## 3. King County: the observed-first check reproduced

Everything recorded before registration reproduced exactly. In case-investigation seasoning,
2 of 11 results were ≥ 2 ppm (6 more rows have no value). In community testing events,
0 of 184 were. For Seasoning + Food the figures are 5 of 57 against 0 of 197, and the
community maximum is 1.3 ppm. Fisher p is 55/18,915 ≈ 0.0029 and ≈ 0.00049. The
King County case set is small: its Wilson interval for seasoning is 5–48%.

## 4. Follow-up (descriptive, not pre-registered): period and threshold

Store surveys are nearly all recent. Only 20 of the 477 come from 2011–2015, against 345
of the 2,790 case results, and those early case results ran hot: 111 of 345 (32.2%) were
≥ 2 ppm. So part of the 1.7× gap is a period effect. `frame_period.py` (0.1.0) splits
the same rows by period and threshold (`data/frame_period_ladder.csv`):

| 2016–2025 | Case (n = 2,445) | Store survey (n = 457) | Ratio |
|---|---:|---:|---:|
| ≥ 2 ppm | 292 (11.9%) | 38 (8.3%) | 1.4× |
| ≥ 10 ppm | 158 (6.5%) | 10 (2.2%) | 3.0× |
| ≥ 50 ppm | 117 (4.8%) | 2 (0.44%) | 10.9× |
| ≥ 500 ppm | 66 (2.7%) | 2 (0.44%) | 6.2× |

Within 2016–2025 the gap at 2 ppm is small and only nominally significant: exact Fisher
p is about 0.02 (the test pins it between 0.005 and 0.05). At 50 ppm it is large
(p < 0.001). Both store-survey results ≥ 50 ppm are two tests of **one** product,
a Yemeni spice mix collected on 2019-01-15 (570 and 610 ppm). Across all years, 171 of
the 219 results ≥ 50 ppm (78%) came from case investigations, 46 (21%) from code A and
2 (0.9%) from store surveys.

**Reading.** Low-level lead (2–10 ppm) turns up on New York store shelves nearly as
often as in homes. Gross contamination does not. Results of 50 ppm and above, the range
of deliberate adulteration such as lead chromate, came almost entirely from homes visited
in lead-poisoning investigations. A screen that sees only gross adulteration (a pocket Raman
reading near 0.1% lead chromate by mass is about 640 ppm lead) would almost never fire
on a store-survey sample here, and would fire on about 1 in 37 case-investigation samples
from 2016–2025 at ≥ 500 ppm. That is an argument for carrying such a screen on home
visits, and against running it as a shelf survey.

## 5. Prior art and what is new

- Hore et al. 2019 (*J Public Health Manag Pract* 25:S63, NYC 2008–2017, 1,496 samples)
  report that more than 30% of samples exceeded 2 ppm. They compared purchases made abroad
  with purchases made in the US. They also noted that store-survey samples never reached
  the levels seen in case investigations (store-survey maximum 21 ppm). We could read only
  the abstract and excerpts, because the full text is paywalled.
- Angelon-Gaetz et al. 2023 (*Public Health Rep*, North Carolina) found market-basket
  spices had a median of 0.07 mg/kg, against 0.26 mg/kg for spices from home
  investigations. The home maximum was 6,504 mg/kg.
- Porterfield et al. 2024 (*EHP* 132:075002) tally how often consumer products were
  the exposure source in four jurisdictions' investigations. They do not report
  sample-level hit rates by frame.

What this note adds is modest, and we say so plainly. It is an open, rerunnable split of two
cities' public tables by sampling frame, extended through 2025. It shows that the frame gap
**depends on the threshold**: about 1.4× at 2 ppm and about 11× at 50 ppm within the same
years. It also finds that a third city-scale table (King County, 0 of 197 community-event
results ≥ 2 ppm) agrees. We found no earlier published threshold ladder by frame.

## 6. Limits

- Neither frame is a random sample. Store surveys follow up products implicated in cases
  (Hore 2019), so even S leans toward suspect products. These are yields per test, not
  prevalence.
- The table counts test results, not distinct products. Repeated tests of one product
  (as with the two store-survey hits ≥ 50 ppm) count more than once.
- Section 4 was chosen after the grading. Treat its ratios as descriptive. The ≥ 500 ppm
  row rests on 2 store-survey results from one product.
- Case samples are often bought abroad and store samples never are. Purchase place is
  the obvious next variable, and it is pre-registered separately in
  [purchase-place-0.1.0-prereg.md](purchase-place-0.1.0-prereg.md).
