# Twelve coriander powders by ICP-MS: how much of their chromium is natural?

MV2 of Munim, Inc., 2026-10-16. Made with AI agents working in his name. Text CC BY 4.0.

**Why.** NYC's two coriander pairs are the only chromate-like pairs that `cr_baseline.py` leaves "unresolved"
(README section 2): Georgia 2019 (Pb 51, Cr 9.1 ppm, edge 2.70) and Bangladesh 2017 (Pb 52, Cr 12, edge 5.48). Their
edges sit above the ICP-MS values for natural chromium in coriander (0.13 and 0.91 ppm) but below the ICP-OES and
flame AAS values (12.45 and 10.8-18.9 ppm). [coriander-chromium.md](coriander-chromium.md) gathers the published
whole-seed values. This page adds the one series we know of in which one laboratory measured lead and chromium by
ICP-MS on coriander powders running from clean to laced.

**Source.** Lopez et al. Assessing analytical methods for the rapid detection of
lead adulteration in the global spice market. *Environ Sci Technol* 56:16996 (2022), doi:10.1021/acs.est.2c03241,
PMC9730856. Supporting Information Table S1 (`es2c03241_si_001.pdf`, sha256 `f5ed50d02b0a...`), text extracted in
the sealed job `turmeric-forsyth-pbcr-v1`. The rows below are factual values quoted from that table with
attribution (the article is CC BY-NC-ND 4.0); they are not relicensed here.

## The coriander rows (Patna, India, 2020; ICP-MS, mg/kg)

| sample | Pb | Cr | molar Pb:Cr | DPC colour test |
|---|---|---|---|---|
| CP-01 | 0.05 | 0.22 | 0.06 | none |
| CP-10 | 7.99 | 1.77 | 1.13 | none |
| CP-02 | 35 | 6.52 | 1.37 | none |
| CP-04 | 47 | 8.80 | 1.33 | none |
| CP-05 | 51 | 11 | 1.13 | none |
| CP-06 | 85 | 18 | 1.18 | none |
| CP-07 | 87 | 13 | 1.63 | slight |
| CP-09 | 114 | 24 | 1.20 | slight |
| CP-12 | 143 | 27 | 1.33 | slight |
| CP-03 | 167 | 37 | 1.14 | none |
| CP-11 | 177 | 35 | 1.26 | slight |
| CP-08 | 250 | 46 | 1.38 | slight |

## What it shows

1. **Chromium follows lead at the lead chromate ratio from 8 to 250 mg/kg.** All 11 samples with Pb >= 5 have
   molar Pb:Cr 1.13-1.63 (lead chromate = 1; chrome yellows cut with lead sulfate run above 1). Lopez et al. report
   this for all spices together (median 1.26); the coriander-only series is in their table, not their text.
2. **The background these samples allow is about 0.3 ppm, not 10-19.** A least-squares line through the 12 points
   gives Cr = 0.28 + 0.193 x Pb (mg/kg). The slope is a molar Pb:Cr of 1.30. The intercept, the chromium left at
   zero lead, is **0.28 ppm (95% interval about -2.1 to +2.7)**. Two samples bound it directly: the clean one (CP-01)
   holds 0.22 ppm chromium in total, and the one with 8 ppm lead (CP-10) holds 1.77 ppm in total, pigment included.
   A natural background of 10.8-18.9 ppm (the flame AAS ceilings) cannot fit either. This agrees with the two
   whole-seed ICP-MS values (0.13, 0.91), the hydride-generation AAS value (0.46-0.55) and the neutron activation
   value (< 0.35) in coriander-chromium.md, and now in powder of South Asian origin.
3. **Same lead, same chromium as the NYC pairs.** CP-04 (Pb 47, Cr 8.80) and CP-05 (Pb 51, Cr 11) sit beside NYC's
   Georgia (51, 9.1) and Bangladesh (52, 12) coriander. In Lopez's series those levels are lead chromate on a ~0.3
   ppm background.
4. **What it does to the NYC verdicts: nothing, by rule.** `cr_baseline.py` compares each edge with every published
   ceiling for the spice and calls a pair unresolved while any ceiling is at or above the edge. The flame AAS and
   ICP-OES ceilings still stand, so both pairs stay unresolved; we do not change the rule after seeing this. Read as
   evidence, the series points one way: the Bangladesh pair's edge (5.48) is twice the upper end of the interval
   above, while the Georgia pair's edge (2.70) sits right at it, so the fit alone cannot settle Georgia.

## A side count: the colour test misses half

cr_baseline 0.2.0 treats a negative diphenylcarbazide (DPC) colour test as not exculpatory. Table S1 puts a number on
that. Of the 50 samples (all spices, powders and roots) with Pb >= 50 mg/kg, every one has an ICP-MS molar Pb:Cr of
0.93-1.89. **27 gave a slight or clear colour, 3 a transient one, and 20 none**, including all 8 red chilis (54-240
mg/kg Pb) and all 6 Svaneti salts (86-2,496 mg/kg). For coriander, 5 of the 8 with Pb >= 50 coloured. Lopez et al.
describe these misses spice by spice (red background in chili; matrix interference in salt); the tally across the
table is ours.

## Limits

- One laboratory, one city, one year; 12 samples, of which only one is clean. The interval on the intercept is wide
  because the fit leans on laced samples.
- Values are as printed (two or three significant figures, e.g. "11", "13"); the fit carries that rounding.
- Ordinary least squares; the scatter grows with lead, which a weighted fit would handle differently. The two direct
  bounds (0.22 and 1.77 ppm total chromium) do not depend on the fit.
- Powder, not whole seed; Lopez et al. do not say whether the powders were bought loose or packaged.
- This is Indian coriander. Neither NYC pair is origin-matched (Georgia, Bangladesh), so an origin-matched ICP-MS
  blank is still the clean test.

## Next (pre-registered here, before any run)

Lopez Table S1 also gives clean-sample ICP-MS chromium for other spices: turmeric powder TP-01 (Bangladesh, Pb 0.00,
Cr 2.88), coriander CP-01 (0.22), blue fenugreek BF-05/06 (1.54, 0.92), khmeli suneli KS-01/02 (1.43, 0.62) and
Svaneti salt SS-05/06/08 (0.49, 0.25, 0.31). Adding the turmeric and coriander values to
`data/natural_cr_ceilings.csv` (0.1.2) raises the turmeric ICP-MS ceiling from 1.9 to 2.88 ppm and adds a third
coriander ICP-MS value. Predictions for the cr_baseline run on 0.1.2: still 34 chromate-like pairs, 32 robust and the
same 2 coriander pairs unresolved; the Algerian turmeric pair (edge 3.59) stays robust, now 0.71 ppm above its
highest ceiling instead of 1.69.
