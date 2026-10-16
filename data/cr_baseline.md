# Natural chromium vs NYC's chromate-like spice pairs

cr_baseline 0.2.0. Pairs: https://raw.githubusercontent.com/munimtechnologies/spice-lead-recalls/main/data/nyc_spice_pb_cr_pairs.csv (sha256 0dd4a2c4685d). Ceilings sha256 6f8a9886531d.

- Chromate-like pairs (molar Pb:Cr 0.7-2): 34.
- baseline robust: 32.
- baseline unresolved: 2.
- baseline background-limited: 0.

The **baseline verdict** uses total chromium only. The **final verdict** folds in an optional Cr(VI) speciation test (`cr6_result` per pair): a positive test confirms hexavalent chromium on the product and overrides the ceiling-only verdict as `cr6-confirmed`; a negative test is not exculpatory and leaves the baseline verdict (Lopez et al. 2022 report a 167 mg/kg-Pb coriander that developed no DPC colour). 0 of 34 pairs carry a speciation result; the rest are `untested`, so their final verdict equals their baseline verdict.

The edge is the most natural chromium the pair can lose before its ratio rises above 2.

| Pb row | Cr row | collected | product | bought in | Pb ppm | Cr ppm | molar Pb:Cr | ceilings | edge ppm | highest ceiling | baseline verdict | speciation | final verdict | ceilings at or above the edge |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 3282 | 3281 | 2019-01-22 | Coriander | GEORGIA | 51 | 9.1 | 1.406 | coriander | 2.7 | 18.93 | unresolved | untested | unresolved | ICP-OES 12.45 (Gazwi et al. 2022, Sci Rep 12:9834, PMC9013364); FAAS 18.93 (Tefera & Teklewold 2021, Heliyon 7:e07048, PMC8138603) |
| 2968 | 2967 | 2018-09-24 | Turmeric | ALGERIA | 20 | 6.1 | 0.823 | turmeric | 3.59 | 2.88 | robust | untested | robust | - |
| 2290 | 2289 | 2017-06-07 | Coriander Powder | BANGLADESH | 52 | 12 | 1.087 | coriander | 5.48 | 18.93 | unresolved | untested | unresolved | ICP-OES 12.45 (Gazwi et al. 2022, Sci Rep 12:9834, PMC9013364); FAAS 18.93 (Tefera & Teklewold 2021, Heliyon 7:e07048, PMC8138603) |
| 707 | 706 | 2013-02-14 | Black Pepper | BANGLADESH | 85 | 21 | 1.016 | black pepper | 10.33 | 0.113 | robust | untested | robust | - |
| 2156 | 2155 | 2017-03-23 | Spice Mix | BANGLADESH | 170 | 38 | 1.123 | generic | 16.67 | 8.59 | robust | untested | robust | - |
| 1371 | 1370 | 2015-03-18 | Chili powder | BANGLADESH | 110 | 34 | 0.812 | chili/paprika | 20.2 | 3.17 | robust | untested | robust | - |
| 2231 | 2230 | 2017-05-03 | Curry Masala | PAKISTAN | 300 | 69 | 1.091 | curry | 31.36 | 3.55 | robust | untested | robust | - |
| 3034 | 3033 | 2018-10-20 | Raz El Hanout | ALGERIA | 2200 | 310 | 1.781 | generic | 33.96 | 8.59 | robust | untested | robust | - |
| 704 | 703 | 2013-02-14 | Cumin Powder | BANGLADESH | 560 | 120 | 1.171 | cumin | 49.74 | 8.59 | robust | untested | robust | - |
| 3227 | 3226 | 2019-01-15 | Balqees Spices Yemeni Spices Mix | UNITED STATES | 570 | 130 | 1.1 | generic | 58.48 | 8.59 | robust | untested | robust | - |
| 3254 | 3253 | 2019-01-15 | Balqees Spices Yemeni Spices Mix | UNITED STATES | 610 | 140 | 1.093 | generic | 63.46 | 8.59 | robust | untested | robust | - |
| 1234 | 1233 | 2015-01-20 | Curry Powder | BANGLADESH | 530 | 140 | 0.95 | curry | 73.5 | 3.55 | robust | untested | robust | - |
| 702 | 701 | 2013-02-14 | Cinnamon Powder | BANGLADESH | 880 | 220 | 1.004 | cinnamon | 109.58 | 4 | robust | untested | robust | - |
| 4400 | 4399 | 2019-09-11 | Khmeli Suneli | GEORGIA | 2500 | 500 | 1.255 | generic | 186.32 | 8.59 | robust | untested | robust | - |
| 4686 | 4685 | 2019-11-19 | Turmeric | INDIA | 2000 | 460 | 1.091 | turmeric | 209.05 | 2.88 | robust | untested | robust | - |
| 2385 | 2384 | 2017-07-19 | Svanuri Marili | GEORGIA | 2000 | 500 | 1.004 | generic | 249.05 | 8.59 | robust | untested | robust | - |
| 1641 | 1640 | 2016-05-04 | Uckho Suneli | GEORGIA | 3500 | 740 | 1.187 | generic | 300.84 | 8.59 | robust | untested | robust | - |
| 2219 | 2218 | 2017-04-24 | Turmeric Spice Powder | NEPAL | 2700 | 640 | 1.059 | turmeric | 301.22 | 2.88 | robust | untested | robust | - |
| 1244 | 1243 | 2015-01-29 | Svaneti salt | GEORGIA | 4100 | 880 | 1.169 | generic | 365.56 | 8.59 | robust | untested | robust | - |
| 2604 | 2603 | 2018-01-06 | Marili Spice Mix Powder | GEORGIA | 4300 | 910 | 1.186 | generic | 370.47 | 8.59 | robust | untested | robust | - |
| 5263 | 5262 | 2020-10-19 | Cumin Powder | UZBEKISTAN | 6700 | 1300 | 1.293 | cumin | 459.33 | 8.59 | robust | untested | robust | - |
| 2958 | 2957 | 2018-09-24 | Paprika | ALGERIA | 5800 | 1200 | 1.213 | chili/paprika | 472.26 | 3.17 | robust | untested | robust | - |
| 814 | 813 | 2013-06-27 | Green spices | PAKISTAN | 7100 | 1400 | 1.273 | generic | 509.14 | 8.59 | robust | untested | robust | - |
| 872 | 871 | 2013-08-15 | Xarcho Sunely | GEORGIA | 7100 | 1400 | 1.273 | generic | 509.14 | 8.59 | robust | untested | robust | - |
| 2195 | 2194 | 2017-04-07 | All purpose soup base powder | GEORGIA | 9600 | 1800 | 1.338 | generic | 595.46 | 8.59 | robust | untested | robust | - |
| 1778 | 1777 | 2016-08-16 | Saffron | RUSSIAN FEDERATION | 8000 | 1600 | 1.255 | generic | 596.22 | 8.59 | robust | untested | robust | - |
| 3494 | 3493 | 2019-02-21 | Cumin | ECUADOR | 4700 | 1200 | 0.983 | cumin | 610.28 | 8.59 | robust | untested | robust | - |
| 2325 | 2324 | 2017-06-28 | Khneli suneli | GEORGIA | 11000 | 2000 | 1.38 | generic | 619.8 | 8.59 | robust | untested | robust | - |
| 2193 | 2192 | 2017-04-07 | Yellow flower | GEORGIA | 22000 | 4100 | 1.347 | generic | 1339.59 | 8.59 | robust | untested | robust | - |
| 2052 | 2051 | 2017-02-02 | Orange Spice | GEORGIA | 13000 | 3100 | 1.052 | generic | 1468.85 | 8.59 | robust | untested | robust | - |
| 1776 | 1775 | 2016-08-16 | No name Seasoning | RUSSIAN FEDERATION | 17000 | 3700 | 1.153 | generic | 1566.96 | 8.59 | robust | untested | robust | - |
| 2380 | 2379 | 2017-07-19 | Hviteli Hvavili | GEORGIA | 21000 | 4500 | 1.171 | generic | 1865.07 | 8.59 | robust | untested | robust | - |
| 5235 | 5234 | 2020-09-25 | TMT Khmeli Suneli | GEORGIA | 78000 | 15000 | 1.305 | generic | 5213.11 | 8.59 | robust | untested | robust | - |
| 2376 | 2375 | 2017-07-18 | Georgian saffron (zaprana) | GEORGIA | 48000 | 12000 | 1.004 | generic | 5977.3 | 8.59 | robust | untested | robust | - |

Ceilings are the highest published natural chromium for each spice and method; they are not limits for any one sample. NYC's chromium results are total chromium, as sold. `cr6-confirmed` means hexavalent chromium was confirmed present on the product, not that lead chromate is proven.
