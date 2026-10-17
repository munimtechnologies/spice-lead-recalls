# Pre-registration: is the home-versus-shelf gap really an abroad-versus-here gap? (purchase-place 0.1.0)

By MV2 of Munim, Inc. Prepared with AI agents. Text CC BY 4.0; code Apache-2.0.

**Status:** written and committed **before** any NYC result was split by purchase
country. No count below has been looked at. While checking other counts, about a dozen
individual rows were seen in passing, which is how the ambiguous "minor outlying
islands" value turned up. No tally by purchase place was made. The code (`purchase_place.py`) will be
written after this file is public. It will read only the committed snapshot
`data/nyc_spice_lead_snapshot_2026-10-17.csv`, and a test will recompute every number.
The result note will report every prediction, met or not.

## Question

[sampling_frame 0.1.0](sampling-frame-0.1.0-result.md) found that, in 2016–2025,
NYC case-investigation spices were 1.4× as likely as store-survey spices to reach
2 ppm lead and 10.9× as likely to reach 50 ppm. Store-survey spices are bought in New
York. Many case-investigation spices were bought abroad and carried in. Hore et al. 2019 found
lead more often in spices bought abroad (66% vs 40% detectable). If purchase place
explains the frame gap, a case-investigation spice **bought in the US** should look
like a store-survey spice.

## Rows and definitions (fixed now)

- Rows: `sampling_frame.nyc_rows` (Food-Spice, lead, laboratory, ppm) with collection
  year 2016–2025. Frames are C (case investigation) and S (store survey).
- `purchase_country` is stripped and upper-cased, then sorted into three groups:
  - **US**: exactly `UNITED STATES`.
  - **unknown**: blank, `UNKNOWN OR NOT STATED`, or `UNITED STATES MINOR OUTLYING ISLANDS`
    (ambiguous, so treated as unknown).
  - **abroad**: any other value. Misspellings of a foreign country still count as abroad.
- Shares are computed among results: a non-detect counts as a result below every
  threshold. Thresholds are inclusive (≥).
- Reference values are already public, from the 0.1.0 result. S in 2016–2025 has
  38 of 457 results ≥ 2 ppm (8.3%) and 2 of 457 ≥ 50 ppm (0.44%).

## Predictions (C rows, 2016–2025)

- **P1:** C-US share ≥ 50 ppm is at most 1.5%.
- **P2:** C-abroad share ≥ 50 ppm is at least 10%.
- **P3:** C-US share ≥ 2 ppm is between 4% and 16% (within 0.5× to 2× of S's 8.3%).
- **P4:** At least 70% of the C results ≥ 50 ppm are C-abroad.
- **P5:** C-abroad vs C-US at ≥ 50 ppm: exact two-sided Fisher p < 0.001, with
  C-abroad higher.

Reported without prediction: the size of each group, including C-unknown and its
shares. Also reported: the same table for the 2011–2015 rows, and the S rows by purchase
group. These are a check on the assumption that store surveys buy in the US.

## Limits known now

- `purchase_country` is self-reported in a home interview. Hore 2019 suspected at least
  one misreported "bought in the US" result (21,000 ppm).
- A large unknown group would weaken every comparison. Its size is reported, not predicted.
- These are test results, not distinct products, and neither frame is a random sample.
