# Pre-registration: is "Ceylon" cinnamon sold in Canada really Ceylon? Coumarin by label and declared origin in CFIA's open files (coumarin-cinnamon 0.1.0)

**Author:** MV2, Munim, Inc. (mv2@munimtech.com). Work made with AI agents.
**License:** text CC BY 4.0; code Apache-2.0.
**Written:** 2026-10-18, before any row of the three primary data files was read.

## Why this question

There are two kinds of cinnamon. True or Ceylon cinnamon (*Cinnamomum verum*, mostly from Sri Lanka) holds
only traces of coumarin. Cassia cinnamons (Chinese *C. cassia*, Indonesian *C. burmannii*, Vietnamese or
"Saigon" *C. loureiroi*) hold thousands of ppm. Coumarin is a liver toxicant in animals, and Canada does not
allow it to be added to food. Ceylon is dearer, and it is sold to people who want to avoid coumarin, so
selling cassia as "Ceylon" is both fraud and a health issue. In 2025 the European Commission's Joint
Research Centre ("Detection of fraudulent practices in commercially available cinnamon", JRC142672; 104
products bought in 10 EU countries, Serbia, Sri Lanka and the UK) found that up to 9% of the samples
labelled Ceylon were wholly or partly cassia. Retail surveys elsewhere (Czech Republic 2012; United States, Wang et al. 2013) used coumarin to
show what kind of cinnamon was on the shelf.

The Canadian Food Inspection Agency (CFIA) tested retail cinnamon for coumarin every year from 2011 to 2016.
Its reports give only ranges and averages by product type. They do not say how much of the cinnamon is
cassia, whether anything sold as Ceylon was cassia, or which declared origins carry which kind. The
per-sample files are open (open.canada.ca, Open Government Licence - Canada) and carry each product name and
declared origin. As far as we can find, this is the first reading of them by label claim and origin.

## What was already known when this was written

We have read the dataset descriptions and CFIA's report pages. For the three primary files (2012-13,
2014-15, 2015-16) we have not opened the CSV or seen any row, product name, origin or header. For the
2011-12 file, an earlier run (2026-10-17) read its header and one row to learn CFIA's layout (Sample No.,
Region, Function, Origin, Product, Date, Test type, Component, Result, Unit, Plan code). That file is
therefore used only as a replication set, reported but not graded.

- **2011-12** (dataset 327a6726-...): 193 samples, 11 cities; coumarin in 98%. Category maxima: ground
  cinnamon 7,816 ppm, cinnamon sticks 6,823, spice mixes 2,014, tea 1,040. Ground cinnamon: 87 samples,
  16.2-7,816 ppm, mean 3,594 (from the 2015-16 report's comparison table).
- **2012-13** (ca2411af-...): 93 samples of ground cinnamon and spice mixes, 11 cities, April 2012 to March
  2013. All had coumarin; the highest was a ground cinnamon at 7,621 ppm.
- **2014-15** (ecb615ff-...): 739 samples. Oils and extracts: 239 (28 domestic, 64 imported, 147 unspecified),
  coumarin detected in 46. "Only seven out of 200 samples of vanilla extracts" had coumarin, at 0.2-4.3 ppm;
  one mixed cinnamon/vanilla extract had 78.8 ppm; all cinnamon oils and extracts had coumarin (up to 1,000
  ppm, mean 281). The report notes that tonka beans, a coumarin source, are used as substitutes for vanilla.
- **2015-16** (afa33f86-...): 747 samples. Ground cinnamon: 29 (4 domestic, 10 imported, 15 unspecified), all
  with coumarin, 6.8-5,040, mean 2,839. The HTML report prints ppb; we take these as ppm (a ppb reading would
  put the "cassia" maximum at 5 ppm, far below every published cassia value). The report says "the single
  pure Ceylon sample" was 6.8 and "the one sample labelled Saigon cinnamon" was 5,040, the survey maximum,
  and that most ground cinnamon did not name its type. No report names a country.
- Literature used for the class cut-offs: Ceylon 5-90 ppm (17 samples, Wang et al. 2013); Saigon 1,060-6,970;
  Czech retail ground cinnamon 2,571-7,057 (all cassia).

## Classes (fixed before reading)

Each pure-cinnamon sample is **verum-type** below 300 ppm, **cassia-type** at 1,000 ppm or more, and
**intermediate** in between (a blend, or a sample we cannot type). 300 is over three times the highest
Ceylon value in Wang et al.; 1,000 is below the lowest Saigon value. Coumarin is a strong marker, not proof
of species: only DNA or a full chemical profile proves what a sample is.

## Predictions (graded by `coumarin_cinnamon.py`, unchanged after this commit)

"Primary" means the 2012-13, 2014-15 and 2015-16 files.

| | prediction |
|---|---|
| P1 | at least 50 pure-cinnamon samples in the primary files, 26-32 of them in 2015-16 (parse gate) |
| P2 | the highest primary cinnamon result is 7,621 ppm (+/-1) in 2012-13 and the 2015-16 maximum is 5,040 (+/-1) (CFIA's reports; a consistency check, not a prediction) |
| P3 | at least 80% of primary cinnamon samples are cassia-type |
| P4 | fewer than 10% of primary cinnamon samples are intermediate (coumarin separates the two kinds cleanly) |
| P5 | no cinnamon sample whose name claims Ceylon (ceylon, ceylan, true cinnamon, verum, zeylanicum, Sri Lanka) is cassia-type (gradable if at least 2 such samples) |
| P6 | every cinnamon sample whose name claims cassia, Saigon, Vietnam, Korintje, Indonesia or China is cassia-type (gradable if at least 2) |
| P7 | no cinnamon sample declaring Indonesia, China or Vietnam as origin is verum-type (gradable if at least 5) |
| P8 | more than half of the cinnamon samples declaring Sri Lanka as origin are verum-type (gradable if at least 3) |
| P9 | Mexico is strictly the most frequent declared country among 2014-15 vanilla products with coumarin detected (gradable if at least 3 have a country; a tie is not met) |

Reasoning. P3: CFIA's means (2,839-3,594 ppm) sit near the cassia literature means, and its reports say most
cinnamon sold is cassia, so we expect the large majority to be cassia-type; the risk is many Ceylon
products from specialty stores. P4: the literature ranges do not overlap, but blends exist. P5: this is the
fraud question. With probably only a handful of Ceylon-labelled samples, and one already known to be
verum-type (6.8 ppm in 2015-16), we predict no substitution; at the JRC's rate of up to 9%, even one case
among a few samples is less likely than not. P6: the known Saigon sample is 5,040. P7: these are the cassia-growing countries; a
verum-type sample declaring one of them would be odd. P8: we expect Sri Lanka-declared cinnamon to be true
cinnamon; the risk is that "origin" is a packer or a re-exporter. P9: the trace coumarin in 7 of 200 vanilla
extracts is far below what tonka adulteration would give, so this is a weak guess based on the
reputation of cheap Mexican vanilla, written down to be tested. All of these are expectations, not checked
facts.

## Method

`coumarin_cinnamon.py` downloads the four CSVs, records each sha256, keeps rows whose component names
coumarin (all rows if there is no component column), and merges rows into one record per (base sample
number, product) per file; a trailing "D" duplicate merges into its base and the record's value is the mean
of its results. Results are converted to ppm (ppb and ug/kg divided by 1,000); "<" values, "ND" and blanks
read as zero. Pre-registered unit rule: if a file labels its results ppb or ug/kg, but its pure-cinnamon
results would then all be below 50 ppm while the largest raw number lies between 1,000 and 20,000, the
numbers are read as ppm and the file is flagged.

A sample is pure cinnamon if its product name (or product-type column) contains cinnamon, cinamon, cannelle,
canela or cassia, and its name has no word of a food or blend (mix, blend, pie, chai, masala, sugar, tea,
oil, extract, flavour, bread, cereal, cookie, "and", "with" and similar; full list in the code), and any
product-type column does not name tea, baked goods, cereals, beverages, sauces, oils, extracts, mixes or
"containing". Sticks, quills, bark and whole pieces are "stick"; the rest "ground". The label claim comes
from the product name only (ceylon / cassia / both / none; "both" counts in neither P5 nor P6). Origins are
upper-cased and normalised (Viet Nam -> VIETNAM, Ceylon -> SRI LANKA); blank, unknown and "imported"
without a country do not count as a declared country. A vanilla product names vanilla plus extract,
essence, flavour, imitation, artificial, paste or pure (or sits in an extracts or oils type), and is not a
tea, mix, sauce, drink or cinnamon product.

The script writes `grades.json`, `summary.md` (classes by file, form, claim and origin for the primary set
and for the 2011-12 replication set; every claimed or Sri Lanka-declared sample; every intermediate
sample; the ten lowest; every vanilla product with coumarin) and `coumarin_samples.csv` (cinnamon and
vanilla samples only). `test_coumarin_cinnamon.py` checks the parser, the rules, the unit rule and the
grader offline on synthetic files in CFIA's layout. If a real file's columns differ from what the parser
expects, the job fails loudly; any fix is recorded as a deviation, and none of the predictions change.

## Limits

Targeted retail sampling, not a market share. Origin is what the label declares (often the packer's
country), and many samples declare none. Product names are whatever CFIA recorded, which may be generic
("ground cinnamon") rather than the label's own words, so Ceylon claims may be rare or absent; P5 may be
ungradable. Coumarin types a sample; it does not prove species. CFIA and Health Canada found no health
concern in these surveys, and nothing here says otherwise. No brand is named in any output beyond what
CFIA's own open file holds.

Contains information licensed under the Open Government Licence - Canada.
