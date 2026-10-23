<!-- PREREG-MARKER: coumarin-eu-limits-0.1.1-amendment -->
# coumarin-eu-limits 0.1.1: amendment (unit fix after the G0 gate failed)

By MV2 of Munim, Inc. Made with AI agents working in MV2's name. Code Apache-2.0; this note CC BY 4.0.
Amends [`coumarin-eu-limits-0.1.0-prereg.md`](coumarin-eu-limits-0.1.0-prereg.md). Written and
committed **before** the 0.1.1 re-grade reads the CFIA file. Not individual dietary or medical advice.

## What happened in 0.1.0

The sealed 0.1.0 grading job (`coumarin-eu-limits-v1`, 2026-10-23 13:49-13:52 UTC) ran its offline
tests, waited for the pre-registration to be public, verified the raw file's SHA-256
(`3c8a18c0…f4f`) and graded. **The pre-registered gate G0 failed.** It found 749 measured rows (in
range) but a pooled maximum of **2.51** "mg/kg" where CFIA reports 2,510 mg/kg. All four 0.1.0
grades are recorded as they came out (G0 false, P1 false, P2 false, P3 false). Because G0 failed,
the 0.1.0 values were not in mg/kg, so **P1-P3 were not validly graded in 0.1.0**. That is what the
gate was for.

## Diagnosis

The file's `Unit - Unité` column is **`µg/g`** (micrograms per gram, written with the cp1252
micro sign). Read on 2026-10-23 from the public CSV on `ouvert.canada.ca`, e.g. sample
C2013COUM00299, Spice - Mixed: 2260 µg/g. One µg/g equals one mg/kg. The pre-registered parse rule
listed `µg/kg` (divide by 1000) but not `µg/g`, and 0.1.0 implemented it as "divide if the unit
contains `µg`". That test also matched `µg/g`, so every value was divided by 1000. Every value
in the 0.1.0 output is exactly 1/1000 of the published number: the maximum is 2.51 against 2,510,
and the smallest nonzero values shown are 0.0001, matching CFIA's stated minimum of 0.1 mg/kg. The
unit was read through an automated page reader, so the 0.1.1 job's unit census is the check of
record.

The companion coumarin-tdi study is **not** affected. It does no unit conversion and reads the
`ppm` field of the coumarin-cinnamon table.

## The amendment (only this changes)

1. **Unit conversion by an explicit table**, by dimensional analysis only. The two micro signs
   (U+00B5 and U+03BC) are written as `u`, and spaces are dropped:
   `mg/kg`, `ppm`, `ug/g`, `mcg/g`, blank → ×1; `ug/kg`, `mcg/kg`, `ppb`, `ng/g` → ×0.001;
   `mg/g`, `g/kg` → ×1000; `%` → ×10,000. A trailing parenthetical is ignored if the full string is
   unknown. Any other unit is taken as mg/kg, as in 0.1.0, and counted in a new **unit census**
   (`summary.units`, `n_unrecognised_unit`) so nothing is converted silently.
2. The per-sample output gains a `unit` column.

**Unchanged:** the data file and its SHA-256, the classifier and its 12 rules, the EU limits (15 and
20 mg/kg), the strict `>` comparison, the non-detect rule, and **every threshold of G0, P1, P2 and P3**.

## Disclosure: this re-grade is not blind

The 0.1.0 output listed every value at 1/1000 scale, and it was read before this amendment was
written. The raw values carry one decimal in µg/g, so multiplying by 1000 recovers them exactly.
The re-grade outcome is therefore already known to the authors, and it is stated here **before**
the re-grade runs:

| | implied by 0.1.0 output ×1000 | prediction | implied grade |
|---|---|---|---|
| G0 | 749 rows; pooled max 2,510 mg/kg | rows in [740, 749], max in [2200, 2800] | pass |
| P1 | fine-bakery 42 / 100 over 15 mg/kg = 0.42 | in [0.20, 0.50] | pass |
| P2 | cereal-core 3 / 136 over 20 mg/kg = 0.022 | in [0.03, 0.22] | **fail** (below range) |
| P3 | 0.42 > 0.022 | fine-bakery > cereal-core | pass |

Descriptively: oatmeal 3 / 12 over 20 mg/kg; cereal and oatmeal combined 6 / 148.

So the 0.1.1 job **verifies the fix and the arithmetic**; it does not test the predictions again.
The predictions' honest status is: written blind in 0.1.0, graded with values that were visible
(though at the wrong scale) before this amendment. The thresholds were not changed, including
P2's, which this outcome falsifies. If the sealed re-grade disagrees with the table above, or the
unit census shows any unit other than `ug/g`, the result note will say so and report the job's
numbers.

## Limits

All limits from the 0.1.0 pre-registration still apply. This is a reference comparison, not a
compliance finding. The EU's herbs-and-spices derogation cannot be checked from CFIA's generic
product names. The products are a targeted 2013-14 sample, not market shares.

<!-- PREREG-MARKER: coumarin-eu-limits-0.1.1-amendment -->
