# cr-band-sensitivity 0.1.0: does "32 of 34 robust" depend on the band edge or on rounding?

**Author:** MV2, Munim, Inc. (mv2@munimtech.com). Work made with AI agents.
**License:** text and data CC BY 4.0; code Apache-2.0.
**Status:** a descriptive sensitivity table. It was **not** pre-registered and grades no
predictions. It closes the two limits that the
[ceiling stress test](cr-ceiling-stress-0.1.0-result.md) left open.

## Question

`cr_baseline` calls a NYC spice lead/chromium pair **chromate-like** when its molar Pb:Cr
ratio lies in 0.7-2.0. It then asks whether the spice's own chromium could explain the
pair. The `edge` is the most natural chromium that could be subtracted before the ratio
rises above the band's upper edge R = 2.0. If the edge is above every published natural
ceiling for that spice, the pair is **robust**. Two choices in that pipeline were never
varied:

1. **The upper edge R = 2.0.** What if the band were tighter (1.5) or looser (3.0)?
2. **The lab values.** NYC reports lead and chromium to two significant figures. What if
   each pair's true values sit at the worst end of their rounding interval?

## Why these edges

The upper edge stands for "lead chromate plus some extra lead". The common lead chromate
pigments have different molar Pb:Cr ratios:

| pigment | formula | molar Pb:Cr |
|---|---|---|
| chrome yellow | PbCrO4 | 1.0 |
| lead sulfochromate yellow (C.I. Pigment Yellow 34), example grades | 5 PbCrO4 · 2 PbSO4 / 3 PbCrO4 · 2 PbSO4 | 1.4 / 1.67 |
| chrome orange, basic lead chromate (C.I. Pigment Orange 21) | PbCrO4 · PbO = Pb2CrO5 | 2.0 |

Sources: [ColourLex, chrome orange](https://colourlex.com/timeline/chrome-orange/);
[ECHA, lead sulfochromate yellow](https://echa.europa.eu/documents/10162/099b01a2-6ca4-440a-500d-81aa7c23ab7d);
example sulfochromate grades as listed by [ChemBK](https://www.chembk.com/en/chem/lead%20sulfochromate%20yellow).
Commercial sulfochromate compositions vary. Forsyth et al. 2019
([Environ Res, PubMed 31550596](https://pubmed.ncbi.nlm.nih.gov/31550596/)) measured
Bangladeshi yellow pigments at a mean molar Pb:Cr of about 1.3. They read this as a
PbCrO4-based compound with additional lead compounds.

So R = 2.0 is exactly pure chrome orange. R = 1.5 would exclude chrome orange and the
sulfate-rich yellows, so it is chemically too tight and is shown only as a stress case.
R = 3.0 allows for extra lead from other sources.

## Method

- Input: the committed [`data/cr_baseline.csv`](../data/cr_baseline.csv) (34 pairs, with
  each spice's highest and lowest published ceiling) and
  [`data/nyc_spice_pb_cr_pairs.csv`](../data/nyc_spice_pb_cr_pairs.csv) (all 61 NYC
  pairs, used to look for pairs a wider band would admit).
- For R in {1.5, 2.0, 3.0}: `edge_R = Cr - (Pb / 207.2) / R * 51.996`, then the same verdict
  rule as `cr_baseline`. A pair whose own ratio is above R is **outside-band**.
- `r_crit = (Pb / 207.2) * 51.996 / (Cr - highest_ceiling)` is the smallest upper edge at
  which the pair is still robust: it is robust exactly when R > r_crit. It is empty when the
  measured chromium is itself at or below the highest ceiling, because then no edge helps.
- Worst-case rounding at R = 2.0: lead **up** and chromium **down** by half a unit in the
  second significant figure (Pb 20 becomes 20.5, Cr 6.1 becomes 6.05). This gives the
  smallest possible edge.
- Code: [`cr_band_sensitivity.py`](../cr_band_sensitivity.py). Output:
  [`data/cr_band_sensitivity.csv`](../data/cr_band_sensitivity.csv). Test:
  [`test_band_sensitivity.py`](../test_band_sensitivity.py) recomputes every value from the
  committed inputs and pins every count below. It must pass before this note is committed.

## Result

| upper edge R | chromate-like | robust | unresolved | background-limited | new pairs admitted |
|---|---|---|---|---|---|
| 1.5 | 33 | 30 | 3 | 0 | none |
| **2.0 (operating)** | **34** | **32** | **2** | **0** | - |
| 3.0 | 34 | 32 | 2 | 0 | none |
| 2.0, worst-case rounding | 34 | 32 | 2 | 0 | - |

- **Widening the band changes nothing.** At R = 3.0 every edge grows, so all 32 robust
  verdicts hold. No new pair enters: the nearest judged NYC pair above the band is a 2024 ground
  cinnamon at molar Pb:Cr 3.21 (23 ppm lead).
- **Tightening to 1.5 moves exactly two pairs.** These are the only two robust pairs
  with r_crit above 1.5:
  - **Raz El Hanout, Algeria (2018).** Its ratio of 1.78 is above 1.5, so it leaves the band
    entirely (r_crit 1.832). This is the robust pair closest to chrome orange's 2.0.
  - **Turmeric, Algeria (2018).** Its edge drops to 2.75 ppm, below the 2.88 ppm turmeric
    ICP-MS ceiling, so it becomes unresolved (r_crit 1.559).
- **All 32 robust verdicts hold for any upper edge above 1.832**, and 30 of them for any
  edge above 1.451. The operating edge of 2.0 therefore has about 9% headroom over the
  tightest pair.
- **Rounding changes no verdict.** In the worst case the smallest headroom is the Algerian
  turmeric (edge 3.48 vs 2.88 ppm, 1.21x), then the Bangladeshi spice mix (15.54 vs 8.59
  ppm, 1.81x).
- **The two coriander pairs are unresolved at every edge.** Their measured total chromium
  (9.1 and 12 ppm) is already below the FAAS ceiling of 18.93 ppm, so no choice of band can
  make them robust (r_crit is empty). Only method-matched ceilings or a Cr(VI) test can
  settle them, as [the coriander notes](coriander-chromium.md) argue.
- Most robust pairs sit where the pigment does. 27 of the 32 have molar Pb:Cr between 1.0
  and 1.4 (median 1.161). That matches the roughly 1.3 Forsyth et al. measured in the yellow
  pigment itself.

## What it means

The headline still stands after both checks. Three pairs carry most of its fragility, and
they are the same pairs in every check:

| pair | ceiling headroom k (stress test) | r_crit (band edge) | worst-case rounding headroom |
|---|---|---|---|
| Turmeric, Algeria (2018) | 1.25 | 1.559 | 1.21x |
| Spice Mix, Bangladesh (2017) | 1.94 | 1.451 | 1.81x |
| Raz El Hanout, Algeria (2018) | 3.95 | 1.832 | 2.64x |

These three should be reported with their caveats rather than in the same breath as the
others, and they are the first candidates for a Cr(VI) speciation test. The `cr_baseline`
0.2.0 gate would use such a result directly. The other 29 robust verdicts survive a 2-fold
ceiling error, any upper edge above 1.451 (up to 3.0, the widest tested) and worst-case
rounding.

## Prior art and limits

- Published work uses a molar Pb:Cr "near 1:1" as evidence of lead chromate (Forsyth et al.
  2019; Forsyth et al. 2024, [Sci Total Environ](https://www.sciencedirect.com/science/article/pii/S0048969724051532)).
  We found no published sensitivity analysis of where the band's upper edge sits, or of
  rounding, for verdicts made from lab Pb/Cr pairs. This is a check on MV2's own screen,
  not a new chemical result.
- One edge at a time. We did not search jointly over edge, ceilings and rounding. The
  three-way table above is read off the separate checks.
- The lower edge (0.7) is not varied. Subtracting natural chromium only raises the ratio,
  so it does not affect robustness. It does decide which chromium-rich pairs count as
  chromate-like, and no NYC pair currently sits below it.
- "Two significant figures" is our reading of how NYC reports these 34 pairs (every value
  has at most two). It is not a stated lab uncertainty. Real analytical error may be
  larger.
- A chromate-like, robust pair is strong evidence of added chromium with lead. It does not
  prove the compound is lead chromate. Only speciation or Raman can confirm that.

_Prepared by AI agents working in MV2's name. Data from the NYC Department of Health
spice lab table (via the committed CSVs). Every count here is recomputed by
`test_band_sensitivity.py`._
