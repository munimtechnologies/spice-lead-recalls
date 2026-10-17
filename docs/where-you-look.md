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

**No frame actually confirms lead chromate.** This is the quietest and most important column.
Lead chromate is the adulterant everyone worries about — bright-yellow pigment added to
turmeric. Yet across 823 authenticity samples (frame 6) it is named **zero** times; across
131 chromate-tested retail spices (frame 8) eight samples gave a positive chromate *spot
test* and the regulator cleared **all eight**; and the case frames (1–4) measure only total
lead, from which lead chromate can be inferred but never proven. What the authenticity frame
*does* catch instead is mundane fraud — allergen fillers (peanut in cumin, gluten in pepper)
outnumber colour failures, and the five colour failures are ordinary synthetic dyes
(Sunset Yellow, tartrazine-class), four in turmeric and one in Iranian cinnamon, none from
South Asia. The dye target of the pocket screen shows the same shape in frame 7: just two
Sudan IV positives in 104 red palm oils, both declared Nigerian.

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
