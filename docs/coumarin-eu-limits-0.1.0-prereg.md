<!-- PREREG-MARKER: coumarin-eu-limits-0.1.0 -->
# coumarin-eu-limits 0.1.0 — pre-registration

**How often does coumarin in Canadian cinnamon-containing foods exceed the EU maximum level that would apply to the same food category in Europe?**

By MV2 of Munim, Inc. Written and committed **before any coumarin value of any product was read**.
Made with AI agents working in MV2's name. Code Apache-2.0; this note and derived data CC BY 4.0.

## Question

The European Union sets **maximum levels for coumarin in specific finished-food categories**
(Regulation (EC) No 1334/2008, Annex III, Part B), because coumarin occurs naturally in cassia
cinnamon and chronic intake is a health concern. Canada (CFIA) sets **no** such limit; it
surveys coumarin in retail foods and publishes the per-sample concentrations as open data, but
its reports never ask how the Canadian products would compare to the European limits.

This study does that comparison, reproducibly, on CFIA's **2013–14 targeted survey** (749 retail
samples: breads, baking mixes, bakery goods, oatmeal, breakfast cereals, dried beverage/spice
mixes and dried tea), the CFIA open file whose product categories map most directly onto the EU
Annex III Part B rows. It is a **cross-jurisdiction reference comparison, NOT a compliance
finding**: these products were legally sold in Canada, where no coumarin limit applies.

This is an **information/research artifact, not individual dietary or medical advice.**

## EU maximum levels (verified against the primary source)

Regulation (EC) No 1334/2008, Annex III Part B, coumarin rows (verbatim category wording),
cross-checked on 2026-10-23 against EUR-Lex (CELEX 32008R1334) and legislation.gov.uk retained-EU
copy (both agree):

| EU category (verbatim) | Max (mg/kg) |
|---|---|
| Traditional and/or seasonal bakery ware containing a reference to cinnamon in the labelling | 50 |
| Breakfast cereals including muesli | 20 |
| Fine bakery ware, with the exception of traditional and/or seasonal bakery ware containing a reference to cinnamon in the labelling | 15 |
| Desserts | 5 |

## Data

CFIA "Coumarin in dried beverage mixes, breads, baking mixes…" **2013–14** survey, CKAN dataset
`c3675987-71ae-493c-b9be-c2222301ce4f`, resource `66d9cd8f-d44d-4993-8775-65da6857250c`
(CSV, bilingual en/fr, 122,686 bytes, cp1252). Contains information licensed under the Open
Government Licence – Canada. The untouched raw file was saved to the sealed compute data volume
(`cfia-coumarin`) by the companion names-only job on 2026-10-23 with
**SHA-256 `3c8a18c0769d81e9580b9f985722ccd24e9db45c72ea9228f3eda8afd3383f4f`**; the grader asserts
this exact digest (and re-downloads through `ouvert.canada.ca`'s CKAN API and re-checks it if the
saved copy is absent) **before reading any value**. Only the column *names* of this file have been
inspected so far (companion job `coumarin-1314-names-v1`), never the `Result`/`Unit` columns.

CFIA's own summary of this survey states coumarin was detected in ~95% of samples with a range of
0.1–2,510 mg/kg (the maximum in a pumpkin-pie spice blend). These are the **only** figures from
this file seen before this pre-registration, and they are used solely to set the G0 parse gate.

### Columns used
`Product` (English product category), `Region`, `Origin` (English), `Result - Résultat`,
`Unit - Unité`. All concentration arithmetic acts on the published `Result`/`Unit` pair only.

## Method

**Concentration parse (fixed now).** For each row, `parse_ppm(Result, Unit)` returns mg/kg:
non-detect / below-detection tokens (`ND`, `N.D.`, `trace`, a leading `<`, `<LOD`, `<LOQ`, `NQ`)
→ `0.0` (clearly under every EU coumarin limit, all ≥ 5 mg/kg); a decimal comma is normalised;
the leading numeric value is taken; units containing `ppb`, `µg/kg`, `ug/kg` or `ng/g` are divided
by 1000, while `mg/kg`, `ppm` or a blank unit are taken as mg/kg. A blank `Result` → not measured
(excluded from denominators). A sample **exceeds** a limit when `ppm > limit` (strictly).

**EU-analogue classification (fixed now).** `classify(Product)` lower-cases the English product
name and applies these rules in order, returning a sub-category token; the first match wins:

1. `spice` → *out-of-scope* (EU exempts herbs & spices from Annex III Part B).
2. `tea` → *out-of-scope* (a beverage; not an Annex III Part B category).
3. `mix` → *out-of-scope* (a dry mix, not a compound food "as consumed").
4. `infant` → *out-of-scope* (infant food is separately regulated in the EU).
5. `bar` → *out-of-scope* (a granola/cereal **bar** is a snack bar, not a breakfast cereal).
6. `oatmeal` → **breakfast-cereal**, limit 20 (sub-group *oatmeal*).
7. `cereal` → **breakfast-cereal**, limit 20 (sub-group *cereal*).
8. `bread` or `bagel` → *out-of-scope* (bread, EU category 07.1, carries **no** coumarin limit).
9. `cookie` → **fine-bakery**, limit 15.
10. `muffin` → **fine-bakery**, limit 15.
11. the name contains `baked good` → **fine-bakery**, limit 15.
12. anything else → *out-of-scope* (unmapped).

The "Traditional/seasonal bakery ware with a cinnamon reference in the labelling" (50) and
"Desserts" (5) rows have **no** reliable analogue in these generic CFIA names and are not mapped.

Expected group sizes from the names census (context only, not graded): fine-bakery ≈ 100
(Baked Goods 68 + Cookie 31 + English Muffin 1); breakfast-cereal core ≈ 136 (Cereal-Adult 71 +
Cereal-Children 65); oatmeal ≈ 12. The grader reports the exact realised counts.

**Oatmeal choice.** EU "breakfast cereals including muesli" plausibly covers flavoured oatmeal.
It is placed in the breakfast-cereal group but reported **both ways**: the primary cereal
prediction P2 is on the cereal sub-group **excluding** oatmeal; oatmeal and the combined
cereal+oatmeal share are reported descriptively.

**Outputs:** `out/coumarin_eu_limits_samples.csv` (per sample: group, sub-category, product,
region, origin, parsed ppm, over-limit flag), `out/summary.json`, `out/grades.json`.

## Published priors (a different CFIA survey, legitimately seen before this prereg)

CFIA "Coumarin in Selected Foods, 2016-04-01 to 2018-03-31" (1,497 samples; no open CSV). Averages
are over **positive** samples only (table note):

| Product type | n | detected | max ppm | avg ppm (positives) |
|---|---|---|---|---|
| Baked products | 498 | 482 | 80.5 | 16.2 |
| Breakfast cereal | 199 | 173 | 45.6 | 9.75 |
| Flavoured oatmeal | 50 | 48 | ~35–39 | 13.4 |

The baked-products positive-mean (16.2) sits right at the EU fine-bakery line (15), so with a
right-skewed distribution and ~97% detection the share over 15 is plausibly ~1/3; the cereal
positive-mean (9.75, max 45.6) sits well below the EU cereal line (20), so its share over 20 is
plausibly ~1/10. The predictions below are fixed from this reasoning before any 2013–14 value is read.

## Predictions

**G0 — parse/reproduction gate** (confirms the file parsed as mg/kg, not a scientific claim):
the number of measured rows is in **[740, 749]** and the pooled maximum coumarin across all rows
is in **[2200, 2800] mg/kg** (CFIA reports a maximum of 2,510). *Gate; not a hypothesis.*

**P1 — primary, genuinely untested:** in the **fine-bakery** analogue group, the share of samples
with coumarin **> 15 mg/kg** (over all measured samples in the group, non-detects counted as under
the limit) is in **[0.20, 0.50]** (point estimate 0.33). *Falsified if the share is < 0.20 or > 0.50.*

**P2 — genuinely untested:** in the **breakfast-cereal core** group (Cereal-Adult + Cereal-Children,
excluding oatmeal), the share of samples with coumarin **> 20 mg/kg** is in **[0.03, 0.22]**
(point estimate 0.09). *Falsified if the share is < 0.03 or > 0.22.*

**P3 — direction, anticipated:** the fine-bakery share-over-15 is **greater than** the
breakfast-cereal-core share-over-20 — i.e. the bakery analogue exceeds its (lower) EU limit more
often than the cereal analogue exceeds its (higher) limit. *Falsified if fine-bakery ≤ cereal-core.*

I will report every prediction's observed value and pass/fail honestly, including G0 and P3, and
the oatmeal and combined-cereal shares descriptively, and will not change any threshold after grading.

## Limits

- **Reference, not compliance.** EU limits do not apply in Canada; these products were lawfully
  sold. This is a "what if the EU limit applied, as marketed" comparison, nothing more.
- **Spice derogation unknowable.** Annex III Part B does not apply where the only added flavouring
  ingredients are fresh/dried/frozen herbs & spices. CFIA names cannot reveal this, so a mapped
  product may be exempt in reality; results are "share whose level would exceed the limit if it applied".
- **Generic categories.** CFIA product names are generic (no brand, no "cinnamon in labelling"
  field), so the 50 mg/kg seasonal-bakery and 5 mg/kg dessert rows cannot be mapped, and the
  fine-bakery/bread split rests on the product name only.
- **Targeted sampling.** CFIA sampled to find coumarin, so these are not market-share statistics.
- **Old products.** The 2013–14 samples are 12+ years old; formulations may have changed.
- Not individual dietary or medical advice.

<!-- PREREG-MARKER: coumarin-eu-limits-0.1.0 -->
