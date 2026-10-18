# Deviation: raman-reach 0.1.1 (parser fix; predictions unchanged)

**Author:** MV2, Munim, Inc. (mv2@munimtech.com). Work made with AI agents.
**License:** text CC BY 4.0; code Apache-2.0.
**Written:** 2026-10-18, after the 0.1.0 job failed and before any 0.1.1 grade was computed.
**Pre-registration:** [raman-reach-0.1.0-prereg.md](raman-reach-0.1.0-prereg.md). Its nine predictions, thresholds
and ranges are unchanged; only the parser changes, and every rule that needed a choice is reported both ways.

## What happened

The sealed 0.1.0 job (2026-10-18 08:26-08:30 UTC) downloaded the supplement (40 pages, sha256
`f728f8c613ed9dafdc730f595049fd326affd29e9827e4f4a1e20b69079b9193`), found no Table 8 caption, parsed no rows and
stopped with "no lead rows parsed", as designed. It sealed the supplement's full text for a new parser.

**We read that sealed text before writing 0.1.1**, including all rows of Supplementary Table 8, to find out why
the parser failed. We also counted rows with text search to set the targets for this fix. So 0.1.1 was written
with the data in view. The predictions cannot change, but every rule choice below could have been steered. That
is why each one is reported next to the frozen reading.

## Causes and fixes

- **D1 (captions).** The supplement prints a manuscript line number before every caption ("154 Table S8.
  Turmeric market sample data used in analyses (n=503)"). The caption pattern was anchored at line start.
  Fix: allow an optional leading number.
- **D2 (header).** The table's header row holds variable names, not labels:
  `sampid_ city_final all_pb_avg type_groupfull4 sellstate_bin turm_major`. `\bpb\b` cannot match inside
  `all_pb_avg` because `_` is a word character. Fix: read underscores as spaces in headers, so `all_pb_avg` is a
  lead mean column (the caption: "All_pb_avg: average sample lead level in ug/g").
- **D2b (layout).** The table has no ruled lines, and its columns are separated by single spaces, so none of
  0.1.0's three table extractors could split it. Fix: a parser for this table only. It requires the header to be
  exactly those six names and reads each row as `sample city lead code sellstate [turm_major]`. Rows with a blank
  last column are kept. The six columns are sample ID, city, mean lead (ug/g), a type code, Bihar-or-not, and
  major-producing-state-or-not. There is **no state, form-name, market, date or chromium column**.

## Rules that needed a choice (reported both ways)

- **D3 (form codes).** The caption gives "loose powder=1, packaged powder=2, double-polished roots=4,
  single-polished roots=5". The column holds only 1, 2, 3 and 4. These codes are not words, so the frozen
  form rule makes every form unknown. **Reading A** maps the codes by count against the article's own Table S3
  (loose 162, packaged 19 + 11 = 30, double-polished 235, single-polished 76). The column's counts for codes
  1/2/3/4 are exactly 162/30/235/76, and no 5 occurs, so A reads 3 as double-polished and 4 as single-polished.
  **Reading B** applies the caption literally: 4 = double-polished, 3 undefined. As far as we can tell the
  caption's codebook is off by one for the two root types. That matters to anyone re-using the open table.
- **D4 (state).** The frozen rule takes state from a state column or a state name in the row. Neither exists,
  so the frozen reading cannot grade P3 or P6. **Readings A and B** map the 34 cities to their states (13 Bihar,
  6 Jharkhand, 7 Uttar Pradesh, 6 West Bengal, 2 Chhattisgarh; "Brahmpore" is Berhampore, West Bengal). The
  mapped counts reproduce Table S2 exactly: 134 / 77 / 200 / 60 / 32. The table's own `sellstate_bin` (Bihar=1)
  agrees with the map on every row. P3 and P6 only need "Bihar or not", so reading them from `sellstate_bin`
  gives the same grades as A.
- **No chromium column**, so P9 is not gradable in any reading.
- **No purposive marker.** No row names trucks, follow-up or December 2023, so all 503 rows stay in S, as the
  caption ("data used in analyses (n=503)") implies. Dhanbad and Prayagraj rows are in the table. The article
  also names those cities for a purposive follow-up. Nothing in the table separates the two, so we follow the
  caption.
- **Values.** The most common lead value is 2 ug/g (half the 4 ug/g detection limit), which reads as
  non-detects entered at LOD/2. The frozen rules treat it as 2 ug/g, below every threshold used here. One row is
  exactly 10 ug/g. The pre-registered E is strictly above 10, so P2's count can be one below the article's 153
  if the article counts 10 as exceeding. Some sample IDs occur twice; P1 counts rows, as the article's n=503
  does. The grader lists the repeated IDs.

## What 0.1.1 outputs

`summary.md` opens with the nine predictions graded three ways: frozen, A and B. It then lists the consistency
checks against Tables S2 and S3 (per-state counts, `sellstate_bin` agreement, code counts, unmapped cities,
repeated IDs, rows at exactly 10 ug/g). The ladder, state, form and over-500 tables follow under reading A.
`raman_reach_samples.csv` holds every parsed row with both form readings. If the job finds no rows it falls back
to 0.1.0's extractors and fails loudly as before.

Data: Forsyth J.E. et al., npj Science of Food (2026), doi:10.1038/s41538-026-00867-8, Supplementary Table 8,
licensed CC BY 4.0.
