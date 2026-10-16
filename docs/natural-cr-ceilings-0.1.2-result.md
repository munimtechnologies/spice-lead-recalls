# natural_cr_ceilings 0.1.2: a direct turmeric ICP-MS ceiling, and the regrade it gives

MV2 of Munim, Inc., 2026-10-16. Made with AI agents working in his name. Text CC BY 4.0; code Apache-2.0.

This note reports what happens to the natural-chromium baseline when the ceilings
table is tightened with two directly measured, lead-free spice values, and the
`cr_baseline` screen (version 0.2.0, unchanged) is re-run against them. The whole
regrade is reproducible from the live repository; it was run in a sealed container
before these numbers were written up.

## What 0.1.2 adds

`data/natural_cr_ceilings.csv` lists the highest published *natural* (plant,
trivalent) chromium for each spice and analytical method. Until now its turmeric
row rested on a single commercial ICP-MS survey (range 0.32–1.9 mg/kg), and its
coriander ICP-MS rows came from whole-seed studies.

Version 0.1.2 adds two clean-sample ICP-MS values from Lopez et al. 2022
(Environ Sci Technol 56:16996, PMC9730856), both from spice *powders* whose lead
was at or near zero — so their chromium is natural, not pigment:

- **turmeric TP-01** (Bangladesh): Pb 0.00, Cr 2.88 mg/kg — this raises the
  turmeric ICP-MS ceiling from **1.9 to 2.88 ppm**, a 52 % increase, and it is a
  *direct* turmeric measurement rather than a survey maximum.
- **coriander CP-01** (India): Pb 0.05, Cr 0.22 mg/kg — a third coriander ICP-MS
  value, below the two already in the table (0.129, 0.912).

No other row changes. The CSV remains reproducible-from-main: the build fetches
`data/natural_cr_ceilings.csv` from `main`, appends exactly these two rows, and
emits the bytes committed here.

## The regrade (cr_baseline 0.2.0, pairs sha256 0dd4a2c4685d, ceilings sha256 6f8a9886531d)

Re-running the screen over the 34 chromate-like NYC lead/chromium pairs with the
0.1.2 ceilings leaves every verdict as it was under the 0.2.0 result:

- **34** chromate-like pairs (molar Pb:Cr 0.7–2).
- **32** robust, **2** unresolved — both coriander (2019 Georgia, edge 2.70 ppm;
  2017 Bangladesh coriander powder, edge 5.48 ppm).
- No pair changes verdict.

The one visible effect is on the lowest-chromium turmeric pair, as pre-registered
in [docs/lopez2022-coriander-series.md](lopez2022-coriander-series.md):

- the **2018 Algerian turmeric** pair (Pb 20, Cr 6.1 mg/kg, molar Pb:Cr 0.823,
  edge 3.59 ppm) stays **robust**, but its margin above the highest turmeric
  ceiling tightens from **1.69 ppm** (3.59 − 1.9) to **0.71 ppm** (3.59 − 2.88).

The two high-chromium turmeric pairs (2019 India, edge 209 ppm; 2017 Nepal, edge
301 ppm) remain far above any turmeric ceiling.

## Why this is worth recording

The turmeric baseline is the only place a chromate-like pair sat close to its
natural-chromium ceiling, so it is the place a higher ceiling could have flipped a
verdict. It did not: a direct, lead-free turmeric ICP-MS reading 52 % above the
old ceiling still leaves the Algerian pair's chromium 0.71 ppm beyond what natural
turmeric chromium can explain. The call is tighter than before but it holds.

For coriander the opposite lesson holds. The new ICP-MS value (0.22 ppm) is far
below both unresolved coriander edges (2.70 and 5.48 ppm), so the two "unresolved"
verdicts are driven entirely by the FAAS and ICP-OES *extract* ceilings (12.45 and
18.93 ppm), not by anything ICP-MS measures. That is the same conclusion the
coriander series note reaches from the other direction, and it is why — for
coriander specifically — a hexavalent-chromium speciation test, not a tighter total
chromium ceiling, is the cheaper way to settle such pairs
(see [cr-baseline-0.2.0-result.md](cr-baseline-0.2.0-result.md)).

## Honest limits

These are two single-sample values from one study. TP-01 and CP-01 are clean
references, not a distribution, so 2.88 ppm is a defensible ceiling for turmeric
ICP-MS but not a population maximum. Ceilings are the highest published natural
chromium for each spice and method; they are not limits for any one sample. NYC's
chromium results are total chromium, as sold. A "robust" verdict means the pair's
chromium exceeds what natural plant chromium can explain, not that lead chromate is
proven.

Reproduce: the sealed job fetched `cr_baseline.py`, `test_cr_baseline.py` and
`data/natural_cr_ceilings.csv` from `main`, built 0.1.2, ran the unit tests
(including `test_shipped_ceilings`, which re-grades the eight worked pairs against
the shipped CSV), then re-ran the screen over the live NYC pairs and the Lopez
worked example. See `data/cr_baseline.md` for the full per-pair table.
