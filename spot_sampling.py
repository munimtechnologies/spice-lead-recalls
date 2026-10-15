#!/usr/bin/env python3
"""spot_sampling: how many Raman spots does a lead chromate screen need?

A bulk Raman reading of spice powder sees lead chromate (PbCrO4) only when the
pigment is about 0.5% of the probed powder (Erasmus et al. 2021). lod_curve.py
shows that catching 9 in 10 of NYC's spices with >= 100 ppm lead needs about
0.025-0.05%. If the pigment sits in discrete grains instead of being spread
evenly, a small probe that happens to hold a grain sees a local fraction far
above the bulk one, so many small spots can beat one big reading. This script
models that with Poisson statistics and applies it to the same public lab data.

Model (grains of one size, placed at random):
- x = c / L0: the bulk pigment fraction c over the instrument's limit L0.
- r = m_probe * L0 / m_grain: the probed mass, in units of the mass that one
  grain brings exactly to the limit. A spot is positive when it holds at least
  k* = max(1, ceil(r)) grains; the grain count is Poisson with mean r * x.
- p(x, r) = P[Poisson(r x) >= k*]; N spots catch with 1 - (1 - p)^N.
At r = 1, p = 1 - exp(-x), so N = ln(1 / (1 - P)) / x spots reach probability P
whatever the grain size; only the probe size that matches depends on it.

Outputs: spot_sampling.json, spot_sampling.md, spot_sampling.csv.

Made by MV2 of Munim, Inc. with AI agents working in his name. Apache-2.0.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import random
import sys

import lod_curve as lc

__version__ = "0.1.0"

# Bench powder Raman limit, 0.5% w/w PbCrO4 (Erasmus et al. 2021, PLSR model).
L0 = 0.005
# Density of lead(II) chromate, g/cm3 (CRC Handbook). Loose spice powder is
# taken as 0.5 g/cm3; it only sets the probe edge, not the spot counts.
RHO_PBCRO4 = 6.12
RHO_BULK = 0.5

R_GRID = [0.1, 0.3, 1.0, 2.0, 3.0, 10.0, 1000.0]
R_DATA = [1.0, 0.3, 2.0, 1000.0]
N_GRID = [1, 5, 10, 25, 50, 100, 200]
PPM_GRID = [100, 160, 321, 641, 1603, 3206]
GRAIN_UM = [1, 5, 10, 20, 50]
MC_CASES = [(0.05, 1.0), (0.2, 1.0), (0.3, 0.3), (0.5, 2.0), (1.0, 3.0)]


def x_of_ppm(ppm, l0=L0):
    """Lead (ug/g) -> bulk PbCrO4 fraction over the limit, if all the lead is PbCrO4."""
    return ppm / (lc.PB_IN_PBCRO4 * 1e6) / l0


def k_star(r):
    """Grains a probe of relative mass r must hold to reach the limit."""
    return max(1, math.ceil(r - 1e-12))


def _log_pmf(j, lam):
    return -lam + j * math.log(lam) - math.lgamma(j + 1)


def poisson_sf(k, lam):
    """P[Poisson(lam) >= k], without underflow for large lam or cancellation for small."""
    if k <= 0:
        return 1.0
    if lam <= 0:
        return 0.0
    if k == 1:
        return -math.expm1(-lam)
    if lam < k:
        # Upper tail; terms fall from j = k on because k > lam.
        total, j = 0.0, k
        while j <= k + 100000:
            t = math.exp(_log_pmf(j, lam))
            total += t
            if t <= total * 1e-16:
                break
            j += 1
        return min(1.0, total)
    return max(0.0, 1.0 - sum(math.exp(_log_pmf(j, lam)) for j in range(k)))


def spot_p(x, r):
    """Chance that one spot is positive."""
    return poisson_sf(k_star(r), r * x)


def catch_from_p(p, n):
    if p >= 1.0:
        return 1.0
    return -math.expm1(n * math.log1p(-p))


def catch_prob(x, r, n):
    """Chance that at least one of n spots is positive."""
    return catch_from_p(spot_p(x, r), n)


def spots_needed(x, r, prob=0.9):
    """Fewest spots that catch with probability >= prob; None if no number does."""
    p = spot_p(x, r)
    if p <= 0.0:
        return None
    if p >= prob:
        return 1
    return math.ceil(math.log1p(-prob) / math.log1p(-p) - 1e-9)


def grain_mass_g(d_um):
    return RHO_PBCRO4 * math.pi / 6.0 * (d_um * 1e-4) ** 3


def matched_probe(d_um, l0=L0, rho_bulk=RHO_BULK):
    """(probe mass in ug, cube edge in um) at r = 1 for grains of diameter d_um."""
    m = grain_mass_g(d_um) / l0
    return m * 1e6, (m / rho_bulk) ** (1.0 / 3.0) * 1e4


def simulate(x, r, cells, rng):
    """Drop round(cells * r * x) grains at random into `cells` probes and return
    the share of probes holding >= k* grains (checks the Poisson formula)."""
    grains = int(round(cells * r * x))
    counts = [0] * cells
    for _ in range(grains):
        counts[rng.randrange(cells)] += 1
    k = k_star(r)
    return sum(c >= k for c in counts) / cells


def design(l0=L0):
    out = []
    for ppm in PPM_GRID:
        x = x_of_ppm(ppm, l0)
        out.append({"lead_ppm": ppm, "pct_pbcro4": round(100 * x * l0, 4), "x": round(x, 5),
                    "spots_for_90pct": {"%g" % r: spots_needed(x, r) for r in R_GRID}})
    return out


def grains():
    out = []
    for d in GRAIN_UM:
        m_ug, edge = matched_probe(d)
        out.append({"grain_um": d, "grain_ng": round(grain_mass_g(d) * 1e9, 4),
                    "matched_probe_ug": round(m_ug, 6), "matched_cube_edge_um": round(edge, 1)})
    return out


def group_rows(name, values):
    rows = []
    for base in lc.BASES_PPM:
        hot = [v for v in values if v >= base]
        for r in R_DATA:
            ps = [spot_p(x_of_ppm(v), r) for v in hot]
            for n in N_GRID:
                probs = [catch_from_p(p, n) for p in ps]
                rows.append({"channel": name, "base_ppm": base, "samples": len(hot), "r": r, "spots": n,
                             "expected_caught": round(sum(probs), 1),
                             "share": round(sum(probs) / len(hot), 3) if hot else None,
                             "caught_at_90pct": sum(p >= 0.9 for p in probs)})
    return rows


def monte_carlo(cells=200000, seed=20261014):
    rng = random.Random(seed)
    out = []
    for x, r in MC_CASES:
        p = spot_p(x, r)
        sim = simulate(x, r, cells, rng)
        se = math.sqrt(max(p * (1 - p), 1e-12) / cells)
        out.append({"x": x, "r": r, "formula": round(p, 5), "simulated": round(sim, 5),
                    "z": round((sim - p) / se, 2)})
    return out


def summarize(samples, meta, mc_cells=200000):
    groups = {}
    for ch, v in samples:
        groups.setdefault(ch, []).append(v)
    groups["NYC all"] = [v for ch, v in samples if ch.startswith("NYC ")]
    groups["King County all"] = [v for ch, v in samples if ch.startswith("King County ")]
    rows = []
    for ch in sorted(groups):
        rows += group_rows(ch, groups[ch])
    return {"version": __version__, "sources": meta, "l0_pct_pbcro4": 100 * L0,
            "rho_pbcro4": RHO_PBCRO4, "rho_bulk": RHO_BULK, "design": design(), "grains": grains(),
            "data": rows, "monte_carlo": monte_carlo(mc_cells)}


def write_markdown(s, path):
    lines = ["# How many Raman spots does a lead chromate screen need?", "",
             "spot_sampling %s. Instrument limit L0 = %g%% w/w PbCrO4 in the probed powder. r = probe mass over "
             "the mass one grain brings to the limit (r = 1 is the matched probe; r = 1000 is a bulk reading)."
             % (s["version"], s["l0_pct_pbcro4"]), "",
             "## Random spots needed for a 90% catch", "",
             "| lead ppm | % PbCrO4 | " + " | ".join("r=%g" % r for r in R_GRID) + " |",
             "|---|---|" + "---|" * len(R_GRID)]
    for d in s["design"]:
        cells = " | ".join("%s" % (format(d["spots_for_90pct"]["%g" % r], ",") if d["spots_for_90pct"]["%g" % r]
                                   else "never") for r in R_GRID)
        lines.append("| %s | %g | %s |" % (format(d["lead_ppm"], ","), d["pct_pbcro4"], cells))
    lines += ["", "## Matched probe (r = 1) by grain size", "",
              "| grain diameter um | grain mass ng | matched probe ug | cube edge um (bulk %g g/cm3) |" % s["rho_bulk"],
              "|---|---|---|---|"]
    for g in s["grains"]:
        lines.append("| %g | %g | %g | %g |" % (g["grain_um"], g["grain_ng"], g["matched_probe_ug"],
                                               g["matched_cube_edge_um"]))
    lines += ["", "## Public lab data: expected share caught", "",
              "| channel | base ppm | n | r | " + " | ".join("%d spots" % n for n in N_GRID) + " |",
              "|---|---|---|---|" + "---|" * len(N_GRID)]
    by = {}
    for row in s["data"]:
        by.setdefault((row["channel"], row["base_ppm"], row["r"]), []).append(row)
    for (ch, base, r), rs in by.items():
        if not rs[0]["samples"]:
            continue
        lines.append("| %s | %d | %d | %g | %s |" % (ch, base, rs[0]["samples"], r,
                                                    " | ".join("%.0f%%" % (100 * x["share"]) for x in rs)))
    lines += ["", "## Monte Carlo check of the formula", "", "| x | r | formula | simulated | z |", "|---|---|---|---|---|"]
    for m in s["monte_carlo"]:
        lines.append("| %g | %g | %g | %g | %g |" % (m["x"], m["r"], m["formula"], m["simulated"], m["z"]))
    lines += ["", "Assumes every microgram of lead is lead chromate, held in grains of one size placed at random, "
              "and a probe that counts a grain fully or not at all. Real pigment is a mix of sizes and coatings, "
              "and a real beam weights grains by depth and position, so these are design numbers, not a validation."]
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def write_csv(s, path):
    keys = ["channel", "base_ppm", "samples", "r", "spots", "expected_caught", "share", "caught_at_90pct"]
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(keys)
        for row in s["data"]:
            w.writerow([row[k] for k in keys])


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data-dir", default="/data")
    ap.add_argument("--out-dir", default="/out")
    args = ap.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)
    nyc, nyc_meta = lc.fetch(lc.NYC_URL, args.data_dir, "nyc-da9u-wz3r-spice-lead.json")
    kc, kc_meta = lc.fetch(lc.KC_URL, args.data_dir, "kc-i6sy-ckp7.json")
    s = summarize(lc.nyc_samples(nyc) + lc.kc_samples(kc), {"nyc": nyc_meta, "king_county": kc_meta})
    with open(os.path.join(args.out_dir, "spot_sampling.json"), "w", encoding="utf-8") as fh:
        json.dump(s, fh, indent=1)
    write_markdown(s, os.path.join(args.out_dir, "spot_sampling.md"))
    write_csv(s, os.path.join(args.out_dir, "spot_sampling.csv"))
    for d in s["design"]:
        print(d["lead_ppm"], d["spots_for_90pct"])
    for m in s["monte_carlo"]:
        print("mc", m)
    return 0


if __name__ == "__main__":
    sys.exit(main())
