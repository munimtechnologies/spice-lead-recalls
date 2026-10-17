# Pre-registration: where do high-lead spices turn up? (sampling_frame 0.1.0)

Status: **written and committed before the NYC split by sampling frame was computed or
looked at.** The King County figures below *were* seen first (through aggregate queries
on the open portal on 2026-10-17), so they are stated as observations, not predictions.
A sealed compute run of `sampling_frame.py` will recompute both and grade the five NYC
predictions. The result note will report every prediction, met or not.

By MV2 of Munim, Inc. Prepared with AI agents. Text CC BY 4.0; code Apache-2.0.

## Question

When a health department tests a spice for lead, how much does the chance of finding
a high result depend on **how the sample was obtained**? Health departments test spices
from homes during lead-poisoning case investigations, from stores in targeted surveys,
and from community testing events. If almost all high results come from case
investigations, then a quick field screen (such as the pocket Raman screen this
project proposes) will catch the most per test inside home visits, not on store shelves.

## Prior art

- Angelon-Gaetz, Segule & Wilson, *Public Health Reports* 138(1):91-96 (2023),
  doi:10.1177/00333549211066152. In North Carolina they compared 50 market-basket spices
  (2017) with 689 consumable results from 103 home lead investigations (2011-2020).
  The median was 0.07 vs 0.26 mg/kg (Wilcoxon P < .001), the market maximum was 0.88 mg/kg
  and the home maximum 6,504 mg/kg (turmeric bought in India). They report medians, not
  the share of samples above a cut.
- Hore, Alex-Oni, Sedlar & Nagin, *J Public Health Manag Pract* 25(1 Suppl):S63-S70
  (2019). They looked at 1,496 NYC spice samples from 2008 to 2017 and found more than 30%
  above 2 ppm. They split results by country of purchase (abroad vs US), not by how the
  sample was obtained.

What is new here: we ask the same question on two large **open** municipal lab tables
(NYC through 2025, King County through 2026), using the share at or above 2 ppm with exact
tests, in code anyone can rerun from the public portals. If the North Carolina pattern
holds, this is a replication in two more jurisdictions. If it does not, that is worth
knowing too. We found no published frame-by-frame analysis of either open table.

## Data and definitions (fixed now)

- **NYC**: data.cityofnewyork.us dataset `da9u-wz3r`. Rows with `product_type` =
  `Food-Spice`, `metal` = `Lead`, `units` = `ppm`, and `analysis_type` not XRF.
  `-1` (and `0`) are non-detects. Frames come from `investigation_type`: `C`, `S`, `A`.
  The portal does not define these codes. We read `C` as case investigation and `S` as
  store survey, matching the dataset description ("investigating lead poisoning cases"
  and "store surveys"). `A` is reported separately and not used in any prediction.
- **King County**: data.kingcounty.gov dataset `i6sy-ckp7`. Laboratory rows with
  `product_type` `Seasoning` (primary) or `Seasoning`+`Food` (secondary). A `qualifier`
  (`<`, `<LOD`) means a non-detect. Frames come from `data_source`: `Case Investigation`
  and `Community product testing event`.
- **Share at or above 2 ppm** = rows with a reported value of at least 2.0 ppm, divided by
  rows with a result (a value or a non-detect). Rows with no value and no qualifier are
  counted as missing and left out of the denominator. The 2 ppm cut is the one Hore et al.
  report (they used "> 2"; we use "at or above 2", and the result note will say if this
  changes anything). It is a screening cut, not a legal limit.
- Tests: exact two-sided Fisher on the 2x2 table (at or above 2 vs below), and 95% Wilson
  intervals.

## Predictions (NYC; graded by `grade()` in `sampling_frame.py`)

- **P1.** The case-investigation share is at least **twice** the store-survey share.
- **P2.** The store-survey share is **at most 15%**.
- **P3.** The case-investigation share is **between 20% and 50%**.
- **P4.** Store surveys supply **at most 10%** of all NYC spice results at or above 50 ppm.
- **P5.** Fisher's two-sided p for case vs store survey is **below 0.001**, and the case
  share is the higher one.

Why these are real risks: NYC's store surveys target shops that serve the communities
most affected by lead poisoning (Georgian and South Asian), so their hit rate could
come close to the case-investigation rate. Hore et al.'s more-than-30% figure covers
both frames together.

## King County: observed before registration (a reproducibility check, not a prediction)

Aggregate queries on 2026-10-17 (all 260 Seasoning/Food rows are laboratory results):

| Set | Frame | Rows | With a result | At or above 2 ppm | Highest |
|---|---|---|---|---|---|
| Seasoning | Case investigation | 17 | 11 | 2 | 2,800 ppm (homemade turmeric, India) |
| Seasoning | Community event | 184 | 184 | 0 | 1.3 ppm |
| Seasoning+Food | Case investigation | 63 | 57 | 5 | 2,800 ppm |
| Seasoning+Food | Community event | 197 | 197 | 0 | 1.3 ppm |

For the community events (0 of 197), the 95% Wilson upper bound on the share is about
1.9%. Exact two-sided Fisher p: Seasoning 55/18,915 ≈ 0.0029; Seasoning+Food
C(57,5)/C(254,5) ≈ 0.00049. Four of the five case-investigation results at or above
2 ppm carry no brand (three homemade spices from India and one jaggery), so a product
recall could not reach them. The sealed run must reproduce these counts. If the portal has
changed since, the result note will say how.

## Limits, stated in advance

- Neither frame is a random sample. Case investigations test what a poisoned family
  uses. Surveys and events test what staff or residents choose to bring. The comparison
  answers "where does a test find lead", not "how common is lead in spices".
- King County's case-investigation set is small (11 seasoning results). Its "Food" type
  mixes spices with rice, flour and infant formula.
- NYC's `A` code is undefined in the metadata. It is reported, not interpreted.

## Files

`sampling_frame.py` (fetches both tables, writes snapshots, tables, tests and grades),
`test_sampling_frame.py` (offline unit tests: Fisher on Fisher's own tea example and on
the King County tables above, Wilson, parsers, grading).
