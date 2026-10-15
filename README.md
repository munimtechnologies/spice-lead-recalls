# spice-lead-recalls

How much lead do contaminated spices carry, and how much of it could a fast field screen (Raman) see? Three public
sources:

1. **U.S. FDA food recalls** for lead in spices, from openFDA's food enforcement data (`lead_recalls.py`).
2. **NYC Health Department lab results**: 3,575 spice lead tests and 61 spice chromium tests from New York City's
   lead-poisoning investigations and store surveys, 2011-2025 (`nyc_spice_lead.py`, new in 0.2.0).
3. **Public Health - Seattle & King County lab results** for spices from community testing events and case
   investigations, 2019-2026, used with NYC's to ask how low a screen must reach (`lod_curve.py`, new in 0.3.0).

By MV2 of Munim, Inc. Code Apache-2.0; derived data CC BY 4.0. openFDA data are public domain (CC0). NYC data:
NYC Open Data, NYC Department of Health and Mental Hygiene (DOHMH). King County data: King County Open Data, Public
Health - Seattle & King County. This analysis is not endorsed by either agency.
The code, data runs and write-up were made with AI agents working in MV2's name.

The Raman limit used throughout comes from Erasmus et al. 2021, the first study of FT-Raman for lead chromate in
turmeric: limit of detection 0.6% w/w (840 cm-1 peak) and 0.5% (PLS model). PbCrO4 is 64.1% lead by mass, so 0.5% w/w
is about **3,206 ug/g (ppm) lead**.

## 1. FDA recalls (openFDA export of 2026-10-13, 29,485 enforcement records)

| | count |
|---|---|
| Recalls whose reason names lead | 179 (119 recall events) |
| ... of a spice or a food with a named spice in it | 75 (58 events) |
| ... where FDA's text states a lead level | **11** |
| ... at or above ~3,206 ppm lead (0.5% w/w lead chromate) | **0** |

The stated spice levels run from 0.065 to 53.7 ppm (median 2.92 ppm). The highest, 53.7 ppm in PRAN turmeric
powder from Bangladesh (2013), is **about 60 times below** the Raman limit. The authors of the Raman study already
warned that their limit is "above the highest levels found in practice". This dataset puts numbers on that for U.S. recalls.

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
largest group. The counts below were read from NYC's own API on 2026-10-14; `nyc_spice_lead.py` recomputes all of
them from the raw rows (its outputs will be added to `data/` after the scripted run).

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

- In **477 store-survey samples, nothing came within 5x of the Raman limit**. That matches the FDA recalls (0 of 11).
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
method (Raman, XRD) does. Natural chromium can matter below about 18 ppm lead, so those pairs are left out. Pairing
by name and date was checked by hand for every row above.

### Georgia: did its crackdown reach New York homes? (new)

Georgian blends are 35 of NYC's 46 spices above the Raman limit. Georgia's food-safety authority has paid closer
attention to lead in spices since 2018, and Forsyth et al. (2024) measured the result inside Georgia: across 765
bazaar samples from 29 cities in three rounds, the highest lead fell from over 14,000 ug/g in 2020 to 36 ug/g in
the last round of 2022. NYC's case investigations give a check from outside the country: spices that families carried
from Georgia into New York homes where someone had high blood lead.

| NYC case-investigation spices (codes C and A) | collected | samples | >= 100 ppm lead | highest | investigations (collection dates) | ... with a spice >= 100 ppm |
|---|---|---|---|---|---|---|
| bought in Georgia | 2011-2020 | 262 | 88 (34%) | 78,000 ppm (2020) | 77 | 52 (68%) |
| bought in Georgia | 2021-2024 | 16 | **0** | **3.5 ppm** | 4 | **0** |
| bought anywhere else | 2011-2020 | 1,531 | 88 (5.7%) | 21,000 ppm | | |
| bought anywhere else | 2021-2025 | 1,289 | 12 (0.9%) | 12,700 ppm (2024) | | |

- 30 of the 262 earlier Georgian spices were at or above the Raman limit; none of the later 16 is. The last Georgian
  spice above 100 ppm in NYC's data was collected in December 2020 (a kharcho suneli at 2,600 ppm and a "yellow
  flower" at 890 ppm). Since then, 16 Georgian spices from 4 investigations (March 2021, February and December 2022,
  June 2024) all tested at 3.5 ppm or less, including the marigold "yellow flower" (kviteli kvavili) that carried most
  of the pigment before: 1.4 ppm in 2021 and not detected in 2024.
- If the 4 later investigations had been drawn at random from all 81 Georgian ones, the chance that none found a
  spice at 100 ppm or more is 1.4% (hypergeometric; 0.2% counted by sample).
- Spices from other countries did not stop arriving hot: NYC still found 12,700 ppm in 2024. So NYC's lab and
  methods still catch heavily laced spices, and the Georgian change is not just an artifact of testing.

What it does not show: NYC's case spices from other countries also fell at 100 ppm or more (5.7% to 0.9%), so part
of the change may be in what NYC samples, and this data alone cannot prove a Georgia-only effect. Four
investigations is a small number, and a collection date stands in for one household visit. It agrees with Forsyth et
al.'s in-country result. We found no earlier check of that result from a destination country's lab data.

These counts were read from NYC's API on 2026-10-15 (SoQL, purchase_country = GEORGIA). `nyc_spice_lead.py` 0.3.0
recomputes them from the raw rows (`georgia_trend` in its summary), and its outputs go in `data/` after the run.

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

- Three open U.S. sources agree. **No FDA spice recall level (0 of 11), no NYC store-survey sample (0 of 477) and
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

## What this means for a screening tool

This is why [spice-screen](https://github.com/munimtechnologies/spice-screen) calls itself a screen, never a lab
test. A clean Raman result on powder says nothing about the 2-50 ppm levels behind most recalls, or about the
100-3,000 ppm chromate-laced spices in NYC's data. Raman is useful where the pigment is concentrated: grossly
adulterated home-imported blends (NYC's 46), the polished surface of whole turmeric roots, or visible yellow-orange
grains picked out of a powder. Section 3 sets the target for anything that claims more: about 0.025-0.05% w/w lead
chromate. Reaching recall-level lead needs XRF or a lab.

## Spot check of the FDA classifier (by hand, every spice row)

All 11 parsed lead levels match FDA's own wording. The classifier makes these mistakes; fixes are in the next version:

- **Missed spice:** F-0975-2020 Dragonfly Galanga (galangal) Powder; "galanga" is not in the spice word list.
- **Not a spice:** F-2148-2012 Red Vines black licorice (candy).
- **Supplements counted as spice:** F-0408/0410/0413/0414-2019 NutraNext ginger "Toxin Absorber" and cleansing kits.
- **Chili-coated salted plum candy (saladitos) counted as spice:** F-0821/0823/0824/0856-2022 (F-0858-2022 is correctly a food).
- **Spices counted as "food containing spice"** because of a packaging or company word ("pouch", "beverage"):
  F-2223-2014 PRAN turmeric, F-1796-2024 Asli cinnamon, F-0267-2025 Super Brand cinnamon. F-1612-2017 Gel Spice
  ground turmeric is also a spice but was counted as a food, because of a word in its long description.
- **Missed level:** F-0077-2014 ginger candy, ".012 ppm" (a number with no leading zero).
- F-2242-2019 (pumpkin spice cake roll) is a recall for pieces of metal that include lead, not lead in the spice.

None of these changes the headline: no stated level comes near the Raman limit.

## Limits

- openFDA holds recalls FDA classified. State actions FDA did not classify, import refusals and alerts are not in it.
- Only 11 of 75 spice recalls state a level in openFDA's text. The table in section 1 adds FDA's other published numbers.
- NYC's and King County's samples follow lead-poisoning cases, community testing events and targeted store surveys,
  so they are not a random sample of the market.
- Lead levels are total lead from any source (soil, processing equipment, pigments). Lead chromate is one cause.
- The Raman limit is for bench FT-Raman on ground turmeric. Handheld devices, other spices and SERS differ.

## Run it

```
python -m unittest -v test_lead_recalls test_nyc_spice_lead test_lod_curve
python lead_recalls.py --data-dir data-cache --out-dir out
python nyc_spice_lead.py --data-dir data-cache --out-dir out
python lod_curve.py --data-dir data-cache --out-dir out
```

`lead_recalls.py` downloads `https://download.open.fda.gov/food/enforcement/food-enforcement-0001-of-0001.json.zip`
(about 6 MB) once, then writes `lead_recalls.csv`, `spice_lead_recalls.csv`, `summary.json` and `summary.md`. The
files in [`data/`](data/) are the run on the 2026-10-13 export (sha256 139cb14c05a8...). Every parsed level sits next
to the text it came from.

`nyc_spice_lead.py` downloads NYC's dataset through its API (about 9,500 rows) once, then writes
`nyc_spice_lead.csv`, `nyc_spice_pb_cr_pairs.csv`, `nyc_summary.json` and `nyc_summary.md`. Every row keeps NYC's
row_id.

`lod_curve.py` downloads NYC's spice lead rows and King County's dataset (about 2,200 rows) through their APIs once,
then writes `lod_curve.json`, `lod_curve.md` and `lod_curve.csv`.

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
- Forsyth et al. Evidence of turmeric adulteration with lead chromate across South Asia. Sci Total Environ 949:175003 (2024).
- Forsyth et al. Reductions in spice lead levels in the Republic of Georgia: 2020-2022. Environ Res 250:118504 (2024).
- Kubachka, Witkowski et al. (FDA). Detection of lead (II) chromate in cinnamon. doi:10.1177/27551857261425269
- FDA, Investigation of elevated lead and chromium levels: cinnamon applesauce pouches (November 2023).
- FDA, More ground cinnamon products added to FDA public health alert due to presence of elevated levels of lead.
- CFIA, Lead chromates in spices, April 1, 2019 to March 31, 2021.
- Forsyth et al. npj Sci Food (2026).

Contact: MV2, Munim, Inc. - munimversion2@gmail.com
