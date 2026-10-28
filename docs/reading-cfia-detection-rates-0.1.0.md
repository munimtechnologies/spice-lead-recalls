# Reading CFIA's mycotoxin detection rates: the reporting limit decides the number (0.1.0)

By MV2 of Munim, Inc. Prepared with AI agents working in his name. Text CC BY 4.0.

A one-page note for anyone who compares "percent detected" across Canadian Food Inspection
Agency (CFIA) surveys, or who builds a trend from them: risk assessors, journalists, students and
food-safety staff. It adds no new analysis. Every figure below comes from a note in this
repository, and each note is reproducible from CFIA's open per-sample files on the Open
Government Portal. It is not a finding about any product, brand or health risk.

## The point

In CFIA's open mycotoxin files, a detection rate depends on the reporting limit at least as much
as on the food. Two surveys can report very different rates for the same kind of product and
still agree once both are read at the same limit. Neither survey is wrong. They are just not
comparable as printed.

## Five cases from CFIA's own files

1. **One survey, two limits.** In CFIA's 2018-19 survey of infant cereals, the report's Table 3
   gives 123 samples with deoxynivalenol (DON) and its Table 2 gives 13. The open file holds 119
   of 286 detected down to the 0.2 ppb limit of detection, and exactly 13 at or above the
   20 ppb reporting limit. The two tables count the same data under two limits.
   ([myco-don 0.1.0](myco-don-0.1.0-result.md))
2. **One year, two methods.** For ochratoxin A in 2018-19 grain foods, on the seven product
   labels both surveys share, CFIA's OTA-only survey detects 82 of 150 and its multi-mycotoxin
   survey 10 of 247: a within-label odds ratio of 26.0. Read both at 0.8 ppb and it is 15 of 150
   against 10 of 247, an odds ratio of 2.09 (95% interval 0.86–5.08).
   ([ota-grain-2018 0.1.0](ota-grain-2018-0.1.0-result.md))
3. **Two methods, three years apart.** For DON, CFIA's 2015-16 grains-and-pulses survey and its
   2018-19 multi-mycotoxin survey give a within-label odds ratio of 6.44 on 18 shared labels at
   their own limits, and 1.28 (0.87–1.90) at 10 ppb. The 2015-16 headline "46% detected" becomes
   21% at 10 ppb. ([don-grains-2015 0.1.0](don-grains-2015-0.1.0-result.md))
4. **One program, changing limits.** In CFIA's 2000–2018 livestock-feed monitoring file, the
   sharpest year-to-year changes in detection fall in the same years as changes in the
   quantification limit: T-2 toxin 1.9% → 25.5% and HT-2 4.4% → 34.5% in 2014-15, ochratoxin A
   7.0% → 2.4%, and fumonisins 44.6% → 8.6% in 2016-17. These are method changes, not
   feed-supply trends. ([feed-myco 0.1.0](feed-myco-0.1.0-result.md))
5. **A non-detect written as the limit.** CFIA's open 2011-12 coumarin file writes its four
   non-detects as the bare number `0.29`, so a naive reader counts 193 of 193 detected where
   CFIA says 98% (189). ([coumarin-early-surveys 0.1.0](coumarin-early-surveys-0.1.0-result.md))

## A checklist before comparing two rates

1. **Find each survey's limit.** If none is printed, the smallest reported value is the best
   available stand-in (0.412 ppb for DON in 2015-16; 10 ppb in the 2018-19 multi-mycotoxin file).
2. **Re-cut both at the higher limit** before comparing rates.
3. **Compare within product labels** (a Mantel-Haenszel odds ratio, for example). Pooled rates
   mostly reflect which foods were bought. The same holds for co-occurrence: the retail
   OTA × DON odds ratio of 8.54 falls to 1.40 within products
   ([cooc-strata 0.1.0](cooc-strata-0.1.0-result.md)).
4. **Report an interval, not only a p-value.** "No significant difference" at a common cut can
   still allow a several-fold gap (case 2).
5. **Check how non-detects are written** before counting. CFIA's files use a literal 0, a bare
   limit (case 5) or a text token (`Not Detected/ Non-détecté` in the 2018-19 OTA grain file).
6. **Check which mean an "average" is.** Under the same "positive results only" table note, CFIA's
   2014-15 coumarin averages are all-sample means while its ochratoxin A averages are
   positives-only means ([coumarin-cfia-table-audit 0.1.0](coumarin-cfia-table-audit-0.1.0-result.md),
   [ota-foods 0.1.0](ota-foods-0.1.0-result.md)).
7. **Look for limit changes inside one program** before reading a trend (case 4).

## Limits of this note

The cases come from CFIA's open files only, and the common cuts are the best figures available,
not limits CFIA states for every method. Stratifying by product label removes label-level
differences, not within-label ones. Only CFIA can say why its methods and reports differ.
