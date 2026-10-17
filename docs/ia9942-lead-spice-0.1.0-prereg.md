# Pre-registration: did FDA's border listings for lead in spices fall after 2020? (ia9942-lead-spice 0.1.0)

By MV2 of Munim, Inc. Prepared with AI agents. Text CC BY 4.0; code Apache-2.0.

**Status:** written and committed **before** any entry on FDA Import Alert 99-42 was
counted by country, spice or year. The code that will grade it, `ia9942_lead_spice.py`,
and its offline test are committed with this file. A sealed compute job will freeze the
FDA page and Wayback Machine copies of it. The result will be graded from those frozen
copies in a later release. Any change to the code after this commit will be listed as a
deviation. Changes are allowed only to fix parsing of the page layout. The definitions
and predictions below stay fixed.

## Question

In NYC's case-investigation spices, gross lead contamination (≥ 50 ppm) fell sharply
after 2020 in every purchase group ([georgia-trend-0.1.0-result.md](georgia-trend-0.1.0-result.md)).
Does a second, independent public record show the same thing? FDA Import Alert 99-42
lists foreign firms whose foods are detained without examination for toxic elements.
Its "Red List" is the US border's own record of which spice exporters shipped lead.

We predict it does **not** show a fall. Border listings follow FDA's sampling effort
and policy, including the Closer to Zero plan (2021) and the response to the 2023
cinnamon applesauce poisonings. NYC's gross cases came mostly from spices carried home
from abroad, which never pass through a commercial import entry. If the two records
diverge, that supports the case for screening at the household and shop level. Border
listings alone would not see what NYC's cases saw.

## What was seen before registration

- The alert's structure: title, charge (POISONOUS, section 402(a)(1)), a Red List grouped
  by country, product lines with an FDA product code, Date Published, Desc, Notes and
  Problems (values seen: LEAD, CADMIUM, ARSENIC, MERCURY, THALLIUM). The list also covers
  many non-spice foods.
- One entry, verbatim: a Bangladeshi firm with turmeric lines (industry 28 and 50), Date
  Published 10/13/2022, Notes "DWPE date: 12/02/2014", Problems "LEAD;". That listing
  year (2014) is outside both periods below.
- Web-search snippets: a Canadian cassia-cinnamon listing with a DWPE date of 08/23/2019.
  A Georgian firm listed 01/08/2026 for ground cassia (outside both periods). Cinnamon or
  cassia listings from firms in China, Georgia and India. Entries published 01/08/2026
  and 04/07/2026. Many lines show Date Published 10/13/2022 with older DWPE dates in
  Notes, so Date Published is often a republication date, not a listing date.
- The Wayback availability API returned no capture near 2021-02-01 when queried through
  a fetch tool. The job queries the full capture index itself.
- NYC context (already published): case-investigation results ≥ 50 ppm bought abroad,
  2016–2025, by purchase country: Georgia 49, Bangladesh 21, Pakistan 9, India 7,
  Russian Federation 6, Algeria 2, and one each from Nepal, Ecuador, Uzbekistan and Morocco.

No count of Red List firms or lines by country, spice or year was made.

## Definitions (fixed now)

- **Lead-spice line:** a product line whose FDA product code is in industry 28 (spices,
  flavors and salts) and whose Problems field contains the word LEAD. If a snapshot has
  no Problems fields at all (an older layout), the word LEAD in Desc, Notes or the
  product text is used instead.
- **Listing date:** the date after "DWPE date" in Notes if present, else the line's Date
  Published.
- **Lead-spice firm:** a (country heading, firm name) pair with at least one lead-spice
  line. Its listing date is the earliest over those lines. Its spice tags come from the
  product text and Desc of those lines: cinnamon (cinnamon, cassia), turmeric (turmeric,
  curcuma, haldi), chili (chilli, chile, paprika, cayenne, red pepper), cumin, coriander,
  ginger, curry_masala (curry, masala), else other. A firm can carry several tags.
- **E:** lead-spice firms with listing year 2016–2020. They are counted on the latest
  Wayback capture from 2021, or else the latest from 2020. This counts firms close to
  the end of the period, before later removals. If neither capture exists or parses,
  E is counted on the current page, and the grade is flagged as survivorship-biased.
- **L:** lead-spice firms with listing year 2021–2025, counted on the current page
  (fetched by the job, October 2026).
- If E + L < 10, P1 and P2 are reported as **not gradable**.

## Predictions

- **P1:** L > E. Border listings for lead in spices did not fall after 2020.
- **P2:** L ≥ 2E.
- **P3:** Among L firms, cinnamon is the most common spice tag, with strictly more firms
  than any other tag.
- **P4:** Among E firms, turmeric is the most common spice tag, with strictly more firms
  than any other tag.
- **P5:** No E firm is under the Georgia heading. NYC's largest source of gross
  contamination in 2016–2020 was invisible to the border list, consistent with spices
  carried home rather than imported commercially.

Reported without prediction: lead-spice firms by listing year and by country; the stock
of lead-spice firms on each year's last Wayback capture (2015–2026); the same grading on
the current page alone; and which of NYC's top five abroad purchase countries (Georgia,
Bangladesh, Pakistan, India, Russian Federation) appear among E and L firms.

## Limits known now

- A listing is an enforcement action, not a measure of contamination. It depends on what
  FDA sampled, which firms shipped to the US, and policy.
- Firms that were removed before a capture are not seen. E counts on a 2020/2021 capture
  to limit this, and L counts on a page up to about ten months after its period ends.
- The Wayback Machine may have gaps, and the page layout may have changed over the
  years. The job writes a parse check for every capture (Problems lines in the text
  against parsed lines) so misreads can be seen.
- Firms are not products or shipments. One listing can cover many entries.
- Country is the Red List heading, not necessarily where the spice was grown.

## Files

- `ia9942_lead_spice.py`: fetches, parses and grades. It writes the frozen pages, every
  parsed line, the lead-spice firms per capture, the stock by capture and `grades.json`.
- `test_ia9942_lead_spice.py`: offline test of the parser (on a fixture that copies the
  page's entry layout) and of the grading rules.
