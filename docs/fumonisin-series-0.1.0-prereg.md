# Pre-registration: CFIA's newly opened 2011-12 and 2012-2018 fumonisin files against their reports (fumonisin-series 0.1.0)

PREREG-MARKER: fumonisin-series-0.1.0-prereg

Made with AI agents working in MV2's (Munim, Inc.) name. Text CC BY 4.0; code Apache-2.0.
Not a compliance finding and not dietary or medical advice. Canada has no maximum level for
fumonisins in food, as both reports say, so no sample is judged against one here.

## Why these files

On 2026-11-03 the Canadian Food Inspection Agency (CFIA) published three per-sample fumonisin files
on open.canada.ca (Open Government Licence - Canada). The 2010-11 file has its own
[pre-registration](fumonisin-2010-0.1.0-prereg.md). This note covers the other two. Their reports
date from 2018 and 2024; the files are new. Searches on 2026-11-07 found no analysis of either
file. As in the rest of the [CFIA chemistry surveys index](cfia-chemistry-surveys-index.md), every
prediction below is fixed from the printed reports alone, **before any part of either file has
been opened** (not its header, its labels or its values).

- **A, 2011-12.** Report page: inspection.canada.ca, "2011-2012 Fumonisins in Corn-Based and
  Soy-Based Products" (a summary page, modified 2018-09-04; the full report is available only on
  request). Dataset e5906422-e8bf-498b-972e-faf2b688aa97, resource
  fe5490e6-35c6-4175-be9d-8b679548784d, "CHEM TS 2011-2012 Fumonisins in Selected Foods", CSV.
  Portal metadata read on 2026-11-07: size 155, MD5 9f6fddeb2448a199d1beae925a5f3a96, created
  2026-11-03T18:42:14.
- **B, 2012-2018.** Report page: inspection.canada.ca, "Fumonisins in grain-based foods, soy
  products and teas, April 1, 2012 to March 31, 2018" (full report with 16 tables and two
  appendices, modified 2024-06-20). Dataset 449c63d9-c545-4cce-b907-e32840967873, resource
  df04bd3f-d591-49dc-91c7-0e498b74f22f, "CHEM TS 2012-2018 Fumonisins in Selected Foods", CSV.
  Portal metadata read on 2026-11-07: size 1371, MD5 6c87fb0bc35b3fc0cea0d3bd2e93e97b, created
  2026-11-03T18:42:25.

## What the reports print

**A (2011-12 page).** 454 samples: 274 corn-based and 180 soy-based. All analysed for fumonisins
B1 and B2. 162 of 454 (36%) had detectable fumonisins: 161 corn-based (59%), 20.8 to 4442.5 ppb,
the 4442.5 ppb a cornmeal; and one soy flour at 22.4 ppb. No averages, origins or dates.

**B (2012-2018 report).** 4,261 samples (grain-based foods 3,650, soy-based products 185, tea
426), sampled April 2012 to March 2018 in six cities, tested for fumonisins B1 and B2; "FB level"
is their sum, and averages are of detectable values only. 1,076 positive (25%). Table 1 splits
each group by origin (domestic / imported / unspecified: grain 721 / 1770 / 1159, soy 64 / 83 /
38, tea 61 / 171 / 194; total 846 / 2024 / 1391). Table 2: grain 1073 (29) 20-7790, average 365;
soy 2 (1) 27-45, average 36; tea 1 (0.2), 43; total 1076 (25) 20-7790, average 364. Table 3 gives
16 grains; Tables 4-16 give CFIA rows by survey year (labelled by the April-March year's first
year); Appendix A splits conventional and organic, Appendix B corn foods. Table 7 also restates
the 2010-11 and 2011-12 corn surveys.

## Report arithmetic (no file needed; checked now)

`test_fumonisin_series_prereg.py` pins the printed figures and checks each item below with
standard-library Python.

- R1. Table 1's rows and columns add up (3650 / 185 / 426; 846 / 2024 / 1391; 4261). **Holds.**
- R2. Table 2: 1073 + 2 + 1 = 1076; every share rounds as printed; 365, 36 and 43 weighted by
  1073, 2 and 1 give 364.1 (printed 364). **Holds.**
- R3. Table 3's sixteen grain rows add to **3,584**, not 3,650; their positives add to 1,073 as
  they should. **Fails.** The teff table's CFIA rows (2012-2015: 13 + 8 + 14 + 42) add to 77,
  and with 77 in place of Table 3's 11 the grain rows add to exactly 3,650. Table 3's own teff
  share fits 77 too: 1 of 77 is 1.3% (printed "1"), while 1 of 11 would be 9%.
- R4. Every grain's year rows add to its Table 3 count and positives, except teff (77 against
  11) and rice (170 against 189; the rice table has no 2012 row). Soy's year rows add to 185 and
  tea's single row to 426. **Fails for teff and rice only.**
- R5. Three year rows cannot be right as printed. **Fails.**
  - Wheat 2012: three positives with a minimum of 28.8 and a maximum of 393 cannot average 99.7
    (the 2013 row's figure): the three must average at least (28.8 + 28.8 + 393) / 3 = 150.2.
  - Rice 2014: one positive cannot have a minimum of 33 and a maximum of 249; its 33 and 41.7 are
    the 2013 row's minimum and average.
  - Oat 2017: 1 positive of 3 is printed "(67)"; it is 33% (67% is the wheat row's 2 of 3).
- R6. Appendix B's eighteen corn foods add to 1,688 samples and 1,030 positives (Table 3's corn
  row). Every share rounds as printed except children's breakfast cereals: 167 of 214 is **78%**,
  printed 68. **Fails for that cell.**
- R7. Corn's year rows (2012-2017), weighted by their positives, average 375.50, and oat's
  128.55; Table 3 prints 375.5 and 128.5, within the rounding of the year averages. Rice's five
  positives and wheat's thirteen are taken up in B-V7 and B-V6. **Holds.**
- R8. Appendix A's organic columns add to 1,322, the text's organic count, exactly, once the
  organic black teas (printed "N/A") are taken as 100 - 86 = 14. The conventional columns add to
  2,865, which is 74 short of the text's 2,939. Teff is the one row of Table A1 that matches
  neither Table 3 nor Table 13 (2 conventional + 1 organic = 3); 76 conventional teff samples
  would make the conventional total 2,939 and teff 77. **Fails as printed**; the arithmetic points
  to 77 teff samples in three independent ways (R3, R4, R8).
- R9. The sentence "The 185 soy-based products tested included 26 tofu samples, 24 soybean
  samples, 16 ..." lists Table A2's **conventional** column, which adds to 111; A2's totals add to
  185 (tofu 30, soybeans 40, soy beverages 40, soy flour 29, formula 20, ...). Recorded as a text
  slip.
- R10. The text says "Only 2 samples of tofu contained detectable levels of fumonisins". Table A2
  gives one positive tofu (conventional, 1 of 26, maximum 27) and one positive soy flour
  (organic, 1 of 16, maximum 45), and Table 15 gives one positive in 2012 (27) and one in 2013
  (45). **The report contradicts itself**; V3 lets the file decide.
- R11. The text gives conventional products' range as 20 to 7710 ppb; Table A1 (corn, and the 2012
  corn row) gives 7711. Recorded as a slip of the text.
- R12. Report against report: Table 7's 2011 corn row (274, 161 (59), 4 442.5) has a minimum of
  **23.1**, where the 2011-12 page says 20.8. Its 2010 row (276, 157 (57), 20, 6650) matches the
  2010-11 page and adds an average, **268**, which that page does not print. V2 for file A and
  V5 for the 2010-11 file let the files decide.

## Gates (G), checked before anything else

For each file, the job downloads the resource and fails that file's gate unless:
1. its MD5 is the portal's (A: 9f6fddeb2448a199d1beae925a5f3a96; B: 6c87fb0bc35b3fc0cea0d3bd2e93e97b);
2. its size is in the portal's band, read as bytes divided by 1,024 and **rounded up** (the
   convention that fits all four files checked so far): A, 155 KiB, more than 157,696 and at
   most 158,720 bytes; B, 1371 KiB, more than 1,402,880 and at most 1,403,904 bytes; and
3. it parses as a CSV with a sample, product, analyte, value and unit column (found by name).

If CFIA replaces a file, its gate fails and is reported as failed; this note is not edited.

## Census items (names and counts only; read before any value)

File A:
- A-C1. 454 distinct samples.
- A-C2. The product labels split into 274 corn-based and 180 soy-based samples (map from names,
  published before any value is read).
- A-C3 / A-C4. Analyte labels are a subset of {B1, B2, total} with no B3; every unit is on the ppb
  scale (ppb, ng/g or µg/kg).

File B:
- B-C1. 4,261 distinct samples.
- B-C2. The labels split into 3,650 grain-based, 185 soy-based and 426 tea samples.
- B-C3 / B-C4. As A-C3 / A-C4.
- B-C5. If the file has an origin column, its split is Table 1's in all nine group cells
  (721 / 1770 / 1159, 64 / 83 / 38, 61 / 171 / 194).
- B-C6. **Teff: 77 samples, not Table 3's 11**, by the April-March year of the sampling date
  13 / 8 / 14 / 42 for 2012-13 to 2015-16. Graded from the grain named in the labels; if no
  label or column names teff, B-C6 is reported as not gradable, not as held.
- B-C7. Rice: 189 samples, 19 of them sampled in 2012-13 (the year the rice table leaves out).
- B-C8. By sampling year: soy 94 in 2012-13 and 91 in 2013-14; all 426 teas in 2016-17; corn
  328 / 307 / 320 / 0 / 1 / 732 for 2012-13 to 2017-18. (A reading by the year in the sample ID
  is reported beside it and does not change the grade.)
- B-C9. If the file marks organic products, 1,322 are organic and 2,939 conventional.

## Value items (graded only after the census note, label maps and grader are public)

A sample's **total** is its stored total-fumonisins value if the file has one; otherwise B1 plus
B2, with a missing or non-detect row counted as zero. A sample is **positive** when its total is
above zero. Printed figures are matched at their printed precision (for example, 253.2 means at
least 253.15 and below 253.25). Averages are of positives only, as both reports state.

File A:
- A-V1. 162 positives: 161 corn-based and 1 soy-based, a soy flour whose total rounds to 22.4.
- A-V2. The smallest corn-based positive rounds to **20.8** (the 2011-12 page), not 23.1
  (Table 7). Whichever value the file holds is reported.
- A-V3. The largest total rounds to 4442.5 and is a cornmeal.
- A-V4. The 161 corn-based positives average 253.2 (Table 7).

File B:
- B-V1. 1,076 positives: 1,073 grain-based, 2 soy-based, 1 tea.
- B-V2. The smallest positive rounds to 20 and the largest to 7790; the largest is a cornmeal.
- B-V3. The two soy positives are a tofu sampled in 2012-13 (rounds to 27) and a soy flour sampled
  in 2013-14 (rounds to 45), as Tables A2 and 15 say. If both are tofu, the text's sentence holds
  and B-V3 fails.
- B-V4. The tea positive is a black tea and rounds to 43.
- B-V5. Table 3, cell by cell, for the eleven grains with positives (positives, minimum, maximum,
  average), with the grain map published in the census note. Each cell is reported; the item
  holds if every cell matches.
- B-V6. **Wheat 2012-13: three positives, 28.8 and 393 and a middle value from 130.2 to 136.8, so
  an average from 184.0 to 186.2, not 99.7.** (Table 3's 122.8 over 13 positives, less the 2013,
  2014 and 2017 rows, leaves 552.0 to 558.6 for the three.)
- B-V7. **Rice: five positives, 33 and 47 and a middle value from 44.95 to 45.25 in 2013-14, a
  single 249 in 2014-15, and 42 in 2017-18.** (The 2013 row's average 41.7 and Table 3's 83.2 over
  five both fit only this.)
- B-V8. Oat 2017-18: 1 positive of 3 samples, rounding to 53.
- B-V9. Children's breakfast cereals with corn: 167 positives of 214 (78%), if the labels let that
  group be mapped from names; otherwise not gradable.
- B-V10. Table 7's corn rows for 2012-13, 2013-14, 2014-15 and 2017-18 (samples, positives,
  minimum, maximum, average), cell by cell.
- B-V11. Table 2's averages: grain 365, soy 36, total 364.

Added item for the 2010-11 file (fixed now, before any value of that file has been read; its
names-only census has not yet run):
- 2010-V5. The 157 positives of the 2010-11 file average 268 (at least 267.5 and below 268.5), as
  Table 7 of the 2012-2018 report prints.

## Reported afterwards, not graded

Origin, region and organic splits beyond the items above, how each file writes non-detects,
positives by product label, the per-year corn rows not graded, and Table 1's origin split for
grain foods if the file has no origin column.

## Order of work

1. This note and its arithmetic test are published.
2. A names-only census job (gates, A-C1 to A-C4, B-C1 to B-C9) runs; the census note publishes the
   label maps and a grader before any value is read.
3. A sealed job grades the value items only after step 2 is public.
4. An independent test re-runs the published result from GitHub.

MV2, Munim, Inc., mv2@munimtech.com
