<!-- RESULT-MARKER: coumarin-tdi-0.1.0 -->
# coumarin-tdi 0.1.0 — result

**How small a serving of Canadian retail cinnamon reaches the EFSA tolerable daily intake (TDI) for coumarin?**

By MV2 of Munim, Inc. Made with AI agents working in MV2's name. Code Apache-2.0; this note and
`data/coumarin_tdi_samples.csv` CC BY 4.0. Contains information licensed under the Open Government
Licence – Canada (CFIA).

Graded against [`coumarin-tdi-0.1.0-prereg.md`](coumarin-tdi-0.1.0-prereg.md), which was public
on GitHub (tag `v0.4.35`) before the sealed job read any CFIA row: the job's `check_prereg.py`
step confirmed the pre-registration marker on `main` first, then `coumarin_tdi.py` downloaded and
graded the data. Nothing was changed after grading.

This is an **information/research note, not individual dietary or medical advice.** The TDI is a
population guidance value for lifelong daily intake, not an acute-hazard threshold.

## Headline

Across **176** CFIA retail cinnamon samples (2011–2016), the **median** sample reaches a 60 kg
adult's coumarin TDI (6 mg/day) in **1.80 g** of cinnamon, and a 15 kg child's (1.5 mg/day) in
**0.45 g**. **88%** of samples (155 of 176) put a 60 kg adult over the TDI with one level teaspoon
(2.6 g); **97%** (170 of 176) do so for a 15 kg child.

## Pre-registered predictions: 4 of 4 held

| ID | Kind | Prediction | Observed | Held? |
|----|------|-----------|----------|-------|
| G0 | parse gate | n ≥ 120 and pooled max ppm in [7000, 8200] | n = 176, max = 7816.3 ppm | yes |
| P1 | primary | median adult (60 kg) serving-to-TDI < 3.0 g | 1.796 g | yes |
| P2 | test | ≥ 25% of samples reach adult TDI in < 2.0 g (ppm > 3000) | 69.3% (122 of 176) | yes |
| P3 | anticipated | > 80% of samples put a 15 kg child over TDI at one teaspoon (ppm > 577) | 96.6% (170 of 176) | yes |

G0 only confirms that the reused `coumarin_cinnamon.py` loader (pinned at `v0.4.34`) reproduced
the companion study's sample set (176 samples; pooled maximum 7816.3 ppm, a 2011–12 Vietnamese
ground cinnamon). P3 was marked *anticipated* in advance: it follows almost directly from the
companion finding that 168 of 176 samples are cassia-type, so it is a confirmation, not a
discovery. P1 and P2 were the genuinely untested predictions, and both cleared their thresholds
by a wide margin.

## Distribution

| | value |
|---|---|
| samples (2011–12 / 2012–13 / 2015–16) | 176 (107 / 40 / 29); the 2014–15 file (titled cinnamon-*containing* products) contributes no sample flagged as cinnamon itself |
| coumarin, min / median / max | 6.2 / 3339.9 / 7816.3 ppm |
| adult (60 kg) serving-to-TDI, most concentrated sample | 0.77 g |
| adult serving-to-TDI, median | 1.80 g |
| child (15 kg) serving-to-TDI, median | 0.45 g |
| cassia-type samples (168): adult serving-to-TDI | 0.77–4.73 g |
| intermediate samples (3): adult serving-to-TDI | 6.98–11.36 g |
| verum/Ceylon-type samples (5): adult serving-to-TDI | 293–968 g |

The split is stark: for the 5 verum-type (Ceylon) samples an adult would need hundreds of grams a
day to reach the TDI; for every one of the 168 cassia-type samples it is under 5 g.

## Sensitivity (exploratory, not pre-registered)

These were computed after grading from the committed sample table and are checked by
`test_coumarin_tdi_result.py`. They do not change any grade.

- **70 kg adult instead of 60 kg:** median serving-to-TDI 2.10 g; 44.3% of samples (78 of 176)
  still reach the TDI in under 2.0 g. P1 would still hold (< 3.0 g) and so would P2 (≥ 25%).
- **Teaspoon mass 2.3 g or 2.8 g instead of 2.6 g:** one teaspoon puts a 60 kg adult over the TDI
  for 150 or 157 of 176 samples (85% / 89%), and a 15 kg child for 169 or 170 (96% / 97%).
- **Ground cinnamon only (156 samples; drops the 20 stick samples, which are usually infused
  rather than eaten):** median adult serving-to-TDI 1.75 g; 74.4% (116 of 156) under 2.0 g;
  97.4% (152 of 156) put a 15 kg child over the TDI at one teaspoon.

## How this fits prior work

The arithmetic itself is not new. Germany's Federal Institute for Risk Assessment (BfR) gives the
same illustration for an *assumed average* cassia content of about 3000 mg/kg: a 60 kg adult reaches
the TDI with about 2 g a day and a 15 kg child with about 0.5 g. European exposure studies
(Norway's porridge scenario, Danish market surveys) reached similar conclusions on European samples.
What this note adds is the **per-sample** version on **CFIA's open Canadian measurements**, which
CFIA's own reports do not compute: the Canadian median sample (3339.9 ppm) is slightly more
concentrated than BfR's 3000 mg/kg average, so its serving-to-TDI (1.80 g adult, 0.45 g child) is
slightly smaller than BfR's illustrative 2 g and 0.5 g, and the full table lets anyone recompute
with their own body weight, serving size or guidance value.

## Limits

- Population guidance value, not individual advice. EFSA notes that intake up to three times the
  TDI for one to two weeks is not a safety concern; the TDI concerns sustained daily intake.
- Single-food assumption: coumarin from other foods eaten the same day is not added, which would
  make the real serving-to-TDI smaller.
- Body weights and teaspoon mass are illustrative point values (see sensitivity above).
- Stick samples are included in the pre-registered set; their coumarin is only partly extracted
  when infused, so their servings overstate intake from sticks (the ground-only check addresses this).
- CFIA product names are generic and 118 of 176 samples have no declared country of origin, so
  these are retail-level population figures for 2011–2016, not brand, lot or present-day statements.

## Reproduce

```
python coumarin_tdi.py --out-dir out          # downloads the four CFIA CSVs via coumarin_cinnamon.py
python -m unittest -v test_coumarin_tdi        # offline arithmetic and grading tests
python -m unittest -v test_coumarin_tdi_result # recomputes every number above from data/coumarin_tdi_samples.csv
```

`data/coumarin_tdi_samples.csv` is the sealed job's own output (one row per graded sample, sorted
by coumarin, with the adult and child serving-to-TDI in grams).

<!-- RESULT-MARKER: coumarin-tdi-0.1.0 -->
