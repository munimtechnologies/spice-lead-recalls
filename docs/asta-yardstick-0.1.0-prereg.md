# ASTA yardstick 0.1.0 — pre-registration (2026-10-18)

Made with AI agents working in the name of MV2 of Munim, Inc. Apache-2.0 code / CC BY 4.0 text.

This file is written **before** any per-sample lead value is compared against ASTA's
category levels. It fixes the method, the hypotheses and the numeric predictions so a
later grader can be scored honestly against them. No count below has been computed yet.

## Why

Across the sixteen sampling frames in `docs/where-you-look.md` we have measured spice-lead
exceedance against one bar: **gross lead, ≥ 50 ppm** — a bar chosen to isolate deliberate
lead-chromate adulteration from background uptake. That bar is ours, not a standard.

The American Spice Trade Association publishes **Guidance Levels for Heavy Metals in
Spices**, V3, dated 2026-06-08 (https://astaspice.org/safe-view/2481182; 13-page PDF,
sha256 bcdbc5ba387f6c141546ab680028d16d44a2be3133447f1d5db3e63852515f70 of the extracted
text). These are **voluntary industry guidance**, not law — the document itself says
"compliance with it is solely at the discretion of the user" — and ASTA set them to mirror
the EU's 2021 regulatory limits for lead in spices. They sit **near background**: the same
document reports that CCCF found background lead in spices typically runs 0.4–3 ppm.

ASTA V3, Table 2 (per plant-part category, maximum level for lead):

| ASTA spice category          | Level (ppm = mg/kg = µg/g) |
|------------------------------|-----------------------------|
| Fruit spices                 | 0.60 |
| Seed spices (and dried aril) | 0.90 |
| Bud spices                   | 1.0  |
| Flower pistil spices         | 1.0  |
| Root and rhizome spices      | 1.50 |
| Bark spices                  | 2.0  |
| Herbs (Table 3)              | 2.0  |

Note: for **turmeric** (root/rhizome) the ASTA level, 1.5 µg/g, is *stricter* than India's
FSSAI limit of 10 µg/g.

**Prior art (checked 2026-10-18).** A web search for a per-sample exceedance analysis of
open lab data against ASTA V3 returned ASTA's own document, Pure Earth's hosting of the
2024 version, vendor explainers (Smith & Truslow, Certified Laboratories, Red Ape Cinnamon)
and a Journal of Regulatory Science article — none of which counts per-sample exceedances of
public datasets against these category levels. ASTA, like FDA, does not publish such counts;
it frames the numbers as voluntary guidance. We found no prior work doing this comparison.

## The question

When you re-score the same open datasets against a *near-background industry guidance* bar
instead of our *gross-adulteration* bar, does the picture change, and how? Two things can
push a sample over an ASTA level: deliberate adulteration (chromate, lead oxide) **and**
ordinary environmental background. The 50-ppm bar sees essentially only the first; the ASTA
bar sees both. So the ASTA bar should (a) lift retail/store exceedance well above the near-
zero gross rate, because background alone brushes the 0.6–0.9 ppm levels, while (b) at a
source market where adulteration is gross, exceedance stays dominated by the same heavily-
contaminated tail.

## Method (to be implemented as a stdlib grader + offline test in a later run)

1. **Category map.** A deterministic, auditable dict maps each spice name to one ASTA
   category and its level: fruit 0.60 (pepper/Piper, chili/paprika/Capsicum, allspice,
   star anise, juniper, sumac); seed/aril 0.90 (cumin, coriander, fennel, fenugreek,
   mustard, caraway, celery seed, anise, dill seed, nigella, sesame, cardamom, ajwain,
   nutmeg, mace); bud 1.0 (clove); flower pistil 1.0 (saffron); root/rhizome 1.50
   (turmeric, ginger, galangal, horseradish, wasabi); bark 2.0 (cinnamon, cassia); herb
   2.0 (oregano, basil, thyme, rosemary, sage, parsley, bay, marjoram, mint, dill weed,
   tarragon, curry leaf). **Blends** (curry/garam masala/"mixed spice") have no single ASTA
   category; they are counted separately under a 2.0 ppm bucket and also reported excluded.
   Any name the map does not cover is listed, not silently dropped.
2. **Exceedance.** A per-sample row counts if its lead result (µg/g) > its category level.
   Units are checked per dataset; CRLF and cp1252 handled as in the existing graders.
3. **Report.** Per frame: n, n categorised, n exceeding, rate, and the breakdown by category.
   Negative/partial results published as-is.

## Frames and pre-registered predictions

Primary test = the two frames that **certainly** carry per-sample lead with a spice name:

- **Frame 3 — NYC store survey, n = 477.** Store-bought spices, NYC DOHMH open lab data.
  Gross (≥ 50 ppm): 2/477 = 0.4%.
- **Frame 15 — raman-reach, n = 503.** Eastern-India market turmeric, Forsyth et al. 2026
  open per-sample table. 152 samples > 10 µg/g (FSSAI); 139 ≥ 50 ppm (27.6%); 105 of the 152
  ≥ 500 ppm; median exceedance 1,294 µg/g.

Conditional, pending a check that it reports per-sample **lead** (the playbook named a "CFIA
retail 2018-19, n=131" frame; the 2018-19 CFIA retail survey I have graded measured synthetic
**dyes**, not lead — frame 8). It is **not** pre-registered here; it is added only if the
grader confirms a lead component.

### Predictions (point estimate, with an 80% interval; these are expectations, not results)

- **Frame 3 (NYC store, 477):** ASTA-level exceedances = **25** (5.2%); 80% interval [8, 55].
- **Frame 15 (raman-reach, 503):** ASTA-level exceedances = **175** (34.8%); hard floor 152
  (every sample over 10 µg/g also clears the 1.5 µg/g turmeric level); 80% interval [152, 210].

### Directional hypotheses (scored true/false)

- **H1.** NYC store ASTA exceedance rate ≥ 3× its gross (≥50 ppm) rate of 0.4% — i.e. ≥ ~1.2%
  (≥ 6 samples). Rationale: ASTA fruit/seed levels (0.6–0.9 ppm) sit inside the 0.4–3 ppm
  background band, so background alone should lift the count well above the gross rate.
- **H2.** raman-reach ASTA exceedance rate > 30% **and** > 3× the NYC store ASTA rate.
  Rationale: at the source the contamination is gross, so the heavily-adulterated tail, not
  background, sets the rate.
- **H3.** In NYC store, most ASTA exceedances fall in the *low* categories (fruit 0.60, seed
  0.90), reflecting background; in raman-reach, exceedances are turmeric (root/rhizome 1.50)
  and far above the level, reflecting adulteration.

## Honest limits, fixed in advance

- ASTA levels are **voluntary industry guidance, not law**, and chosen to match EU limits;
  "exceeds ASTA" ≠ "illegal" and ≠ "unsafe for an individual." We will say this plainly.
- Exceedance against a near-background bar mixes adulteration with ordinary uptake; the
  category breakdown (H3) is how we separate them, not the headline rate.
- The category map is a judgement call at the margins (e.g. cardamom seed vs pod, blends);
  the map is published in full and a sensitivity run excludes blends and unmapped names.
- Different datasets report different detection limits and units; non-detects are treated as
  below level, which makes exceedance a lower bound.
