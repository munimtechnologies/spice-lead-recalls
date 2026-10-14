# spice-lead-recalls

U.S. FDA food recalls for **lead in spices**, from openFDA's food enforcement data. Each recall is sorted by spice,
and the lead level FDA quotes in its free text (ppm, ppb, mg/kg, ug/g, mg/g) is parsed out. The study asks one
question that matters to anyone building a fast field screen: **how often did a recalled spice carry enough lead for
a Raman spectrometer to see lead chromate at all?**

By MV2 of Munim, Inc. Code Apache-2.0; derived data CC BY 4.0. openFDA data are public domain (CC0).
The code, data run and write-up were made with AI agents working in MV2's name.

## Result (openFDA export of 2026-10-13, 29,485 enforcement records)

| | count |
|---|---|
| Recalls whose reason names lead | 179 (119 recall events) |
| ... of a spice or a food with a named spice in it | 75 (58 events) |
| ... where FDA's text states a lead level | **11** |
| ... at or above ~3,206 ppm lead (0.5% w/w lead chromate) | **0** |

The stated spice levels run from 0.065 to 53.7 ppm (median 2.92 ppm). The highest, 53.7 ppm in PRAN turmeric
powder from Bangladesh (2013), is **about 60 times below** the lowest lead chromate level a published Raman method
detects in turmeric powder.

The Raman limit comes from Erasmus et al. 2021, the first study of FT-Raman for lead chromate in turmeric. Their
840 cm-1 peak model reached a limit of detection of 0.6% w/w and their PLS model 0.5%. PbCrO4 is 64.1% lead by mass,
so 0.5% w/w is about 3,206 ug/g (ppm) lead. The authors already warned that this limit is "above the highest
levels found in practice". This dataset puts numbers on that for U.S. recalls.

### The same picture from FDA's other public numbers (not in openFDA's text)

| source | lead in the spice | at or above ~3,206 ppm? |
|---|---|---|
| FDA ground-cinnamon public health alert, 2024-2025 (18+ brands) | 2.03 - 10.7 ppm; El Servidor 20 ppm | no |
| FDA/Ecuador, cinnamon behind the 2023 WanaBana applesauce outbreak (566 cases, CDC) | 2,270 and 5,110 ppm | **one of two samples** |
| CFIA survey, 132 yellow/brown spices, 2019-2021 (2 ginger samples chromate-positive) | all samples <= 1.84 ppm | no |
| Bangladesh turmeric (Forsyth et al. 2019) | up to 1,152 ug/g | no |
| Eastern India, 503 samples 2021-23 (npj Sci Food 2026) | up to 6,416 ug/g | the top of the range |

So bulk Raman on spice powder sees only the most extreme, deliberate adulteration: the WanaBana cinnamon at
5,110 ppm, or the worst Indian samples. It would not have flagged a single U.S. ground-cinnamon recall. The
chromate-positive ginger CFIA found held under 2 ppm lead, roughly 1,700 times below the Raman limit.

**What this means for a screening tool** (it is why [spice-screen](https://github.com/munimtechnologies/spice-screen)
calls itself a screen, never a lab test): a clean Raman result on powder says nothing about the 2-50 ppm levels
behind most recalls. Raman is useful where the pigment is concentrated: on the polished surface of whole turmeric
roots, on visible yellow-orange grains, or in heavily adulterated lots. Reaching recall-level lead needs XRF or a lab.

## Spot check (by hand, every spice row)

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
- Only 11 of 75 spice recalls state a level in openFDA's text. The table above adds FDA's other published numbers.
- Recall levels are total lead from any source (soil, processing equipment, pigments). Lead chromate is one cause.
- The Raman limit is for bench FT-Raman on ground turmeric. Handheld devices, other spices and SERS differ.

## Run it

```
python -m unittest -v test_lead_recalls
python lead_recalls.py --data-dir data-cache --out-dir out
```

It downloads `https://download.open.fda.gov/food/enforcement/food-enforcement-0001-of-0001.json.zip` (about 6 MB)
once, then writes `lead_recalls.csv`, `spice_lead_recalls.csv`, `summary.json` and `summary.md`. The files in
[`data/`](data/) are the run on the 2026-10-13 export (sha256 139cb14c05a8...). Every parsed level sits next to the text it came from.

## Sources

- openFDA food enforcement reports: https://open.fda.gov/apis/food/enforcement/
- Erasmus, van Hasselt, Ebbinge, van Ruth. Real or fake yellow in the vibrant colour craze: rapid detection of lead
  chromate in turmeric. Food Control 121:107714 (2021). doi:10.1016/j.foodcont.2020.107714
- FDA, Investigation of elevated lead and chromium levels: cinnamon applesauce pouches (November 2023).
- FDA, More ground cinnamon products added to FDA public health alert due to presence of elevated levels of lead.
- CFIA, Lead chromates in spices, April 1, 2019 to March 31, 2021.
- Forsyth et al. Environ Res 179:108722 (2019); Forsyth et al. npj Sci Food (2026).

Contact: MV2, Munim, Inc. - munimversion2@gmail.com
