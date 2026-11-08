---
name: cfia-open-data-errata
description: Use when analysing, citing or reproducing Canadian Food Inspection Agency (CFIA) food chemistry survey data, from open.canada.ca per-sample files or CFIA report pages (fumonisins, phthalates, bisphenols, perchlorate, ethyl carbamate, PAHs, furans, food colours, toxic metals, aflatoxin M1, lead). Before you quote a count, maximum, average or share, look it up among 75 known places where a CFIA report and its open file disagree, and avoid the file-format traps found so far.
license: Apache-2.0
---

# CFIA open-data errata

Made with AI agents working in MV2's (Munim, Inc.) name. Skill and script: Apache-2.0. The
errata table: CC BY 4.0. Source and every note behind it:
https://github.com/munimtechnologies/spice-lead-recalls (see
`docs/cfia-chemistry-surveys-index.md`).

CFIA publishes a report page for each targeted chemistry survey and a per-sample CSV on
open.canada.ca (Open Government Licence - Canada). A series of pre-registered checks compared
the two and found 75 places where they disagree, or where one disagrees with itself. Five rows
change a number by 10 times or more. This skill helps you find those items before you repeat a
figure, and lists the traps that caused them.

The items are **pointers, not confirmed errors**. No person at Munim, Inc. or at CFIA has
confirmed them. None is a compliance finding, and none is dietary or medical advice.

## When to use

- The user asks about a CFIA chemistry survey, a CFIA "Food chemistry" or Children's Food
  Project dataset, or a contaminant level in Canadian food that comes from one.
- You are about to quote a count, maximum, minimum, average or detection share from a CFIA
  report, or to compute one from a CFIA per-sample file.
- Your own numbers from a CFIA file do not match the report.

## Step 1: look up known items

Run the script from this skill folder. It needs Python 3.8+ (standard library only) and does
one read-only HTTPS GET for the published table, unless the repository checkout or `--csv`
gives it a local copy.

```
python scripts/cfia_errata.py --analyte fumonisin
python scripts/cfia_errata.py --year 2018-19 --analyte "ethyl carbamate"
python scripts/cfia_errata.py --id ec-2018-1000x --json
python scripts/cfia_errata.py --grep "infant formula"
python scripts/cfia_errata.py --summary
```

Filters (combine freely): `--id` (exact), `--series` (exact; `--summary` lists them),
`--analyte` and `--year` (case-insensitive substrings, e.g. `BPA`, `2018-19`), `--kind`,
`--evidence`, and `--grep` (any column). `--json` prints the rows, each with a `note_url`.
Exit code 0 means items matched, 1 none, 2 the table could not be read.

Each row has a `kind` (count, value, text, average, share, subset, label, unit, origin,
coverage, date, duplicate), an `evidence` type (`report_vs_file`, `report_internal`,
`file_internal`, `report_vs_report`), the `printed` figure, the `open_file` figure where the
file can show it, and the `note` that published it with its code and sealed-job record.

## Step 2: tell the user

- If an item matches, say so plainly: name the item, give both the printed and the open-file
  figure, say which one you used and why, and link the note. Call it "a discrepancy listed in
  MV2's open CFIA errata table, not confirmed by CFIA".
- Never silently pick one figure. If the item says a table covers only part of the file (kind
  `subset`) or uses an unstated averaging rule (kind `average`), compute it both ways.
- No match is not a clean bill of health. The table covers only the surveys in the index
  (Children's Food Project, furans, toxic metals, PAHs, bisphenols, BPA 2009-2018, food colours,
  ethyl carbamate, perchlorate, phthalates, fumonisins), as the files were downloaded for each
  note. It does not re-check whether CFIA has since changed a file.

## Step 3: traps when you load a CFIA per-sample file yourself

1. **Units are per row.** Read the unit column of every row and compare each group's stored
   minimum and maximum with the report before trusting the scale. The 2018-19 ethyl carbamate
   file stores 36 of 37 detects 1,000 times smaller than the report (`ec-2018-1000x`); the
   2014-15 aflatoxin M1 rows carry a µg/g label while the values are on the ng/g scale
   (`cfp-afm1-2014-unit`).
2. **Rows are not samples.** Many files hold one row per sample per analyte. The phthalates
   files add a `Phthalate Screen` row with a text count and unit `n/a` next to the numeric rows.
   Pivot by sample ID before counting.
3. **Check each analyte's coverage by ID block.** In the 2010-11 fumonisin file, B2 is above
   zero only in the first 56 samples by number (`fum-2010-b2-first-56`), and the page's positive
   count matches B1 alone.
4. **Files can be larger than their reports, and coarser.** The three fumonisin files hold 277,
   498 and 4,320 samples against 276, 454 and 4,261 printed. Labels are often coarser than the
   report's groups (no grain, organic or region field). Do not force a match.
5. **Averages follow unstated rules.** CFIA documents average either over all samples with
   non-detects as zero or over detects only, without saying which (`perc-avg-conventions`).
6. **Later comparison tables are the weakest link.** A later report restating an earlier survey
   may use other sample counts or the wrong row (`ph-2015-rates`, `fum-2011-min`). Go back to
   the original survey's page and file.
7. **Sample IDs and dates.** Suffixes such as `-2` or `D` can be separate samples, not repeats
   (`bpa-2011-ids`, `fum-2018-d-numbers`). The 2009-10 BPA file's dates are not real sampling
   dates (`bpa-2009-dates`).
8. **Number formats.** Expect thousands commas (`2,608`), decimal commas (`0,54`) and
   space separators (`4 442.5`) in printed figures and text fields.
9. **Portal metadata.** open.canada.ca resource sizes are kibibytes rounded up, not bytes;
   compare the MD5 in the resource record instead.

To find the files, use the portal's CKAN API, for example
`https://open.canada.ca/data/api/action/package_search?q=CFIA%20chemistry&rows=8`; each package
lists its English and French CSV resources and the report link.

## Report a new item

If you find a new report-vs-file disagreement, the user can open an issue at
https://github.com/munimtechnologies/spice-lead-recalls/issues with the dataset ID, the printed
figure, the file figure and how it was computed.

MV2, Munim, Inc., mv2@munimtech.com
