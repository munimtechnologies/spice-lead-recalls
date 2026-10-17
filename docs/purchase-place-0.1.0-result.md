# Is the home-versus-shelf gap an abroad-versus-here gap? Result of purchase-place 0.1.0

By MV2 of Munim, Inc. Prepared with AI agents. Text CC BY 4.0; code Apache-2.0.

**Status:** graded against [the pre-registration](purchase-place-0.1.0-prereg.md), which
was committed (in release v0.4.0) before any NYC result was split by purchase country.
Every prediction is reported, met or not. Sections 4 and 5 report the figures the
pre-registration listed as "reported without prediction", plus a short country and
product breakdown added after grading. They grade nothing.

## 1. What ran

`purchase_place.py` 0.1.0 reads only the committed snapshot
`data/nyc_spice_lead_snapshot_2026-10-17.csv` (NYC DOHMH *Metal Content of Consumer
Products*, `da9u-wz3r`, Food-Spice lead). It keeps exactly the rows `sampling_frame.nyc_rows`
keeps (3,575 laboratory results in ppm) and tags each with its purchase group:

- **US:** `purchase_country` is exactly `UNITED STATES`.
- **unknown:** blank, `UNKNOWN OR NOT STATED`, or `UNITED STATES MINOR OUTLYING ISLANDS`.
- **abroad:** any other value (58 distinct countries among 2016–2025 case results).

The table is `data/purchase_place.csv`. `test_purchase_place.py` recomputes it offline
and checks that the three groups add up exactly to the published
`data/frame_period_ladder.csv`. The counts were also tallied independently by
pattern-matching the snapshot, and a live aggregate query of the NYC table (17 October
2026) gave the same group sizes (771 US, 556 unknown, 1,118 abroad).

## 2. The five predictions (case-investigation results, 2016–2025)

| Group | Results | ≥ 2 ppm | ≥ 10 ppm | ≥ 50 ppm | ≥ 500 ppm |
|---|---:|---:|---:|---:|---:|
| C, bought in the US | 771 | 45 (5.8%) | 14 (1.8%) | 9 (1.2%) | 4 (0.52%) |
| C, purchase place unknown | 556 | 27 (4.9%) | 11 (2.0%) | 10 (1.8%) | 5 (0.90%) |
| C, bought abroad | 1,118 | 220 (19.7%) | 133 (11.9%) | 98 (8.8%) | 57 (5.1%) |
| S, store survey (all bought in the US) | 457 | 38 (8.3%) | 10 (2.2%) | 2 (0.44%) | 2 (0.44%) |

| # | Prediction | Observed | Verdict |
|---|---|---|---|
| P1 | C-US share ≥ 50 ppm at most 1.5% | 9 of 771 = 1.17% | met |
| P2 | C-abroad share ≥ 50 ppm at least 10% | 98 of 1,118 = 8.77% | **failed** (too low) |
| P3 | C-US share ≥ 2 ppm between 4% and 16% | 45 of 771 = 5.84% | met |
| P4 | At least 70% of C results ≥ 50 ppm are C-abroad | 98 of 117 = 83.8% | met |
| P5 | Fisher two-sided p < 0.001, C-abroad higher, at ≥ 50 ppm | p < 10⁻⁶ (8.8% vs 1.2%) | met |

**4 of 5 met.** I overestimated how often a spice bought abroad reaches 50 ppm: it is
8.8%, not 10% or more. The other four held. The exact Fisher p in P5 is pinned below
10⁻⁶ by the test, not quoted to more digits.

## 3. What it means

**Case-investigation spices bought in the US look like store-shelf spices.** At 2 and 10 ppm
they are, if anything, slightly *less* often positive than store-survey samples (5.8%
vs 8.3%, and 1.8% vs 2.2%). The 2 ppm difference is not significant: exact Fisher p is
about 0.1, and the test pins it between 0.03 and 0.3. At 50 ppm the US-bought case share
is 1.2% against 0.44% (9 vs 2 results). That is not significant either (p about 0.2,
pinned between 0.1 and 0.4).

Spices bought abroad are another matter. They are 2.4× as often ≥ 2 ppm as store-survey
samples (19.7% vs 8.3%, p < 10⁻⁵) and 20× as often ≥ 50 ppm (8.8% vs 0.44%).

So most of the home-versus-shelf gap found in
[sampling_frame 0.1.0](sampling-frame-0.1.0-result.md) (1.4× at 2 ppm and 10.9× at
50 ppm within 2016–2025) comes from where a spice was bought, not from being in a home.
For a health worker this means that "where was this bought?" is a strong triage
question on a home visit. It is not a safe filter on its own: US-bought and
unknown-origin spices still supplied 19 of the 117 case results ≥ 50 ppm (16%).

## 4. Reported without prediction

**Store surveys.** All 477 store-survey results (20 from 2011–2015 and 457 from
2016–2025) list the United States as the purchase country. This confirms the
assumption behind the comparison.

**C-unknown** (556 results in 2016–2025) behaves like C-US at low levels (4.9% ≥ 2 ppm)
and sits between C-US and C-abroad at 50 ppm (1.8%).

**2011–2015** (case results, n = 345; store surveys 20, of which 3 were ≥ 2 ppm and none ≥ 10):

| Group | Results | ≥ 2 ppm | ≥ 10 ppm | ≥ 50 ppm | ≥ 500 ppm |
|---|---:|---:|---:|---:|---:|
| C-US | 95 | 16 (16.8%) | 5 | 3 (3.2%) | 2 |
| C-unknown | 36 | 6 | 2 | 2 | 1 |
| C-abroad | 214 | 89 (41.6%) | 58 | 49 (22.9%) | 33 |

The early case results run hotter in every group, which matches the period effect
noted in sampling_frame 0.1.0.

## 5. Where the abroad results come from (descriptive, added after grading)

Case results from 2016–2025 by purchase country, for the four largest contributors of
results ≥ 50 ppm (all pinned in the test):

| Purchase country | Results | ≥ 50 ppm | Share |
|---|---:|---:|---:|
| Georgia | 157 | 49 | 31.2% |
| Bangladesh | 398 | 21 | 5.3% |
| Pakistan | 88 | 9 | 10.2% |
| India | 181 | 7 | 3.9% |

Spices bought in Georgia supply half of the abroad results ≥ 50 ppm (49 of 98), and
86 of their 157 results (55%) are ≥ 2 ppm. "GEORGIA" here is the country. 149 of those
157 rows also give Georgia as the country of manufacture, and the product names are
Georgian (svanuri marili, ajika, utskho suneli). This matches NYC's own advisory on
Georgian spices.

Of the 9 US-bought case results ≥ 50 ppm, five were made in Bangladesh (three of them,
with consecutive row IDs, were collected on 2020-02-14), one in India, and three give no origin. One of those
three is a Balqees Yemeni spice mix (600 ppm, 2018-12-05). The only two store-survey
results ≥ 50 ppm are the same brand's Yemeni spice mix, collected six weeks later. That
fits the documented practice of store surveys following up products implicated in cases.

## 6. Prior art and what is new

Hore et al. 2019 (*J Public Health Manag Pract* 25:S63; NYC 2008–2017, 1,496 samples)
already reported that spices bought abroad had higher mean lead than those bought in the
US. They named Georgia, Bangladesh, Pakistan, Nepal and Morocco, and reported that the
same spices (turmeric, Georgian kharcho suneli) averaged under 2 ppm when bought in NYC
and over 50 ppm when bought abroad. The direction of this result is therefore not new.

What this note adds is narrower. It holds purchase place fixed **across sampling frames**
and asks whether a case-investigation spice bought in the US differs from a store-survey
spice. On 2016–2025 data, after Hore's window, it does not detectably differ, at four
thresholds. The predictions were registered before the split, and the test reruns the
whole result from a committed snapshot. We found no earlier published comparison of this
kind.

## 7. Limits

- `purchase_country` is self-reported in a home interview, and Hore 2019 suspected at
  least one misreported "bought in the US" result. Misreporting abroad as US would make
  C-US look worse than it is, so it cannot explain C-US looking like the store survey.
- These are test results, not products or households. One household's collection can
  add several rows (three of the nine US-bought results ≥ 50 ppm share a date). Fisher's
  test assumes independent results, so every p value here is optimistic.
- Neither frame is a random sample. Store surveys follow up implicated products, and
  case investigations sample homes with a lead-poisoned resident.
- The 50 ppm comparison of C-US with S rests on 9 and 2 results. It cannot rule out a
  2–3× difference.
