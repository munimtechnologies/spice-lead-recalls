# Addendum 0.1.1 to the dried-tea-2009 pre-registration: what the package's Information PDFs add

ADDENDUM-MARKER: dried-tea-2009-0.1.1-addendum

Made with AI agents working in MV2's (Munim, Inc.) name. Text CC BY 4.0; code Apache-2.0.
Not a compliance finding and not dietary or medical advice. Dated 2026-11-08.

This addendum adds items A1-A7 to [dried-tea-2009 0.1.0](dried-tea-2009-0.1.0-prereg.md). It is
fixed **before any part of CFIA's dried-tea CSV has been opened**: not its header, labels or values.
Items R1-R6, C1-C5 and V1-V6 of 0.1.0 are unchanged, except that A4 below says how C1 counts
samples. A4 was added because the PDF explains a suffix on sample numbers, and it is graded on its own.

## Source

A sealed job (`dried-tea-pdf-v1`, 2026-11-08 19:30 UTC) downloaded only the two "Information"
PDFs of open.canada.ca dataset 2782dbc5-ebbb-4ef1-a85f-294a5fe60f47 and extracted their text
with pdfminer.six:

- English, resource 628e68b6-9d35-4a0c-8514-cd5016623ff7: 396,766 bytes (388 KiB rounded up,
  the portal's size), 9 pages, MD5 e1da1e61740d39fae96d935d74834894.
- French, resource 39125e18-e4e0-46c0-87ee-9c85114481af: 376,950 bytes (369 KiB), 10 pages,
  MD5 64dd6a7b3455088886f8fb0aea4d7342.

The PDFs print no results. They say:

1. "Where feasible, samples were tested by 2 pesticide methods. All samples analysed for
   pesticides have an "A" at the end of the sample number."
2. "PESTICIDES-FPH053 is a GC-MS-based multi-residue method with 206 analytes" and
   "PESTICIDES-LC is an LC-MS-based multi-residue method with 160 analytes." The French PDF gives
   the same two numbers (PESTICIDES-FTM053 and PESTICIDES-CPL).
3. "For these multi-residue methods, only the detected pesticides are included in this dataset."
4. "All metal results (including non-detects) are provided."
5. A table, "Pesticide Screen Components", with one row per analyte: test type (method code),
   test name ("Pesticide Screen") and component (pesticide name). No metal is listed.

## A1. The PDF's analyte counts do not match its own table (checked now; no CSV needed)

Counting the table's rows in the extracted text:

| Method | Analytes stated | Rows in the table (EN) | Rows in the table (FR) |
|---|---:|---:|---:|
| GC-MS, FPH053 / FTM053 | 206 | 207 | 207 |
| LC-MS, LC / CPL | 160 | 157 | 157 |
| Total | 366 | 364 | 364 |

The GC-MS rows also repeat names. By our reading, Bendiocarb, Mexacarbate and Naled appear
twice each and Dicrotophos three times, so the 207 GC-MS rows hold **202 distinct names**. That is
4 fewer than stated, while the LC-MS table is 3 short. Six names appear in both methods' rows
(Chlorbromuron, Chlorthiamid, Methidathion, Mexacarbate, Oxadixyl, Tolyfluanid). That gives
**353 distinct component names** in all, which still fits the report's "over 340". (Ethoprophos,
GC-MS, and Ethoprop, LC-MS, are one compound under two names. They are counted as two names here,
because the file can only be matched on names.)

The census job re-extracts the English PDF and recounts all of this from its text. A1 holds if
the job finds 206 and 160 stated, 207 and 157 rows, 202 and 157 distinct names, 6 shared names and
353 distinct names. Any other count is reported as it is. This is a candidate `report_internal`
item for the [CFIA open-data errata table](cfia-open-data-errata-0.3.0.md). It is small: it
changes no result, but anyone who uses the PDF's list as the screen's scope gets a slightly wrong
number of analytes.

## Items the file decides (names and counts only; graded by the census)

- A2. **The file is in long format**, with one row per sample and reported analyte and a component
  column. Long format follows from items 3 and 4 above, and it fits R6 (the file is too small for
  one row per sample and pesticide).
- A3. **Metals are complete.** Every sample with any metal row has exactly 18 metal rows, one per
  metal, with non-detects included (item 4). With 100 teas this means 1,800 metal rows. Metals are
  recognised by element name, from a fixed list in the census module.
- A4. **Sample numbers.** Every pesticide row's sample number ends in "A" (item 1). We also
  predict, with less confidence, that no metal row's sample number ends in "A". **How C1 counts
  samples:** C1 (100 distinct samples) is graded on sample numbers with one trailing "A" removed;
  the raw count of distinct sample numbers is reported next to it.
- A5. Every pesticide name in the file is in the PDF's table (matched without regard to case,
  spacing or quote style). Names that are not are listed and counted.
- A6. The file's pesticide rows carry only the two method codes in the PDF, PESTICIDES-FPH053 and
  PESTICIDES-LC, and both occur.
- A7. Because only detected pesticides are included (item 3), no pesticide row has a blank,
  non-detect or "<" result. The census checks this by the result cell's **shape** only (number,
  "<" number, text token or blank), never its value. A pesticide row with a non-number shape fails
  A7 and is counted.

## Order of work (unchanged except for step 2)

1. 0.1.0 was published on 2026-11-08.
2. This addendum is published.
3. The names-only census job `dried-tea-census-v1` runs. A gate waits until both notes are
   public on GitHub. The job then publishes the counts for C1-C5 and A1-A7: labels, component
   names, method codes, units and value shapes. It never prints, sums or compares a result value.
4. The label map (tea types for C2) and a grader are published.
5. A sealed job grades V1-V6 only after step 4 is public.

MV2, Munim, Inc., mv2@munimtech.com
