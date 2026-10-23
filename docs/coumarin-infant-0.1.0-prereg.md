<!-- PREREG-MARKER: coumarin-infant-0.1.0-prereg -->
# coumarin-infant 0.1.0: pre-registration

By MV2 of Munim, Inc. Made with AI agents working in MV2's name. Code Apache-2.0; this note
CC BY 4.0. Data: CFIA 2013-14 coumarin survey (Open Government Licence - Canada).
An exposure screen on open data. It is not a compliance finding (Canada sets no coumarin limit),
not a statement about any brand, and not individual dietary or medical advice.

## Question

How much of the tolerable daily intake (TDI) for coumarin would the cinnamon-containing **infant
cereals** in CFIA's 2013-14 targeted survey give an infant who eats them every day?

EFSA's TDI is **0.1 mg coumarin per kg body weight per day** (EFSA 2004, confirmed 2008; BfR
uses the same value). Infants eat much more food per kg of body weight than adults, which is why
BfR's 2006 assessment expected a higher intake per kg for infants than for adults. The EU's
Annex III Part B maximum levels (Regulation (EC) No 1334/2008) have no infant-food row, and
our earlier comparison with those levels (`coumarin-eu-limits` 0.1.1) left infant cereals out of
scope. This study covers them, on a per-day intake basis.

## Data and status of the values (read this first)

- File: CFIA 2013-14 coumarin survey, resource `66d9cd8f-d44d-4993-8775-65da6857250c`, SHA-256
  `3c8a18c0769d81e9580b9f985722ccd24e9db45c72ea9228f3eda8afd3383f4f`, parsed by
  `coumarin_eu_limits.py` 0.1.1 (explicit unit table; every value is `ug/g` = mg/kg).
- The file has **52 rows named "Infant Food - Cereal"**. That count was taken from product names
  only (classifier labels in `data/coumarin_eu_limits_samples.csv`).
- **The infant-cereal values are already public** (the per-sample table published with
  `coumarin-eu-limits` 0.1.1 lists all 749 rows), **but no agent has read them.** Earlier work
  read only bakery and breakfast-cereal rows. This pre-registration was written from names-only
  counts, the published children's-cereal and oatmeal summaries, and the literature below. We
  also did not open CFIA's own report text for infant-cereal figures before writing this. We
  cannot prove a negative, so the public commit time of this file and of the grading job is the
  record.
- Known comparison values (already published in `coumarin-eu-limits` 0.1.1): children's breakfast
  cereals median 3.4 mg/kg (n = 65, max 13.9); adult cereals median 2.2; flavoured oatmeal median
  13.3 (n = 12).

## Exposure scenarios (fixed now)

Daily intake (mg/kg bw/day) = concentration (mg/kg) x dry cereal eaten (kg/day) / body weight (kg).

| id | body weight | dry infant cereal per day | concentration that reaches the TDI | role |
|---|---|---|---|---|
| S1 | 8 kg | 30 g (one Canadian reference amount) | 26.67 mg/kg | primary |
| S2 | 8 kg | 60 g (two reference amounts) | 13.33 mg/kg | test |
| S3 | 8 kg | 15 g (one US reference amount) | 53.33 mg/kg | descriptive |

- 30 g: Health Canada, *Nutrition labelling: Table of reference amounts for food*, item W.1
  "Cereals, dry, instant, to be prepared with water, breast milk or infant formula", reference
  amount 30 g (the amount typically eaten at one sitting).
- 15 g: US 21 CFR 101.12, infant and toddler "cereals, dry instant" reference amount.
- 8 kg: about the WHO growth-standard median weight for infants of roughly 7-9 months, the age
  when infant cereal is a daily food. It is a scenario value, not a measured weight.
- "Over the TDI" means strictly above the scenario's concentration. Non-detects count as 0 mg/kg.

## Gate and predictions

| id | kind | prediction |
|---|---|---|
| G0 | parse gate | measured rows in [740, 749]; pooled max in [2200, 2800] mg/kg (CFIA's 2,510); exactly 52 "Infant Food - Cereal" rows, all 52 measured; unit census of those rows exactly `{"ug/g": 52}` |
| P1 | primary | share of infant cereals over the TDI under S1 in **[0.00, 0.10]** (point 0.02) |
| P2 | test | share of infant cereals over the TDI under S2 in **[0.02, 0.30]** (point 0.10) |
| P3 | direction | median infant-cereal coumarin **<** median children's breakfast-cereal coumarin (same file, product "Cereal - Children") |
| P4 | test | share of infant cereals with coumarin detected in **[0.80, 1.00]** |

Reasoning, written before any infant value was seen: the survey targeted cinnamon-containing
foods, so most samples should have detectable coumarin (P4). Infant-cereal makers formulate
mildly flavoured products, and a UK product cited in the coumarin literature (an oat-and-apple
infant cereal) measured about 5.6 mg/kg, so we expect infant cereals to sit lower than the
cinnamon-coated children's cereals (P3), with only a thin tail reaching 13-27 mg/kg (P1, P2).
If G0 fails, P1-P4 are not graded; an amendment would be published first, as with
`coumarin-eu-limits` 0.1.1.

## Grading

Sealed compute job (`python:3.12`, no host paths): `check_prereg.py` waits until this file is
public on GitHub and checks that the bundled parser equals the published `coumarin_eu_limits.py`;
then the offline tests `test_coumarin_infant.py` run; then `coumarin_infant.py` reads the
SHA-verified file and writes `summary.json`, `grades.json` and `coumarin_infant_samples.csv`
(each sample's mg/kg and % of the TDI under S1-S3). The result note will be published next,
with a result test that recomputes every number from the per-sample table.

Descriptive, not graded: % of the TDI at the median and maximum under each scenario; the 90th
percentile; the count over 20 mg/kg (the EU breakfast-cereal row, for reference only); and, after
grading, a comparison with whatever CFIA's own reports say about these samples.

## Limits (stated in advance)

- **TDI is a lifetime value.** Going over it on some days is not a health finding; BfR has said
  a slight exceedance for one to two weeks is not a concern. Daily intake over months is the
  scenario here.
- **Cereal only.** Coumarin from other foods (and, for older children, cinnamon sprinkled at
  home) adds to these figures; this screen does not count it.
- **Targeted 2013-14 sampling**, not market shares; recipes may have changed since.
- **Generic names.** CFIA names the products only "Infant Food - Cereal"; brands and flavours are
  not in the file, and none are implied.

## Prior art (searched 2026-10-23)

- BfR Health Assessment 043/2006 and later FAQs: TDI, infant exposure in general, cinnamon stars
  and gingerbread examples for a 15 kg child. No infant-cereal concentration data.
- Norwegian benchmark-dose risk assessment (Food Chem Toxicol 2012, PubMed 22178604): small
  children eating oatmeal porridge with cinnamon may exceed the TDI several-fold. That concerns
  cinnamon added at home, not commercial infant cereal.
- Danish market study (Food Control 2014): coumarin in cinnamon-containing foods; no infant
  cereal series.
- We found no open, per-sample, reproducible screen of commercial infant cereals against the
  coumarin TDI. This study is meant to be that.

<!-- PREREG-MARKER: coumarin-infant-0.1.0-prereg -->
