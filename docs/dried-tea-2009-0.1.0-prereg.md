# Pre-registration: CFIA's open 2009-10 dried-tea pesticides and metals file against its report (dried-tea-2009 0.1.0)

PREREG-MARKER: dried-tea-2009-0.1.0-prereg

Made with AI agents working in MV2's (Munim, Inc.) name. Text CC BY 4.0; code Apache-2.0.
Not a compliance finding and not dietary or medical advice. CFIA's own health assessment says
the residues found are not expected to pose a health concern, given how much tea is consumed;
nothing here re-judges any sample or brand.

## Why this file

The Canadian Food Inspection Agency (CFIA) tested 100 retail dried teas in 2009-10 for over 340
pesticide residues and 18 metals. Its per-sample file was first published on open.canada.ca on
2026-07-22 (Open Government Licence - Canada). Web searches on 2026-11-08 found the report page,
CFIA's 2012 news release and later CFIA pages that cite the survey, but no analysis of the open
file; the searches cannot see work that is not indexed. As in the other notes of the
[CFIA chemistry surveys index](cfia-chemistry-surveys-index.md), every prediction below is fixed
from CFIA's printed pages alone, **before any part of the file has been opened** (not its header,
its labels or its values; the portal's DataStore preview has not been opened either).

- Report page: inspection.canada.ca, "2009-2010 Pesticide Residues and Metals in Dried Tea"
  (summary page, date modified 2018-09-04; the full report is available on request).
- Later page: inspection.canada.ca, "2010-2011 Mercury in Dried Tea, Soft Drinks and Corn Syrup"
  (date modified 2018-09-04), which compares its tea results with earlier years.
- Dataset 2782dbc5-ebbb-4ef1-a85f-294a5fe60f47, "Food Safety Action Plan Targeted Survey -
  Pesticide Residues and Metals in Dried Teas - 2009-2010". Resource
  6fbadab4-f46f-4ab3-a1a6-e3d857253beb, CSV, English and French. Portal metadata read on
  2026-11-08: size 276, MD5 f21f016693b4608ff7059d28be35bb26 (the record sets `ignore_hash`),
  created 2026-07-22T18:42:20, validation status success.
- The package also holds a 9-page English "Information" PDF (resource
  628e68b6-9d35-4a0c-8514-cd5016623ff7) and a French one. Our tools could not extract its text
  on 2026-11-08, so nothing below comes from it. A separate sealed job extracts the PDFs' text
  without touching the CSV; if the PDF prints further figures, they will be pre-registered in a
  dated addendum (0.1.1) **before** the census opens the file, and kept apart from the items here.

## What the pages print

From the 2009-10 report page:
- 100 dried teas (loose leaf and bagged) from retail stores: 24 black, 41 green, 12
  herbal/blends, 13 oolong and 10 white.
- Over 340 pesticide residues and 18 metals analysed.
- 31% had no detectable pesticide residue; the other 69 samples had at least one.
- 41 samples had at least one residue "in violation of the 0.1 ppm General MRL"; the overall
  compliance rate was 59%. No specific MRL is mentioned.
- Violations by type: oolong 92% (12 of 13), herbal/blends 58% (7 of 12), green 44% (18 of 41),
  white 20% (2 of 10), black 8% (2 of 24).
- "Of the 18 metals analysed, all metals except beryllium, were detected in all dried tea
  samples." The metals are not named and no level is printed.
- No pesticide names, values, origins or sampling dates are printed.

From the 2010-11 mercury page:
- 87% of its dried tea samples had detectable mercury; its highest mercury value in any sample
  was 0.023 ppm.
- Compared with "previous years", the maximum and average mercury values in tea were similar,
  but "the percentage of samples with detectable levels of mercury were much higher in the
  current year's survey". One of its objectives was to compare with the 2009-10 survey.

## Report arithmetic (no file needed; checked now)

- R1. The type counts add to 100 (24 + 41 + 12 + 13 + 10). **Holds.**
- R2. The type violations add to 41 (12 + 7 + 18 + 2 + 2), and 100 - 41 = 59, the printed
  compliance rate. **Holds.**
- R3. Each printed type share is its count rounded to a whole percent (92.3, 58.3, 43.9, 20.0,
  8.3). **Holds.**
- R4. 69 - 41 = 28 samples had a detectable residue and no violation. Recorded for the grade.
- R5. **The two pages conflict if mercury was one of the 18 metals.** The 2009-10 page says every
  metal except beryllium was detected in all 100 teas, which would make 2009-10 mercury
  detection 100%; the 2010-11 page says its own 87% was "much higher" than in earlier years. Both
  cannot hold for mercury. The file decides (items C4, V4 and V6). This is a candidate for the
  CFIA open-data errata table as a `report_vs_report` item once the file is graded.
- R6. **Layout from size alone.** The portal size 276 means at most 276 x 1,024 = 282,624 bytes
  (the series' rounded-up KiB convention). One row per sample for each of 340 pesticides would
  be at least 34,000 rows of about 8.3 bytes each at most, too few for a sample ID and a value. So the
  file is either wide (analytes as columns) or lists only some analytes per sample (for example
  detected residues and the metals). The census reports which.

## Gate (G), checked before anything else

The job downloads the resource and fails the gate unless:
1. its size is in the portal's 276 KiB band, read as bytes divided by 1,024 and **rounded up**
   (more than 281,600 and at most 282,624 bytes), and
2. it parses as a CSV with a sample column found by name, as in the earlier notes.

Because the record sets `ignore_hash`, the MD5 match is **reported, not gated**. If CFIA has
replaced the file, the gate fails and is reported as failed; it is not edited.

## Census items (names and counts only; read before any value)

- C1. The file has 100 distinct samples. (Earlier files were sometimes larger than their
  reports; a different count fails C1 and is reported, and the value items are then graded on
  the file as it is.)
- C2. Its tea-type labels map to the page's five types with exactly 24 / 41 / 12 / 13 / 10. The
  map is fixed from label names and counts and published before any value is read. If the file
  has no type field, C2 is reported as not decidable and V3 is not graded.
- C3. The file names exactly 18 distinct metals.
- C4. Mercury is one of them. **We predict it is.**
- C5. Pesticide values and metal values carry units; the census publishes a table of units per
  analyte group. Any conversion below uses only that table: 0.1 ppm = 0.1 mg/kg = 0.1 µg/g =
  100 ppb = 100 ng/g = 100 µg/kg.

## Value items (graded only after the census note, label map and grader are public)

A pesticide residue is **detected** when its stored value is above zero (or the file marks it
detected); a non-detect may have no row. A **violation** is a pesticide value above 0.1 ppm; the
count at or above 0.1 ppm is reported alongside and does not change the grade.

- V1. Exactly 69 samples have at least one detected pesticide residue.
- V2. Exactly 41 samples have at least one pesticide value above 0.1 ppm.
- V3. By type (if C2 holds), the samples with a value above 0.1 ppm are 12 oolong, 7
  herbal/blends, 18 green, 2 white and 2 black.
- V4. The page's sentence: every metal except beryllium is above zero in all of the file's
  samples.
- V5. Beryllium is above zero in fewer than all of the file's samples.
- V6. **Our prediction for R5:** if C4 holds, mercury is above zero in fewer than 87% of the
  file's samples, as the 2010-11 page implies, so V4 fails for mercury. If C4 fails, V6 is not
  graded and R5 is reported as not decided by this file.

## Reported afterwards, not graded

The pesticides found and how many teas each was found in, the largest value per pesticide, how
many samples exceed 0.1 ppm for two or more residues, metal ranges by type next to the 2010-11
mercury maximum of 0.023 ppm, how the file writes non-detects, and any origin or date field.

## Order of work

1. This note is published.
2. A sealed job extracts the text of the package's PDFs (not the CSV); any further figures are
   pre-registered in a dated 0.1.1 addendum before step 3.
3. A names-only census job (gate, C1-C5) publishes the label map and a grader.
4. A sealed job grades V1-V6 only after step 3 is public.
5. An independent test re-runs the published result from GitHub.

MV2, Munim, Inc., mv2@munimtech.com
