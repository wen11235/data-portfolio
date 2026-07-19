# Scientific Data Visualization: Galaxy Simulation Analysis

**TL;DR:** Every other project in this portfolio visualizes business or web data. This one visualizes a raw astrophysics simulation — 315,372 gas/star/dark-matter particles from a galaxy formation snapshot — to show the same visualization judgment (right chart for the question, honest scale choices, don't let noise dominate a plot) transfers to a domain with zero customers or revenue in it.

[📄 Full report](report.html) · [📓 Notebook](notebooks/analysis.ipynb)

*Originally built as an extra-credit assignment for a Data Visualization course (Information Management, UIUC), reworked here with corrected scale handling, a fixed spatial plot, and an actual data-quality investigation the original assignment didn't need to do.*

## Why this exists

A portfolio full of customer churn, retail sales, and job postings makes a specific kind of analyst look believable. It says nothing about whether the underlying skill — deciding what chart a question actually needs, and not shipping a chart that quietly misrepresents the data — generalizes. This project is here specifically to test that: astrophysics simulation output, a genuinely unfamiliar data domain, same standards applied.

## Data & tooling

[TipsyGalaxy](https://yt-project.org/data/TipsyGalaxy.tar.gz) — a sample N-body/SPH galaxy formation snapshot (Tipsy format) from the [yt-project](https://yt-project.org/) data archive. [`yt`](https://yt-project.org/) is the analysis library — purpose-built for astrophysical simulation data (particle fields, spatial deposition/projection, unit-aware physical quantities) rather than a general-purpose dataframe tool. Not committed to this repo (~11MB, see `data/README.md`).

## What's in the snapshot

315,372 particles: 76,962 gas, 138,410 star, 100,000 dark matter — one frozen moment (t=20.1 code_time units) of a simulated galaxy's evolution.

## Two things that looked like bugs and weren't (or were, and got fixed)

**1. "Most stars form in the future" — a sentinel value, not a units bug.** A first pass at star formation times showed 81% of star particles (112,508 of 138,410) with a formation time *after* the snapshot's current time — which would mean they hadn't formed yet. Before assuming that's fine, I checked units directly rather than guessing (`ds.current_time.in_units(field.units)`) — both fields are genuinely in the same `code_time` units, so it isn't a conversion bug. What it actually is: those 112,508 particles all share the *exact same* value (6706.9, ~330x past the snapshot's current time) — the signature of a sentinel flag marking "pre-existing initial-condition star," not a real measurement. Only the remaining 25,902 particles (19%) are stars that actually formed during the simulated window, and that's the population the formation-time histogram now describes explicitly rather than silently mixing both groups together.

**2. A metallicity scatter plot that blew up to `1e-35` on the y-axis.** ~81% of star particles have exactly zero recorded metallicity (a separate, if similarly-sized, "pristine" population), and among the rest, values form a smooth continuum down to floating-point noise rather than a clean signal/noise split — so there's no principled data cutoff to apply. The fix isn't filtering the data further; it's clipping the axis display range (`ylim(bottom=1e-6)`) and saying so directly in the chart title, rather than either hiding the noise or letting a handful of extreme values stretch the whole plot into unreadability.

**3. The spatial plot originally showed almost nothing.** A first pass at `yt.ParticleProjectionPlot` over the full simulation domain (1 Mpc box) rendered the entire galaxy as a tiny dot — technically correct, visually useless. Re-centering and zooming to a 60 kpc window around the galaxy is what actually reveals the spiral structure.

## Findings

- **Spatial structure**: a clear spiral/disk pattern is visible in the gas-mass projection once zoomed to the galaxy's actual scale — spatial visualization shows structure no histogram could.
- **Gas temperature** spans ~5 orders of magnitude (10¹–10⁶ K), with most mass in a cool, dense population (~10³–10⁴ K, the disk) and a long hot tail (shocked/diffuse gas).
- **Star formation** (among the 19% that genuinely formed during the run) is heaviest early and continues at a roughly steady, noisy rate — consistent with an actively star-forming galaxy, not a single burst.
- **Mass vs. metallicity**: among enriched stars, metallicity rises with stellar mass and converges toward ~0.01–0.04 at higher masses — consistent with more massive stars forming later, from more chemically enriched gas.

## Skills demonstrated

Scientific/domain-specific visualization (`yt`), unit-aware data handling, data-quality investigation (distinguishing a units bug from a sentinel-value artifact by actually checking rather than guessing), log/linear scale judgment, spatial (projection) plotting, honest handling of noisy/degenerate data ranges.
