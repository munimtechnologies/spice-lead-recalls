# Pre-registration: cr_baseline 0.2.0 — a Cr(VI) speciation flag

Written **before** the code, so the design and its success criteria cannot be
adjusted after seeing the output. It specifies one planned change to
`cr_baseline.py` and the exact predictions (P0–P4) by which the implementing run
will be graded. A failed prediction is reported as failed.

By MV2 of Munim, Inc. Text CC BY 4.0. Made with AI agents working in MV2's name.
Companion to `cr_baseline.py` and `docs/coriander-chromium.md`.

Date written: 2026-10-16.

## Background and the gap this fills

`cr_baseline.py` 0.1.0 asks whether a spice's own natural chromium could account
for a chromate-like molar Pb:Cr ratio, by subtracting a published natural-chromium
ceiling for that spice and ruling a pair **robust**, **unresolved** or
**background-limited**. That test uses only *total* chromium. It cannot tell
Cr(III), which is what plants carry, from Cr(VI), which is the oxidation state of
the lead-chromate pigment (PbCrO₄). For coriander the two published ceiling
ranges straddle the signal, so both NYC coriander pairs come out **unresolved**
(see `docs/coriander-chromium.md`), and a worked example from Lopez et al. 2022
(a Patna coriander powder, 87 mg/kg Pb / 13 mg/kg Cr, molar ratio 1.68) whose
chromium was *shown to be hexavalent by a diphenylcarbazide (DPC) colour test*
would also come out unresolved by ceilings alone — the ceiling-only rule gets a
Cr(VI)-confirmed sample wrong.

Speciation resolves exactly this: natural plant chromium is Cr(III); a positive
Cr(VI) result on the product is evidence of added chromate that no total-chromium
ratio can give.

## Prior art (so the novelty claim is honest and narrow)

Using Cr(VI)/DPC speciation as a proxy for lead-chromate adulteration is **not
new**. It is the method of Lopez et al. 2022 (*Environ Sci Technol* 56:16996),
and the Pb:Cr ≈ 1 molar fingerprint is used by the same group and by the
Bangladesh, cinnamon (Kubachka & Witkowski) and Ecuadorian-spice studies.

What does **not** appear in that literature, and what this increment adds, is a
single open, reproducible tool that combines both lines of evidence into one
auditable verdict per sample: a total-chromium ceiling test **and** an optional
Cr(VI) speciation gate, with every ceiling sourced to a primary paper and every
rule in tested code. 0.2.0 is a tool-integration step, not a new chemical
finding; it is pre-registered to keep it honest, not because the chemistry is
novel.

## The planned change

1. `cr_baseline.py` gains an **optional** per-pair input column `cr6_result`
   with three allowed values:
   - `positive` — a Cr(VI) test on this product was positive;
   - `negative` — a Cr(VI) test was run and was negative;
   - empty / column absent — no speciation data (the 0.1.0 situation).
   Any other value is an error (the run stops with a clear message).

2. The existing ceiling-based verdict is kept unchanged and renamed in the
   output to `baseline_verdict` (same three values, same arithmetic). A new
   column `speciation` records the three states above (`untested` when empty),
   and a new column `final_verdict` is derived:
   - `cr6_result == positive`  → `final_verdict = "cr6-confirmed"`,
     **regardless** of `baseline_verdict`;
   - `cr6_result == negative`  → `final_verdict = baseline_verdict`
     (a negative DPC is **not** exculpatory: Lopez et al. report a 167 mg/kg-Pb
     coriander powder that developed no colour, so absence of colour is not
     absence of chromate);
   - untested → `final_verdict = baseline_verdict` (identical to 0.1.0).

3. `cr6-confirmed` means "hexavalent chromium confirmed present on the product",
   not "lead chromate proven". The markdown output will state this in words and
   will cite the DPC limit above.

4. The summary counts both `baseline_verdict` and `final_verdict`, so a reader
   sees what speciation changed and what it did not.

## Predictions (graded P0–P4)

- **P0 — backward compatibility.** Run 0.2.0 on the live NYC pairs CSV with **no**
  `cr6_result` column. The per-pair `baseline_verdict` values and their counts are
  **identical** to a 0.1.0 run on the same inputs; `final_verdict` equals
  `baseline_verdict` for every row; `speciation` is `untested` for every row.
  (If P0 fails, the change is not backward-compatible and must be fixed before
  grading the rest.)
- **P1 — positive gate.** A pair with `cr6_result = positive` gets
  `final_verdict = cr6-confirmed` whatever its `baseline_verdict`
  (robust, unresolved or background-limited). Tested on all three baseline cases.
- **P2 — negative is not exculpatory.** A pair with `cr6_result = negative` keeps
  `final_verdict = baseline_verdict` and records `speciation = negative`.
- **P3 — Lopez worked example.** The Lopez 2022 Patna coriander powder
  (Pb 87, Cr 13, matrix coriander), entered with `cr6_result = positive`, yields
  `baseline_verdict = unresolved` (edge 2.08 ppm, below the flame-AAS and
  ICP-OES coriander ceilings) **and** `final_verdict = cr6-confirmed`. This is
  the case the ceiling-only rule gets wrong and speciation gets right.
- **P4 — NYC verdicts unchanged.** On the real NYC pairs (which carry no Cr(VI)
  data), the chromate-like, robust and unresolved counts match the
  `spice-cr-baseline` pre-registration (34 chromate-like, 32 robust, 2
  unresolved — the two coriander pairs). 0.2.0 adds no speciation data to NYC, so
  it must not change any NYC verdict.

Honest expectation stated up front: because no NYC pair has a Cr(VI) result,
0.2.0 **changes nothing about the NYC conclusions**. Its value is (a) a correct
verdict on the Lopez worked example, and (b) a documented, tested slot so that a
future DPC or laboratory speciation result on any product can be folded in
without re-litigating the rules. This limitation will be stated plainly in the
shipped output and README, not hidden.

## Tests to be written (committed with the code, `test_first`)

- `test_backward_compat_no_cr6_column`: output on a CSV without the column equals
  the 0.1.0 verdicts (P0).
- `test_positive_overrides_each_baseline`: positive → cr6-confirmed for a
  robust, an unresolved and a background-limited fixture (P1).
- `test_negative_not_exculpatory`: negative leaves the baseline verdict, flags
  `negative` (P2).
- `test_lopez_coriander_example`: the 87/13 coriander row, positive, →
  unresolved baseline, cr6-confirmed final (P3).
- `test_bad_cr6_value_errors`: an unexpected `cr6_result` value raises.
- the existing 0.1.0 tests continue to pass unchanged.

## What will ship if it passes

- `cr_baseline.py` 0.2.0 + its tests (`test_first`), committed only if the tests
  pass in the sealed runner.
- `data/cr_baseline.md` / `.json` / `.csv` regenerated from the live NYC run
  (exact bytes from the job's `out/`), showing the new columns with every NYC row
  `untested` and P0/P4 holding.
- a short README pointer and a one-line note in `docs/coriander-chromium.md`
  linking the Lopez worked example to the new `cr6-confirmed` verdict.

## What will NOT change

- No ceiling values change; `data/natural_cr_ceilings.csv` is untouched by this
  increment.
- No NYC verdict changes.
- The `cr6-confirmed` label never asserts "lead chromate proven", only "Cr(VI)
  present on the product".

## References

- Lopez AM, et al. Assessing analytical methods for the rapid detection of lead
  adulteration in the global spice market. *Environ Sci Technol* 56(23):16996
  (2022). doi:10.1021/acs.est.2c03241. PMC9730856. (ICP-MS, pXRF and DPC; DPC
  detects Cr(VI); one 167 mg/kg-Pb coriander gave no colour.)
- See `docs/coriander-chromium.md` for the full method-stratified coriander
  chromium compilation and the Lopez worked example.

Contact: MV2, Munim, Inc. — mv2@munimtech.com
