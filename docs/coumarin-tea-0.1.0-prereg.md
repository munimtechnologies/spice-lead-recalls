<!-- PREREG-MARKER: coumarin-tea-0.1.0-prereg -->
# coumarin-tea 0.1.0: pre-registration

By MV2 of Munim, Inc. Made with AI agents working in MV2's name. Code Apache-2.0; this note
CC BY 4.0. Data: CFIA 2013-14 coumarin survey (Open Government Licence - Canada).
A bounded exposure screen on open data. It is not a compliance finding (Canada sets no coumarin
limit), not a statement about any brand, and not individual dietary or medical advice.

## Question

For the **cinnamon-containing teas** in CFIA's 2013-14 targeted survey, how much of the tolerable
daily intake (TDI) for coumarin could a single brewed **cup** deliver, **even if every bit of the
coumarin in the dry tea transferred into the cup**?

EFSA's TDI is **0.1 mg coumarin per kg body weight per day** (EFSA 2004, confirmed 2008; BfR uses
the same value). A 60 kg adult's daily budget is 6 mg; a 15 kg child's is 1.5 mg. CFIA measures
coumarin in the *dry* tea (mg/kg); what reaches the drinker depends on how much coumarin leaves
the leaf during steeping. Published extraction yields vary, so this screen fixes transfer at a
**100% upper bound** ("even if all of it came out") - a figure no one can dispute as too high, and
the real cup is always lower. The companion `coumarin-eu-limits` study put tea out of scope (a
beverage carries no EU bakery/cereal limit); this study covers it, on a per-cup basis.

## Data and status of the values (read this first)

- File: CFIA 2013-14 coumarin survey, resource `66d9cd8f-d44d-4993-8775-65da6857250c`, SHA-256
  `3c8a18c0769d81e9580b9f985722ccd24e9db45c72ea9228f3eda8afd3383f4f`, parsed by
  `coumarin_eu_limits.py` 0.1.1 (explicit unit table; every value is `ug/g` = mg/kg).
- The file has **115 rows the classifier labels "tea"**. A names-only census (reading only the
  Product column, never the Result column) confirms the bucket is five genuine dried teas and
  nothing else: **Tea - Herbal (72), Tea - Black (38), Tea - Green (3), Tea - Other (1),
  Tea - White (1)**. No "tea biscuit/cake" or other non-beverage leaked in.
- **The tea values are already public** (the per-sample table published with `coumarin-eu-limits`
  0.1.1 lists all 749 rows, including out-of-scope tea rows), **but no agent has read them.**
  Earlier work read only the bakery, breakfast-cereal and infant-cereal rows. This
  pre-registration was written from the names-only census and from CFIA's **published headline
  figures** for the tea category (below). We cannot prove a negative, so the public commit time of
  this file and of the grading job is the record.
- CFIA's published tea headline for this survey (2013 tea row): **115 samples, minimum 0.3,
  maximum 2,430, average 500 mg/kg, coumarin detected in 99%.** The predictions are grounded on
  these headline figures and the names census only - not on any per-sample value.

## Per-cup scenarios (fixed now)

Coumarin in one cup (mg) = concentration (mg/kg) x dry tea per cup (kg) x transfer. "Over the TDI"
means a **single cup** delivers more than the drinker's **whole-day** budget (strictly above the
threshold concentration below). Non-detects count as 0 mg/kg. Transfer is fixed at 1.0.

| id | drinker | dry tea per cup | concentration that puts one cup over the day's TDI | role |
|---|---|---|---|---|
| A1 | 60 kg adult | 2 g (one standard cup/bag) | 3,000 mg/kg | primary |
| A2 | 60 kg adult | 4 g (one strong / double cup) | 1,500 mg/kg | test |
| C1 | 15 kg child | 2 g (one standard cup/bag) | 750 mg/kg | test |
| C2 | 15 kg child | 4 g (one strong / double cup) | 375 mg/kg | test |

- 2 g: a typical single tea bag / one cup of loose leaf. 4 g is a strong or double-bag cup, used
  as an upper reference.
- 60 kg adult, 15 kg child: the same scenario weights used throughout this repo's coumarin work
  (`coumarin-tdi`, BfR's illustrative 2 g adult / 0.5 g child at an assumed 3,000 mg/kg). They are
  scenario values, not measured weights.

## Gate and predictions

| id | kind | prediction |
|---|---|---|
| G0 | parse gate | measured rows in [740, 749]; pooled max in [2200, 2800] mg/kg (CFIA's 2,510); exactly 115 "tea" rows, all 115 measured; tea max in [2300, 2500] (CFIA's published 2,430); tea detected in [112, 115] (CFIA's 99%); tea unit census exactly `{"ug/g": 115}` |
| P1 | primary | **no** tea exceeds an adult's whole-day TDI in one standard 2 g cup (A1 count = 0) |
| P2 | test | share of teas over the TDI in an adult's strong 4 g cup in **[0.005, 0.12]** |
| P3 | test | share of teas over the TDI in a child's standard 2 g cup in **[0.07, 0.40]** |
| P4 | test | share of teas over the TDI in a child's strong 4 g cup in **[0.25, 0.70]** |

Reasoning, written before any per-sample tea value was seen. CFIA's published tea maximum is
2,430 mg/kg, below the A1 threshold of 3,000, so even a 100%-transfer standard adult cup of the
single most coumarin-rich tea stays under an adult's day budget (**P1**; the headline max alone
makes this near-certain, but it is the study's main point and is graded). The published average is
~500 mg/kg with a long right tail to 2,430: a strong 4 g adult cup (threshold 1,500) should catch
only the high tail (**P2**), a standard child cup (threshold 750) a meaningful minority around the
mean (**P3**), and a strong child cup (threshold 375) a larger share (**P4**). P2-P4 depend on the
distribution's shape, which the headline figures do not give, so they are genuinely uncertain.
If G0 fails, P1-P4 are not graded; an amendment would be published first, as with
`coumarin-eu-limits` 0.1.1.

## Grading

Sealed compute job (`python:3.12`, no host paths): `check_prereg.py` waits until this file is
public on GitHub and checks that the bundled parser equals the published `coumarin_eu_limits.py`;
then the offline tests `test_coumarin_tea.py` run; then `coumarin_tea.py` reads the SHA-verified
file and writes `summary.json`, `grades.json` and `coumarin_tea_samples.csv` (each tea's mg/kg,
the coumarin in a cup as a percentage of the drinker's day budget under A1-C2, and the four
over-TDI flags). The result note will be published next, with a result test that recomputes every
number from the per-sample table.

Descriptive, not graded: the coumarin (mg) and % of the day's budget at the median and maximum tea
under each scenario; and the tea detection rate and median/mean against CFIA's published headline.

## Limits (stated in advance)

- **100% transfer is an upper bound, not reality.** A real cup delivers only the fraction of
  coumarin that steeps out; these counts are ceilings, deliberately so. We use the bound because
  it needs no contested extraction figure.
- **TDI is a lifetime value.** Going over it on a single day is not a health finding; BfR has said
  a slight exceedance for one to two weeks is not a concern. This screen counts single cups against
  a whole-day budget as a bounded reference, not a daily-habit estimate.
- **Children rarely drink cinnamon tea.** The child scenarios are a reference bound, not a claim
  that children commonly drink these teas.
- **One cup only.** Coumarin from food and other drinks adds to these figures; this screen does
  not count it.
- **Generic names.** CFIA names the products only "Tea - Herbal/Black/Green/Other/White"; brands,
  blends and whether cinnamon is a main or trace ingredient are not in the file, and none are
  implied. Targeted 2013-14 sampling, not market shares.

## Prior art (searched 2026-10-24)

- CFIA's own 2013-14 report gives the tea category headline (115 samples, 0.3-2,430, avg 500,
  99% detected) but no per-cup exposure and no transfer model.
- BfR Health Assessment 043/2006 and later FAQs: the coumarin TDI and cinnamon examples (stars,
  gingerbread, cinnamon in food) for a 15 kg child; no cinnamon-tea per-cup series.
- Studies of coumarin extraction from cinnamon bark into hot-water infusions report partial
  transfer; none screens an open per-sample national tea survey against the TDI on a per-cup basis.
- We found no open, per-sample, reproducible per-cup screen of commercial cinnamon teas against the
  coumarin TDI. This study is meant to be that, with an explicit 100% transfer ceiling.

<!-- PREREG-MARKER: coumarin-tea-0.1.0-prereg -->
