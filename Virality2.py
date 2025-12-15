"""
NetLogo-style *live* viral-spread simulator in pure Python (matplotlib animation + sliders).

What you get:
- A 2D "world" (like NetLogo patches) with moving agents (like turtles)
- States: Susceptible (unseen), Exposed (seen), Sharer (active), Recovered (won't share)
- Live animation (agents move, interact, spread)
- Interactive UI controls:
    - Sliders: exposure radius, exposure probability, share probability, infectious period, speed, initial sharers
    - Buttons: Reset, Pause/Resume
- A live time-series chart updating while the sim runs

Dependencies:
    pip install numpy matplotlib

Run:
    python live_viral_sim.py
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import Optional

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider, Button

import matplotlib
print("Matplotlib backend:", matplotlib.get_backend())


class State(IntEnum):
    UNAFFECTED = 0   # Green
    INITIAL = 1      # Blue (seed holders)
    SPREADER = 2     # Red (got it from others)
    RECOVERED = 3    # Gray

@dataclass
class Params:
    n: int = 800
    world_size: float = 100  # coordinates in [0, world_size)
    speed: float = 0.10         # movement step per tick
    exposure_radius: float = 2.0
    exposure_p: float = 0.22   # S -> E if near a sharer
    infectious_period: int = 90
    initial_sharers: int = 1
    max_history: int = 600     # points shown in chart


class ViralWorld:
    def __init__(self, params: Params, rng_seed: int = 42):
        self.p = params
        self.rng = np.random.default_rng(rng_seed)
        self.t = 0
        self.paused = False

        # Agent attributes
        self.x = self.rng.uniform(0, self.p.world_size, size=self.p.n)
        self.y = self.rng.uniform(0, self.p.world_size, size=self.p.n)

        self.state = np.full(self.p.n, State.UNAFFECTED, dtype=np.int8)
        self.time_left = np.zeros(self.p.n, dtype=np.int16)

        self._seed_initial_sharers(self.p.initial_sharers)

        # History for the chart
        self.hist_t = []
        self.hist_S = []
        self.hist_E = []
        self.hist_I = []
        self.hist_R = []
        self._record()

    def reset(self, params: Optional[Params] = None):
        if params is not None:
            self.p = params

        self.t = 0
        self.paused = False

        self.x = self.rng.uniform(0, self.p.world_size, size=self.p.n)
        self.y = self.rng.uniform(0, self.p.world_size, size=self.p.n)

        self.state.fill(State.UNAFFECTED)
        self.time_left.fill(0)

        self._seed_initial_sharers(self.p.initial_sharers)

        self.hist_t.clear()
        self.hist_S.clear()
        self.hist_E.clear()
        self.hist_I.clear()
        self.hist_R.clear()
        self._record()

    def _seed_initial_sharers(self, k: int):
        k = int(np.clip(k, 1, self.p.n))
        idx = self.rng.choice(self.p.n, size=k, replace=False)
        self.state[idx] = State.INITIAL
        self.time_left[idx] = self.p.infectious_period


    def _record(self):
        S = int(np.sum(self.state == State.UNAFFECTED))
        I0 = int(np.sum(self.state == State.INITIAL))
        I1 = int(np.sum(self.state == State.SPREADER))
        R = int(np.sum(self.state == State.RECOVERED))

        self.hist_t.append(self.t)
        self.hist_S.append(S)
        self.hist_E.append(I0)   # lineE = Initial (blue)
        self.hist_I.append(I1)   # lineI = Spreaders (red)
        self.hist_R.append(R)

        if len(self.hist_t) > self.p.max_history:
            self.hist_t = self.hist_t[-self.p.max_history:]
            self.hist_S = self.hist_S[-self.p.max_history:]
            self.hist_E = self.hist_E[-self.p.max_history:]
            self.hist_I = self.hist_I[-self.p.max_history:]
            self.hist_R = self.hist_R[-self.p.max_history:]
    def step(self):
        if self.paused:
            return

        # 1) Move: random walk with wrap-around (torus world like NetLogo)
        angles = self.rng.uniform(0, 2 * np.pi, size=self.p.n)
        dx = self.p.speed * np.cos(angles)
        dy = self.p.speed * np.sin(angles)

        self.x = (self.x + dx) % self.p.world_size
        self.y = (self.y + dy) % self.p.world_size

        # 2) Spread: Susceptible become Exposed if within radius of any Sharer
        sharers = np.where(
        (self.state == State.INITIAL) | (self.state == State.SPREADER))[0]
        if sharers.size > 0:
            S_idx = np.where(self.state == State.UNAFFECTED)[0]
            if S_idx.size > 0:
                # Compute distance to nearest sharer (vectorized in blocks to be memory-safe)
                radius2 = float(self.p.exposure_radius ** 2)

                # Blocked computation: for S nodes, test if any sharer within radius
                # Use broadcasting in blocks to avoid huge matrices
                block = 2000  # tune if needed
                exposed_now = []

                sx = self.x[sharers]
                sy = self.y[sharers]

                for start in range(0, S_idx.size, block):
                    chunk = S_idx[start : start + block]
                    cx = self.x[chunk][:, None]
                    cy = self.y[chunk][:, None]

                    # Torus distance: consider wrap-around
                    dx = np.abs(cx - sx[None, :])
                    dy = np.abs(cy - sy[None, :])

                    dx = np.minimum(dx, self.p.world_size - dx)
                    dy = np.minimum(dy, self.p.world_size - dy)

                    d2 = dx * dx + dy * dy
                    near_any = np.any(d2 <= radius2, axis=1)

                    if np.any(near_any):
                        candidates = chunk[near_any]
                        # apply probability
                        roll = self.rng.random(size=candidates.size)
                        to_expose = candidates[roll < self.p.exposure_p]
                        if to_expose.size:
                            exposed_now.append(to_expose)

                if exposed_now:
                    exposed_now = np.concatenate(exposed_now)
                    self.state[exposed_now] = State.SPREADER
                    self.time_left[exposed_now] = self.p.infectious_period

        # 4) Sharer countdown -> Recovered
        active = np.where((self.state == State.INITIAL) | (self.state == State.SPREADER))[0]
        if active.size > 0:
            self.time_left[active] -= 1
            done = active[self.time_left[active] <= 0]
            if done.size:
                self.state[done] = State.RECOVERED

        self.t += 1
        self._record()


def build_ui_and_run():
    params = Params()

    world = ViralWorld(params=params, rng_seed=42)

    # --- Figure layout ---
    fig = plt.figure()
    fig.canvas.manager.set_window_title("Live Viral Spread Simulator")
    gs = fig.add_gridspec(2, 2, height_ratios=[3, 1], width_ratios=[3, 2])

    ax_world = fig.add_subplot(gs[0, 0])
    ax_chart = fig.add_subplot(gs[1, 0])
    ax_controls = fig.add_subplot(gs[:, 1])
    ax_controls.axis("off")

    # World plot setup
    ax_world.set_title("World")
    ax_world.set_xlim(0, world.p.world_size)
    ax_world.set_ylim(0, world.p.world_size)
    ax_world.set_aspect("equal", adjustable="box")
    ax_world.grid(True)

    # Scatter (we'll update colors and positions)
    scat = ax_world.scatter(world.x, world.y, s=10)

    # Chart plot setup
    ax_chart.set_title("Counts over time")
    ax_chart.set_xlabel("Tick")
    ax_chart.set_ylabel("Count")
    (lineS,) = ax_chart.plot([], [], label="S")
    (lineE,) = ax_chart.plot([], [], label="Initial (blue)")
    (lineI,) = ax_chart.plot([], [], label="Spreaders (red)")
    (lineR,) = ax_chart.plot([], [], label="R")
    ax_chart.legend(loc="upper right")
    ax_chart.grid(True)

    # --- Controls: place sliders inside the right panel using inset axes ---
    def add_slider(y, label, vmin, vmax, vinit, valstep=None):
        ax = ax_controls.inset_axes([0.08, y, 0.84, 0.05])
        return Slider(ax=ax, label=label, valmin=vmin, valmax=vmax, valinit=vinit, valstep=valstep)

    def add_button(y, label):
        ax = ax_controls.inset_axes([0.08, y, 0.38, 0.06])
        return Button(ax=ax, label=label)

    # Sliders
    s_radius = add_slider(0.88, "Exposure radius", 0.5, 8.0, params.exposure_radius, valstep=0.1)
    s_expp   = add_slider(0.80, "Exposure P",      0.0, 1.0, params.exposure_p,      valstep=0.01)
    s_inf    = add_slider(0.64, "Infectious period", 1, 120, params.infectious_period, valstep=1)
    s_speed  = add_slider(0.56, "Speed",           0.0, 3.0, params.speed,           valstep=0.05)
    s_seedI  = add_slider(0.48, "Initial sharers", 1, 50,  params.initial_sharers,   valstep=1)

    # Buttons
    b_reset = add_button(0.36, "Reset")
    b_pause = add_button(0.28, "Pause/Resume")

    # Simple text readout
    ax_text = ax_controls.inset_axes([0.08, 0.05, 0.84, 0.18])
    ax_text.axis("off")
    status_text = ax_text.text(0.0, 0.75, "", fontsize=10)
    hint_text = ax_text.text(
        0.0,
        0.15,
        "Tip: Try BA-like virality by increasing radius slightly and raising exposure/share.",
        fontsize=9,
    )

    def apply_slider_params():
        world.p.exposure_radius = float(s_radius.val)
        world.p.exposure_p = float(s_expp.val)
        world.p.infectious_period = int(s_inf.val)
        world.p.speed = float(s_speed.val)
        world.p.initial_sharers = int(s_seedI.val)

    def on_reset(_event):
        apply_slider_params()
        world.reset(params=world.p)

    def on_pause(_event):
        world.paused = not world.paused

    b_reset.on_clicked(on_reset)
    b_pause.on_clicked(on_pause)

    def update(_frame):
        # Update params live (without resetting)
        apply_slider_params()

        world.step()

        # Update scatter positions + colors
        offsets = np.column_stack([world.x, world.y])
        scat.set_offsets(offsets)

        # Map states to colors
        colors = np.zeros((world.p.n, 4), dtype=float)

        colors[world.state == State.UNAFFECTED] = [0.2, 0.8, 0.2, 1.0]  # Green
        colors[world.state == State.INITIAL]    = [0.2, 0.4, 1.0, 1.0]  # Blue
        colors[world.state == State.SPREADER]   = [0.9, 0.2, 0.2, 1.0]  # Red
        colors[world.state == State.RECOVERED]  = [0.5, 0.5, 0.5, 0.5]  # Gray (faded)
        scat.set_facecolors(colors)
        scat.set_edgecolors(colors)


        # Update chart
        t = np.array(world.hist_t)
        lineS.set_data(t, np.array(world.hist_S))
        lineE.set_data(t, np.array(world.hist_E))
        lineI.set_data(t, np.array(world.hist_I))
        lineR.set_data(t, np.array(world.hist_R))

        ax_chart.set_xlim(t.min() if t.size else 0, (t.max() if t.size else 1) + 1)
        ymax = max(max(world.hist_S), max(world.hist_E), max(world.hist_I), max(world.hist_R), 1)
        ax_chart.set_ylim(0, ymax * 1.05)

        # Status text
        S = world.hist_S[-1]
        E = world.hist_E[-1]
        I = world.hist_I[-1]
        R = world.hist_R[-1]
        status_text.set_text(
            f"Tick: {world.t}\n"
            f"S: {S}  E: {E}  I: {I}  R: {R}\n"
            f"Paused: {world.paused}"
        )

        return scat, lineS, lineE, lineI, lineR, status_text

    ani = FuncAnimation(fig, update, interval=100, blit=False, cache_frame_data=False)
    fig._ani = ani
    plt.show()


if __name__ == "__main__":
    build_ui_and_run()