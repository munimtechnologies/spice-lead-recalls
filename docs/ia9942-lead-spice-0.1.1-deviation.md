# Deviation note: ia9942-lead-spice 0.1.0 → 0.1.1 (parser fix, and lead in spices lived on another alert)

By MV2 of Munim, Inc. Prepared with AI agents. Text CC BY 4.0; code Apache-2.0.

**Status:** written and committed **before** any lead-spice firm was counted on FDA
Import Alert 99-42's current page or on any copy of Import Alert 28-13. The
predictions in [the pre-registration](ia9942-lead-spice-0.1.0-prereg.md) are unchanged.
This note records two problems found in the first job's output, how 0.1.1 fixes them,
and which grade will be the headline grade.

## 1. The first job misread the page (parsing fix, allowed by the pre-registration)

The sealed job `ia9942-lead-spice-v1` (2026-10-17, 07:46 UTC) froze the live 99-42 page and
Wayback copies from December 2021, December 2023 and December 2025. Its own parse check
flagged the failure: the live page has 606 `Problems` lines, but 0 of the 492 parsed
product lines carried a Problems value, so it found no lead-spice firm (E = L = 0).

The cause is layout. The page prints `Problems:` alone on a line and the value under it
(`LEAD;`, or `CADMIUM; LEAD;`). Older copies print one value per line. Version 0.1.0
expected `Problems: LEAD;` on one line, so it left Problems empty. It also read the
stray `LEAD;` line as the next firm's country heading.

Version 0.1.1 changes parsing only:

- a field label alone on its line takes the problem-value lines printed under it;
- after "DWPE date", the separator may be ":", ";" or "-" (all three occur in the live
  Notes, e.g. `DWPE Date-9/25/2019`, `Original DWPE date; 3/27/2007`);
- a product code may read `54 - - - --` (older copies);
- Wayback copies that come back gzip-encoded are decoded (the December 2023 copy was
  saved compressed and could not be read);
- after a rate-limit error (HTTP 429), the job waits longer before retrying (the 2022, 2024 and 2026 copies failed
  this way), and it pauses 20 s between Wayback fetches.

The offline test now includes the live page's text lines and every DWPE-date separator found in its Notes.

## 2. In 2021, lead in spices was not on 99-42 at all (a deviation, declared now)

The December 2021 copy of 99-42 (published 11/24/2021) says, verbatim:

> Spice and spice products containing lead fall under the scope of Import Alert 28-13.

That copy has no industry-28 product line at all. So the registered early count, E on the
latest 2021 copy of 99-42, is **zero by construction**. With E = 0, P1 (L > E), P2
(L ≥ 2E) and P5 (no Georgia firm in E) would all be "met" whatever FDA did. That grade
would say nothing about the question.

The current 99-42 page no longer carries that sentence, and many of its spice lines show
a Date Published of 10/13/2022 with much older DWPE dates in Notes. This suggests that
listings were moved into 99-42 around October 2022. The page does not say so, and FDA's
old 28-13 page (`importalert_1143.html`) now returns 404.

**Declared now, before counting:**

- **Headline grade (deviation, E_D):** E_D is the set of lead-spice firms with listing year 2016–2020,
  counted on the latest 2021 Wayback copy of Import Alert 28-13 (else the latest 2020
  copy), merged with the same-year copy of 99-42 (one record per country and firm). On
  28-13, every industry-28 product line counts as a lead-spice line, because the whole
  alert is about lead in spices. L, the predictions P1–P5 and every other rule are as
  registered. If no 2020 or 2021 copy of 28-13 can be read, the deviation is reported
  as not gradable.
- **The registered grade** (E from 99-42 alone) is still computed and reported. It is
  flagged as invalid by scope and is not counted as support for any prediction.
- **Robustness check (declared now):** L without any firm whose normalised country and
  name appears on any Wayback copy of 28-13. This removes listings that were moved
  across and might carry a 2022 republication date instead of their original DWPE date.
- **Reported without prediction:** lead-spice firms on each year's last copy of each
  alert (2015–2026) and their union; the current page's lead-spice firms by listing year;
  E_D and L by country; and NYC's top five abroad purchase countries among them.

## What was seen before this note was written

- The v1 job's check files and grades (all zeros, as above). The 2021 copy's scope text,
  and the fact that it has no industry-28 lines.
- On the live page: its header text; the first 30 parsed rows (firms from Afghanistan to
  Bangladesh, mostly non-spice, including the Bangladeshi turmeric firms already named in
  the pre-registration); the sequence of Problems values in page order, not tied to firms
  or products (lead, cadmium, arsenic, mercury, thallium); and the first ~60 Notes values
  in page order. These show the DWPE-date formats and some dates, which were not tied to products or countries. Also
  the count of industry-28 code lines (92), not split by year, country, spice or Problems,
  and 4 notes reading "Listing moved from deactivated IA 15-01" (duck eggs).
- A web search reporting that a December 2019 Food Safety News roundup lists IA 28-13,
  "Detention Without Physical Examination of Spices and Spice Products Due to Lead
  Contamination", at `importalert_1143.html`.

No lead-spice firm was counted by listing year, country or spice on any page, and no
copy of 28-13 has been opened.

## Why this matters beyond the grade

Anyone who trends FDA's lead-in-spice border listings from Import Alert 99-42 alone will see an
artificial jump around 2022, because the listings changed alerts. The 2021 copy shows
the earlier scope, and the live page drops the cross-reference without saying so. Any
before/after comparison has to join the two alerts.

## Files

- `ia9942_lead_spice.py` 0.1.1 and `test_ia9942_lead_spice.py` (offline).
- `data/ia9942_wayback_20211205053251.txt`: text of the December 2021 copy of 99-42
  (US government work), frozen by the v1 job, showing the 28-13 scope sentence.
