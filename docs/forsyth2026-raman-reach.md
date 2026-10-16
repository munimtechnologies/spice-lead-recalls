# Eastern India's market turmeric: how much could a lead chromate screen see?

MV2 of Munim, Inc., 2026-10-16. Made with AI agents working in his name. Text CC BY 4.0; code Apache-2.0.

**Source.** Forsyth JE, Sinha M, Bandekar A, et al. Systemic drivers of toxic food adulteration: lead chromate in
turmeric across eastern India. *npj Science of Food* 10:220 (2026), doi:10.1038/s41538-026-00867-8 (CC BY 4.0).
503 turmeric samples from 34 cities in Bihar, Uttar Pradesh, Jharkhand, West Bengal and Chhattisgarh, 2021-2023;
lead by handheld XRF (LOD 4 ug/g). Per-sample data: Supplementary Table 8, inside the one supplementary PDF
(`41538_2026_867_MOESM1_ESM.pdf`, sha256 `f728f8c613ed...`, 40 pages).

**Question.** Section 3 of the README asks how low a lead chromate screen must reach to catch the lead-laced spices
in U.S. public-health lab data (NYC, King County). Those are case samples from poisoned households. This asks the
same question of a market survey in a producing region, where samples were bought, not selected because someone was
poisoned. The predictions were written before the job ran; they are quoted at the end of this page.

## Result

Table S8 lists 503 rows: sample ID, city, average lead (ug/g), product type, Bihar or not, and major-producer state.
**It has no chromium column**, so no Pb:Cr ratio can be read from it. The lead column alone answers the reach
question. A screen's limit, written as % w/w lead chromate (PbCrO4 is 64.1% lead), is converted to lead and counted
against the 153 samples with at least 10 ug/g lead (the paper's own cut, 30% of 503).

| screen limit, % w/w PbCrO4 | **0.5%** (bench Raman) | 0.1% | 0.05% | 0.025% | 0.005% |
|---|---|---|---|---|---|
| same limit as lead | 3,206 ug/g | 641 ug/g | 321 ug/g | 160 ug/g | 32 ug/g |
| caught, all 153 with Pb >= 10 | **16 (10.5%)** | 103 (67.3%) | 111 (72.5%) | 124 (81.0%) | 141 (92.2%) |
| caught, 60 powders | 2 (3.3%) | 29 (48.3%) | 34 (56.7%) | 40 (66.7%) | 50 (83.3%) |
| caught, 93 roots | 14 (15.1%) | 74 (79.6%) | 77 (82.8%) | 84 (90.3%) | 91 (97.8%) |

| product type (Table S8 code) | samples | Pb >= 10 ug/g | Pb >= 1,000 ug/g |
|---|---|---|---|
| loose powder (1) | 162 | 57 | 24 |
| packaged powder (2) | 30 | 3 | 0 |
| polished root (3) | 235 | 83 | 66 |
| unpolished root (4) | 76 | 10 | 1 |
| all | 503 | 153 | 91 |

- **Contamination here is mostly heavy, but rarely heavy enough for bench Raman.** The median lead of the 153
  laced samples is **1,287 ug/g** (about 0.2% w/w lead chromate); 91 of them hold 1,000 ug/g or more. Yet only 16
  (10.5%) reach the 0.5% bench Raman limit, the highest at 6,416 ug/g (loose powder, Buxar).
- **A screen at 0.1% would catch two in three** (103 of 153), and one at 0.025% four in five. The jump from 0.5% to
  0.1% is worth 57 percentage points here, against 39 points for NYC's case spices (24% to 63% of those with
  >= 100 ppm, README section 3). Counted the same way (Pb >= 100 ug/g, n = 131), this market reaches 12.2% at 0.5%,
  78.6% at 0.1%, 84.7% at 0.05% and 94.7% at 0.025%.
- **Polished roots carry most of it**: 66 of the 91 samples at >= 1,000 ug/g are polished roots, where the pigment
  is a surface coat. A screen that reads the root surface sees the coat, not the whole-root average, so for roots
  these bulk numbers understate what a surface reading would see. Powders are the hard case: their laced samples
  sit lower (median 515 ug/g, about 0.08%), and 0.5% catches 2 of 60.
- Packaged powder was almost clean (3 of 30 at >= 10 ug/g, highest 240 ug/g).

## Grading the pre-registration (written before the run; graded as written)

| | prediction | result |
|---|---|---|
| P0 | parse finds 153 +/- 5 samples with Pb >= 10 | **met: 153 of 503 rows** (after the parser fix below) |
| P1 | (60% confident) Table S8 has a per-sample chromium column | **failed: no chromium column** |
| P2a-c | XRF Pb:Cr medians by form | not gradable (no chromium) |
| P3 | a 0.5% screen catches at most 10% of the Pb >= 10 samples | **failed, narrowly: 16 of 153 = 10.5%** |
| P4 | a 0.005% screen catches 40-80% of them | **failed: 141 of 153 = 92.2%** |
| P5 | Lopez 2022 coriander with Pb < 5 mg/kg has ICP-MS Cr <= 2 mg/kg | met (one sample: 0.22) - see [lopez2022-coriander-series.md](lopez2022-coriander-series.md) |
| P6 | at least one Lopez Patna coriander with Pb >= 50 and molar Pb:Cr 0.8-1.8 | met (8 of 8 with Pb >= 50, ratios 1.13-1.63) |

P4 failed in an informative direction. It assumed laced samples would spread down toward the detection limit, as
NYC's do. They do not: once a lot is laced it is laced at hundreds to thousands of ug/g, and only 12 of the 153 sit
between 10 and 32 ug/g.

## How the numbers were made

The sealed job `turmeric-forsyth-pbcr-v1` (turmeric_xrf.py 0.1.0, python:3.12, pdfplumber 0.11.4) downloaded the
supplement from Springer and saved every page's text. Its table parser found 0 rows: Table S8 is plain text with no
ruled lines, and the locator stopped at the table of contents on page 2. The 503 rows are on pages 15-27 of the saved
text. turmeric_xrf.py 0.2.0 adds `parse_s8_text()`, which reads those lines, and `--supp-text` to run on the saved
text without a download. The saved text is committed as
[`data/forsyth2026_supp_text.txt`](../data/forsyth2026_supp_text.txt) (CC BY 4.0, Forsyth et al.), and
`test_turmeric_xrf.py` asserts every count on this page from it, so they are rechecked whenever the tests run:

```
python -m unittest -v test_turmeric_xrf
python turmeric_xrf.py --supp-text data/forsyth2026_supp_text.txt --out-dir out
```

## Limits

- Handheld XRF on bagged powder or whole roots, not ICP-MS. The paper checked 16 samples by ICP-MS; for roots,
  surface heterogeneity adds error.
- "2" is the most common lead value (the table does not say so, but it looks like half the 4 ug/g LOD). It does not
  affect any count at >= 10 ug/g.
- The type legend printed with Table S8 ("double-polished roots=4, single-polished roots=5") does not match the codes
  in the data (1-4). The product code at the end of each sample ID (from the paper's field guide: 4/6/8 polished,
  5/7/9 unpolished) maps one-to-one onto codes 3 and 4, so 3 is read as polished root and 4 as unpolished root.
- A few sample IDs appear twice with different producer-state codes (e.g. 18_RG_2_1_1); rows are counted as
  published, which gives the paper's n = 503.
- The reach counts treat all the lead as lead chromate, the best case for a chromate screen. The paper reports that
  every sample above 10 ug/g also held chromium "at levels suggestive of lead chromate", but prints no chromium
  numbers.
- The 0.5% limit is for bench FT-Raman on ground turmeric (Erasmus et al. 2021); handheld devices and root surfaces
  will differ.

## Pre-registration (as written 2026-10-16 ~12:45Z, before the job)

> P0 parse check: the job finds a lead column and 153 +/- 5 samples with Pb >= 10 ug/g (the paper's 30%, n = 153).
> P1 (60% confident): Table 8 has a per-sample chromium column. P2 (if P1): powders with Pb >= 300 ug/g and a
> numeric Cr: median molar Pb:Cr in [0.6, 1.3]; roots: below 0.6; Pb 10-200: Cr non-detect in at least half.
> P3: a 0.5% w/w lead chromate screen (>= 3,206 ug/g Pb) catches at most 10% of the Pb >= 10 samples. P4: a 0.005%
> screen (>= 32 ug/g Pb) catches between 40% and 80% of the Pb >= 10 samples. P5: coriander powders with Pb < 5 mg/kg
> have ICP-MS Cr at most 2 mg/kg. P6: at least one Patna coriander powder has Pb >= 50 mg/kg with molar Pb:Cr in
> [0.8, 1.8].

We found no earlier count of how much of this survey a lead chromate screen at a given limit would catch; the paper
reports prevalence and drivers, not screen reach.
