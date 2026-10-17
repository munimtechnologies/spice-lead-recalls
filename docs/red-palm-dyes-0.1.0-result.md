# Result: where does Sudan-dyed red palm oil on Canadian shelves come from? (red-palm-dyes 0.1.0)

**Author:** MV2, Munim, Inc. (mv2@munimtech.com). Work made with AI agents.
**License:** text and derived data CC BY 4.0; code Apache-2.0.
**Grades:** [red-palm-dyes-0.1.0-prereg.md](red-palm-dyes-0.1.0-prereg.md) (release v0.4.8),
written before any amount in the 2019-20 file was read.

**Status: confirmed by a sealed compute run (2026-10-17).** This grade was first produced by
reading the two CFIA files directly and transcribing every sample number, declared origin and
non-zero amount into `data/red_palm_dyes_transcribed_samples.csv`, then running the committed
grader on it. The pre-registered sealed run of `red_palm_dyes.py` (job `red-palm-dyes-v1`) has
now downloaded and frozen both files (2019-20 sha256 `4454588b…`, 2020-21 sha256 `13d83be3…`)
and graded them with no network at analysis time. **It reproduced the transcription exactly:**
same 72 + 32 samples, same two Sudan IV positives (47.5 and 15.61 ppm, both Nigeria), same
per-origin counts, same 5-of-6 grade. The sealed per-sample table is committed as
`data/red_palm_dyes_sealed_samples.csv`; it agrees row for row with the transcription.

## Checks on the transcription

- **Every block was read.** The 2019-20 file is sorted by colour (18 blocks of 72 rows).
  Each block's row count and every non-zero value were read in three overlapping chunks,
  and the Sudan blocks were read twice, with different questions. The 2020-21 file (576 rows,
  sorted by sample) was read twice. Across both files there are two non-zero amounts, and
  both passes found the same two. The sealed run later confirmed these are the only two.
- **CFIA's own reports agree.** The 2019-20 report says "Of the 72 samples tested, 1 sample
  was positive for Sudan IV with a concentration of 47.5 ppm". The 2020-21 report says 1 of 32,
  Sudan IV at 15.6 ppm. Neither report names a country of origin or breaks results down by
  origin.
- **A recall agrees.** The 2020-21 report footnotes the recall "Obiji brand Palm Oil recalled
  due to Sudan IV": Obiji *Nigerian* Palm Oil Grade A, sold in Alberta and British Columbia,
  recalled 1 February 2021. In the file, the 2020-21 positive is declared from Nigeria and was
  sampled in CFIA's West region on 2020-11-08. This fits, but the file gives no brand, so the
  match is not proven.

## Grade: 5 of 6 met

| | prediction | value | status |
|---|---|---|---|
| P1 | in 2019-20, at least one sample carries a Sudan dye | 1 | met |
| P2 | in 2019-20, at most 10% of samples carry a Sudan dye | 1 of 72 (1.4%) | met |
| P3 | every Sudan-positive sample (both years) declares a West or Central African origin, or none | 0 of 2 outside | met |
| P4 | Sudan IV is found in at least as many positives as any other Sudan dye | Sudan IV 2, others 0 | met |
| P5 | Ghana is the declared origin of at least as many positives as any other single origin | Nigeria 2, Ghana 0 | **not met** |
| P6 | no non-Sudan non-permitted colour in any sample of either year | 0 | met |

The parse was gradable: 72 base samples in 2019-20 (at least 60 were needed) and Sudan IV present. The two "D" ids
(C2019FFPO00019D and C2019FFPO00035D) have no undecorated twin in the file, so no
duplicate merge happened.

## The two dyed samples

| year | sample | declared origin | CFIA region | sampled | dye | ug/g |
|---|---|---|---|---|---|---|
| 2019-20 | C2019FFPO00009 | Nigeria | Atlantic | 2020-03-17 | Sudan IV | 47.5 |
| 2020-21 | C2020FFPO00041 | Nigeria | West | 2020-11-08 | Sudan IV | 15.61 |

## By declared origin (both years, descriptive)

| origin | 2019-20 | 2020-21 | both | dyed |
|---|---|---|---|---|
| Ecuador | 47 | 13 | 60 | 0 |
| Ghana | 10 | 4 | 14 | 0 |
| Malaysia | 6 | 4 | 10 | 0 |
| Nigeria | 3 | 5 | 8 | **2** |
| Colombia | 2 | 1 | 3 | 0 |
| Togo | 1 | 2 | 3 | 0 |
| Unknown | 2 | 1 | 3 | 0 |
| Senegal | 1 | 0 | 1 | 0 |
| Ivory Coast | 0 | 1 | 1 | 0 |
| Cameroon | 0 | 1 | 1 | 0 |
| **all** | 72 | 32 | 104 | 2 |

West or Central African origins: 2 dyed out of 28 (7.1%). Malaysia, Ecuador and Colombia:
0 out of 73. Chlorophyllin, which is reported but not graded, was zero in every sample.

## What it means

1. **The dye in Canada's imported red palm oil was rare and came only from West Africa.**
   Two of 104 retail samples were dyed (1.9%), both with Sudan IV and both declared from
   Nigeria. Every Malaysian and South American oil was clean. CFIA's 2017-18 survey (1 of 27,
   44.9 ppm Sudan IV, from its 2020-21 report) points the same way: about one dyed retail
   sample a year.
2. **Ghana was the wrong guess (P5).** We predicted Ghana because Ghana's regulator reports
   the most dyed oil in its own market. None of the 14 Ghana-declared samples in Canada was
   dyed. In 2019-20 the count was 0 of 10. If Ghana-declared export oil were dyed at FDA Ghana's
   2019 market rate (26.6%), the chance of 0 in 10 would be about 4.5%. The exact one-sided
   95% upper bound on the dyed share is 25.9% for 0 of 10 and 19.3% for 0 of 14.
3. **A caution on that comparison.** The two figures come from different sampling frames.
   FDA Ghana sampled open-market oil, much of it unbranded. CFIA bought packaged, labelled,
   imported oil at Canadian retail (46 of the 72 were organic, per CFIA's report). The
   counts are small, "origin" is what the label declares, and FDA Ghana's figures are quoted
   from its own trend paper (SSRN 4954945), not recomputed. The safe reading is narrow:
   *the dyed oil that reached Canadian shelves was declared Nigerian, not Ghanaian*. It does not
   show that Ghanaian oil is clean, and it does not show that Nigeria has a worse problem.
4. **For screening.** Both findings were Sudan IV alone, at 15-48 ppm. That is 15 to 95 times
   the 0.5-1 mg/kg detection limit the EU requires of official laboratories (Commission
   Decision 2004/92/EC). So a dye screen at an importer could catch the cases CFIA found with
   far less than lab sensitivity: a target of about 10 ppm Sudan IV in oil would have caught both.
   We have not checked any particular handheld method against that target. It is a
   requirement, not a claim about a device. With one dye and one origin in both years,
   declared West African origin is the obvious place to start sampling.

## Prior art and why this is new

CFIA publishes one headline per survey and no breakdown by origin (checked on both report
pages). FDA Ghana, KNUST (2016), Scientific African (2021) and J Food Qual (2026) measure
inside Ghana. We found no published per-origin analysis of CFIA's open red palm oil files,
and no comparison of a destination country's retail results with Ghana's market trend.

## Files

- `data/red_palm_dyes_transcribed_samples.csv`: 104 rows (year, sample id, declared origin,
  non-zero colours), transcribed from the CFIA files (Open Government Licence - Canada).
- `data/red_palm_dyes_sealed_samples.csv`: the sealed run's 104-row per-sample table
  (adds CFIA region, date, Sudan dye list, highest Sudan ug/g and component count), produced
  by `red_palm_dyes.py` from the frozen downloads; agrees with the transcription.
- `test_red_palm_dyes_result.py`: rebuilds CFIA's 18-colour layout from the transcription,
  runs the registered `red_palm_dyes.py` grader, and pins every number above.
- Sources: open.canada.ca datasets f0aa9c6f-984f-4cc8-a7d7-b679c6e64e10 (2019-20) and
  5841c1a3-055e-489a-8766-1781a908903f (2020-21); CFIA reports "Non-Permitted Food Colours
  in Red Palm Oil" (April 2019-March 2020 and April 2020-March 2021), inspection.canada.ca;
  recall "Obiji brand Palm Oil recalled due to Sudan IV", recalls-rappels.canada.ca (2021).

Contains information licensed under the Open Government Licence - Canada.
