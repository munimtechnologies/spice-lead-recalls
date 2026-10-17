# cr-ceiling-stress 0.1.0: how fragile is "32 of 34 robust"? (result)

**Author:** MV2, Munim, Inc. (mv2@munimtech.com). Work made with AI agents.
**License:** text and data CC BY 4.0; code Apache-2.0.
**Pre-registration:** [cr-ceiling-stress-0.1.0-prereg.md](cr-ceiling-stress-0.1.0-prereg.md),
committed before this result. Predictions graded below, failures included.

## Question

The open `cr_baseline` analysis scores the 34 NYC lab spice pairs whose lead:chromium
ratio looks like lead chromate against published natural-chromium ceilings for each
spice. It calls 32 of them **robust**: their chromium is more than any published natural
level for that spice could explain. A fair critic asks how much that depends on the
ceilings being right. If natural chromium is really 2, 5 or 10 times higher than the
literature we used, how many verdicts survive?

## Method (as pre-registered)

For each robust pair, `k = edge_ppm / highest_ceiling_ppm`. Here `edge_ppm` is the most
natural chromium that could be subtracted before the pair's Pb:Cr ratio leaves the
chromate band. `k` is the factor by which that spice's highest published ceiling would
have to be inflated before the pair stops being robust. Because each pair's `k` depends
only on its own spice's ceilings, it also answers the narrower question of one spice's
literature being wrong while the others are right. A pair survives an inflation *s*
when `k > s`.

- Input: committed [`data/cr_baseline.csv`](../data/cr_baseline.csv) (34 pairs).
- Code: [`cr_ceiling_stress.py`](../cr_ceiling_stress.py), a pure transform with no new chemistry.
- Output: [`data/cr_ceiling_stress.csv`](../data/cr_ceiling_stress.csv), one row per robust pair.
- Test: [`test_stress.py`](../test_stress.py) recomputes every `k` from the committed
  input and pins each graded prediction. It must pass before this note can be committed.

## Result

| ceiling inflation *s* | robust pairs still robust (k > s) | share of 32 |
|---|---|---|
| 1.25x | 31 | 97% |
| 1.5x | 31 | 97% |
| 2x | 30 | 94% |
| 3x | 30 | 94% |
| 5x | 29 | 91% |
| 10x | 24 | 75% |

The median `k` is about 56: half of the robust verdicts would survive natural chromium
more than 50 times the highest published value for their spice.

**Only two verdicts can be flipped by a 2-fold error in the ceilings:**

| pair | edge ppm | highest ceiling ppm | k |
|---|---|---|---|
| Turmeric, Algeria (2018) | 3.59 | 2.88 (turmeric, ICP-MS) | 1.2465 |
| Spice Mix, Bangladesh (2017) | 16.67 | 8.59 (generic) | 1.9406 |

The next most fragile is Raz El Hanout from Algeria (k 3.95). Five more fall between
5x and 10x: Cumin Powder from Bangladesh (5.79), Chili powder from Bangladesh (6.37), two
Yemeni spice-mix samples (6.81, 7.39) and Curry Masala from Pakistan (8.83). The other 24
have `k` from 20.7 to 696.

## Predictions, graded

- **H1 (sanity): MET.** 32 robust pairs, all with k > 1. Neither coriander pair is in
  the robust set.
- **H2: MET.** The most fragile robust pair is the Algerian turmeric, k = 1.2465
  (predicted 1.247 ± 0.003).
- **H3 (main): MET.** Doubling every ceiling leaves 30 of 32 robust (predicted ≥ 24).
- **H4: FAILED.** Survivor counts are monotone, as predicted, but 24 pairs survive a
  10-fold inflation against a predicted maximum of 8. We underestimated how far most
  NYC chromate-like pairs sit above any natural background. Most are hundreds to
  thousands of ppm of lead with chromium to match.

## What it means

The "32 of 34" headline does not rest on fine-tuned ceilings. Two verdicts are sensitive:
the low-level Algerian turmeric (20 ppm lead) and a Bangladeshi spice mix judged
against the generic 8.59 ppm ceiling. They should be described as "robust only if the
published ceilings are right within a factor of about 1.2 and 1.9", not reported
alongside the rest. Both are good candidates for a Cr(VI) speciation test, which the
`cr_baseline` 0.2.0 gate would use if a result existed.

## Limits

- Only the ceilings are stressed. The chromate band (`edge_ppm` uses a molar Pb:Cr upper
  edge of 2.0) and lab measurement error in lead and chromium, reported to two
  significant figures, are not varied here.
- 20 of the 32 robust pairs are mixes judged against one generic ceiling (8.59 ppm).
  Their `k` is only as good as that ceiling's coverage of the ingredients actually in
  each mix.
- A chromate-like ratio far above natural chromium is strong evidence of added chromium
  with lead. It does not by itself prove the compound is lead chromate. Only speciation
  can confirm that.
- The black pepper ceiling (0.113 ppm) is low. That pair's k of 91 would still exceed 1
  even if its ceiling were raised to 10 ppm.

_Prepared by AI agents working in MV2's name. Data from the NYC Department of Health
spice lab table (via `cr_baseline.csv`). Every number here is recomputed by
`test_stress.py`._
