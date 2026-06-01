#!/usr/bin/env python3
"""
Monte Carlo simulation of the 2026 FIFA World Cup.

Format (new 48-team format, first used in 2026):
  * 48 teams in 12 groups (A-L) of 4.
  * Round-robin within each group (6 matches per group).
  * Advancing to the Round of 32:
        - top 2 of every group  -> 24 teams
        - 8 best 3rd-placed teams -> 8 teams
  * Single-elimination knockout: R32 -> R16 -> QF -> SF -> Final.

Match model:
  * Each team carries a World-Football-Elo style rating.
  * Group matches are simulated as two independent Poisson goal counts whose
    means are driven by the Elo difference (so draws emerge naturally).
  * Knockout matches use the same goal model; ties are resolved by extra
    time / penalties modelled as an Elo-weighted coin flip.

The group draw is randomised on every tournament run, respecting FIFA pot
seeding (pot 1 = strongest by Elo, ... pot 4 = weakest), because the precise
matchups materially affect a team's path. This makes the output an ensemble
over plausible brackets rather than a single fixed draw.

Pure standard library - no third-party dependencies.
"""

from __future__ import annotations

import argparse
import math
import random
from collections import defaultdict

# ---------------------------------------------------------------------------
# Team pool and ratings
# ---------------------------------------------------------------------------
# Approximate World-Football-Elo ratings for the 48-team field, calibrated to
# early-2026 form. Hosts (USA, Mexico, Canada) qualify automatically; the rest
# reflect a plausible qualified field. These are estimates, not official
# numbers, and are the single biggest driver of the output - tweak them to
# reflect your own priors.
TEAMS_ELO: dict[str, float] = {
    # --- Pot 1 tier: elite contenders + hosts ---
    "Spain":        2120,
    "France":       2105,
    "Argentina":    2095,
    "England":      2070,
    "Brazil":       2045,
    "Portugal":     2025,
    "Netherlands":  2000,
    "Germany":      1990,
    "Belgium":      1945,
    "Italy":        1940,
    # hosts
    "USA":          1830,
    "Mexico":       1810,
    "Canada":       1815,
    # --- strong sides ---
    "Croatia":      1930,
    "Uruguay":      1925,
    "Colombia":     1920,
    "Morocco":      1910,
    "Switzerland":  1860,
    "Japan":        1850,
    "Denmark":      1845,
    "Senegal":      1840,
    "Ecuador":      1800,
    "Austria":      1795,
    "Korea Republic": 1775,
    # --- mid tier ---
    "Serbia":       1770,
    "Ukraine":      1765,
    "Iran":         1760,
    "Australia":    1750,
    "Poland":       1745,
    "Sweden":       1740,
    "Nigeria":      1735,
    "Egypt":        1730,
    "Norway":       1760,
    "Turkey":       1755,
    "Greece":       1725,
    "Ivory Coast":  1720,
    "Algeria":      1715,
    # --- lower tier ---
    "Cameroon":     1690,
    "Tunisia":      1685,
    "Paraguay":     1680,
    "Ghana":        1675,
    "Qatar":        1640,
    "Saudi Arabia": 1635,
    "Costa Rica":   1620,
    "Panama":       1600,
    "Jamaica":      1580,
    "New Zealand":  1500,
    "Uzbekistan":   1560,
}

# Host nations get a modest field advantage applied throughout the tournament.
HOSTS = {"USA", "Mexico", "Canada"}
HOST_ELO_BONUS = 35.0

# Goal model constants.
BASE_TOTAL_GOALS = 2.60   # expected total goals in an even match
ELO_PER_GOAL = 130.0      # Elo difference worth ~1 goal of expected supremacy
MAX_SUPREMACY = 3.2       # cap on expected goal difference

# Per-tournament "form" noise (Elo points, std dev). Each edition we draw a
# fresh strength for every team: injuries, peaking, chemistry, luck of form.
# This is what stops a pure-Elo model from being over-confident about the
# favourites and brings the spread in line with real betting markets.
FORM_NOISE_SD = 70.0


def base_effective_elo(team: str) -> float:
    elo = TEAMS_ELO[team]
    if team in HOSTS:
        elo += HOST_ELO_BONUS
    return elo


def draw_strengths(rng: random.Random) -> dict[str, float]:
    """One realised strength per team for a single tournament run."""
    return {t: base_effective_elo(t) + rng.gauss(0.0, FORM_NOISE_SD)
            for t in TEAMS_ELO}


def expected_lambdas(strength: dict[str, float],
                     team_a: str, team_b: str) -> tuple[float, float]:
    """Expected Poisson goal means for each side from the strength gap."""
    diff = strength[team_a] - strength[team_b]
    supremacy = max(-MAX_SUPREMACY, min(MAX_SUPREMACY, diff / ELO_PER_GOAL))
    lam_a = max(0.15, (BASE_TOTAL_GOALS + supremacy) / 2.0)
    lam_b = max(0.15, (BASE_TOTAL_GOALS - supremacy) / 2.0)
    return lam_a, lam_b


def poisson(lam: float, rng: random.Random) -> int:
    """Knuth's algorithm for sampling a Poisson random variable."""
    target = math.exp(-lam)
    k = 0
    p = 1.0
    while True:
        k += 1
        p *= rng.random()
        if p <= target:
            return k - 1


def play_match(strength: dict[str, float],
               team_a: str, team_b: str, rng: random.Random) -> tuple[int, int]:
    lam_a, lam_b = expected_lambdas(strength, team_a, team_b)
    return poisson(lam_a, rng), poisson(lam_b, rng)


def win_prob(strength: dict[str, float], team_a: str, team_b: str) -> float:
    """Probability team_a beats team_b (used for shootouts)."""
    diff = strength[team_a] - strength[team_b]
    return 1.0 / (1.0 + 10.0 ** (-diff / 400.0))


def play_knockout(strength: dict[str, float],
                  team_a: str, team_b: str, rng: random.Random) -> str:
    """Return the winner of a single-elimination match."""
    ga, gb = play_match(strength, team_a, team_b, rng)
    if ga > gb:
        return team_a
    if gb > ga:
        return team_b
    # Draw after 90' -> extra time / penalties, strength-weighted coin flip.
    return team_a if rng.random() < win_prob(strength, team_a, team_b) else team_b


# ---------------------------------------------------------------------------
# Draw
# ---------------------------------------------------------------------------
GROUP_NAMES = [chr(ord("A") + i) for i in range(12)]


def make_draw(rng: random.Random) -> dict[str, list[str]]:
    """Seed teams into 4 pots by Elo, then draw one per pot into 12 groups."""
    ranked = sorted(TEAMS_ELO, key=lambda t: base_effective_elo(t), reverse=True)
    pots = [ranked[i * 12:(i + 1) * 12] for i in range(4)]
    for pot in pots:
        rng.shuffle(pot)
    groups: dict[str, list[str]] = {g: [] for g in GROUP_NAMES}
    for pot in pots:
        for gi, team in enumerate(pot):
            groups[GROUP_NAMES[gi]].append(team)
    return groups


# ---------------------------------------------------------------------------
# Group stage
# ---------------------------------------------------------------------------
class Standing:
    __slots__ = ("team", "pts", "gd", "gf")

    def __init__(self, team: str):
        self.team = team
        self.pts = 0
        self.gd = 0
        self.gf = 0

    def add(self, scored: int, conceded: int) -> None:
        self.gf += scored
        self.gd += scored - conceded
        if scored > conceded:
            self.pts += 3
        elif scored == conceded:
            self.pts += 1


def sort_key(s: Standing, rng: random.Random) -> tuple:
    # Points, goal difference, goals for, then random tie-break.
    return (s.pts, s.gd, s.gf, rng.random())


def simulate_group(strength: dict[str, float],
                   teams: list[str], rng: random.Random) -> list[Standing]:
    table = {t: Standing(t) for t in teams}
    for i in range(len(teams)):
        for j in range(i + 1, len(teams)):
            a, b = teams[i], teams[j]
            ga, gb = play_match(strength, a, b, rng)
            table[a].add(ga, gb)
            table[b].add(gb, ga)
    return sorted(table.values(), key=lambda s: sort_key(s, rng), reverse=True)


def standard_bracket_order(n: int) -> list[int]:
    """Standard single-elimination seeding positions for n (a power of 2).

    Returns 1-based seed numbers in bracket-slot order so that the top two
    seeds can only meet in the final, seeds 1-4 only in the semis, etc.
    Adjacent pairs play each other in round one.
    """
    if n == 1:
        return [1]
    prev = standard_bracket_order(n // 2)
    out: list[int] = []
    for s in prev:
        out.append(s)
        out.append(n + 1 - s)
    return out


# ---------------------------------------------------------------------------
# Full tournament
# ---------------------------------------------------------------------------
def simulate_tournament(rng: random.Random) -> str:
    strength = draw_strengths(rng)
    groups = make_draw(rng)

    winners: list[str] = []
    runners_up: list[str] = []
    thirds: list[Standing] = []

    for g in GROUP_NAMES:
        standings = simulate_group(strength, groups[g], rng)
        winners.append(standings[0].team)
        runners_up.append(standings[1].team)
        thirds.append(standings[2])

    # 8 best third-placed teams.
    best_thirds = sorted(thirds, key=lambda s: sort_key(s, rng), reverse=True)[:8]
    third_teams = [s.team for s in best_thirds]

    # Seed the 32 qualifiers by realised strength and place them into a FIXED
    # bracket tree (group winners are the strongest pool, so they earn the top
    # seed lines and a softer R32 opponent). The tree is then fixed: no
    # re-seeding between rounds, so two giants can land in the same half and
    # knock each other out early - the main source of realistic upset variance.
    qualifiers = winners + runners_up + third_teams
    qualifiers.sort(key=lambda t: strength[t], reverse=True)
    order = standard_bracket_order(len(qualifiers))   # 1-based seed slots
    bracket = [qualifiers[s - 1] for s in order]

    # Snapshot which teams reach each stage. The bracket size when a round
    # begins names the teams that "reached" that stage: 8 = quarter-finalists,
    # 4 = semi-finalists, 2 = finalists, 1 = champion.
    reached: dict[str, list[str]] = {}
    stage_by_size = {8: "QF", 4: "SF", 2: "F"}
    while len(bracket) > 1:
        if len(bracket) in stage_by_size:
            reached[stage_by_size[len(bracket)]] = list(bracket)
        bracket = [play_knockout(strength, bracket[i], bracket[i + 1], rng)
                   for i in range(0, len(bracket), 2)]
    reached["W"] = list(bracket)   # champion
    return reached


# Stages tracked, from deepest to shallowest, with display labels.
STAGES = [("W", "Win %"), ("F", "Final %"), ("SF", "Semi %"), ("QF", "QF %")]


def run(num_sims: int, seed: int | None) -> dict[str, dict[str, int]]:
    """Return per-stage appearance counts: counts[stage][team]."""
    rng = random.Random(seed)
    counts: dict[str, dict[str, int]] = {s: defaultdict(int) for s, _ in STAGES}
    for _ in range(num_sims):
        reached = simulate_tournament(rng)
        for stage, _ in STAGES:
            for team in reached.get(stage, ()):
                counts[stage][team] += 1
    return counts


def main() -> None:
    parser = argparse.ArgumentParser(description="2026 World Cup Monte Carlo")
    parser.add_argument("-n", "--num-sims", type=int, default=100_000,
                        help="number of tournament simulations (default 100000)")
    parser.add_argument("-s", "--seed", type=int, default=42,
                        help="RNG seed for reproducibility (default 42)")
    parser.add_argument("-t", "--top", type=int, default=5,
                        help="how many teams to report (default 5)")
    args = parser.parse_args()

    print(f"Running {args.num_sims:,} simulations of the 2026 World Cup "
          f"(seed={args.seed})...\n")
    counts = run(args.num_sims, args.seed)
    total = args.num_sims

    # Rank by title probability.
    ranked = sorted(counts["W"].items(), key=lambda kv: kv[1], reverse=True)

    header = (f"{'Rank':<5}{'Team':<16}" +
              "".join(f"{label:>10}" for _, label in STAGES) +
              f"{'Title odds':>13}")
    print(header)
    print("-" * len(header))
    for i, (team, w) in enumerate(ranked[:args.top], start=1):
        cells = "".join(f"{100.0 * counts[s][team] / total:>9.2f}%"
                        for s, _ in STAGES)
        dec_odds = total / w if w else float("inf")
        print(f"{i:<5}{team:<16}{cells}{dec_odds:>12.1f}x")

    reported = sum(w for _, w in ranked[:args.top])
    print("-" * len(header))
    print(f"Top {args.top} combined title prob: {100.0 * reported / total:.1f}%  "
          f"| field of {len(TEAMS_ELO)} teams")


if __name__ == "__main__":
    main()
