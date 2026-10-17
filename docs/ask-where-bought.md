# On a home visit, ask where each spice was bought (a one-page note)

By MV2 of Munim, Inc. Prepared with AI agents. Text CC BY 4.0.

This is a plain summary for lead-program staff and others who read spice lead data. It
is information drawn from open data, not official guidance, and it replaces no health
department's protocol. Every number comes from NYC DOHMH's open table of spice lead
results (da9u-wz3r, snapshot 2026-10-17) and is recomputed by a test in this repository.

## What the open NYC data show (case investigations, 2016–2025)

1. **Gross lead comes from spices bought abroad.** 98 of 1,118 results for spices bought
   outside the US (8.8%) were at or above 50 ppm, against 9 of 771 (1.2%) for spices
   bought in the US. Of the 107 gross results with a recorded purchase country, 98 (92%)
   were bought abroad, and about half of those in Georgia (the country).
   ([purchase-place 0.1.0](purchase-place-0.1.0-result.md))
2. **Low-level lead is everywhere.** Spices bought in the US and tested in case
   investigations reached 2 ppm about as often (5.8%) as spices from store surveys
   (8.3%). That did not change after 2020: 6.2% in 2016–2020, 5.5% in 2021–2025.
   ([purchase-place 0.1.0](purchase-place-0.1.0-result.md), [georgia-trend 0.1.0](georgia-trend-0.1.0-result.md))
3. **Gross results fell sharply after 2020.** 99 of 1,159 case results were ≥ 50 ppm in
   2016–2020, and 18 of 1,286 in 2021–2025. The fall shows up in every purchase group, so
   this table alone cannot credit it to any single intervention.
   ([georgia-trend 0.1.0](georgia-trend-0.1.0-result.md), [purchase-recording 0.1.0](purchase-recording-0.1.0.md))
4. **Purchase place is going unrecorded.** It was missing for 4.8% of case results in
   2016–2020 and 38.9% in 2021–2025 (59.7% in 2023). Nine of the 18 gross results since
   2021 have no purchase country.
   ([purchase-recording 0.1.0](purchase-recording-0.1.0.md))

## What that suggests in practice

- **Ask one question per spice: where was it bought?** Record the country, and whether
  it came from a market, a shop, a relative or a home grinder. It is the cheapest and
  strongest marker in this table, and it is now missing for many records.
- **Send spices bought abroad to the lab first**, above all loose, homemade or
  unbranded ones and yellow or orange spices such as turmeric, where lead chromate has
  been found (Forsyth et al. 2019).
- **Do not clear a spice because it was bought in the US.** US-bought spices still
  reached 2 ppm in 5.8% of case results, and 9 reached 50 ppm. Only a lab test settles
  it.
- **Keep the purchase field and the result together** in shared data, so that the next
  analysis can tell a real decline from a change in recording.

## Limits

- One city, case-investigation samples, results not households. A spice in this table
  was tested because someone was poisoned, so these rates are not market prevalence.
- The fall after 2020 has several possible causes: enforcement abroad (Bangladesh 2019;
  Forsyth et al. 2023), action in Georgia (Forsyth et al. 2024), changes in NYC's case
  mix, or recording.
- The analyses behind this note were done with AI agents. The pre-registered ones are
  marked as such, with their failed predictions reported.

Contact: MV2, Munim, Inc., mv2@munimtech.com
