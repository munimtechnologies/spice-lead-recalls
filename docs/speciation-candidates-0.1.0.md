# Which chromate-like spices to confirm first: three Cr(VI) speciation candidates

By MV2 of Munim, Inc. Prepared with AI agents. Text and data CC BY 4.0; code Apache-2.0.

## The question

The open `cr_baseline` analysis finds 34 NYC lab spice pairs whose lead-to-chromium
ratio looks like lead chromate (PbCrO₄), and calls 32 of them **robust**: their chromium
is higher than any published *natural* chromium level for that spice could explain. A
chromate-like ratio far above natural chromium is strong evidence of **added** chromium
with lead, but it does not by itself prove the added compound is lead chromate. Only a
**speciation** test can confirm that. A lab or health department with limited speciation
capacity needs to know *which* samples to send first.

This sheet names the three pairs where confirmation would resolve the most uncertainty.
It adds no new chemistry: every number is taken from the committed
[`data/cr_baseline.csv`](../data/cr_baseline.csv) and
[`data/cr_ceiling_stress.csv`](../data/cr_ceiling_stress.csv), and recomputed by
[`test_speciation_candidates.py`](../test_speciation_candidates.py).

## How the three were chosen (fixed, reproducible rule)

For each robust pair, `k = edge_ppm / highest_natural_ceiling_ppm` is the factor by which
that spice's highest published natural-chromium ceiling would have to be inflated before
the pair stops being robust (see
[cr-ceiling-stress 0.1.0](cr-ceiling-stress-0.1.0-result.md)). The **candidates are the
robust pairs with `k < 5`** — the only ones whose verdict a five-fold error in the
ceilings could overturn. There are exactly three. The median `k` across all 32 robust
pairs is about 56, so these three sit far below the rest.

## The three candidates

| # | Product | Origin | Collected | Pb (ppm) | Cr (ppm) | molar Pb:Cr | natural-Cr ceiling used | k (ceiling headroom) |
|---|---|---|---|---|---|---|---|---|
| 1 | Turmeric | Algeria | 2018-09-24 | 20 | 6.1 | 0.82 | 2.88 (turmeric, ICP-MS) | **1.25** |
| 2 | Spice Mix | Bangladesh | 2017-03-23 | 170 | 38 | 1.12 | 8.59 (generic mix) | **1.94** |
| 3 | Raz El Hanout | Algeria | 2018-10-20 | 2200 | 310 | 1.78 | 8.59 (generic mix) | **3.95** |

- **#1 and #2** can be flipped by a **2-fold** error in the ceilings (`k < 2`). They
  should always be reported as "robust *only if* the published natural-chromium ceilings
  are right to within a factor of about 1.2 (turmeric) and 1.9 (generic mix)", not quoted
  alongside the other 30.
- **#3** survives a 2-fold but not a 5-fold inflation.
- A second, independent sensitivity axis agrees. In
  [cr-band-sensitivity 0.1.0](cr-band-sensitivity-0.1.0.md), tightening the molar Pb:Cr
  band edge from 2.0 to 1.5 moves **only** Raz El Hanout (out of the band) and the
  Algerian turmeric (to unresolved) — the same two Algerian samples. So these pairs are
  the most sensitive both to the natural-chromium ceiling *and* to where the chromate band
  is drawn. They are the right place to replace a modelled verdict with a measured one.

## What to measure

A confirmed lead chromate needs lead **and** hexavalent chromium in the same sample:

- **Lead** — a sodium-rhodizonate spot test is a fast field confirmation; the lab ICP
  value is already in the table.
- **Hexavalent chromium, Cr(VI)** — the diphenylcarbazide (DPC) colorimetric test on an
  acid extract is specific to Cr(VI). A positive DPC alongside the lead is consistent
  with PbCrO₄.
- **Direct identification** — Raman spectroscopy on the solid shows the lead-chromate
  chromate band near 840 cm⁻¹, identifying the compound without extraction. This is the
  same signal the pocket screen this repository supports looks for.

If a Cr(VI) result is obtained, the open `cr_baseline` 0.2.0 gate records it: a positive
result upgrades the pair to **Cr(VI)-confirmed**, and a negative result is treated as
**non-exculpatory** (chromate can be reduced or missed in extraction), not as a clearance.

## Honest framing

These three are the **least certain** chromate-like pairs, not the **worst**. The heavily
contaminated samples — thousands of ppm of lead with chromium to match, `k` in the
hundreds (e.g. a Georgian "TMT Khmeli Suneli" at 78,000 ppm lead, `k` ≈ 607) — are
near-certain added chromium and need no confirmation before a health department acts on
them. The value of speciation here is narrow and specific: it turns three modelled "robust"
calls, each resting on one published ceiling, into measured facts, and it closes the two
open coriander cases the model leaves "unresolved" (both Georgian/Bangladeshi coriander,
where natural chromium genuinely overlaps the observed level).

## Limits

- One sample per pair; lab values are reported to two significant figures.
- The turmeric ceiling (2.88 ppm) is the ICP-MS value from
  [natural_cr_ceilings 0.1.2](natural-cr-ceilings-0.1.2-result.md); the generic 8.59 ppm
  ceiling covers mixes whose exact ingredients are unknown.
- A speciation test needs physical access to the archived sample, which this analysis does
  not have; this sheet is a prioritisation for whoever holds them.
