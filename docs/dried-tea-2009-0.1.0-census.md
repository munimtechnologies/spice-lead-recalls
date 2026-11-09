# Census of CFIA's open 2009-10 dried-tea file: names and counts graded (dried-tea-2009 0.1.0 census)

CENSUS-MARKER: dried-tea-2009-0.1.0-census

Made with AI agents working in MV2's (Munim, Inc.) name. Text CC BY 4.0; code Apache-2.0.
Not a compliance finding and not dietary or medical advice. Dated 2026-11-09.

This note grades the census items of the [pre-registration 0.1.0](dried-tea-2009-0.1.0-prereg.md)
(gate, C1-C5) and its [addendum 0.1.1](dried-tea-2009-0.1.1-addendum.md) (A1-A7), from the
names-only census job `dried-tea-census-v1` (2026-11-09 04:05-04:09 UTC, sealed container, the
published `dried_tea_census.py` 0.1.0). Its full output is
[results/dried_tea_census_2009.json](../results/dried_tea_census_2009.json). **No concentration
value has been read.** One deviation is disclosed below (section "Deviation"). The value items
V1-V6 are graded by a separate job that runs only after this note and the grader
([dried_tea_grade.py](../dried_tea_grade.py)) are public.

## The file

- Resource 6fbadab4-f46f-4ab3-a1a6-e3d857253beb: 281,817 bytes, UTF-8 with a byte-order mark,
  MD5 f21f016693b4608ff7059d28be35bb26 (same as the portal record), SHA-256
  cdd6538d7a772d0edf638c630e2e287d1fd200d5f3b4916a1705decdc6b7ae2a.
- 2,166 rows, 15 columns: sample number, function (EN/FR), origin (EN/FR), product (EN/FR), date
  sampled, type of test (EN/FR), component (EN/FR), result, unit, plan code.
- Product is "Tea" in all 2,166 rows. Function: 311 "Domestic" rows, 1,855 "Import". Origin: 13
  countries or territories plus "UNKNOWN" (China 1,193 rows). Every row is dated 3, 9, 16 or 18
  December 2009, and the plan code is 2009_SB457 throughout.

## Gate

| Item | Result |
|---|---|
| G1 size in the portal's 276 KiB band (281,600 < bytes <= 282,624) | **Holds** (281,817) |
| G2 parses as CSV with a sample column found by name | **Holds** (column 0) |
| MD5 vs portal (reported, not gated) | Matches |

## Census items

| Item | Prediction | Census | Grade |
|---|---|---|---|
| C1 | 100 distinct samples (one trailing "A" removed) | 200 | **Fails** |
| C2 | Tea-type labels map to 24 / 41 / 12 / 13 / 10 | No tea-type field | **Not decidable** |
| C3 | Exactly 18 distinct metals | 18 | **Holds** |
| C4 | Mercury is one of them | Mercury, 100 rows | **Holds** |
| C5 | Units published per analyte group | Table below | **Holds** |
| A1 | PDF: 206/160 stated, 207/157 rows, 202/157 distinct, 6 shared, 353 names | Same counts | **Holds** |
| A2 | Long format | Long (component column) | **Holds** |
| A3 | 18 metal rows for every metal sample, 1,800 in all | 100 samples x 18 = 1,800 | **Holds** |
| A4 | Every pesticide row ends in "A"; no metal row does | 366 of 366; 0 of 1,800 | **Holds** |
| A5 | Every pesticide name is in the PDF table | 2 names are not | **Fails** |
| A6 | Only PESTICIDES-FPH053 and PESTICIDES-LC, both present | 148 and 218 rows | **Holds** |
| A7 | No pesticide row has a non-number result shape | 200 text rows | **Fails** |

**C1 fails because of how the file numbers samples.** Pesticide rows use 100 sample numbers
ending in "A" (2009TEA0001A, ...), as the PDF says. Metal rows use 100 other numbers, and the
examples the census printed end in "B" (2009TEA0001B, ...). The PDF does not mention a "B". With
one trailing "A" removed, the two sets never meet, so the census counts 200 samples. It found no
sample number that carries both metal and pesticide rows. The file looks like 100 teas, each
split into a pesticide part "A" and a metal part "B": both halves have the same origin mix (China 54
teas, Canada 15, Vietnam 5, the United Kingdom 5, the United States 5, Japan 3, Sri Lanka 3, and 10
from six other origins or of unknown origin). The census did not test the pairing directly, so it is
pre-registered below (P1). As 0.1.0 says, the value items are graded on the file as it is:
pesticide items over the 100 "A" samples and metal items over the 100 "B" samples.

**C2 is not decidable.** The file has no field for tea type (black, green, herbal/blend, oolong,
white). Product is "Tea" in every row. So V3 (violations by type) is **not graded**, and no label
map is needed. The per-type table on CFIA's report page cannot be rebuilt from the open file.

**C5 units.**

| Group | Unit | Rows |
|---|---|---:|
| Metals | µg/g | 1,800 |
| Named pesticides | µg/g | 166 |
| "Pesticide Screen" summary rows | n/a | 200 |

0.1 ppm = 0.1 µg/g, so the value job compares pesticide values with 0.1 as stored, without
converting.

**A1 holds.** The census re-extracted the English Information PDF (same MD5,
e1da1e61740d39fae96d935d74834894) and counted 207 GC-MS rows for 206 stated analytes, 157 LC-MS rows
for 160 stated, 202 and 157 distinct names, 6 names in both methods and 353 distinct names. So the
PDF's table disagrees with its own stated analyte counts. This is a small `report_internal` item for
the [CFIA open-data errata table](cfia-open-data-errata-0.3.0.md).

**A5 fails on two names.** The file's pesticide rows use 26 component names. 24 of them appear in
the PDF table. The other two:
- "Pesticide Screen" (200 rows): the table's *test* name. The file uses it as a summary row, one per
  sample and method (100 GC-MS and 100 LC-MS).
- "Endosulfan Total" (4 rows, GC-MS): the table lists endosulfan-alpha, endosulfan-beta and
  endosulfan sulfate, but no total. The file reports a sum of components it does not list
  separately.

**A7 fails on the summary rows.** 200 pesticide-group rows hold text, not a number, and their unit
is "n/a". The text has the form "2 Pesticides detected/détectés". There are as many of them as
"Pesticide Screen" rows (200), and every number-shaped pesticide row (166) has the unit µg/g, so the
166 rows of named pesticides appear to be all numbers, as A7 intended. The census counted shapes by
group, not by component, so the grader checks this row by row (P3). No pesticide row is blank or "<".

## Deviation: the census printed the screen rows' text

The addendum said the census "never prints, sums or compares a result value". It classified
result cells by shape and printed the text of the cells whose shape was text, to show how
non-detects are written. Those text cells turned out to be the 200 "Pesticide Screen" results, so
their content is now public:

| Screen text | Rows (sample x method) |
|---|---:|
| 0 Pesticides detected | 106 |
| 1 Pesticide detected | 45 |
| 2 Pesticides detected | 32 |
| 3 Pesticides detected | 11 |
| 4 Pesticides detected | 6 |

These are counts of detections, not concentrations. Two things follow:

1. **A file-internal check that holds.** The screen counts add up to 45 + 64 + 33 + 24 = 166
   detections, exactly the number of named-pesticide rows. By method, GC-MS has 148 - 100 = 48
   named rows and LC-MS 218 - 100 = 118.
2. **V1 is no longer fully blind.** The table does not say which GC-MS row belongs with which LC-MS
   row, but it bounds V1 (teas with any detected residue): 106 zero rows over 100 teas means
   between 6 and 53 teas have zero detections from both methods, so V1 lies between 47 and 94. The
   report's 69 is inside that range. V1 is still graded as registered, and this disclosure goes
   with it. V2 and V4-V6 depend on concentrations, which nobody has read.

## Added before any value is read (graded by the value job)

- **P1. Pairing.** With one trailing "A" or "B" removed, the 100 pesticide and 100 metal sample
  numbers are the same 100 numbers. We predict this **holds**. The job also reports how many metal
  sample numbers end in "B".
- **P2. Screen vs rows.** For each sample and method, the count in the "Pesticide Screen" text
  equals the number of named-pesticide rows for that sample and method. We predict this **holds**
  for all 200, with no row lacking a screen row.
- **P3. Named rows are numbers.** All 166 named-pesticide rows (components other than "Pesticide
  Screen") have a number shape and unit µg/g. We predict this **holds**.
- **V1 counted two ways.** V1 is graded on stored values above zero, as registered. The count of
  teas whose screen text is above zero for either method is reported alongside; P2 says the two agree.

V1, V2, V4, V5 and V6 stand as registered in 0.1.0. V3 is not graded (C2). The grader's rules:
- A named pesticide is detected when its value is above 0.
- A violation is a value above 0.1 µg/g. The count at or above 0.1 is reported too.
- A metal is detected when its value is above 0.
- V4 is graded for each of the 17 metals other than beryllium over the 100 metal samples.
- V6 holds if mercury is above zero in fewer than 87 of the 100 metal samples.
- The job also reports how the file writes metal non-detects (zero, blank or anything else), each
  metal's minimum and maximum, the maximum for mercury next to the 2010-11 page's 0.023 ppm, and
  violations by origin. None of these is graded.

## Next

1. This note, the census output and the grader are published (release v0.4.128).
2. Job `dried-tea-grade-v1` waits until this note and the grader are public, syncs the published
   code, runs its tests and grades V1, V2, V4-V6 and P1-P3 on the same file (same MD5).
3. The result note says which CFIA page the file supports on mercury (R5).

MV2, Munim, Inc., mv2@munimtech.com
