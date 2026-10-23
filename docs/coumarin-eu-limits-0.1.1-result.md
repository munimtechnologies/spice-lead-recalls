<!-- RESULT-MARKER: coumarin-eu-limits-0.1.1-result -->
# coumarin-eu-limits 0.1.1: result

By MV2 of Munim, Inc. Made with AI agents working in MV2's name. Code Apache-2.0; this note and
the tables CC BY 4.0. Data: CFIA 2013-14 coumarin survey (Open Government Licence - Canada).
A cross-jurisdiction **reference comparison**: the EU's coumarin maximum levels do not apply in
Canada, and this is not a compliance finding, nor individual dietary or medical advice.

Grades [`coumarin-eu-limits-0.1.0-prereg.md`](coumarin-eu-limits-0.1.0-prereg.md) as amended by
[`coumarin-eu-limits-0.1.1-amendment.md`](coumarin-eu-limits-0.1.1-amendment.md).

## Headline

In CFIA's 2013-14 targeted survey of cinnamon-containing foods, **42 of 100 bakery samples** carry
more coumarin than the EU maximum for fine bakery ware (15 mg/kg). Almost all of them (39 of 42) are
in CFIA's generic "Baked Goods" category, where **39 of 68** are over. Only 2 of 31 cookies are
over. Breakfast cereals are mostly well under the EU's 20 mg/kg level: **3 of 136** cereals are
over (all three adult cereals, none of 65 children's cereals), plus 3 of 12 flavoured oatmeals.

## How it was graded

Sealed compute job `coumarin-eu-limits-v2` (2026-10-23 16:20-16:22 UTC, `python:3.12`, no host
paths): 21 offline unit tests passed, then `check_prereg.py` confirmed the amendment was public on
GitHub, then `coumarin_eu_limits.py` 0.1.1 read the CFIA file (SHA-256 `3c8a18c0…3f4f`, 122,686
bytes, resource `66d9cd8f-d44d-4993-8775-65da6857250c`, re-downloaded via ouvert.canada.ca) and
graded. **Unit census: all 749 measured rows are `ug/g`** (= mg/kg); no unrecognised unit.

**This re-grade was not blind.** The 0.1.0 job's output had shown every value at 1/1000 scale,
so the outcome below was known and was written into the amendment *before* this job ran. The job
reproduced that stated outcome exactly. The predictions themselves were written blind in 0.1.0,
and no threshold was changed, including P2's, which the data falsify.

## Pre-registered predictions

| | prediction | observed | grade |
|---|---|---|---|
| G0 (parse gate) | measured rows in [740, 749]; pooled max in [2200, 2800] mg/kg | 749 rows; max 2,510 mg/kg (CFIA's published figure) | **pass** |
| P1 (primary) | fine-bakery share over 15 mg/kg in [0.20, 0.50] (point 0.33) | 42 / 100 = 0.42 | **met** |
| P2 | cereal-core share over 20 mg/kg in [0.03, 0.22] (point 0.09) | 3 / 136 = 0.022 | **failed** (below range) |
| P3 (direction) | fine-bakery share > cereal-core share | 0.42 > 0.022 | **met** |

**3 of 4 met** (gate passed, P1 and P3 met, P2 falsified). The 0.1.0 grades (all false, from the
unit bug) stay on record in the amendment.

Why P2 failed: it was anchored on CFIA's 2016-18 report, where breakfast cereals averaged 9.75
mg/kg *among positives*. In 2013-14 the cereal distribution is tighter and lower (median 2.7
mg/kg, 11 of 136 not detected), so only the far tail crosses 20.

## Descriptive table (`data/coumarin-eu-limits.csv`)

"Over" means strictly above the limit; non-detects count as 0 mg/kg.

| group | subset | n | detected | over | limit (mg/kg) | share over | median | max |
|---|---|---|---|---|---|---|---|---|
| fine bakery | all | 100 | 100 | 42 | 15 | 0.42 | 8.4 | 83.3 |
| fine bakery | "Baked Goods" | 68 | 68 | 39 | 15 | 0.574 | 19.25 | 83.3 |
| fine bakery | cookies | 31 | 31 | 2 | 15 | 0.065 | 5.5 | 36.1 |
| fine bakery | English muffin | 1 | 1 | 1 | 15 | 1.0 | 20.7 | 20.7 |
| fine bakery | all, vs the 50 mg/kg seasonal row | 100 | 100 | 11 | 50 | 0.11 | 8.4 | 83.3 |
| breakfast cereal | core (adult + children) | 136 | 125 | 3 | 20 | 0.022 | 2.7 | 70.7 |
| breakfast cereal | adult | 71 | 65 | 3 | 20 | 0.042 | 2.2 | 70.7 |
| breakfast cereal | children's | 65 | 60 | 0 | 20 | 0.0 | 3.4 | 13.9 |
| breakfast cereal | flavoured oatmeal | 12 | 12 | 3 | 20 | 0.25 | 13.3 | 51.8 |
| breakfast cereal | core + oatmeal | 148 | 137 | 6 | 20 | 0.041 | 2.9 | 70.7 |

The sub-category, adult/children and 50 mg/kg rows are **descriptive and not pre-registered**.
The 50 mg/kg row is a bound for the EU's derogation for "traditional and/or seasonal bakery ware
containing a reference to cinnamon in the labelling": CFIA's generic names cannot tell which items
would qualify, so the true EU-analogue share lies somewhere between **11%** (every item treated as
seasonal/cinnamon-labelled, 50 mg/kg) and **42%** (none, 15 mg/kg). All 11 items over 50 mg/kg are
"Baked Goods".

The sealed per-sample output is in `data/coumarin_eu_limits_samples.csv` (all 749 rows, with the
classifier's group and sub-category, region, declared origin, mg/kg, the EU analogue limit and the
unit). `test_coumarin_eu_limits_result.py` recomputes every number above from it with plain `csv`
and `unittest`.

## Context and what is new

- A Danish market study of cinnamon-containing foods ([Food Control, 2014](https://sciencedirect.com/science/article/abs/pii/S0956713513005379))
  reported that roughly half of the fine bakery ware it tested exceeded the EU limit. The 42% here
  is the same order, measured on the other side of the Atlantic, where no such limit exists.
- CFIA's own 2016-18 summary (not open per sample) gives only means among positives (baked
  products 16.2, cereals 9.75 mg/kg) and no comparison with any limit.
- We found no open, per-sample, reproducible comparison of CFIA's coumarin data with the EU's
  category limits. This note, its table and its test are that comparison.

## Limits

- **Reference only.** Canada sets no coumarin maximum level; nothing here says any product broke a
  rule.
- **Spice exemption.** Under the regulation's Article 6(3), the Annex III Part B maximum levels do
  not apply to compound foods with no added flavourings whose only flavouring ingredients are
  fresh, dried or frozen herbs and spices. A bakery item flavoured only with ground cinnamon may fall
  under that exemption, and CFIA's names cannot tell. The seasonal 50 mg/kg row is bounded above,
  not resolved.
- **Generic names.** "Baked Goods" is CFIA's label, not ours; it likely holds cinnamon buns and
  rolls, but the file does not say.
- **Targeted sampling, 2013-14.** These are not market shares, and recipes may have changed since.
- One English muffin is a sample of one.

<!-- RESULT-MARKER: coumarin-eu-limits-0.1.1-result -->
