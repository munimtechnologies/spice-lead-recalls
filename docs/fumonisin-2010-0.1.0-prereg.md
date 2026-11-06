# Pre-registration: CFIA's newly opened 2010-11 fumonisin file against its report (fumonisin-2010 0.1.0)

PREREG-MARKER: fumonisin-2010-0.1.0-prereg

Made with AI agents working in MV2's (Munim, Inc.) name. Text CC BY 4.0; code Apache-2.0.
Not a compliance finding and not dietary or medical advice. Canada has no maximum level for
fumonisins in corn products, as the report says, so no sample is judged against one here.

## Why this file

On 2026-11-03 the Canadian Food Inspection Agency (CFIA) published the per-sample file of its
2010-11 targeted survey of fumonisins in corn products on open.canada.ca (Open Government Licence -
Canada). The survey's report page dates from 2018; the file is new. A search on 2026-11-06 found
no analysis of the file. As in the other notes of the
[CFIA chemistry surveys index](cfia-chemistry-surveys-index.md), every prediction below is fixed
from the printed report page alone, **before any part of the file has been opened** (not its
header, its labels or its values).

- Report page: inspection.canada.ca, "2010-2011 Fumonisins in Corn Products" (summary page; the
  full report is available only on request, so only the page is used).
- Dataset 5ac4ed9e-9dc4-4c3c-9a2b-e99530fbda13, "Food Safety Action Plan Targeted Survey -
  Fumonsin in Corn Products - 2010/11" (the title's spelling). Resource
  48123e67-3a23-44f3-8cf1-ef8054ca1766, "CHEM TS 2010-2011 Fumonisins in Selected Foods", CSV,
  English and French. Portal metadata read on 2026-11-06: size 86, MD5
  219641dd2317367eb87069eef88a88b6, created 2026-11-03T18:42:17, record modified
  2026-11-05T13:11:43.

## What the report page prints

- 276 samples: corn-based breakfast cereals 56, corn/tortilla chips 45, cornmeal 34, popcorn 30,
  canned corn 27, corn starch 23, corn tacos 21, corn flour 21, corn tortillas 10, corn grits 7,
  cornbread mix 2.
- All samples analysed for fumonisins B1 and B2 with a multi-residue method.
- 157 of 276 (57%) had detectable fumonisins.
- Total fumonisins ranged from 20 ppb (in corn chips and corn grits) to 6650 ppb (in cornmeal).
- Eight samples had more than 800 ppb: four corn cereals, two corn grits, one corn tortilla and
  one cornmeal.
- No averages, detection limits, sampling dates or origin split are printed.

## Report arithmetic (no file needed; checked now)

- R1. The eleven product counts add to 276. **Holds.**
- R2. 157 / 276 = 56.88%, which rounds to 57%. **Holds.**
- R3. If V2 and V4 both hold, at least three of the seven grits have fumonisins (two above 800
  ppb and one at the 20 ppb minimum). Recorded so the result can say whether it is so.

## Gate (G), checked before anything else

The job downloads the resource and fails the gate unless:
1. the file's MD5 is 219641dd2317367eb87069eef88a88b6, and
2. its size is in the portal's 86 KiB band, read as bytes divided by 1,024 and **rounded up**
   (more than 87,040 and at most 88,064 bytes). This convention fits all four files checked so
   far (see the [phthalates census note](phthalates-series-0.1.0-census.md)), and
3. it parses as a CSV with a sample column, a product column, an analyte column, a value column
   and a unit column (found by name, as in the earlier notes).

If CFIA replaces the file, the gate fails and is reported as failed; it is not edited.

## Census items (names and counts only; read before any value)

- C1. The file has 276 distinct samples.
- C2. Its product labels can be mapped to the page's eleven groups with exactly the printed
  counts (56 / 45 / 34 / 30 / 27 / 23 / 21 / 21 / 10 / 7 / 2). The map is fixed from label names
  and counts and published before any value is read. Corn tacos and corn flour both have 21, so
  their names decide; if labels are coarser or finer than the page's groups, C2 fails and the
  map the names allow is published instead.
- C3. The fumonisin analyte labels are a subset of {fumonisin B1, fumonisin B2, total
  fumonisins}; there is no fumonisin B3 row. (A non-detect may have no row, so the file is not
  predicted to hold every analyte for every sample.)
- C4. Every value row carries a unit on the ppb scale (ppb, ng/g or µg/kg). The census reports a
  table of units; any other unit (for example µg/g or ppm) fails C4 and is shown, not converted.

## Value items (graded only after the census note, label map and grader are public)

A sample's **total** is its stored total-fumonisins value if the file has one; otherwise it is
fumonisin B1 plus fumonisin B2, with a missing or non-detect row counted as zero. If the file has
both, items are graded on the stored total and the B1 + B2 sum is reported alongside. A sample is
**positive** when its total is above zero.

- V1. Exactly 157 samples are positive.
- V2. The smallest positive total rounds to 20 ppb (at least 19.5 and below 20.5), and the samples
  at that minimum (after rounding to a whole ppb) include at least one corn or tortilla chip and
  at least one corn grit.
- V3. The largest total rounds to 6650 ppb (at least 6649.5 and below 6650.5) and belongs to a
  cornmeal sample. A looser reading (6645 to below 6655, for a figure rounded to tens) is
  reported apart and does not change the grade.
- V4. Exactly 8 samples have a total above 800 ppb: 4 corn cereals, 2 corn grits, 1 corn tortilla
  and 1 cornmeal.

## Reported afterwards, not graded

Positives and ranges by product group, the origin and date fields if the file has them, how the
file writes non-detects, and a side-by-side with the 2011-12 report's corn figures (274 corn
samples, 161 or 59% positive, 20.8 to 4442.5 ppb), which come from a different file.

## Order of work

1. This note is published.
2. A names-only census job (gate, C1-C4) publishes the label map and a grader.
3. A sealed job grades V1-V4 only after step 2 is public.
4. An independent test re-runs the published result from GitHub.

MV2, Munim, Inc., mv2@munimtech.com
