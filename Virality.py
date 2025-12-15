"""
Viral post spread simulation (agent-based, NetLogo-inspired) in pure Python.

Model: SIR-style diffusion on a social network
- Susceptible: hasn't seen the post
- Exposed: has seen but not yet decided to share (optional delay)
- Infected (Sharer): actively sharing for a limited time
- Recovered: won't share anymore (lost interest)
- Removed (optional): "blocked/hidden" users who never see it

Key ideas you can tune:
- network structure (Erdos-Renyi / Barabasi-Albert / Watts-Strogatz)
- transmissibility (probability a sharer makes a neighbor see/share)
- attention/novelty decay over time
- sharing fatigue (infectious period)
- exposure delay (time from seeing to sharing)
- algorithmic boost (increasing reach temporarily)
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Tuple, Optional

import random
import math

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt


class State(Enum):
    SUSCEPTIBLE = 0  # hasn't seen
    EXPOSED = 1      # has seen, may share after delay
    SHARER = 2       # currently sharing
    RECOVERED = 3    # won't share anymore


@dataclass
class Params:
    # Network
    n: int = 3000
    network_type: str = "ba"  # "er", "ba", "ws"
    er_p: float = 0.0025
    ba_m: int = 3
    ws_k: int = 10
    ws_p: float = 0.10

    # Seed & initial conditions
    rng_seed: int = 42
    initial_sharers: int = 5

    # Spread mechanics
    base_exposure_p: float = 0.08  # per edge per tick: sharer -> neighbor becomes exposed
    base_share_p: float = 0.35     # per tick: exposed -> becomes sharer
    exposure_delay_mean: float = 0.0  # 0 = immediate eligibility to share
    exposure_delay_std: float = 0.0   # used if mean > 0

    # Attention dynamics
    novelty_half_life: float = 60.0  # ticks; higher = slower decay
    algorithm_boost_start: int = 10   # ticks; set to None to disable
    algorithm_boost_end: int = 40
    algorithm_boost_multiplier: float = 1.8

    # Sharing duration / fatigue
    infectious_period_mean: float = 8.0  # ticks sharer stays active
    infectious_period_std: float = 2.0

    # Simulation controls
    max_ticks: int = 250
    stop_when_no_sharers: bool = True


class ViralSpreadSim:
    def __init__(self, params: Params):
        self.p = params
        self.rng = random.Random(self.p.rng_seed)
        np.random.seed(self.p.rng_seed)

        self.G = self._build_network()
        self.state: Dict[int, State] = {u: State.SUSCEPTIBLE for u in self.G.nodes()}

        # Per-node timers
        self.exposure_delay: Dict[int, int] = {u: 0 for u in self.G.nodes()}
        self.sharer_time_left: Dict[int, int] = {u: 0 for u in self.G.nodes()}

        self.t = 0
        self.history: List[Tuple[int, int, int, int]] = []  # (S,E,I,R)

        self._seed_initial_sharers()

    def _build_network(self) -> nx.Graph:
        n = self.p.n
        nt = self.p.network_type.lower()

        if nt == "er":
            return nx.erdos_renyi_graph(n=n, p=self.p.er_p, seed=self.p.rng_seed)
        if nt == "ba":
            return nx.barabasi_albert_graph(n=n, m=self.p.ba_m, seed=self.p.rng_seed)
        if nt == "ws":
            return nx.watts_strogatz_graph(n=n, k=self.p.ws_k, p=self.p.ws_p, seed=self.p.rng_seed)

        raise ValueError(f"Unknown network_type='{self.p.network_type}'. Use 'er', 'ba', or 'ws'.")

    def _sample_nonnegative_int(self, mean: float, std: float, minimum: int = 0) -> int:
        if mean <= 0:
            return minimum
        if std <= 0:
            return max(minimum, int(round(mean)))
        x = int(round(self.rng.gauss(mean, std)))
        return max(minimum, x)

    def _seed_initial_sharers(self) -> None:
        candidates = list(self.G.nodes())
        self.rng.shuffle(candidates)
        seeds = candidates[: self.p.initial_sharers]

        for u in seeds:
            self.state[u] = State.SHARER
            self.sharer_time_left[u] = self._sample_nonnegative_int(
                self.p.infectious_period_mean, self.p.infectious_period_std, minimum=1
            )

    def _novelty_multiplier(self, t: int) -> float:
        """
        Decays from 1.0 downward with a half-life.
        multiplier(t) = 0.5^(t / half_life)
        """
        hl = self.p.novelty_half_life
        if hl <= 0:
            return 1.0
        return 0.5 ** (t / hl)

    def _algo_boost_multiplier(self, t: int) -> float:
        if self.p.algorithm_boost_start is None:
            return 1.0
        if self.p.algorithm_boost_start <= t <= self.p.algorithm_boost_end:
            return self.p.algorithm_boost_multiplier
        return 1.0

    def _effective_exposure_p(self, t: int) -> float:
        p = self.p.base_exposure_p
        p *= self._novelty_multiplier(t)
        p *= self._algo_boost_multiplier(t)
        return min(1.0, max(0.0, p))

    def _effective_share_p(self, t: int) -> float:
        p = self.p.base_share_p
        p *= self._novelty_multiplier(t)
        p *= self._algo_boost_multiplier(t)
        return min(1.0, max(0.0, p))

    def step(self) -> None:
        """
        One tick:
        1) Sharers expose neighbors with probability p_expose
        2) Exposed become sharers with probability p_share (if delay expired)
        3) Sharers count down infectious period; then recover
        """
        t = self.t
        p_expose = self._effective_exposure_p(t)
        p_share = self._effective_share_p(t)

        sharers = [u for u, s in self.state.items() if s == State.SHARER]
        newly_exposed: List[int] = []

        # 1) Exposure
        for u in sharers:
            for v in self.G.neighbors(u):
                if self.state[v] == State.SUSCEPTIBLE:
                    if self.rng.random() < p_expose:
                        newly_exposed.append(v)

        # Apply exposures (dedupe)
        for v in set(newly_exposed):
            self.state[v] = State.EXPOSED
            self.exposure_delay[v] = self._sample_nonnegative_int(
                self.p.exposure_delay_mean, self.p.exposure_delay_std, minimum=0
            )

        # 2) EXPOSED -> SHARER
        exposed = [u for u, s in self.state.items() if s == State.EXPOSED]
        for u in exposed:
            if self.exposure_delay[u] > 0:
                self.exposure_delay[u] -= 1
                continue
            if self.rng.random() < p_share:
                self.state[u] = State.SHARER
                self.sharer_time_left[u] = self._sample_nonnegative_int(
                    self.p.infectious_period_mean, self.p.infectious_period_std, minimum=1
                )

        # 3) SHARER countdown -> RECOVERED
        sharers = [u for u, s in self.state.items() if s == State.SHARER]
        for u in sharers:
            self.sharer_time_left[u] -= 1
            if self.sharer_time_left[u] <= 0:
                self.state[u] = State.RECOVERED

        self._record()
        self.t += 1

    def _record(self) -> None:
        s = sum(1 for v in self.state.values() if v == State.SUSCEPTIBLE)
        e = sum(1 for v in self.state.values() if v == State.EXPOSED)
        i = sum(1 for v in self.state.values() if v == State.SHARER)
        r = sum(1 for v in self.state.values() if v == State.RECOVERED)
        self.history.append((s, e, i, r))

    def run(self) -> None:
        self._record()
        for _ in range(self.p.max_ticks):
            if self.p.stop_when_no_sharers:
                if sum(1 for v in self.state.values() if v == State.SHARER) == 0:
                    break
            self.step()

    def get_history_arrays(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        arr = np.array(self.history, dtype=int)
        return arr[:, 0], arr[:, 1], arr[:, 2], arr[:, 3]

    def plot(self, title: Optional[str] = None) -> None:
        S, E, I, R = self.get_history_arrays()
        x = np.arange(len(S))

        plt.figure()
        plt.plot(x, S, label="Susceptible (unseen)")
        plt.plot(x, E, label="Exposed (seen)")
        plt.plot(x, I, label="Sharers (active)")
        plt.plot(x, R, label="Recovered (won't share)")

        plt.xlabel("Tick")
        plt.ylabel("Count of users")
        plt.legend()
        plt.grid(True)

        if title is None:
            title = f"Viral Spread Simulation ({self.p.network_type.upper()} network, n={self.p.n})"
        plt.title(title)
        plt.show()


def main():
    params = Params(
        n=3000,
        network_type="ba",   # try: "er", "ba", "ws"
        ba_m=3,

        initial_sharers=5,

        base_exposure_p=0.08,
        base_share_p=0.35,

        exposure_delay_mean=1.0,   # try 0 for instant
        exposure_delay_std=1.0,

        novelty_half_life=60.0,

        algorithm_boost_start=10,
        algorithm_boost_end=40,
        algorithm_boost_multiplier=1.8,

        infectious_period_mean=8.0,
        infectious_period_std=2.0,

        max_ticks=250,
        stop_when_no_sharers=True,
        rng_seed=42,
    )

    sim = ViralSpreadSim(params)
    sim.run()
    sim.plot()


if __name__ == "__main__":
    main()