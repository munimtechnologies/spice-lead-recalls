# cfia-chromate-2018 0.1.0: does the Pb:Cr chromate screen stay quiet on spices a regulator called clean?

A pre-registered test of the lead-chromate screen against a labelled clean set. The
Canadian Food Inspection Agency's open 2018-19 survey measured lead, total chromium and
a chromate spot test on **131 retail spices** and found **none adulterated**. The five
predictions and the grading code (`cfia_chromate_2018.py`) were written and committed
before any value in the file was read; see
[the pre-registration](cfia-chromate-2018-0.1.0-prereg.md). This note reports the grade,
computed by a sealed compute run with no network at analysis time.

By MV2 of Munim, Inc. Prepared with AI agents. Text CC BY 4.0; code Apache-2.0.
Contains information licensed under the Open Government Licence - Canada.

## Source and parse

- CFIA, *Lead Chromates in Spices, 2018-2019* — https://open.canada.ca/data/en/dataset/06033736-6095-4b85-8760-95dd8c209576 (Open Government Licence - Canada).
- File sha256 `6ad69f7dc0dceaac1555b3aa581df6eac5a05c1498322d8fbdb1a07444b88d16`, 393 data rows → **131 samples**, each with Lead, Chromium (total) and a Chromates spot test, all in µg/g. 0 bad numbers, 0 duplicates. The frozen per-sample table is [`data/cfia_chromate_2018_samples.csv`](../data/cfia_chromate_2018_samples.csv).

## Result: 4 of 5 pre-registered predictions met

| | prediction | value | status |
|---|---|---|---|
| P1 | ≤5% of samples of a spice with its own natural-Cr ceiling exceed that ceiling | 1 of 81 (1.2%) | **met** |
| P2 | at most 2 samples carry more than 8.59 ppm chromium | 1 | **met** |
| P3 | with no 18 ppm lead floor, no sample's molar Pb:Cr lies in 0.7-2.0 | 21 | **not met** |
| P4 | the published screen (lead ≥ 18 ppm *and* molar Pb:Cr 0.7-2.0) flags none | 0 | **met** |
| P5 | fewer than 8.3% of samples (NYC's store-survey rate) reach 2 ppm lead | 6 of 131 (4.6%) | **met** |

The screen as published (**P4**) agrees with CFIA exactly: zero of 131 clean spices are
flagged, because none carries the ≥ 18 ppm lead that lead chromate adulteration leaves
behind. The natural-chromium ceilings (**P1, P2**) are also quiet: only one spice exceeds
any ceiling.

## Why P3 failed — and why it is the point

Drop the 18 ppm lead floor and keep only the chromate-like molar band, and **21 of 131**
clean samples fall inside it. Every one has lead below 5 ppm (median 1.0 ppm) and a
**negative** chromate spot test. The molar Pb:Cr band alone is not specific to lead
chromate; a spice can land in the ratio window simply by having little of both metals.
The 18 ppm lead floor — the quantity of lead that visible yellow lead-chromate lacing
deposits — is what makes the screen specific. P3 failing while P4 holds is direct evidence
for that design choice, on a set a regulator independently called clean.

## The one over-ceiling sample is not lead chromate

The single sample above a natural-Cr ceiling is an Indian **cumin** (C2018CLAS00046):
chromium **16.91 ppm** (ceiling 8.59) with a **positive** chromate spot test — yet lead
only **0.52 ppm**. Chromium and chromate are present, but without the paired lead, this is
not the lead-chromate signature; the Pb:Cr screen correctly leaves it unflagged (molar
ratio 0.008). High chromium with a positive spot test but negligible lead is exactly the
false positive a lead floor is meant to reject.

Eight of the 131 samples returned a positive chromate spot test; CFIA still judged none
adulterated, consistent with a spot test being a screen that confirmation follow-up clears.

## A low-level lead tail in "clean" retail spice (P5)

Six samples reached 2 ppm lead (4.6%, below NYC's 8.3% store rate): a thyme at 6.57 ppm,
a **domestic Canadian** spice blend at 4.47 ppm, a Chinese star anise at 3.13, an Indian
turmeric at 2.97, an Indian cumin at 2.51 and a spice blend at 1.75. None is gross
contamination, but the tail matches our NYC and FDA findings: low-level lead persists in
retail spice sold where enforcement is active, while the gross (≥ 50 ppm) lead that drives
poisoning cases turns up in spice bought abroad, which surveillance like this does not see.

## Limits

This is a stock survey of retail spice a regulator selected and already cleared, so the
"clean" label is not independent of CFIA's own screening. The chromate spot test and total
chromium do not speciate Cr(VI). The ceilings are our own literature-derived values
(`natural_cr_ceilings 0.1.2`); P1 depends on them. Every figure here is recomputed from
the committed CSV by [`test_cfia_chromate_2018_result.py`](../test_cfia_chromate_2018_result.py).
