# ota-spices 0.1.0 — result (parse gate failed; exploratory regrade under a declared deviation)

Result for the pre-registration in [`ota-spices-0.1.0-prereg.md`](ota-spices-0.1.0-prereg.md).
No prediction has been changed. **The pre-registered parse gate failed, so formally none
of the eight predictions is graded.** The cause was a bug in our own spice keyword rule, not
in CFIA's file. This note reports that plainly, then regrades under CFIA's own product label.
The regrade is a deviation chosen after the data were seen, and is labelled exploratory.

- **Source:** CFIA, "Ochratoxin A in Selected Foods - April 1, 2012 to March 31, 2018 and
  April 1, 2019 to March 31, 2022", open.canada.ca dataset `37300d06-0887-4353-bc9b-4f030f1089a2`
  (released 2026-10-06; Open Government Licence – Canada).
- **File:** sha256 `3d86e455cb3855cdea7fced6f72f30ab5d435467cb242a578d00fa91764fbe82`,
  8,384 rows, 8,384 samples, all in ng/g (= ppb). No unparseable numbers.
- **Sealed per-sample table:** [`../data/ota_samples.csv`](../data/ota_samples.csv) (all 8,384
  samples). [`../test_ota_spices_result.py`](../test_ota_spices_result.py) recomputes every
  count below from it with the Python standard library only.

## What failed, and why

P1 required 700-860 spice samples (CFIA's report counts 778). The pre-registered rule found
**1,024**, so the gate failed. Reading the sealed table shows why. The file has no
product-type column, so product-name keywords decided, and the mixture keyword `\bmix`
matched products that are not spices:

| swept in by the keyword rule | samples |
|---|---|
| Baking Mixes | 254 |
| Mixed Fruit | 14 |
| Dried mixes | 3 |
| "Pepper" (no "Spice -" prefix; 2015-16, mostly 0-4 ppb) and "Pepper - Hot - Fresh" | 38 |
| Herb - Marjoram - Fresh | 1 |

Our exclusion list covered breads, cereals and teas but not "baking", "mixed fruit" or "fresh".
That is our error, found only after the run.

## Deviation (declared after seeing the data)

CFIA names its spices in the file itself: every spice product is "Spice - <name>"
(e.g. "Spice - Paprika", "Spice - Nutmeg"). **Rule B = product name begins with "Spice"
(714 samples).** Spice types, EU limits and every grading formula are unchanged. We did not try
other rules. Rule B still does not reproduce CFIA's 778 exactly: the 64-sample gap is probably
CFIA counting dried herbs and the unprefixed "Pepper" products as spices, which we could not
confirm.

## Predictions

| | prediction | pre-registered rule (1,024 "spices") | Rule B, exploratory (714 "Spice -") |
|---|---|---|---|
| P1 | >= 8,000 samples and 700-860 spices (gate) | 8,384; 1,024: **not met** | 8,384; 714: met |
| P2 | highest spice 1,700-1,850 ppb in a paprika (consistency) | not gradable | 1,770 ppb paprika: met |
| P3 | 5-15% of spices over their EU limit | not gradable (108 / 1,024 = 10.5%) | 106 / 714 = 14.8%: met (narrowly) |
| P4 | highest-OTA paprika declares Spain or Hungary | not gradable (Hungary) | Hungary: met |
| P5 | India strictly the most frequent declared country among over-limit spices | not gradable | India 8, Spain 6, Canada 5, Hungary 4, Grenada 1: met |
| P6 | Canada-declared spices over EU limits less often than foreign-declared | not gradable | Canada 5/34 (14.7%) vs foreign 19/199 (9.5%): **not met** |
| P7 | no raisin/sultana/currant above 10 ppb declares the United States | not gradable | 4 above 10 ppb; only Iran declared: met |
| P8 | Indonesia strictly the most frequent declared country among nutmeg over 15 ppb | not gradable | India 3, Canada 1, Grenada 1: **not met** |

So: **0 of 8 graded under the pre-registered rule; 6 of 8 met under Rule B (exploratory).**
The two Rule B misses are informative. Canada-declared spices did no better than imports.
Nutmeg over the limit declared India, never Indonesia. P3's 14.8% sits just under the 15%
edge, so treat it as a coin-flip pass.

## Origin-level reading (Rule B; the first we can find for this programme)

| spice type | EU limit (ppb) | n | over EU limit | share over |
|---|---|---|---|---|
| paprika | 20 | 122 | 53 | 43% |
| nutmeg | 15 | 96 | 33 | 34% |
| chili / cayenne | 20 | 97 | 17 | 18% |
| ginger | 15 | 40 | 2 | 5% |
| mixtures ("Spice - Mixed" etc.) | 15 | 53 | 1 | 2% |
| pepper ("Spice - Pepper ...") | 15 | 36 | 0 | 0% |
| turmeric | 15 | 63 | 0 | 0% |
| other (no EU limit) | - | 207 | - | - |

Declared origins of the 106 over-limit spices: **no country 82 (77%)**, India 8, Spain 6,
Canada 5, Hungary 4, Grenada 1. Paprika by declared origin: **Hungary 4 of 4 over** (298,
277, 37.5 and the survey maximum, 1,770 ppb), Spain 6 of 15 over (max 631), India 2 of 6,
Canada 2 of 5, no country 39 of 86. Spices declaring the United States: 0 of 21 over.

Health Canada's 2009-2014 study of the same programme wrote that the country of origin "is
rarely known, so it is not possible to correlate country of origin and OTA concentrations".
The open file confirms that for most samples: 481 of 714 spices (67%) carry no country.
For the minority that do, the pattern is concrete. Every Hungarian-declared paprika exceeded
the EU limit, and Spanish paprika exceeded it 40% of the time.

## Limits

- The gate failed. Everything in the Rule B column and the origin tables is exploratory, read
  under a rule fixed after the data were seen. Its counts are small (4 Hungarian paprikas).
- Declared origin is often the packer's country. "No country" means the open file carries
  none, not that CFIA did not know it.
- EU limits are a yardstick. Canada has no OTA limit for spices, so no Canadian rule is broken
  by any result here, and Health Canada judged the survey results unlikely to pose a health
  risk. Spice portions are small.
- CFIA's report counts 6 raisin samples over the proposed 10 ppb limit; the open file shows 4
  raisin samples above 10 ppb. We could not reconcile the difference.

---

Made by MV2 of Munim, Inc. with AI agents. Code Apache-2.0; text and derived data
CC BY 4.0. Contains information licensed under the Open Government Licence – Canada.
