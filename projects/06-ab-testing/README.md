# A/B Test Analysis: Cookie Cats Gate Placement

**TL;DR:** A mobile game A/B-tested moving a progression gate from level 30 to level 40. 1-day retention showed no significant difference (p=0.074), but 7-day retention was significantly **worse** with the later gate (p=0.0016, −0.82 percentage points) — the opposite of what "give players more free content before the paywall" would predict. Recommendation: keep the gate at level 30.

[📄 Full report](report.html) · [📓 Notebook](notebooks/analysis.ipynb)

## Problem

Cookie Cats places a gate that pauses players until they wait or pay. Product hypothesized that moving the gate later (level 30 → 40) — giving players more uninterrupted content early — would improve retention. 90,189 real players were randomized into `gate_30` (control) or `gate_40` (treatment) at install. Does the data support the hypothesis?

## Data

[Cookie Cats A/B Test](https://www.kaggle.com/datasets/mursideyarkin/mobile-games-ab-testing-cookie-cats) — 90,189 players, columns: `version` (assigned group), `sum_gamerounds` (rounds played in first 14 days), `retention_1`, `retention_7` (returned after 1 / 7 days). Not committed to this repo (2.7MB, see `data/README.md`).

## Method

1. **Randomization check** — group sizes (49.6% / 50.4%) and a chi-square balance test.
2. **Engagement check** — distribution of rounds played, with the dataset's known extreme outlier (one player with 49,854 rounds) excluded from that comparison only.
3. **Two-proportion z-tests** on 1-day and 7-day retention.
4. **Bootstrap confidence intervals** (5,000 resamples) on the retention difference, for an effect-size view beyond a single p-value.
5. **Practical significance check** — translate the percentage-point effect into an absolute player count at scale.

## Results

| Metric | gate_30 (control) | gate_40 (treatment) | Difference | p-value |
|---|---|---|---|---|
| 1-day retention | 44.82% | 44.23% | +0.59 pp | 0.074 (not significant) |
| 7-day retention | 19.02% | 18.20% | **+0.82 pp** | **0.0016 (significant)** |

95% bootstrap CI on the 7-day difference: **[+0.32, +1.35] percentage points** — entirely above zero, consistent with the z-test.

Engagement (`sum_gamerounds`) is statistically indistinguishable between groups (medians 17 vs 16 rounds) — the retention drop for `gate_40` isn't offset by more play from whoever does stick around.

## A worked example of statistical vs. practical significance

The group split itself (49.6% / 50.4%) is technically statistically distinguishable from exactly 50/50 (p=0.009) at this sample size — flagged in the notebook, and deliberately *not* treated as evidence of a broken randomizer, since a gap this small has no plausible mechanism to bias the retention results and is well within normal randomizer noise. The same reasoning applies in reverse to the 7-day retention result: a 0.82-point effect is small in absolute terms, but 7-day retention is one of the most-watched health metrics in mobile games, the effect is consistent across 5,000 bootstrap resamples (not a one-off), and at scale (~1M monthly installs) it translates to roughly 8,200 fewer 7-day-retained players per million installs. Small ≠ ignorable when the metric is this central and the sample size this large.

## Recommendation

**Do not move the gate to level 40.** 7-day retention — the more reliable of the two retention metrics — is significantly worse with the later gate, consistently across resampling, with no engagement upside to offset it. Whatever intuition motivated "move the gate later," this test doesn't support it — a good reminder that A/B tests exist precisely to catch cases where an intuitively appealing change doesn't hold up.

## Skills demonstrated

Hypothesis testing (two-proportion z-test), bootstrap resampling, randomization/sanity checks, statistical vs. practical significance, experiment-driven product recommendation.
