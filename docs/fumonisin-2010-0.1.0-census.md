# Census: CFIA's open 2010-11 fumonisin file, names and counts only (fumonisin-2010 0.1.0)

CENSUS-MARKER: fumonisin-2010-0.1.0-census

Made with AI agents working in MV2's (Munim, Inc.) name. Text CC BY 4.0; code Apache-2.0.
Not a compliance finding and not dietary or medical advice.

This note grades the census items of the [pre-registration](fumonisin-2010-0.1.0-prereg.md) and
fixes the label map and grading rules for its value items. It was written from the sealed
names-only census (job `fumonisin-census-v1`, run 2026-11-07 03:32 UTC, after the pre-registration
was public). That job read labels, counts and cell shapes; **no result value of the file has been
read**. Its record is published as
[data/fumonisin_2010_census.json](../data/fumonisin_2010_census.json), and
`test_fumonisin_census_notes.py` checks every count below against it.

## Gate (G): holds

MD5 219641dd2317367eb87069eef88a88b6 as on the portal; 87,748 bytes, inside the 86 KiB band read
as rounded up (more than 87,040, at most 88,064); sample, product, analyte, value and unit columns
found by name. The file has 15 columns (English and French side by side): sample number,
function, origin, product, sampling date, test type, component, result, unit and plan code.

## Census items

| Item | Registered | File | Grade |
|---|---|---|---|
| C1 | 276 distinct samples | **277** | **fails** |
| C2 | labels map to the page's 11 groups with its counts | 9 labels; see the map | **fails** |
| C3 | analytes a subset of {B1, B2, total}, no B3 | Fumonisin B1, Fumonisin B2 | holds |
| C4 | every unit on the ppb scale | ng/g on all 554 rows | holds |

Two of four hold. Every sample has exactly two rows (B1 and B2) and every result cell is a
number; the file stores no total, so a sample's total is B1 + B2, as registered. Sample numbers
run 2010FMN0001 onward. Function is Domestic 138 / Import 139; origin is Canada 138, United States
94, unknown 35, Mexico 5, Italy 3 and Colombia 2. All 277 sampling dates fall from 2010-10-03 to
2011-03-11, inside the 2010-11 survey year.

## C2: the label map

| File label | Samples | Page group(s) | Page count |
|---|---|---|---|
| Cereal - Corn | 56 | corn-based breakfast cereals | 56 |
| Popcorn | 30 | popcorn | 30 |
| Corn | 27 | canned corn | 27 |
| Corn Starch | 23 | corn starch | 23 |
| Flour - Corn | 21 | corn flour (the name decides against corn tacos, also 21) | 21 |
| Cornmeal | 41 | cornmeal 34 + corn grits 7 | 41 |
| Chips - Corn, Bakery Product - Tortilla/Wrap/Pita, Corn Products | 42 + 15 + 22 = **79** | chips 45 + tacos 21 + tortillas 10 + cornbread mix 2 | **78** |

Five labels match a page group one to one. Cornmeal and grits share one label, whose 41 equals
the page's 34 + 7. The extra 277th sample is in the last block: no label names tacos, grits or
cornbread mix, and the chips label is three short of the page's chips, so the names alone cannot
split that block.

## How the value items are graded (fixed now, before any value is read)

The labels are coarser than the page's groups, so each value item is graded on the map above.
"Cornmeal label" stands for cornmeal or grits; "chip block" for the three labels of the last row.

- V1. Exactly 157 positives (total above zero) among all 277 samples.
- V2. The smallest positive total is at least 19.5 and below 20.5; among the samples whose total
  rounds to the same whole number, at least one is in the chip block and at least one carries
  the Cornmeal label (the page's corn grit). Whether a chip-block sample at the minimum is
  labelled "Chips - Corn" is reported beside it.
- V3. The largest total is at least 6649.5 and below 6650.5 and carries the Cornmeal label. The
  looser 6645 to 6655 reading is reported apart.
- V4. Exactly 8 totals above 800: 4 with the Cereal - Corn label, 3 with the Cornmeal label (the
  page's two grits and one cornmeal) and 1 in the chip block (the page's tortilla), and no other.
- 2010-V5 (registered in the [fumonisin-series note](fumonisin-series-0.1.0-prereg.md)). The
  positives' average is at least 267.5 and below 268.5.

Reported, not graded: positives and ranges by label, the origin split of positives, how the file
writes non-detects (zeros, if it does), and the extra sample.

## What the census decides

The file holds one sample more than the report page says. No value is needed to see it. The
grader is in [fumonisin-0.1.0-grader.md](fumonisin-0.1.0-grader.md).

MV2, Munim, Inc., mv2@munimtech.com
