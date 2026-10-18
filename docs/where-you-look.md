# What you see depends on where you look: eight frames on lead and adulteration in spice

*By MV2 of Munim, Inc. Prepared with AI agents. Text licensed CC BY 4.0; the code it
cites is Apache-2.0. This note adds no new data — it places eight already-published,
already-tested analyses from this repository side by side and reads across them. Every
number in the table is recomputed from committed CSVs by `test_where_you_look.py`.*

## The question

"How often is retail spice dangerously adulterated, and where does the danger come from?"
has no single answer. It has one answer per **sampling frame** — the rule that decided
which spices got measured in the first place. This repository has now graded eight
different frames against pre-registered predictions. Laid side by side they disagree so
sharply that the frame, not the spice supply, drives the headline. That disagreement is
the finding.

Throughout, **gross lead** means a measured lead concentration of **≥50 ppm** — the band
associated with clinical lead poisoning, not trace contamination.

## The eight frames

| # | Frame (source) | n | What it measures | Gross-lead rate (Pb ≥50 ppm) | Top origin | Georgia (country) visible? | Lead chromate *named*? |
|---|---|---|---|---|---|---|---|
| 1 | NYC — case, spice **bought abroad** (DOHMH) | 1,332 | Pb in a spice tied to a blood-lead case | **147 / 1,332 = 11.0%** | Georgia | **Yes** | No (Pb only) |
| 2 | NYC — case, spice **bought in US** (DOHMH) | 866 | same, US-purchased | 12 / 866 = 1.4% | United States | No | No |
| 3 | NYC — **store survey** (DOHMH) | 477 | Pb in spice bought off NYC shelves | 2 / 477 = 0.4% | United States | No | No |
| 4 | King County — seasoning + food (PHSKC) | 254 | Pb, case + community | 2 / 254 = 0.8% | not recorded | No | No |
| 5 | FDA **border list**, IA 99-42 / 28-13 | 48 firms | firms refused entry for lead | n/a — a firm list, no Pb values | India (14 firms) | 1 cinnamon firm (2026) | No |
| 6 | CFIA **spice authenticity** 2020-23 | 823 | fraud: added colour, allergen filler | 0 lead findings of 823 | India | No | **No (0 of 823)** |
| 7 | CFIA **red palm oil** 2019-21 | 104 | banned Sudan dyes | 2 / 104 = 1.9% Sudan IV (dye, not Pb) | Ghana (declared) | No | No |
| 8 | CFIA **retail spices** 2018-19 | 131 | Pb + Cr + chromate spot test | 0 / 131 gross; 6 / 131 ≥2 ppm | imports (mixed) | No | spot-tested; **0 confirmed** |

## Reading across the rows

**The gross danger is almost entirely in frame 1, and nowhere else.** The one frame that
looks at spice people carried home from a trip and that later turned up in a lead-poisoning
investigation shows an 11% gross-lead rate — more than twenty-six times the rate in the
store survey (frame 3) that samples the same city's shelves. Frames 2, 3, 4 and 8 — every
frame built on commerce, retail or routine surveillance — sit below 1.5%. If you only run
a store survey or a surveillance programme, you will conclude spice lead is rare. If you
only read clinical case reports of spice bought abroad, you will conclude it is common.
Both are true of their frame; neither is true of "spice."

**The top origin flips with the frame too.** The gross-lead frame (1) points at the country
of Georgia, whose ground spice blends have repeatedly carried extreme lead. But Georgia is
invisible to every commerce-facing frame: it is not the top origin in any of frames 2–8, and
it appears on the FDA border list only as a single *cinnamon* firm added in 2026 — not the
ground blends that drive frame 1. A border list keyed to cinnamon and cassia (frames 5 and 6
are both led by cinnamon/India) cannot surface a hazard that travels in checked luggage.

**None of the eight frames confirms lead chromate.** This is the quietest and most important column.
Lead chromate is the adulterant everyone worries about — bright-yellow pigment added to
turmeric. Yet across 823 authenticity samples (frame 6) it is named **zero** times; across
131 chromate-tested retail spices (frame 8) eight samples gave a positive chromate *spot
test* and the regulator cleared **all eight**; and the case frames (1–4) measure only total
lead, from which lead chromate can be inferred but never proven. What the authenticity frame
*does* catch instead is mundane fraud — allergen fillers (peanut in cumin, gluten in pepper)
outnumber colour failures, and the five colour failures are ordinary synthetic dyes
(Sunset Yellow, tartrazine-class), four in turmeric and one in Iranian cinnamon, none from
South Asia. The dye target of the pocket screen shows the same shape in frame 7: just two
Sudan IV positives in 104 red palm oils, both declared Nigerian. (A ninth CFIA survey, which
has no open per-sample file, *does* name lead chromate, at trace lead. See the addendum below.)

## Why this is worth saying

The practical lesson for anyone screening spice — a health department, an importer, a
pocket-Raman project like this one's — is that **the sampling frame is a design decision with
as much leverage as the instrument.** A screen deployed at the border (frame 5) or in a
retail audit (frames 3, 6, 8) is, by construction, blind to the gross-lead pathway that
actually poisons people (frame 1). Covering that pathway means sampling where it lives:
spice brought back from travel, screened at the clinic or the community level, not only at
the shelf. The eight frames are not contradictory measurements of one number; they are eight
different numbers, and the honest report names which one it is quoting.

## Reproduce

```
python -m unittest -v test_where_you_look.py
```

The test reads only committed CSVs in `data/` and recomputes every value in the table above:
`purchase_place.csv` (frames 1–3), `frame_yield.csv` (frames 3–4), `ia9942_lead_spice_firms.csv`
(frame 5), `cfia_spice_auth_rows.csv` (frame 6), `red_palm_dyes_sealed_samples.csv` (frame 7),
`cfia_chromate_2018_samples.csv` (frame 8). Each underlying frame has its own pre-registration
and result note under `docs/` and in the releases from v0.4.0 to v0.4.13; this note only joins
them. The "Georgia #1" and origin-trend claims are carried from the graded Georgia-trend
result and `data/georgia_trend_by_year.csv`.

## Limits

These are observational surveillance and case datasets with uneven origin recording (frame 4
records no origin; frames 1–3 record a purchase place, not always a country). Rates are not
age- or exposure-adjusted and the frames cover different years, regions and products, so the
cross-frame comparison is qualitative: it shows that the *frame* changes the answer, not that
any two rates are directly comparable. "Lead chromate named" counts explicit regulatory
findings, not inference from a Pb:Cr ratio. Full methods and deviations are in each frame's
own note.

## Addendum (2026-10-17, v0.4.15): two more CFIA frames, from CFIA's reports

The first version of this note said "no frame actually confirms lead chromate". That was true
of the eight frames in the table, but too broad. CFIA ran a **second** lead chromate survey,
and it does name the pigment. Neither frame below has a committed per-sample file, so the
test does not cover their numbers. They are quoted from CFIA's own pages (checked 2026-10-17).

| # | Frame (source) | n | What it measures | Result (CFIA's words and figures) | Lead chromate *named*? |
|---|---|---|---|---|---|
| 9 | CFIA **Lead Chromates in Spices**, April 2019 to March 2021 (final report; no open per-sample file found) | 132 (cumin 23, ginger 23, mustard 18, blends 46, turmeric 22; 80 imported, 8 domestic, 44 origin unknown) | Pb, total Cr, colorimetric chromate test | lead not detected to **1.84 ppm** (mean 0.31); chromium up to 10.58 ppm; no health risk, no recalls | **Yes: 2 ground gingers**, "potential adulteration" (Pb:Cr in lead chromate's ratio *and* chromate-positive) |
| 10 | CFIA **Non-Permitted Colours in Spices** 2019-20 (open.canada.ca c2003a7b) | 63 red spices (paprika, sumac, chili, cayenne) | Sudan I-IV and other non-permitted colours | "none ... found to contain detectable amounts" | n/a (dyes) |

**What frame 9 changes.** It is the one place in these sources where a regulator names lead
chromate in retail spice, and it did so at **trace** lead. No sample in that survey exceeded
1.84 ppm lead. That is 27 times below the gross band used above (≥50 ppm), and about 1,700 times
below the ~3,200 ppm lead (0.5% w/w lead chromate) at which bench Raman sees the pigment in
turmeric powder. CFIA's three-criteria test can find lead chromate at levels no field screen
reaches, and at those levels it was not a health risk. The reading of the table holds:
the gross, poisoning-level lead chromate is in frame 1, not in Canadian or U.S. retail.
The sentence that needed correcting was the claim that no regulator ever named the pigment.

**What frame 10 adds.** CFIA's Sudan-dye survey of red spices found nothing, while the same
programme found Sudan IV in Nigerian-declared red palm oil (frame 7). Whether 0 of 63 means
"clean" or "not looking where the dye is" depends on the declared origins sampled. That
question is pre-registered in `docs/sudan-spices-0.1.0-prereg.md` and will be graded from the
open file, which no one has yet read for this analysis.

Sources: inspection.canada.ca, "Lead Chromates in Spices – April 1, 2019 to March 31, 2021"
(Food chemistry – Targeted surveys – Final report; page modified 2023-07-18; Government of
Canada Publications A104-386/2023E-PDF); open.canada.ca dataset
c2003a7b-9ca8-46cd-ba83-ecafd1c8569c. Contains information licensed under the Open Government
Licence - Canada.

## Addendum 2 (2026-10-18, v0.4.25): three more graded CFIA frames — a dye, a mould toxin, an authenticity marker

Since the v0.4.15 addendum, three more CFIA surveys have been graded against pre-registered
predictions and shipped from this repository, each with its own committed per-sample file and
offline test (releases **v0.4.22**, **v0.4.23**, **v0.4.24**). The figures below are quoted
from those result notes, not recomputed by `test_where_you_look.py`; each note holds the full
predictions, deviations and limits. These frames do not look for lead, but read through the
same lens they extend the central pattern rather than break it.

| # | Frame (source, release) | n | What it measures | Headline | Declared-origin pattern |
|---|---|---|---|---|---|
| 11 | CFIA **Food Colours** in essences/oils/sweets/processed vegetables 2018-19 (v0.4.22) | 399 | 43 colours, incl. non-permitted dyes | **1** Rhodamine B hit (10.8 ppm) + 2 trace Orange II; 181/399 carried any colour | the one Rhodamine B sample is a pickled vegetable declared **Lebanon**; all 23 palm oils (incl. 5 West African) clean of Sudan dyes |
| 12 | CFIA **Ochratoxin A** in selected foods 2012-2022 (v0.4.23; parse gate failed, figures exploratory) | 714 "Spice -" | mould toxin OTA vs EU limits | 106/714 over the EU limit; survey max **1,770 ppb** in a paprika | **77%** of over-limit spices declare no origin; every Hungarian paprika over (4/4), Spain 6/15 |
| 13 | CFIA **Coumarin** in cinnamon 2011-2016, pooled (v0.4.24) | 176 cinnamon | coumarin → cassia vs true cinnamon | **168/176 (95.5%)** cassia-type | 17/17 samples declaring Indonesia/Vietnam/China are cassia; Sri Lanka-declared 4/6 true cinnamon, one ground sample at **4,717 ppm** |

**The dye frame repeats the Sudan-IV shape.** Frame 7 found Sudan IV only in red palm oil
declared Nigeria — a product-origin pair with a long public record of that dye. Frame 11 adds
the single non-permitted dye in a 399-sample colour survey: Rhodamine B in a pickled vegetable
declared **Lebanon**, the same product family and country whose own authorities were
prosecuting Rhodamine B in pickled turnips that very autumn (RASFF 2018.2883; Lebanon's
Ministry of Public Health, December 2018). Neither hit came from a survey aimed at that origin,
and the same colour survey sampled five West African palm oils and found them clean. The dye
the pocket screen targets keeps appearing as one sample that matches an alert already public
abroad — not as a retail-wide rate.

**Two non-lead frames show the same origin blindness.** Ochratoxin A (frame 12) and coumarin
(frame 13) are not lead, but the frame decides the headline just as plainly. The OTA tail is
not spread across spices: it concentrates in paprika and nutmeg, and among the few over-limit
spices that declare a country, Hungarian paprika is 4 of 4 over the EU limit — while 77% of
the over-limit spices declare no origin at all. Coumarin cleanly separates cassia from true
cinnamon, and 95% of Canadian retail cinnamon is cassia; every sample declaring a
cassia-growing country is cassia without exception, and the "Sri Lanka" samples are mostly —
not always — true cinnamon (one ground sample reached a cassia-level 4,717 ppm). In each
frame the signal that can be pinned to an origin fits a known product-origin pairing, while
the majority of samples carry no declared origin, so the frame still sets what can be said.

**What does not change.** These three frames add no lead and no confirmed lead chromate. They
sharpen the central claim: across now thirteen data frames, the adulteration that can be
*located* travels with a specific product from a specific place that had a prior public alert —
Georgia ground blends (frame 1), Nigerian palm oil (frame 7), Lebanese pickles (frame 11),
Hungarian paprika (frame 12) — while broad retail surveys, where most samples name no origin,
report low rates and cannot see that pathway. The honest screen names its frame.

Caveats carried from the notes: frame 12's parse gate failed, so its figures are exploratory
under a post-hoc rule (CFIA's own "Spice -" product prefix), and its origin counts are small
(4 Hungarian paprikas). Neither OTA nor coumarin breaches Canadian law in these foods — Canada
sets no OTA limit for spices and no coumarin limit for cinnamon; the EU limits are a yardstick
only. A declared origin is a label (often the packer's country), not verified provenance, and
"no origin" means the open file carries none. CFIA and Health Canada judged none of these
surveys a health concern.

Sources: open.canada.ca datasets 1b0c4141-7a22-4c93-8679-63eb49f7be24 (food colours 2018-19),
37300d06-0887-4353-bc9b-4f030f1089a2 (ochratoxin A 2012-2022), and CFIA's coumarin surveys
2011-12 to 2015-16; full result notes `docs/food-colours-2018-0.1.0-result.md`,
`docs/ota-spices-0.1.0-result.md` and `docs/coumarin-cinnamon-0.1.0-result.md`. Contains
information licensed under the Open Government Licence – Canada.
