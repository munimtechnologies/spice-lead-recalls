# cfia-spice-auth 0.1.0: lead chromate, dyes and fillers in Canada's spice surveillance

A pre-registered look at what Canada's spice-authenticity surveillance does and does not
catch, and whether the lead-chromate screen's two targets — lead chromate and illegal
dyes — appear in it. The five predictions and the grading code (`cfia_spice_auth.py`)
were written and committed before any assessment or note in the files was read; see
[the pre-registration](cfia-spice-auth-0.1.0-prereg.md). This note reports the grade,
computed by a **sealed compute run** that downloaded and parsed the three open files with
no network at analysis time. It supersedes an earlier provisional transcription (which had
missed one 2022-23 turmeric row) and corrects it.

By MV2 of Munim, Inc. Prepared with AI agents. Text CC BY 4.0; code Apache-2.0.
Contains information licensed under the Open Government Licence - Canada.

## Source and parse

CFIA, *Spices — Authenticity* summary data (three per-sample files), https://open.canada.ca/data/en/dataset/2d34ba67-f4a3-4c54-95f5-6073b59ad880 (Open Government Licence - Canada).

| file | rows | S | U-I | INV | sha256 |
|---|---|---|---|---|---|
| 2020-2021 | 127 | 118 | 9 | 0 | 554c76916ae2 |
| 2021-2022 | 402 | 365 | 23 | 14 | 5bbd9eb42777 |
| 2022-2023 | 294 | 255 | 25 | 14 | aad9c00f44b4 |
| **total** | **823** | **738** | **57** | **28** | |

The frozen per-sample table, with each row's flags, is
[`data/cfia_spice_auth_rows.csv`](../data/cfia_spice_auth_rows.csv).

## Result: 2 of 3 gradable predictions met

| | prediction | value | status |
|---|---|---|---|
| P1 | at least one sample's notes name lead chromate (lead/chromate/Pb) | 0 | **not met** |
| P2 | lead-chromate samples are at most 3% of all samples | 0 of 823 | **met** |
| P3 | among unsatisfactory samples, filler notes outnumber lead notes | filler 53 vs lead 0 of 57 | **met** |
| P4 | ≥ half of lead-chromate samples are turmeric or ginger | 0 of 0 | not gradable |
| P5 | ≥ half of single-origin lead-chromate samples declare South Asia | 0 of 0 | not gradable |

**Not one of 823 samples' notes names lead, chromate or lead chromate.** P1 failed and
P4/P5 cannot be graded, because this surveillance does not report the lead-chromate
signature the screen targets — it is an authenticity programme (species substitution,
undeclared allergens, undeclared colours), not a heavy-metals programme.

## What the failures actually are: allergens, not metals

Among the 57 unsatisfactory samples, 53 carry an allergen-protein "filler" note and **none
names lead** (P3). Across all assessments, 80 notes flag undeclared allergen proteins:
**peanut in cumin** and **gluten in pepper and coriander**. Cumin is by far the most-failed
spice (41 of 155 unsatisfactory). The largest readings are a Vietnamese white pepper at
**19,000 ppm gluten** and a Vietnamese black pepper at **1,600 ppm** (both 2022-23) — these
are food-safety failures for undeclared allergens, a different hazard from lead.

## The screen's second target: illegal colours

Five samples drew an undeclared-colour failure: **four turmerics and one cinnamon**.

- The cinnamon was declared from **Iran** — undeclared **Sunset Yellow FCF at 486.8 ppm**
  (2020-21). Sunset Yellow is a permitted colour in many foods but not a declared
  ingredient here.
- The four turmeric colour failures were declared from the **United States** (two), **Iran**
  and **Madagascar**. **None was declared from South Asia**, even though India alone
  accounts for most declared turmeric in the files.

This is the honest limit of the open notes: CFIA tests a turmeric "for colours" by both
HPLC (synthetic dyes) and ICP-MS (lead and chromate), and the public note says only
"unsatisfactory for colours." So an open-data reader **cannot tell a banned dye from lead
chromate** from these files alone — exactly the gap a point-of-use screen that separates
the two signatures would close.

## No Georgia, as in every frame

No sample in 823 declares **Georgia** — the country that supplies the gross (≥ 50 ppm) lead
in New York City's poisoning cases. A trade-and-retail authenticity frame does not see the
abroad-bought lead, the same blind spot found in FDA's border list and NYC's store survey.

## Limits

These are summary files of samples CFIA selected; the "satisfactory" label is CFIA's own.
The notes are free text, so "filler" and "colour" tags are keyword-derived and reported as
such. P4/P5 are ungradable here by design (no lead-chromate rows). Every figure is
recomputed from the committed CSV by
[`test_cfia_spice_auth_result.py`](../test_cfia_spice_auth_result.py).
