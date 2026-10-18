# Pre-registration: how much of the lead-adulterated turmeric in eastern Indian markets could a Raman screen see? (raman-reach 0.1.0)

**Author:** MV2, Munim, Inc. (mv2@munimtech.com). Work made with AI agents.
**License:** text CC BY 4.0; code Apache-2.0.
**Written:** 2026-10-18, before any row, header or caption of the data table was read.

## Why this question

MV2's Yellow Flag pitch (Blaise xTech, Carrot Ventures x XPRIZE) proposes a pocket Raman screen for lead
chromate in spices, and `spice-screen` is its open-source engine. The best published bench result we know
(Wageningen, FT-Raman, *Food Control* 2021, "Real or fake yellow in the vibrant colour craze: rapid
detection of lead chromate in turmeric") detects lead chromate in turmeric powder from **0.5% w/w** (PLSR;
0.6% from the 840 cm-1 band alone). Lead chromate (PbCrO4) is 64.1% lead by mass, so 0.5% w/w is about
**3,200 ug/g (ppm) lead**. The authors wrote that this limit "is still above the maximum levels that have
been found in practice", but did not count samples against it. India's legal limit for lead in turmeric is
10 ug/g.

Forsyth, Sinha, Bandekar, Mistree and Luby, "Systemic drivers of toxic food adulteration: lead chromate in
turmeric across eastern India", *npj Science of Food* (2026), doi:10.1038/s41538-026-00867-8 (CC BY 4.0),
surveyed 503 turmeric samples from wholesale and retail markets in 34 cities of five states in 2021 and 2023
and says its data are in Supplementary Table 8. The article reports exceedance of 10 ug/g, geometric means
and the maximum; it does not report how lead is distributed against any field-screen detection limit. We
found no published count of real market samples against Raman's limit. This study makes that count. It is
a test of MV2's own pitch: if almost no adulterated sample reaches 3,200 ug/g, a Raman screen at today's
bench sensitivity cannot enforce the 10 ug/g limit, and the pitch must say so.

## What was already known when this was written

From the article text (read through a summary of the PubMed Central full text, PMC13357593, and search
abstracts; the supplement itself has not been opened by us):

- 503 turmeric samples, 34 cities, five states (Bihar, Jharkhand, Uttar Pradesh, West Bengal,
  Chhattisgarh), summers of 2021 and 2023; one sample of every distinct turmeric type on sale (dried root,
  loose powder, packaged powder; single or double polished). Also 80 chili and coriander samples, and a
  purposive December 2023 follow-up (139 roots from delivery trucks; 51 samples from Dhanbad and
  Prayagraj, none with detectable lead).
- Lead by handheld XRF (Olympus DELTA, triplicate, LOD 4 ug/g), calibrated against ICP-MS on 7 powders and
  9 roots spanning 4-6,094 ug/g.
- 30% of samples (n = 153), from 25 cities, exceeded 10 ug/g. States by exceedance: Bihar > Jharkhand >
  Uttar Pradesh > Chhattisgarh > West Bengal; no West Bengal city exceeded. Bihar: every city adulterated,
  more than half of samples above 10 ug/g, geometric mean 48 ug/g, **maximum 6,416 ug/g**.
- Double-polished roots and loose powder had more than four times the odds of exceeding 10 ug/g compared
  with single-polished roots. Every sample above 10 ug/g "also contained chromium at levels suggestive of
  lead chromate"; no chromium values are given in the text.
- Chili and coriander: 5 with detectable lead, maximum 573 ug/g.

Consequences we state now: at least one sample (6,416) is above 3,200 ug/g, so P4 cannot hold vacuously;
P2 and P3 are consistency checks against the article. We do not know the table's columns: whether it
gives form, polishing, state, chromium, or flags the purposive samples.

## Rules (fixed before reading)

- **Analysis set S**: rows of Supplementary Table 8 with a lead value that are turmeric (no chili, chilli,
  coriander, cumin, mirch or dhania in the row) and not purposive follow-up samples (no truck, purposive,
  follow-up or December 2023 marker in the row). **E** = samples in S above 10 ug/g (strictly).
- Values: "<LOD", "ND", "BDL", "<x" and 0 are not detected and count as 0; "-", "NA" and blanks are
  missing; thousands separators are dropped; "a +/- b" reads as a. ppb or ug/kg columns are divided by 1,000.
- If the table gives several lead columns, the mean is used; SD, LOD, ratio and log columns are never used.
- **Form classes** from the form and polishing columns: packaged powder (packaged, packet, sachet, brand);
  else loose powder (powder); else double-polished root, single-polished root, other root; else unknown.
- State is the state column (full name or BR/JH/UP/WB/CG), else a state name found in the row.
- **Gate:** if P1 fails, P2-P9 are reported as "not graded (gate failed)", the parser fix is recorded as a
  deviation, and no prediction changes.

## Predictions (graded by `raman_reach.py`, unchanged after this commit)

| | prediction |
|---|---|
| P1 | 495-515 samples in S (parse gate; the article says 503) |
| P2 | 148-158 samples in S are above 10 ug/g (consistency check; the article says 153) |
| P3 | the highest lead in S is 6,300-6,500 ug/g and is from Bihar (consistency check; Bihar's maximum is 6,416) |
| P4 | at most 10% of E is at or above 3,200 ug/g, the bench-Raman threshold (gradable if E has at least 20) |
| P5 | the median lead in E is below 320 ug/g, ten times below that threshold (gradable if E has at least 20) |
| P6 | Bihar holds strictly more than half of the samples at or above 500 ug/g (gradable if at least 3, all with a state) |
| P7 | among samples at or above 500 ug/g with a known form, roots outnumber powders (gradable if at least 5) |
| P8 | no packaged-powder sample is above 100 ug/g (gradable if at least 10 packaged powders) |
| P9 | among E with chromium detected, the median Pb:Cr mass ratio is 2-8 (lead chromate is 3.98) (gradable if a chromium column exists and at least 20 such samples) |

Reasoning, all expectations rather than checked facts. P4 and P5: a geometric mean of 48 ug/g in the
worst state, with most exceedances there, suggests a lognormal spread in which only the far tail reaches
thousands of ug/g. P6: Bihar leads every reported measure. P7: the pigment is applied while polishing roots,
and grinding with other stock should dilute it; but loose powder had high odds too, so this is the least
certain call. P8: packaged powders come from larger processors; a weak guess. P9: XRF chromium at low
levels is noisy and soils add background chromium, so we allow a wide band around 3.98.

## What each outcome would mean

If P4 and P5 hold, a 0.5% w/w Raman screen would miss at least nine in ten samples that break India's limit
even in the worst market, and Yellow Flag's honest role is triage of the gross tail (and of dyes), not
enforcement; XRF (LOD 4 ug/g) stays the enforcement tool. If they fail, Raman's limit reaches more of the
real problem than its authors expected. Handheld Raman is usually less sensitive than bench FT-Raman, so
this count is a best case for a pocket device.

## Method

`raman_reach.py` downloads the supplement PDF (springer static content, then PubMed Central and Europe PMC
mirrors), records its sha256, finds the page carrying the "Supplementary Table 8" caption, and extracts the
table with pdfplumber (ruled lines, then text alignment, then layout text; the attempt with most parsed rows
wins). It writes `structure.json` (captions, pages, header, column roles, every extraction attempt),
`grades.json`, `summary.md` (the P-table; a ladder of counts at 10, 50, 100, 320, 640, 1,000, 3,200 and
10,000 ug/g; tables by state and form; every sample at or above 500 ug/g; the Pb:Cr summary) and
`raman_reach_samples.csv` (every parsed row). `test_raman_reach.py` tests the value parser, the header and
column-role logic, the row builder and the grader offline on synthetic tables. If no lead column is found,
the job fails loudly and keeps the raw table text sealed for a v2 parser.

## Limits

XRF readings calibrated to ICP-MS, not ICP-MS per sample (roots: mean error 18%). One sample per distinct
type on sale, not market shares. The 3,200 ug/g threshold is one bench study on spiked powder; whole or
polished roots, other instruments and better models may differ. Lead is not lead chromate: low-level lead
can come from soil or equipment, so if some samples in E are not chromate-adulterated, the share of E at or
above 3,200 ug/g understates the share among truly adulterated samples (the article says every sample above
10 ug/g had chromium suggestive of lead chromate, which limits this). Nothing here is advice to any person.

Data: Forsyth J.E. et al., npj Science of Food (2026), doi:10.1038/s41538-026-00867-8, licensed CC BY 4.0.
