# food-colours 0.1.0: CFIA's open food-colour files (2009-10 and 2018-19) against their printed reports — pre-registration

PREREG-MARKER: food-colours-0.1.0-prereg

By MV2 of Munim, Inc. Prepared with AI agents working in his name. Text CC BY 4.0; code Apache-2.0.

Fixed on 2026-11-01 from the printed reports alone. No value in either open file has been read by
anyone working on this, and neither file has been opened. A sealed job will first run a
names-only census (labels, units and cell shapes, never values) once this note is public. The
label maps and a grader will then be published before any value is read, as in the earlier
series ([index](cfia-chemistry-surveys-index.md)).

This is a reproducibility check of open government data. It is not a compliance finding, not
about any brand, and not dietary or medical advice. In Canada, food colours are food additives
permitted under Health Canada's Marketing Authorizations. The 2018-19 report says Health Canada
found no sample posed an unacceptable health concern.

## The files

| ID | Survey | open.canada.ca dataset / resource | Bytes | Portal MD5 |
|---|---|---|---|---|
| c18 | Food Colours in Essences/Flavourings, Oils, Sweets and Processed Vegetables, 2018-04-01 to 2019-03-31 | `1b0c4141-7a22-4c93-8679-63eb49f7be24` / `3006ff94-fa7a-4cc4-8b58-a2164ce6a937` | 3,771,543 | `7651427618a70aa3ad2a51ab90bcae8c` |
| c09 | 2009-2010 Food Colours Used in the Production of Manufactured Foods | `e750a5e1-40e5-4428-b23f-cc3f613e7f9a` / `9c6e2a16-c552-41cb-b95c-240db3c75b8d` | 33,724 | `dc558d850720b90610da2c75424d1cd7` |

Reports: the CFIA pages "Food Colours in Essences/Flavourings, Oils, Sweets and Processed
Vegetables – April 1, 2018 to March 31, 2019" and "2009-2010 Food Colours Used in the Production
of Manufactured Foods" (summary page; it says the full text is available on request). The
2013-14 and 2021-22 food-colour reports reprint each survey's headline row.

## What the printed reports already say about themselves (no file needed)

- **R1. 2018-19 Table 3 and Table 2 differ by one detection.** Table 3's per-colour sample counts
  (Allura Red 101, Tartrazine 100, Brilliant Blue FCF 61, Sunset Yellow FCF 44, Erythrosin B 13,
  Amaranth 12, Indigo Carmine 3, Orange II 2, Rhodamine B 1) add up to **337**. Table 2's "number
  of times colours detected" (23 + 13 + 40 + 260) adds up to **336**.
- **R2. 2018-19: 218 or 219 colour-free samples.** Table 2 has 181 of 399 samples with colours, so
  218 have none, which the summary and the dataset record repeat. The results text says 219.
- **R3. Orange II.** Table 3 gives Orange II 2 detections, a maximum of 0.221 ppm and an average
  "below LQ (0.13)". For the average to be under 0.13, the second result must be under 0.039 ppm,
  well below the LQ. A below-LQ result counted in one table but not the other would explain R1.
- **R4. The 91% sentence fits both totals.** Allura Red, Tartrazine, Brilliant Blue and Sunset
  Yellow give 306 detections: 91.1% of 336 and 90.8% of 337.
- **R5. 2009-10's later reprints agree with its own page.** The 2013-14 report's Table 4 gives
  100 samples, 41% detection, 93% compliance and 7 non-compliant samples (8 results), which
  matches the 2009-10 page (59 without colour; 4 + 2 + 1 = 7 violations, the dried papaya with
  two). The 2021-22 report's Table 4 reprints 2018-19 as 399 / 45 / 98.7 / 5 (5), as printed.

## Predictions

Graded by the census (labels, counts and cell shapes only):

- **G18 (gate).** c18: byte size and MD5 as on the portal; **399** distinct sample IDs; every
  result row names a colour and a unit; no more than 43 distinct colour labels (Appendix A lists
  45 entries; Orange II and Rhodamine B appear in both the water-soluble and fat-soluble lists).
- **G09 (gate).** c09: byte size and MD5 as on the portal; **100** distinct sample IDs.
- **S1.** c18's product-type counts are 50 essences/flavourings, 99 oils, 50 processed vegetables
  and 200 sweets, once product labels are mapped to these four (the map is published with the
  census before any value is read).
- **S2.** c18's origin totals are 56 domestic, 184 imported and 159 unspecified, if the file has an
  origin or Function column. **S2b** (stricter): all 12 cells of Table 1 match (essences 10 / 14 /
  26, oils 15 / 51 / 33, processed vegetables 8 / 38 / 4, sweets 23 / 81 / 96). Totals have matched
  far more often than splits in this series, so S2b is the less certain one.
- **S3.** c09 is far smaller than 100 samples × 212 colours. Prediction: it does **not** carry one
  row per sample per colour tested (fewer than 2,000 rows).

Graded later by a published grader (values; ppm):

- **V1. 2018-19 Table 2.** Samples with at least one colour above zero: essences 9, oils 13,
  processed vegetables 28, sweets 131 (**181**). Colour results above zero: 23, 13, 40, 260
  (**336** under Table 2), with each of the 13 oil positives carrying exactly one colour.
- **V2. 2018-19 Table 3.** For each of the nine colours, the number of samples and the maximum
  match (539, 144, 85, 98.6, 124, 83.5, 50.6, 0.221, 10.8). The averages match within rounding
  (78.7, 27.1, 9.5, 20.5, 39.3, 26.9, 21.3; Rhodamine B 10.8). No other colour has a result above
  zero.
- **V3. R1 settled (directional).** The file holds **337** colour results above zero, so Table 3
  matches it. One Orange II result is under 0.039 ppm, and Table 2's 336 leaves that result out.
  If the file has 336, this fails and Table 3 has one row too many.
- **V4. R2 settled.** The file has **218** samples without any colour above zero (Table 2 and the
  summary), not 219.
- **V5.** Among samples with colours, 177 or 178 carry one to four colours ("98%"), so 3 or 4
  carry five or more.
- **V6.** The highest level of any colour (Allura Red, 539 ppm) is in a sample labelled as candy
  ("highest levels ... in soft and hard candy").
- **V7.** Rhodamine B (the non-permitted colour) is in exactly one sample, at 10.8 ppm.
- **V8. 2009-10.** 41 of 100 samples have a colour above zero and 59 have none. No fat-soluble
  colour (Sudan dyes and the others in the fat-soluble list) is above zero. Sunset Yellow,
  Tartrazine, Brilliant Blue, Allura Red and Amaranth make up 93% of colour results above zero
  (92.5-93.5%).
- **V9. 2009-10 named samples.** If the file has product names, it holds a chicken tandoori
  seasoning, a lumpfish, a horseradish with beets, a cheddar cheese, an almond paste, a curing
  powder and a dried papaya. Their origins are USA, USA, Canada, Canada, Belgium, Thailand and
  Canada, if the file records origin. Each carries a colour above zero.

Descriptive, not graded: whether c18 lists every colour for every sample or only the colours
tested in that sample (water-soluble, oil-dispersible or both); how below-LQ results are coded;
duplicate or identical multi-colour profiles (twin scan); and sample-number blocks and date
columns, which have shown problems elsewhere in this series.

## Limits

- Neither file gives a regulatory limit per colour, so compliance (5 and 7 non-compliant samples)
  cannot be graded. V7 and V9 check only presence.
- The 2009-10 full report is not online. Its predictions come from the summary page and the
  2013-14 reprint.
- "Above zero" is the file's own coding. If the files code non-detects in another way, the census
  note will say how, and the grader will use that coding as written in the census note, before
  any value is read.

Prior art: searches on 2026-11-01 found the CFIA report pages, the open-data records and later
CFIA reports that reprint these surveys' headline rows. They found no analysis of the per-sample
food-colour files and no check of the reports' tables against them or against each other.

MV2, Munim, Inc., mv2@munimtech.com
