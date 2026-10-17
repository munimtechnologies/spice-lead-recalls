# spice-lead-recalls

How much lead do contaminated spices carry, and how much of it could a fast field screen (Raman) see? Three public
sources:

1. **U.S. FDA food recalls** for lead in spices, from openFDA's food enforcement data (`lead_recalls.py`).
2. **NYC Health Department lab results**: 3,575 spice lead tests and 61 spice chromium tests from New York City's
   lead-poisoning investigations and store surveys, 2011-2025 (`nyc_spice_lead.py`, new in 0.2.0). Each pair that
   looks like lead chromate is also checked against the chromium the spice could carry naturally (`cr_baseline.py`,
   new).
3. **Public Health - Seattle & King County lab results** for spices from community testing events and case
   investigations, 2019-2026, used with NYC's to ask how low a screen must reach (`lod_curve.py`, new in 0.3.0).

Section 4 adds a sampling model (`spot_sampling.py`): how many small Raman spots a screen needs when the pigment
sits in grains, applied to the same lab data.

By MV2 of Munim, Inc. Code Apache-2.0; derived data CC BY 4.0. openFDA data are public domain (CC0). NYC data:
NYC Open Data, NYC Department of Health and Mental Hygiene (DOHMH). King County data: King County Open Data, Public
Health - Seattle & King County. This analysis is not endorsed by either agency.
The code, data runs and write-up were made with AI agents working in MV2's name.

## Pre-registered follow-ups (0.3.2 onward)

Since 0.3.2 most new work here is pre-registered. The predictions are committed in one release, before the data
that grades them is read, and the result follows in a later release, with failures reported as failures.
[`docs/analyses-index.md`](docs/analyses-index.md) lists every note. The main results so far:

- **The natural-chromium check holds up.** 30 of the 32 robust lead-chromate verdicts in section 2 survive a 2-fold
  error in every natural-chromium ceiling, and 24 survive a 10-fold error (cr-ceiling-stress).
- **Gross lead comes from spices bought abroad.** NYC case-investigation spices bought in the U.S. were at or above
  2 ppm lead about as often as store-survey spices (5.8% against 8.3%, 2016-2025). Spices bought abroad were 20
  times as likely as store spices to reach 50 ppm (purchase-place).
- **The post-2020 fall is citywide.** Georgia-bought case spices at or above 50 ppm fell from 49 of 141 (2016-2020)
  to 0 of 16 (2021-2025), but the pre-registered Bangladesh control and every other group fell too, so NYC's data
  alone cannot credit Georgia (georgia-trend). Since 2023 most case records leave the purchase country blank
  (purchase-recording), and a one-page note for lead-program staff asks them to record it
  ([`docs/ask-where-bought.md`](docs/ask-where-bought.md)).
- **FDA's border list fell too, and listed no Georgian firm in 2016-2020.** Its lead-in-spice listings moved from
  Import Alert 28-13 to 99-42 around October 2022, so a trend read from 99-42 alone shows an artificial jump
  (ia9942-lead-spice).
- **Waiting for a grade:** Canada's spice authenticity surveillance, 2020-2023 (cfia-spice-auth); Canada's 2018-19
  survey of clean retail spices, used to test whether the chromate screen stays quiet (cfia-chromate-2018); and
  banned Sudan dyes in red palm oil sold in Canada, by declared origin (red-palm-dyes).

The Raman limit used throughout comes from Erasmus et al. 2021, the first study of FT-Raman for lead chromate in
turmeric: limit of detection 0.6% w/w (840 cm-1 peak) and 0.5% (PLS model). PbCrO4 is 64.1% lead by mass, so 0.5% w/w
is about **3,206 ug/g (ppm) lead**.

## 1. FDA recalls (openFDA export of 2026-10-13, 29,485 enforcement records)

| | count |
|---|---|
| Recalls whose reason names lead | 179 (119 recall events) |
| ... of a spice or a food with a named spice in it | 75 (58 events) |
| ... where FDA's text states a lead level | **12** |
| ... at or above ~3,206 ppm lead (0.5% w/w lead chromate) | **0** |

The stated levels run from 0.012 ppm (a ginger candy) to 53.7 ppm (median 2.66 ppm). The highest, 53.7 ppm in PRAN
turmeric powder from Bangladesh (2013), is **about 60 times below** the Raman limit. The authors of the Raman study
already warned that their limit is "above the highest levels found in practice". This dataset puts numbers on that
for U.S. recalls.

> **Correction (2026-10-16).** Version 0.1.0 counted 11 stated levels, from 0.065 to 53.7 ppm (median 2.92 ppm). It
> missed F-0077-2014, where FDA wrote ".012 ppm" with no leading zero. `lead_recalls.py` 0.1.1 reads it, and the
> counts above are from its run on the same export (15 offline tests passed). The headline does not change: no
> stated level reaches the Raman limit.

### The same picture from FDA's other public numbers (not in openFDA's text)

| source | lead in the spice | at or above ~3,206 ppm? |
|---|---|---|
| FDA ground-cinnamon public health alert, 2024-2025 (18+ brands) | 2.03 - 10.7 ppm; El Servidor 20 ppm | no |
| FDA/Ecuador, cinnamon behind the 2023 WanaBana applesauce outbreak (566 cases, CDC) | 2,270 and 5,110 ppm | **one of two samples** |
| CFIA survey, 132 yellow/brown spices, 2019-2021 (2 ginger samples chromate-positive) | all samples <= 1.84 ppm | no |
| Bangladesh turmeric (Forsyth et al. 2019) | up to 1,152 ug/g | no |
| Eastern India, 503 samples 2021-23 (npj Sci Food 2026) | up to 6,416 ug/g | the top of the range |

## 2. NYC Health Department lab results (new in 0.2.0)

NYC DOHMH publishes every consumer product it has tested for metals ("Metal Content of Consumer Products Tested by
the NYC Health Department", https://data.cityofnewyork.us/d/da9u-wz3r, rows updated 2026-06-22). Spices are the
largest group. The counts below were first read from NYC's own API on 2026-10-14. `nyc_spice_lead.py` 0.3.0 then
recomputed every one of them from the raw rows (run of 2026-10-15, 9,520 rows, 13 offline tests passed), and all of
them matched. Its outputs are in [`data/nyc_summary.md`](data/nyc_summary.md),
[`data/nyc_summary.json`](data/nyc_summary.json), [`data/nyc_spice_lead.csv`](data/nyc_spice_lead.csv) and
[`data/nyc_spice_pb_cr_pairs.csv`](data/nyc_spice_pb_cr_pairs.csv).

### Lead: who could a Raman screen help?

| how the sample was obtained (NYC code) | spice lead tests | >= 2 ppm | >= 1,000 ppm | >= 3,206 ppm | highest |
|---|---|---|---|---|---|
| S | 477 | 41 | **0** | **0** | 610 ppm |
| C | 2,790 | 403 | 72 | 32 | 78,000 ppm |
| A | 308 | 93 | 26 | 14 | 27,000 ppm |
| all | 3,575 | 537 | 98 | **46** | 78,000 ppm |

NYC's description says products come from lead-poisoning investigations and store surveys. Hore et al. 2019 (NYC
DOHMH) describe the same three sources: cases among children, cases among adults, and store surveys. The S samples are
shop brands bought in New York (for example the 2024 cinnamon sweep), so S is the store survey. C and A are
case-investigation samples, mostly brought from abroad. NYC's data dictionary defines the codes, and the next data run
saves it.

- In **477 store-survey samples, nothing came within 5x of the Raman limit**. That matches the FDA recalls (0 of 12).
- The **46 samples at or above it all came from case investigations**. 35 of them are Georgian spice blends (khmeli
  suneli, "yellow flower"/zaprana marigold, svanuri marili, ajika), found by name or country of purchase. The other
  11 were bought in Pakistan (4), Russia (2), Algeria, Morocco, Uzbekistan and Ecuador (1 each), plus a curry powder
  bought in the U.S. (21,000 ppm).
- Of 1,438 spice samples bought in the U.S., 2 reach the limit. Both are from case investigations, not store surveys.

So bulk Raman on powder is a tool for the extreme tail that public-health staff meet in homes. These spices are
often carried in from abroad, where the pigment was added by the kilo. It is not a tool for shelf screening of the
U.S. retail market.

### Chromium: is it lead chromate? (a first look at NYC's paired results)

Lead chromate (PbCrO4) holds one lead atom per chromium atom, so a **molar Pb:Cr ratio near 1** marks it. The test
comes from Forsyth et al.: Bangladeshi turmeric pigments averaged 1.3 (2019), and South Asian turmeric with more than
18 ug/g lead sat near 1:1 (2024). NYC also tested 61 spices for chromium. We paired each one with the lead result for
the same product: same name, collection date, purchase country and investigation code. Lead and chromium are NYC's
own lab numbers. The ratio is (Pb/207.2)/(Cr/51.996).

Of the **39 pairs with at least 18 ppm lead, 34 have a molar Pb:Cr ratio between 0.81 and 1.78 (median 1.16)**, which
fits lead chromate pigments (PbCrO4 = 1; chrome yellows cut with lead sulfate run above 1). The other 5 do not fit:
Eritrean berbere (220 ppm lead), Malian fa powder (240) and Moroccan hot paprika (23) had no detectable chromium, so
their lead has another source. A Guyanese five-spice powder (40 ppm Pb, 1 ppm Cr) and El Servidor cinnamon (23 ppm Pb,
1.8 ppm Cr) had far more lead than chromate would carry.

| NYC rows (Pb/Cr) | collected | code | spice | bought in | Pb ppm | Cr ppm | molar Pb:Cr |
|---|---|---|---|---|---|---|---|
| 5235/5234 | 2020-09-25 | C | TMT Khmeli Suneli | Georgia | 78,000 | 15,000 | 1.30 |
| 2376/2375 | 2017-07-18 | C | Georgian saffron (zaprana) | Georgia | 48,000 | 12,000 | 1.00 |
| 2193/2192 | 2017-04-07 | C | Yellow flower | Georgia | 22,000 | 4,100 | 1.35 |
| 2380/2379 | 2017-07-19 | A | Hviteli Hvavili | Georgia | 21,000 | 4,500 | 1.17 |
| 1776/1775 | 2016-08-16 | C | No name seasoning | Russia | 17,000 | 3,700 | 1.15 |
| 2052/2051 | 2017-02-02 | C | Orange spice | Georgia | 13,000 | 3,100 | 1.05 |
| 2325/2324 | 2017-06-28 | C | Khneli suneli | Georgia | 11,000 | 2,000 | 1.38 |
| 2195/2194 | 2017-04-07 | C | All purpose soup base powder | Georgia | 9,600 | 1,800 | 1.34 |
| 1778/1777 | 2016-08-16 | C | Saffron | Russia | 8,000 | 1,600 | 1.25 |
| 872/871 | 2013-08-15 | C | Xarcho Sunely | Georgia | 7,100 | 1,400 | 1.27 |
| 814/813 | 2013-06-27 | C | Green spices | Pakistan | 7,100 | 1,400 | 1.27 |
| 5263/5262 | 2020-10-19 | C | Cumin powder | Uzbekistan | 6,700 | 1,300 | 1.29 |
| 2958/2957 | 2018-09-24 | A | Paprika | Algeria | 5,800 | 1,200 | 1.21 |
| 3494/3493 | 2019-02-21 | C | Cumin | Ecuador | 4,700 | 1,200 | 0.98 |
| 2604/2603 | 2018-01-06 | C | Marili spice mix powder | Georgia | 4,300 | 910 | 1.19 |
| 1244/1243 | 2015-01-29 | C | Svaneti salt | Georgia | 4,100 | 880 | 1.17 |
| 1641/1640 | 2016-05-04 | C | Uckho Suneli | Georgia | 3,500 | 740 | 1.19 |
| 2219/2218 | 2017-04-24 | C | Turmeric spice powder | Nepal | 2,700 | 640 | 1.06 |
| 4400/4399 | 2019-09-11 | C | Khmeli Suneli | Georgia | 2,500 | 500 | 1.25 |
| 3034/3033 | 2018-10-20 | C | Raz El Hanout | Algeria | 2,200 | 310 | 1.78 |
| 2385/2384 | 2017-07-19 | A | Svanuri Marili | Georgia | 2,000 | 500 | 1.00 |
| 4686/4685 | 2019-11-19 | C | Turmeric | India | 2,000 | 460 | 1.09 |
| 702/701 | 2013-02-14 | C | Cinnamon powder | Bangladesh | 880 | 220 | 1.00 |
| 3254/3253 | 2019-01-15 | **S** | Yemeni spices mix (packaged brand) | U.S. (NYC shop) | 610 | 140 | 1.09 |
| 3227/3226 | 2019-01-15 | **S** | Yemeni spices mix (packaged brand) | U.S. (NYC shop) | 570 | 130 | 1.10 |
| 704/703 | 2013-02-14 | C | Cumin powder | Bangladesh | 560 | 120 | 1.17 |
| 1234/1233 | 2015-01-20 | C | Curry powder | Bangladesh | 530 | 140 | 0.95 |
| 2231/2230 | 2017-05-03 | C | Curry masala | Pakistan | 300 | 69 | 1.09 |
| 2156/2155 | 2017-03-23 | C | Spice mix | Bangladesh | 170 | 38 | 1.12 |
| 1371/1370 | 2015-03-18 | A | Chili powder | Bangladesh | 110 | 34 | 0.81 |
| 707/706 | 2013-02-14 | C | Black pepper | Bangladesh | 85 | 21 | 1.02 |
| 2290/2289 | 2017-06-07 | A | Coriander powder | Bangladesh | 52 | 12 | 1.09 |
| 3282/3281 | 2019-01-22 | A | Coriander | Georgia | 51 | 9.1 | 1.41 |
| 2968/2967 | 2018-09-24 | A | Turmeric | Algeria | 20 | 6.1 | 0.82 |

What this adds:

- **The chromate signature reaches well past turmeric and Georgia.** It shows up in cumin from Ecuador (2019),
  Uzbekistan and Bangladesh, paprika and raz el hanout from Algeria, Russian seasonings, Bangladeshi cinnamon, black
  pepper and coriander, and two samples of a Yemeni spice mix sold in a New York shop. The Ecuadorian cumin is worth
  noting: it is one sample, from four years before chromate-laced cinnamon processed in Ecuador poisoned U.S.
  children through WanaBana applesauce (2023).
- **Half of the chromate-like samples are out of a powder Raman screen's reach.** Only 17 of the 34 hold 3,206 ppm
  lead or more. The other 17 (20-2,700 ppm lead) contain the pigment, but too dilute to see in bulk powder. Finding
  them needs particle-level methods (Raman microspectroscopy on isolated yellow-orange grains, as FDA used on
  cinnamon), XRF or a lab.

Limits: NYC chose which samples to test for chromium (61 of 3,575 spices), probably ones already suspected, so 34 of
39 is not a rate for spices in general. A ratio near 1 fits lead chromate but does not prove it; only a structural
method (Raman, XRD) does. Natural chromium can matter below about 18 ppm lead, so those pairs are left out; the next
part checks the chromate-like pairs that carry little chromium. Pairing by name and date was checked by hand for
every row above.

### Could the spice's own chromium explain the ratio? (new: `cr_baseline.py`)

The ratio test treats all of a sample's chromium as coming with the lead. Plants carry some chromium of their own,
and taking a natural background off the measured chromium raises the ratio. A pair leaves the 0.7-2 band once that
background passes

    edge = Cr - (Pb / 207.2) / 2 x 51.996   (ppm)

`cr_baseline.py` compares each chromate-like pair's edge with the highest natural chromium published for that spice,
by analytical method ([`data/natural_cr_ceilings.csv`](data/natural_cr_ceilings.csv); every value was read from the
paper's own table). Blends and spices with no row of their own use a generic ceiling of 8.59 ppm, the highest
single-spice value in the ICP-MS surveys used (cumin, Ghuniem et al. 2025). A spice's own ceiling always replaces
the generic one. A pair is **robust** if its edge is above every ceiling for its spice, **unresolved** if it is
above some and not others, and **background-limited** if it is above none.

- **28 of the 34 pairs hold 69 ppm chromium or more.** Their edges are all 31 ppm or more, above every ceiling in
  the table (the highest is 18.9 ppm, coriander by flame AAS), so natural chromium cannot explain any of them.
- **Of the 6 with less chromium, 4 are robust**: Algerian turmeric, Bangladeshi black pepper, chili powder and a
  spice mix (table below).
- **Both coriander pairs are unresolved, and the split follows the method.** Their edges (2.7 and 5.5 ppm) are
  above the two ICP-MS values for coriander (0.13 ppm, whole seed from India, Cicero et al. 2022; 0.91 ppm, Bulgaria,
  Voica et al. 2021) but below the ICP-OES value (12.45 ppm, an aqueous seed extract, Gazwi et al. 2022) and the
  flame AAS values (10.8-18.9 ppm, Ethiopian market seed, Tefera & Teklewold 2021). If ICP-MS gives the true
  background, both are lead chromate; if the other methods do, their chromium may be natural and only their lead
  (51-52 ppm) is a finding. The lead stands either way.

| NYC rows (Pb/Cr) | collected | spice | bought in | Pb ppm | Cr ppm | molar Pb:Cr | edge ppm | ceilings for that spice (ppm) | verdict |
|---|---|---|---|---|---|---|---|---|---|
| 3282/3281 | 2019-01-22 | Coriander | Georgia | 51 | 9.1 | 1.41 | 2.70 | 0.129, 0.912 (ICP-MS); 12.45 (ICP-OES); 18.93 (FAAS) | **unresolved** |
| 2968/2967 | 2018-09-24 | Turmeric | Algeria | 20 | 6.1 | 0.82 | 3.59 | 1.9 (ICP-MS) | robust |
| 2290/2289 | 2017-06-07 | Coriander powder | Bangladesh | 52 | 12 | 1.09 | 5.48 | as for coriander above | **unresolved** |
| 707/706 | 2013-02-14 | Black pepper | Bangladesh | 85 | 21 | 1.02 | 10.33 | 0.096, 0.113 (ICP-MS) | robust |
| 2156/2155 | 2017-03-23 | Spice mix | Bangladesh | 170 | 38 | 1.12 | 16.67 | 8.59 (generic, ICP-MS) | robust |
| 1371/1370 | 2015-03-18 | Chili powder | Bangladesh | 110 | 34 | 0.81 | 20.20 | 3.17 (ICP-MS) | robust |
| 2231/2230 | 2017-05-03 | Curry masala | Pakistan | 300 | 69 | 1.09 | 31.36 | 3.55 (ICP-MS) | robust |

Turmeric shows why the generic ceiling must not replace a spice's own: against 8.59 ppm the Algerian turmeric would
look background-limited, but every turmeric in the ICP-MS survey used held 1.9 ppm or less.

Coriander is the one spice here where published natural chromium spans the chromate signal, and the spread is
between methods (0.1-0.9 ppm by ICP-MS, 10-19 ppm by ICP-OES and flame AAS) more than between samples. Flame AAS and
ICP-OES are known to read chromium high in plant digests, but two ICP-MS samples cannot settle it. Settling a lead
chromate claim on coriander needs a chromium blank measured by ICP-MS on clean coriander of the same origin. We have
not found a published Pb:Cr chromate test that subtracts a spice-specific natural chromium ceiling.

Limits: the ceilings are the highest values in small published surveys (1-40 samples per spice), not limits for any
one sample, and the coriander ICP-MS values rest on two samples. NYC reports total chromium as sold; the papers
report dry weight or do not say. The edge uses the top of the band (2.0) and ignores each lab result's own
uncertainty. "Robust" means natural chromium cannot explain the ratio, not that the pigment is proven.
`test_cr_baseline.py` checks the seven pairs above against the shipped table. The per-pair results for all 34 are in
[`data/cr_baseline.md`](data/cr_baseline.md), [`data/cr_baseline.json`](data/cr_baseline.json) and
[`data/cr_baseline.csv`](data/cr_baseline.csv), from a sealed run on the live NYC pairs (pairs sha256 `0dd4a2c4685d`,
ceilings sha256 `b97b469d8006`): 34 chromate-like pairs, 32 robust and the 2 coriander pairs unresolved.

### Georgia: did its crackdown reach New York homes?

Georgian blends are 35 of NYC's 46 spices above the Raman limit. Georgia's food-safety authority has paid closer
attention to lead in spices since 2018, and Forsyth et al. (2024) measured the result inside Georgia: across 765
bazaar samples from 29 cities in three rounds, the highest lead fell from over 14,000 ug/g in 2020 to 36 ug/g in
the last round of 2022. NYC's case investigations give a check from outside the country: spices that families carried
from Georgia into New York homes where someone had high blood lead.

> **Correction (2026-10-15).** The first version of this check counted only spices whose purchase country NYC
> recorded as Georgia, and said none since 2021 reached 100 ppm. That was wrong. Since 2023 NYC leaves the purchase
> country blank ("UNKNOWN OR NOT STATED") for about half of its case spices (see "Where the hot spices come from
> now" below). One June 2024 investigation with no recorded country held a "Georgian chilli powder" at
> **12,700 ppm** lead and two "utskho suneli / yellow flower" samples at 146 and 1,010 ppm. The earlier text also
> gave that 12,700 ppm sample as proof that spices from *other* countries still arrived hot. The table below now
> counts spices bought in Georgia **plus spices with a Georgian name and no recorded purchase country**.

| NYC case-investigation spices (codes C and A) | collected | samples | >= 100 ppm lead | highest | investigations (collection dates) | ... with a spice >= 100 ppm |
|---|---|---|---|---|---|---|
| Georgian (bought there, or Georgian name, country not recorded) | 2011-2020 | 269 | 90 (33%) | 78,000 ppm (2020) | 78 | 53 (68%) |
| Georgian (same rule) | 2021-2024 | 22 | **3** (all one visit) | 12,700 ppm (June 2024) | 6 | **1** |
| everything else | 2011-2020 | 1,524 | 86 (5.6%) | 21,000 ppm | | |
| everything else | 2021-2025 | 1,283 | 9 (0.7%) | 5,400 ppm (Morocco, 2024) | | |

- Bought in Georgia (as NYC recorded it), the picture is as first reported: 16 spices from 4 investigations since
  2021 (March 2021, February and December 2022, June 2024), all at 3.5 ppm or less, including the marigold "yellow
  flower" (kviteli kvavili) that carried most of the pigment before: 1.4 ppm in 2021 and not detected in 2024.
- But Georgian blends with no recorded origin did not all come clean. On 2024-06-24 one case investigation (NYC rows
  8065-8068) found a Georgian chilli powder at 12,700 ppm (about 2% w/w lead chromate if all the lead is chromate,
  four times the bench Raman limit) and an utskho suneli / yellow flower blend at 1,010 and 146 ppm (a third sample
  7.3 ppm). Where these were bought is not recorded. A September 2024 visit (green ajika, plum sauce) found no
  detectable lead.
- The fall is still large: 53 of 78 earlier investigations found a Georgian spice at 100 ppm or more, against 1 of 6
  since 2021. If the 6 later investigations had been drawn at random from all 84, the chance of 1 or fewer hot ones
  is about 2% (hypergeometric). The pigment has not gone, though: the June 2024 Georgian chilli powder is the most
  leaded case spice in NYC's data for 2021-2025.
- The rule adds one earlier visit too: an April 2014 investigation (code A) with seven Georgian-named spices and no
  recorded country, including Svanetian salt at 4,400 ppm and dry ajika at 3,400 ppm.

What it does not show: NYC's case spices from other countries also fell at 100 ppm or more (5.6% to 0.7%), so part
of the change may be in what NYC samples, and this data alone cannot prove a Georgia-only effect. Almost half of the
earlier hot "everything else" samples (43 of 86) were bought in Bangladesh, which had its own crackdown (next
section); without Bangladesh the rest fell from 43 of 1,177 (3.7%) to 8 of 1,123 (0.7%). Six investigations is a
small number, and a collection date stands in for one household visit. Georgian names were matched by hand-checked
words (suneli, khmeli, utskho/ucxo, svanuri/svan, marili, kvavili/yvavili, yellow flower, ajika/adjika, kharcho,
zaprana, tkemali, "Georgian"); a Georgian spice with a generic name and no recorded country is still missed. The
result agrees with Forsyth et al.'s in-country fall, with one heavily laced exception in 2024. We found no earlier
check of that result from a destination country's lab data.

These counts were read from NYC's API on 2026-10-15 (SoQL). `nyc_spice_lead.py` 0.3.0 (`georgia_trend`) counts by
recorded purchase country only, so the Georgia table in [`data/nyc_summary.md`](data/nyc_summary.md) is the
uncorrected view; the next version will add the name rule.

### Bangladesh: the same check for turmeric (new)

Bangladesh cracked down on lead chromate in turmeric after Forsyth et al. (2019) traced it to polishing mills.
Forsyth et al. (2023) describe the campaign (2017-2021): news coverage of the findings, notices and meetings for
consumers and traders, and enforcement by the Bangladesh Food Safety Authority with a rapid lead test. At the
country's largest turmeric wholesale market, samples with detectable lead fell from 47% in 2019 to 0% in 2021
(n = 631). NYC's case investigations again give a check from outside: turmeric that families brought from Bangladesh
into New York homes where someone had high blood lead.

| NYC case-investigation turmeric bought in Bangladesh (codes C and A) | samples | >= 100 ppm lead | highest | investigations (collection dates) | ... with a sample >= 100 ppm |
|---|---|---|---|---|---|
| 2011-2018 | 47 | 29 (62%) | 1,300 ppm | 44 | 29 (66%) |
| 2019-2020 | 55 | 8 (15%) | 730 ppm | 53 | 8 (15%) |
| 2021 | 9 | 1 | 150 ppm (July) | 9 | 1 |
| 2022-2025 | 38 | **0** | **37 ppm** | 38 | **0** |

Turmeric is matched by name (turmeric, holud, halud, haldi, and NYC's misspellings "tumeric" and "turmeic"). By
year, samples at >= 100 ppm were 4/8 (2011), 3/3, 2/3, 1/4, 8/9, 5/8, 5/6, 1/6 (2018), 6/50 (2019), 2/5 (2020),
1/9 (2021), then 0/12, 0/11, 0/6 and 0/9 (2022-2025). 23 of the 38 samples from 2022-2025 had no detectable lead.

> **Correction (2026-10-15).** The first version matched only the spelling "turmeric" and missed 9 rows that NYC
> spells "tumeric" or "turmeic" (1 in 2021, 8 in 2022-2025, all below 100 ppm, highest 14 ppm). It reported 1 of 8
> for 2021 and 0 of 30 for 2022-2025; the table now has 1 of 9 and 0 of 38. The comparisons below are updated, and
> so is the other-countries baseline, which had counted Georgian-named spices with no recorded country as
> "other" (Georgia section above).

- The last four hot samples were collected in December 2019 (730 ppm), January 2020 (160), November 2020 (220) and
  July 2021 (150). That trails the market data in Bangladesh by months, as expected for turmeric that families
  bought before the crackdown and carried with them.
- Counting all spices bought in Bangladesh, not only turmeric: 43 of 347 case samples were at >= 100 ppm in
  2011-2020 and 1 of 160 from 2021 on. 38 of the 44 hot ones were turmeric. The other 6 (cinnamon, cumin, curry
  powder, masala, chili powder, a spice mix) were all collected in 2013-2017. NYC's chromium tests put five of them
  (all but the masala, which had no chromium test) near 1:1 Pb:Cr (section 2).
- None of it was within a powder Raman screen's reach. The highest, 1,300 ppm lead, is about 0.2% w/w lead
  chromate, under half the 0.5% limit. Every hot Bangladeshi spice in NYC's case files needed the 0.025-0.05% screen
  of section 3.

How sure is the fall? It depends on what it is compared with.

- **Against NYC's whole earlier record** (97 investigations in 2011-2020, 37 with a hot sample): if the 38 later
  investigations had been drawn at random from all 135, the chance that none found one is below 1 in 100,000
  (hypergeometric).
- **Against the drop everywhere else.** Case spices from countries other than Bangladesh and Georgia (Georgian-named
  spices with no recorded country counted as Georgian) also fell, from 29 of 589 samples at >= 100 ppm (4.9%) in
  2011-2018 to 7 of 1,005 (0.7%) in 2022-2025. If Bangladeshi turmeric had fallen only as much, about 9% of the 38
  later samples would still be hot, and the chance of none is about 3%.
- **Against 2019-2020 only.** In 2019 NYC tested far more case spices than in any earlier year (657 from countries
  other than Georgia, against 51-137 a year in 2011-2018), and the hot share fell that year for Bangladeshi and other
  spices alike. Taking 2019-2020 as the baseline (8 of 53 investigations hot), the chance of 0 of 38 later is about
  1% by investigation. After scaling by the other countries' fall over the same years (14 of 588 samples, 2.4%, to
  0.7%), it is about 18%.

So NYC's data shows the Bangladeshi turmeric that reached New York homes changing from mostly heavily leaded
(2011-2018) to none above 37 ppm (2022-2025), on the timing of the campaign. On its own it cannot separate a
Bangladesh effect from NYC's broader sampling since 2019 and the general fall in hot case spices. Two hot turmeric
samples since 2021 have no recorded purchase country (1,200 ppm in April 2021, 1,500 ppm in September 2023), so
some Bangladeshi turmeric may sit outside the count. It agrees with Forsyth et al.'s in-country result. We found no
earlier check of that result from a destination country's lab data, and with Georgia's it is the second national
spice crackdown visible in the same city's case files.

These counts were read from NYC's API on 2026-10-15 (SoQL: product_type 'Food-Spice', metal 'Lead', units 'ppm',
investigation_type C or A, purchase_country 'BANGLADESH', hot = `concentration >= 100`; a collection date stands in
for one investigation). Anyone can rerun them, for example:

```
https://data.cityofnewyork.us/resource/da9u-wz3r.json?$select=date_extract_y(collection_date) as y,count(*) as n,sum(case(concentration>=100,1,true,0)) as hot,max(concentration) as mx&$where=product_type='Food-Spice' AND metal='Lead' AND units='ppm' AND purchase_country='BANGLADESH' AND investigation_type in('C','A')&$group=y&$order=y
```

For turmeric only, add `AND (lower(product_name) like '%25turmeric%25' OR lower(product_name) like '%25tumeric%25'
OR lower(product_name) like '%25turmeic%25')` (%25 is a URL-encoded %). The next version of `nyc_spice_lead.py` will
compute this check from the raw rows next to `georgia_trend`.

### Where the hot spices come from now (new)

Two things changed in NYC's case files after 2020, and both matter for anyone who uses purchase country to target
screening.

**The purchase country is now often blank.** Among NYC's case-investigation spice lead tests (codes C and A), the
share with purchase country "UNKNOWN OR NOT STATED" was 111 of 1,793 (6%) in 2011-2020. It was 16 of 153 in 2021,
34 of 200 in 2022, then **226 of 383 (59%) in 2023**, 153 of 338 (45%) in 2024 and 75 of 231 (32%) in 2025. Half
of the hot case spices since 2021 (6 of 12 at >= 100 ppm) have no recorded country.

**The hot spices since 2021 (all 12 at >= 100 ppm lead, codes C and A):**

| collected | spice (NYC's name) | recorded purchase country | lead ppm |
|---|---|---|---|
| 2021-04 | Turmeric powder | not stated | 1,200 |
| 2021-07 | Turmeric | Bangladesh | 150 |
| 2022-11 | Mixed Spices | Pakistan | 300 |
| 2023-08 | Tumeric | India | 1,800 |
| 2023-09 | Tumeric | not stated | 1,500 |
| 2023-10 | Curry | not stated | 530 |
| 2024-03 | Turmeric | India | 2,400 |
| 2024-06 | Georgian chilli powder | not stated | 12,700 |
| 2024-06 | Utskho suneli / yellow flower (2 samples) | not stated | 1,010 and 146 |
| 2024-10 | All purpose seasoning | Morocco | 5,400 |
| 2025-12 | Red Chili Powder | Pakistan | 182 |

- **Turmeric is still the most common hot spice** (5 of 12), but the recorded origin has moved: the two with a
  recorded country since 2022 were bought in India, not Bangladesh.
- **India shows no fall.** Case spices bought in India were at >= 100 ppm in 4 of 144 samples (2.8%, highest 2,000
  ppm) in 2011-2020 and 2 of 78 (2.6%, highest 2,400 ppm) in 2021-2025, while Georgia, Bangladesh and Pakistan (10
  of 65 to 2 of 46) fell. The numbers are small, but they fit King County's two hot case spices, both home-made from
  India (2,800 ppm turmeric in 2025, 620 ppm spice mix in 2026, section 3), and Forsyth et al.'s finding of lead
  chromate in turmeric across South Asia (2024).
- **Two of the 12 are above the bench Raman limit** (12,700 and 5,400 ppm); the other ten (146-2,400 ppm) need the
  0.025-0.05% screen of section 3.

Read from NYC's API on 2026-10-15 (SoQL: product_type 'Food-Spice', metal 'Lead', units 'ppm', investigation_type
C or A, grouped by purchase_country and year; the 12 hot rows are NYC rows 5478, 5560, 6539, 7159, 7217, 7392,
7748, 8065, 8066, 8067, 8335 and 9486).

## 3. How low must a lead chromate screen reach? (new in 0.3.0)

Sections 1 and 2 test one detection limit. Lopez et al. (ES&T 2022) made the same point for one dataset: vibrational
spectroscopy's best limit, about 3,200 mg/kg lead, sits above the highest of 252 turmeric samples in a global
database (2,700 mg/kg). `lod_curve.py` turns that into a curve. For each candidate limit, written as % w/w lead
chromate and converted to lead, it counts how many lead-laced spices in public-health lab data a screen with that
limit would have caught. It assumes all the lead is lead chromate, which is the best case for a chromate screen
(34 of 39 NYC lead/chromium pairs fit it, section 2).

A third open dataset joins NYC's: **Public Health - Seattle & King County, "Lead Content of Consumer Products
tested in King County, Washington"** (https://data.kingcounty.gov/d/i6sy-ckp7, 2,220 products, 2019-2026). Its
spices are the "Seasoning" type plus spices filed under "Food", all tested by a laboratory.

### NYC: spice samples with at least 100 ppm lead (190 of 3,575)

| screen limit, % w/w PbCrO4 | 1% | **0.5%** (bench Raman) | 0.25% | 0.1% | 0.05% | 0.025% |
|---|---|---|---|---|---|---|
| same limit as lead | 6,411 ppm | 3,206 ppm | 1,603 ppm | 641 ppm | 321 ppm | 160 ppm |
| caught, all 190 | 33 (17%) | **46 (24%)** | 74 (39%) | 120 (63%) | 148 (78%) | 176 (93%) |
| caught, cases code C (145) | 24 | 32 (22%) | 55 | 90 (62%) | 109 (75%) | 132 (91%) |
| caught, cases code A (43) | 9 | 14 (33%) | 19 | 30 (70%) | 37 (86%) | 42 (98%) |
| caught, store survey (S, 2) | 0 | 0 | 0 | 0 | 2 | 2 |

With the lower cut of 18 ppm lead (268 samples, the level above which Forsyth et al. read Pb:Cr ratios), a 0.5%
screen catches 46 (17%), a 0.05% screen 148 (55%), and catching 9 in 10 needs about 0.005% (32 ppm lead: 245 of 268).

**A screen must see about 0.025-0.05% w/w lead chromate (160-320 ppm lead), 10 to 20 times below bench powder
Raman, to catch 9 in 10 of NYC's spices with 100 ppm lead or more.** At 0.5% it catches 1 in 4.

### King County: none reach the Raman limit

| King County spices, lab-tested | results | lead detected | highest lead | >= 100 ppm | >= 3,206 ppm |
|---|---|---|---|---|---|
| community product testing events | 185 | 124 | 1.3 ppm | 0 | 0 |
| case investigations | 22 | 18 | 2,800 ppm | 2 | **0** |
| all | 207 | 142 | 2,800 ppm | 2 | **0** |

The two high ones are home-made spices from India found in case investigations: a turmeric powder at 2,800 ppm
(2025) and a spice mix at 620 ppm (2026). A 0.5% screen misses both; a 0.05% screen catches both. King County's
data has no chromium results, so whether these are lead chromate is not known.

### What the curve says

- Three open U.S. sources agree. **No FDA spice recall level (0 of 12), no NYC store-survey sample (0 of 477) and
  no King County spice (0 of 207) reaches the bench Raman limit.** Only NYC's case investigations do (46).
- Powder Raman at 0.5% is a tool for the gross tail. To be a general screen it has to gain about 20 times
  sensitivity. Picking out and scanning the yellow-orange grains themselves (particle-level Raman, as Kubachka et
  al. at FDA did on cinnamon) is one candidate, since a picked grain can be mostly pigment rather than pigment
  diluted through the powder. Whether a handheld device reaches an effective 0.025-0.05% that way is untested.
- The first fivefold gain (0.5% to 0.1%) lifts NYC's catch from 24% to 63%; the next fourfold (to 0.025%) adds
  another 30 points.

The NYC and King County counts were first read from each agency's API on 2026-10-14 (SoQL counts per threshold).
`lod_curve.py` then recomputed every one from the raw rows (run of 2026-10-14: 3,575 NYC spice lead rows, 2,220 King
County products, 207 King County spice results), and all of them matched. Its outputs, with the sha256 of each
download, are in [`data/lod_curve.md`](data/lod_curve.md), [`data/lod_curve.json`](data/lod_curve.json) and
[`data/lod_curve.csv`](data/lod_curve.csv).

Limits: the curve treats every microgram of lead as lead chromate; where the lead has another source, no
chromate screen sees it at any limit. Case samples are chosen because someone was poisoned, so they over-represent
heavy adulteration. The 0.5% limit is for bench FT-Raman on ground turmeric (Erasmus et al. 2021); other devices,
lasers (Blaise uses 808 nm) and spices will differ.

## 4. Many small spots instead of one big reading (new)

Section 3 asks for a screen about 20 times more sensitive than bench powder Raman. There may be a way to get there
without a better instrument. A limit like 0.5% w/w applies to the powder inside the probed volume. If the pigment
sits in discrete grains instead of being spread evenly, a small probe that happens to hold one grain sees a local
fraction far above the bulk one. `spot_sampling.py` works out how many random spots that takes.

**Model.** Pigment grains of one size, placed at random. The instrument flags a spot when lead chromate makes up at
least L0 = 0.5% of the probed powder. A probe holding powder mass m therefore needs ceil(m L0 / g) grains, where g
is one grain's mass, and the number of grains it holds is Poisson with mean c m / g at bulk pigment fraction c.

**Result.** The best probe is the one in which a single grain just reaches the limit (m = g / L0). One spot is then
positive with probability 1 - exp(-c / L0), so

    N = ln(10) x L0 / c   random spots catch a sample with 90% probability,

whatever the grain size. Only the size of the matched probe depends on the grain: a powder cube about 11 grain
diameters on a side (lead chromate 6.12 g/cm3, loose powder taken as 0.5 g/cm3).

| lead in the spice | % w/w PbCrO4 | matched random spots for a 90% catch | one bulk reading |
|---|---|---|---|
| 3,206 ppm | 0.5% | 3 | at its limit |
| 1,603 ppm | 0.25% | 5 | no |
| 641 ppm | 0.1% | 12 | no |
| 321 ppm | 0.05% | 23 | no |
| 160 ppm | 0.025% | 47 | no |
| 100 ppm | 0.016% | 74 | no |

| pigment grain diameter | 1 um | 5 um | 10 um | 20 um | 50 um |
|---|---|---|---|---|---|
| matched probe (edge of the powder cube) | 11 um | 54 um | 109 um | 217 um | 543 um |

**The probe size matters more than the spot count.** At 100 ppm lead, a probe a third of the matched size needs
about 250 spots. A probe twice the matched size needs two grains at once, and about 1,230 spots. A probe ten times
the matched size needs over a trillion, and a bulk reading never fires.

### Applied to NYC's case files

`spot_sampling.py` runs the model on every NYC and King County spice sample (the same downloads as section 3),
assuming all the lead is lead chromate. For NYC's 190 spice samples with at least 100 ppm lead, the expected share
caught:

| probe | 1 spot | 10 spots | 25 spots | 50 spots | 100 spots |
|---|---|---|---|---|---|
| matched to the grain | 40% | 83% | 94% | **98%** | 99.8% |
| a third of the matched size | 21% | 61% | 79% | 89% | 96% |
| twice the matched size | 33% | 64% | 75% | 82% | 88% |
| one bulk reading (more readings add nothing) | 24% | 25% | 25% | 25% | 25% |

With 50 matched spots, 180 of the 190 samples are each caught with at least 90% probability; with 100, all 190 are.
The two King County case samples at 100 ppm or more (620 and 2,800 ppm) are caught with 93% expected share at 10
matched spots and 100% at 25. **In this model a raster of about 50 grain-matched spots does what section 3 asks for:
the 20-fold gain comes from sampling rather than from a better instrument.** A probe that is the wrong size for the
grains loses much of it, so in practice the grain size has to be known or several probe sizes tried.

The Poisson formula was checked against a simulation that drops grains at random into 200,000 probes, for five
combinations of pigment level and probe size: every simulated share was within 0.26 standard errors of the formula.

The idea is not new in pharmaceutical analysis, where Raman mapping finds minor components below the bulk limit.
Šašić and Whitlock (Appl Spectrosc 2008) set the number of spectra from sampling statistics to detect a form below
1% w/w in tablets. Li et al. (Anal Chem 2015) reached a 0.03% limit with about 8,400 spectra per powder sample. We
found no published spot budget for lead chromate in spices, and none tied to public-health lab data.

The run of 2026-10-15 (spot_sampling 0.1.0, 13 offline tests passed) is in [`data/spot_sampling.md`](data/spot_sampling.md),
[`data/spot_sampling.json`](data/spot_sampling.json) and [`data/spot_sampling.csv`](data/spot_sampling.csv) (1 to 200
spots, four probe sizes, every channel). Its first table prints exact spot counts even when they are absurd (over a
trillion at 100 ppm with a probe ten times the matched size, and a number with 86 digits for one bulk reading at
0.25%): read those as "never in practice".

Limits: this is a design model, not a measurement. It assumes the pigment sits in grains of one size. If the pigment
is ground fine and coats the spice particles evenly, every spot sees the bulk fraction and more spots gain nothing.
FDA found yellow-orange pigment particles in cinnamon (Kubachka et al.), but we found no published size distribution
of pigment grains in adulterated spices. The model also assumes a probe's limit, as a fraction of the powder it sees,
does not change with probe size. A small probe collects less light, so a real handheld may need a higher local
fraction. A real beam weights grains by depth and position, and turmeric fluoresces. Random spots are the worst
case: picking visibly yellow-orange grains, by eye or by camera, should do better.

## What this means for a screening tool

This is why [spice-screen](https://github.com/munimtechnologies/spice-screen) calls itself a screen, never a lab
test. A clean Raman result on powder says nothing about the 2-50 ppm levels behind most recalls, or about the
100-3,000 ppm chromate-laced spices in NYC's data. Raman is useful where the pigment is concentrated: grossly
adulterated home-imported blends (NYC's 46), the polished surface of whole turmeric roots, or visible yellow-orange
grains picked out of a powder. Section 3 sets the target for anything that claims more: about 0.025-0.05% w/w lead
chromate. Section 4 shows that a raster of about 50 small, grain-matched spots could reach it in principle with
today's limit. That has to be tested on real adulterated spices. Reaching recall-level lead needs XRF or a lab.

## Spot check of the FDA classifier (by hand, every spice row)

A hand check of 0.1.0 found that all 11 levels it parsed matched FDA's own wording, and found these mistakes.
`lead_recalls.py` 0.1.1 fixes all but the last two:

- **Missed spice:** F-0975-2020 Dragonfly Galanga (galangal) Powder; "galanga" was not in the spice word list.
  Fixed.
- **Not a spice:** F-2148-2012 Red Vines black licorice (candy). Fixed: no longer counted.
- **Supplements counted as spice:** F-0408/0410/0413/0414-2019 NutraNext ginger "Toxin Absorber" and cleansing kits.
  Fixed: now counted as supplements.
- **Chili-coated salted plum candy (saladitos) counted as spice:** F-0821/0823/0824/0856-2022 (F-0858-2022 was
  already a food). Fixed: now counted as foods containing spice.
- **Spices counted as "food containing spice"** because of a packaging or company word ("pouch", "beverage"):
  F-2223-2014 PRAN turmeric, F-1796-2024 Asli cinnamon, F-0267-2025 Super Brand cinnamon. Fixed.
- **Missed level:** F-0077-2014 Coconut Tree ginger candy, ".012 ppm" (a number with no leading zero). Fixed: it is
  the 12th stated level.
- Still open: F-1612-2017 Gel Spice ground turmeric is a spice but is still counted as a food, because of a word in
  its long description.
- Still open: F-2242-2019 (pumpkin spice cake roll) is a recall for pieces of metal that include lead, not lead in
  the spice, and is still counted.

With the fixes, spice products alone fall from 61 to 58 recalls and supplements rise from 1 to 4; the total stays
75 (galangal in, licorice out). None of these changes the headline: no stated level comes near the Raman limit.

## Limits

- openFDA holds recalls FDA classified. State actions FDA did not classify, import refusals and alerts are not in it.
- Only 12 of 75 spice recalls state a level in openFDA's text. The table in section 1 adds FDA's other published numbers.
- NYC's and King County's samples follow lead-poisoning cases, community testing events and targeted store surveys,
  so they are not a random sample of the market.
- Lead levels are total lead from any source (soil, processing equipment, pigments). Lead chromate is one cause.
- The Raman limit is for bench FT-Raman on ground turmeric. Handheld devices, other spices and SERS differ.

## Run it

```
python -m unittest -v test_lead_recalls test_nyc_spice_lead test_cr_baseline test_lod_curve test_spot_sampling
python lead_recalls.py --data-dir data-cache --out-dir out
python nyc_spice_lead.py --data-dir data-cache --out-dir out
python cr_baseline.py --pairs out/nyc_spice_pb_cr_pairs.csv --out-dir out
python lod_curve.py --data-dir data-cache --out-dir out
python spot_sampling.py --data-dir data-cache --out-dir out
```

`lead_recalls.py` downloads `https://download.open.fda.gov/food/enforcement/food-enforcement-0001-of-0001.json.zip`
(about 6 MB) once, then writes `lead_recalls.csv`, `spice_lead_recalls.csv`, `summary.json` and `summary.md`. The
files in [`data/`](data/) are the 0.1.1 run on the 2026-10-13 export (sha256 139cb14c05a8...). Every parsed level
sits next to the text it came from.

`nyc_spice_lead.py` downloads NYC's dataset through its API (about 9,500 rows) once, then writes
`nyc_spice_lead.csv`, `nyc_spice_pb_cr_pairs.csv`, `nyc_summary.json` and `nyc_summary.md`. Every row keeps NYC's
row_id.

`cr_baseline.py` reads `nyc_spice_pb_cr_pairs.csv` (a path or a URL) and
[`data/natural_cr_ceilings.csv`](data/natural_cr_ceilings.csv), then writes `cr_baseline.csv`, `cr_baseline.json` and
`cr_baseline.md`. Add a row to the ceilings table, with its source, to test a spice against new data.

`lod_curve.py` downloads NYC's spice lead rows and King County's dataset (about 2,200 rows) through their APIs once,
then writes `lod_curve.json`, `lod_curve.md` and `lod_curve.csv`.

`spot_sampling.py` imports `lod_curve.py`, reads the same two downloads, then writes `spot_sampling.json`,
`spot_sampling.md` and `spot_sampling.csv`.

The pre-registered analyses each have their own script and test, named in their notes
([`docs/analyses-index.md`](docs/analyses-index.md)).

## Sources

- openFDA food enforcement reports: https://open.fda.gov/apis/food/enforcement/
- NYC DOHMH, Metal Content of Consumer Products Tested by the NYC Health Department: https://data.cityofnewyork.us/d/da9u-wz3r
- Public Health - Seattle & King County, Lead Content of Consumer Products tested in King County, Washington:
  https://data.kingcounty.gov/d/i6sy-ckp7
- Hore, Alex-Oni, Sedlar, Nagin. A spoonful of lead: a 10-year look at spices as a potential source of lead exposure.
  J Public Health Manag Pract 25:S63 (2019). doi:10.1097/PHH.0000000000000876
- Erasmus, van Hasselt, Ebbinge, van Ruth. Real or fake yellow in the vibrant colour craze: rapid detection of lead
  chromate in turmeric. Food Control 121:107714 (2021). doi:10.1016/j.foodcont.2020.107714
- Lopez et al. Assessing analytical methods for the rapid detection of lead adulteration in the global spice market.
  Environ Sci Technol (2022). doi:10.1021/acs.est.2c03241
- Forsyth et al. Turmeric means "yellow" in Bengali: lead chromate pigments added to turmeric threaten public health
  across Bangladesh. Environ Res 179:108722 (2019).
- Forsyth, Baker, Nurunnahar et al. Food safety policy enforcement and associated actions reduce lead chromate
  adulteration in turmeric across Bangladesh. Environ Res 232:116328 (2023). doi:10.1016/j.envres.2023.116328
- Forsyth et al. Evidence of turmeric adulteration with lead chromate across South Asia. Sci Total Environ 949:175003 (2024).
- Forsyth et al. Reductions in spice lead levels in the Republic of Georgia: 2020-2022. Environ Res 250:118504 (2024).
- Kubachka, Witkowski et al. (FDA). Detection of lead (II) chromate in cinnamon. doi:10.1177/27551857261425269
- FDA, Investigation of elevated lead and chromium levels: cinnamon applesauce pouches (November 2023).
- FDA, More ground cinnamon products added to FDA public health alert due to presence of elevated levels of lead.
- CFIA, Lead chromates in spices, April 1, 2019 to March 31, 2021.
- Forsyth et al. npj Sci Food (2026).
- Šašić, Whitlock. Raman mapping of low-content active-ingredient pharmaceutical formulations. Part II: statistically
  optimized sampling for detection of less than 1% of an active pharmaceutical ingredient. Appl Spectrosc 62:916
  (2008). doi:10.1366/000370208785284376
- Li, Calvet, Casamayou-Boucau, Morris, Ryder. Low-content quantification in powders using Raman spectroscopy: a
  facile chemometric approach to sub 0.1% limits of detection. Anal Chem 87:3419 (2015). doi:10.1021/ac504776m
- Natural chromium in spices (`data/natural_cr_ceilings.csv`):
  - Cicero et al. Mineral and microbiological analysis of spices and aromatic herbs. Foods 11:548 (2022).
    doi:10.3390/foods11040548 (ICP-MS)
  - Voica et al. ICP-MS assessment of essential and toxic trace elements in foodstuffs with different geographic
    origins. Molecules 26:7081 (2021). doi:10.3390/molecules26237081 (ICP-MS)
  - Ghuniem et al. Health risk assessment of Sudan dyes, toxic elements, and pesticide residues in Egyptian spices.
    Sci Rep (2025). doi:10.1038/s41598-025-31386-3 (ICP-MS)
  - Heavy metal analysis in commercial spices and herbs by ICP-MS and estimated dietary exposure. J Environ Expo
    Assess (2025). https://www.oaepublish.com/articles/jeea.2025.10 (ICP-MS)
  - Gazwi et al. Sci Rep 12:9834 (2022). PMC9013364 (ICP-OES, aqueous coriander seed extract)
  - Tefera, Teklewold. Health risk assessment of heavy metals in selected Ethiopian spices. Heliyon 7:e07048 (2021).
    doi:10.1016/j.heliyon.2021.e07048 (flame AAS)

Contact: MV2, Munim, Inc. - mv2@munimtech.com
