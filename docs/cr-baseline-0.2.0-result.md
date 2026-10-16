# cr_baseline 0.2.0: result of the pre-registered Cr(VI) speciation gate

MV2 of Munim, Inc., 2026-10-16. Made with AI agents working in his name. Text CC BY 4.0; code Apache-2.0.

This reports the outcome of the design pre-registered in
[docs/cr-baseline-0.2.0-prereg.md](cr-baseline-0.2.0-prereg.md), run in a sealed
container before these numbers were written up.

## What 0.2.0 adds

`cr_baseline.py` asks whether a spice's own (natural, trivalent) chromium could
explain a chromate-like molar Pb:Cr pair. Version 0.1.0 answered from total
chromium and published natural-chromium ceilings alone. Natural plant chromium is
Cr(III); the lead-chromate pigment PbCrO4 is Cr(VI). A total-chromium ratio cannot
tell them apart, but a diphenylcarbazide (DPC) or laboratory speciation test can.

Version 0.2.0 adds an optional per-pair `cr6_result` column (`positive`,
`negative`, or empty). A **positive** test confirms hexavalent chromium on the
product and overrides the ceiling-only verdict as `cr6-confirmed`. A **negative**
test is *not* exculpatory — Lopez et al. 2022 report a 167 mg/kg-Pb coriander that
developed no DPC colour — so it leaves the baseline verdict unchanged. An empty
column or no column reproduces the 0.1.0 behaviour exactly.

## Pre-registered predictions, all met in the sealed run

- **P0 — backward compatibility.** With no `cr6_result` column, every pair is
  `untested` and its final verdict equals its baseline verdict; the NYC baseline
  counts are unchanged from 0.1.0.
- **P1 — positive overrides every baseline.** A `positive` test maps a robust, an
  unresolved and a background-limited baseline all to `cr6-confirmed`.
- **P2 — negative is recorded but not exculpatory.** A `negative` test keeps the
  baseline verdict.
- **P3 — Lopez worked example.** The Patna coriander powder (Pb 87, Cr 13 mg/kg,
  molar Pb:Cr 1.68, Cr(VI) positive by DPC; Lopez et al. 2022, Environ Sci Technol
  56:16996, PMC9730856) is `unresolved` by ceilings alone (edge 2.08 ppm) but
  `cr6-confirmed` once its speciation result is folded in.
- **P4 — bad input errors.** A `cr6_result` value outside the allowed set raises.

All pass in `test_cr_baseline.py`, which the publish lane re-ran before this commit.

## NYC result (unchanged, as predicted)

No NYC pair carries a Cr(VI) result, so 0.2.0 changes no NYC verdict. The 34
chromate-like NYC pairs split 32 robust / 2 unresolved, identical to 0.1.0. The two
unresolved pairs are both coriander (2017 Bangladesh coriander powder, edge 5.48
ppm; 2019 Georgia coriander, edge 2.70 ppm): above every ICP-MS ceiling but at or
below the ICP-OES and FAAS coriander ceilings, so the verdict depends on the
analytical method. See `data/cr_baseline.md` for the full table.

`cr6-confirmed` means hexavalent chromium was confirmed present on the product, not
that lead chromate is proven. 0.2.0's value is a correct call on the Lopez worked
example and a tested slot for future speciation data.
