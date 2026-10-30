# CFIA's Children's Food Project open files: what we checked

By MV2 of Munim, Inc. Prepared with AI agents working in his name. Text CC BY 4.0; code Apache-2.0.

The Canadian Food Inspection Agency (CFIA) tests foods for infants and children every year in its
Children's Food Project (CFP) and publishes one per-sample CSV per year on open.canada.ca (Open
Government Licence – Canada), next to a report page with printed tables. This page lists our
checks of those files against the printed figures. Each analysis was pre-registered (fixed and
public before any result value was read), graded by a sealed compute job on SHA-256-pinned files,
and then re-checked from the published GitHub files by a second sealed job running an independent
test. None of it is a finding about any product, brand or health risk; Health Canada reviewed
every CFP result and found none a safety concern.

## Component catalogue (finding aid)

- [`data/cfp_component_catalogue.csv`](../data/cfp_component_catalogue.csv): every component in
  all 16 open CFP files (2008-09 to 2023), with row counts and units per year. Names and counts
  only, no result values.

## Aflatoxin M1 in infant formula and children's dairy foods, 2012-13 to 2022

- [Pre-registration (cfp-afm1-trend 0.1.0)](cfp-afm1-trend-0.1.0-prereg.md), tag `v0.4.77`.
- [Result](cfp-afm1-trend-0.1.0-result.md), tag `v0.4.78`: gate passed in all six years, 10 of 12
  met. The files reproduce every aflatoxin M1 figure CFIA printed (35 of 468 samples detected,
  highest 0.136 ppb). **The 2014-15 file's `µg/g` unit label is 1000 times off**: its values are
  the report's ppb figures. No aflatoxin M1 in any of 160 yogurts and puddings. Formula at a
  common 0.02 ppb cut: 11.8% (2012-13 to 2018) against 2.9% (2022), p = 0.094, not a
  demonstrated decline. The independent test re-ran 13 of 13 from the published files (job
  `cfp-afm1-trend-result-v1`, 2026-10-30).

## Lead, 2017 to 2022, and the U.S. FDA's 2025 baby-food action levels

- [Pre-registration (cfp-lead 0.1.0)](cfp-lead-0.1.0-prereg.md), tag `v0.4.79`.
- [Result](cfp-lead-0.1.0-result.md), tag `v0.4.80`: gate passed in all six years, 12 of 13 met.
  The files reproduce every printed lead table row (979 samples). **The 2021 report's 0.18 ppm
  meal maximum is 0.018 in the file**, a slipped decimal point. The printed means mix all-sample
  and positives-only averages, and 2017's "positives only" note does not fit its own numbers.
  Nothing under 0.010 ppm was reported in 2018-2021, so a "not detected" then cannot show a food
  was under the FDA's 10 ppb level. Above the FDA's 20 ppb dry-infant-cereal level: 6 of 48
  (2019) and 1 of 39 (2022); the fall is entirely in imported cereals. The one miss: the 2021
  text's lower end, 0.015 ppm, where the file's smallest value is 0.016.

## Patulin in apple juice, 2008-09 (CFIA survey, not CFP)

- [Result](patulin-2008-0.1.0-result.md): the gate failed on its own terms (75 of 104 results
  written `<0`), and that was the finding. The independent test later re-ran 10 of 10 from the
  published files (job `patulin-2008-result-v1`).

The full map of every analysis in this repository is the [analyses index](analyses-index.md).
