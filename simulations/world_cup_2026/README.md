# 2026 World Cup — Monte Carlo Simulation

A self-contained, standard-library-only Monte Carlo model of the 2026 FIFA
World Cup (the first 48-team edition).

## Run it

```bash
python3 world_cup_mc.py                 # 100k sims, seed 42, top 5
python3 world_cup_mc.py -n 500000 -t 10 # half a million sims, top 10
python3 world_cup_mc.py --seed 7        # different RNG seed
```

No dependencies (no numpy) — runs anywhere with Python 3.9+.

For each team the output reports the probability of reaching the
**Quarter-finals, Semi-finals, Final**, and winning the **title** (plus
decimal title odds):

```
Rank Team                 Win %   Final %    Semi %      QF %   Title odds
--------------------------------------------------------------------------
1    Spain               23.23%    39.97%    63.36%    86.35%         4.3x
2    France              19.43%    35.01%    58.62%    83.64%         5.1x
3    Argentina           16.98%    31.51%    55.12%    81.55%         5.9x
4    England             12.20%    24.13%    46.19%    75.78%         8.2x
5    Brazil               8.40%    17.80%    37.18%    68.72%        11.9x
```

## Model

| Stage | How it's simulated |
|-------|--------------------|
| **Draw** | 48 teams seeded into 4 pots by Elo, randomly drawn into 12 groups of 4 (re-drawn every run). |
| **Group stage** | Full round-robin. Each match = two independent Poisson goal counts whose means come from the Elo gap, so draws emerge naturally. |
| **Qualification** | Top 2 of each group + the 8 best third-placed teams → 32 teams. |
| **Knockout** | R32→R16→QF→SF→Final in a **fixed** seeded bracket (no re-seeding between rounds). Ties after 90' resolved by a strength-weighted coin flip (extra time / penalties). |

### Key ingredients

- **Elo ratings** (`TEAMS_ELO`) — World-Football-Elo-style estimates calibrated
  to early-2026 form. These are the single biggest driver of the output; edit
  them to reflect your own priors.
- **Form noise** (`FORM_NOISE_SD`, default 70 Elo) — every tournament run draws
  a fresh strength per team (injuries, peaking, chemistry, luck). This is what
  stops a pure-Elo model from being over-confident about the favourites and
  brings the spread in line with real betting markets.
- **Host bonus** (`HOST_ELO_BONUS`) — USA / Mexico / Canada get a modest field
  advantage throughout.

## Caveats

- The official 2026 group draw and the exact R32 bracket-slot mapping are
  approximated (seeded draw + standard seeded bracket), so this is an **ensemble
  over plausible brackets**, not a single fixed draw.
- Ratings are estimates, not official numbers. Treat the odds as
  model-implied probabilities, not a betting recommendation.
- Statistical error at 500k sims is roughly ±0.1 percentage points on the
  top probabilities; results are stable across RNG seeds.
