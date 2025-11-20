#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Path Simulator (cells=0.1m, world 4m x 10m) + Plot
- Radar at (0,0)
- Angle: degrees in [-90, 90], measured from +y axis (left negative, right positive)
- Moving targets:
  A: front loop (never occluded)
  B: far loop (partially occluded behind the blockage)
- One static blockage (axis-aligned rectangle); finite width
- One static target (placed visible; not occluded)
- dt = 0.1 s, record once per time slot

Outputs:
  1) targets_flat.csv
  2) targets_timeslot.csv
  3) blockage_timeslot.csv
  4) blockage_rect.csv, blockage_poly.csv
  5) scene_overview.png   <-- NEW
"""

import math
from dataclasses import dataclass
from typing import Tuple, List

import numpy as np
import pandas as pd
import csv
from pathlib import Path

# --- plotting ---
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

# ------------------------- CONFIG -------------------------
# 脚本目录：/home/haocheng/O-JRC/examples/RL_Simulator_Control
SCRIPT_DIR = Path(__file__).resolve().parent
# 数据目录：/home/haocheng/O-JRC/examples/RL_ResourceAllocation_Data
OUTPUT_DIR = (SCRIPT_DIR.parent / "RL_ResourceAllocation_Data").resolve()
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CELL_SIZE_M = 0.1          # 10 cm grid
DT_S        = 0.1          # seconds per time slot
DURATION_S  = 60.0         # total duration (e.g., 60s)
NUM_SLOTS   = int(round(DURATION_S / DT_S))

# World (meters)
WORLD_XMIN, WORLD_XMAX = -4.0, +4.0   # width 8 m
WORLD_YMIN, WORLD_YMAX =  0.0, +10.0  # length 10 m

# Radar
RADAR_X, RADAR_Y = 0.0, 0.0

# Blockage rectangle (meters)
# Keep ymin/ymax internally for LOS; only xmin/xmax are output per timeslot
BLOCKAGE_XMIN, BLOCKAGE_XMAX = -0.5, +0.5
BLOCKAGE_YMIN, BLOCKAGE_YMAX =  5.5,  6.0   # ← 你当前版本的高度：0.5 m

# Moving target A (front; never occluded)
A_CENTER = (0.0, 3.0)   # center of ellipse
A_A = 1.1               # ellipse x-radius
A_B = 0.6               # ellipse y-radius
A_VAVG = 0.1            # average speed m/s
A_WOBBLE_AMP = 0.10     # small vertical wobble
A_JITTER_STD = 0.20     # speed jitter level

# Moving target B (far; sometimes occluded)
B_CENTER = (0.0, 9.0)
B_A = 3.0
B_B = 0.1
B_VAVG = 1.5
B_WOBBLE_AMP = 0.15
B_JITTER_STD = 0.30

# Static target (guaranteed visible by placement)
STATIC_TID = 101
STATIC_POS = (-2.5, 1.0)  # y=1 m, 不会被上方遮挡体挡住

RNG_SEED = 20250812  # reproducible

# ------------------------- GEOMETRY HELPERS -------------------------
def liang_barsky_segment_intersects_rect(p0: Tuple[float, float],
                                         p1: Tuple[float, float],
                                         rect: Tuple[float, float, float, float]) -> bool:
    (xmin, xmax, ymin, ymax) = rect
    x0, y0 = p0
    x1, y1 = p1
    dx, dy = x1 - x0, y1 - y0

    p = [-dx, dx, -dy, dy]
    q = [x0 - xmin, xmax - x0, y0 - ymin, ymax - y0]

    u1, u2 = 0.0, 1.0
    for pi, qi in zip(p, q):
        if pi == 0:
            if qi < 0:
                return False
            continue
        r = qi / pi
        if pi < 0:
            if r > u2: return False
            if r > u1: u1 = r
        else:
            if r < u1: return False
            if r < u2: u2 = r
    return u1 <= u2 and (0.0 <= u1 <= 1.0 or 0.0 <= u2 <= 1.0)

def is_occluded_by_blockage(x: float, y: float) -> bool:
    rect = (BLOCKAGE_XMIN, BLOCKAGE_XMAX, BLOCKAGE_YMIN, BLOCKAGE_YMAX)
    if BLOCKAGE_XMIN <= x <= BLOCKAGE_XMAX and BLOCKAGE_YMIN <= y <= BLOCKAGE_YMAX:
        return True
    return liang_barsky_segment_intersects_rect((RADAR_X, RADAR_Y), (x, y), rect)

def pol2_range_angle(x: float, y: float) -> Tuple[float, float]:
    r = math.hypot(x - RADAR_X, y - RADAR_Y)
    ang_deg = math.degrees(math.atan2(x - RADAR_X, y - RADAR_Y))
    return r, ang_deg

def ellipse_perimeter_ramanujan(a: float, b: float) -> float:
    h = ((a - b) ** 2) / ((a + b) ** 2)
    return math.pi * (a + b) * (1 + (3 * h) / (10 + math.sqrt(4 - 3 * h)))

def make_theta_increments(num_steps: int, base_delta: float,
                          jitter_std: float, rng: np.random.Generator) -> np.ndarray:
    noise = rng.normal(0.0, jitter_std, size=num_steps)
    kernel_len = max(5, int(0.05 * num_steps))
    kernel = np.ones(kernel_len) / kernel_len
    smooth = np.convolve(noise, kernel, mode="same")
    smooth -= smooth.mean()
    inc = base_delta * (1.0 + smooth)
    min_allowed = 0.2 * base_delta
    inc = np.clip(inc, min_allowed, None)
    inc *= (num_steps * base_delta) / inc.sum()
    return inc

@dataclass
class MovingTarget:
    tid: int
    center: Tuple[float, float]
    a: float
    b: float
    v_avg: float
    wobble_amp: float
    jitter_std: float
    theta0: float

    def plan_motion(self, dt: float, num_slots: int, rng: np.random.Generator):
        L = ellipse_perimeter_ramanujan(self.a, self.b)
        steps_per_lap = max(60, int(round(L / (self.v_avg * dt))))
        base_delta = 2 * math.pi / steps_per_lap
        laps_needed = math.ceil(num_slots / steps_per_lap)

        inc_all: List[np.ndarray] = []
        for _ in range(laps_needed):
            inc = make_theta_increments(steps_per_lap, base_delta, self.jitter_std, rng)
            inc_all.append(inc)
        inc_full = np.concatenate(inc_all)[:num_slots]

        theta = np.cumsum(np.concatenate(([self.theta0], inc_full)))[:-1]
        cx, cy = self.center
        x = cx + self.a * np.cos(theta)
        y = cy + self.b * np.sin(theta) + self.wobble_amp * np.sin(3.0 * theta)

        x = np.clip(x, WORLD_XMIN, WORLD_XMAX)
        y = np.clip(y, WORLD_YMIN, WORLD_YMAX)
        return x, y

def simulate_and_save():
    rng = np.random.default_rng(RNG_SEED)

    # Build moving targets
    mt_a = MovingTarget(
        tid=1, center=A_CENTER, a=A_A, b=A_B, v_avg=A_VAVG,
        wobble_amp=A_WOBBLE_AMP, jitter_std=A_JITTER_STD,
        theta0=rng.uniform(0, 2 * math.pi)
    )
    mt_b = MovingTarget(
        tid=2, center=B_CENTER, a=B_A, b=B_B, v_avg=B_VAVG,
        wobble_amp=B_WOBBLE_AMP, jitter_std=B_JITTER_STD,
        theta0=rng.uniform(0, 2 * math.pi)
    )

    xa, ya = mt_a.plan_motion(DT_S, NUM_SLOTS, rng)
    xb, yb = mt_b.plan_motion(DT_S, NUM_SLOTS, rng)

    # --- Blockage discretization: front face (nearest y-row), cell centers ---
    blk_width = BLOCKAGE_XMAX - BLOCKAGE_XMIN
    n_blk_cells = max(1, int(round(blk_width / CELL_SIZE_M)))
    blk_x_centers = BLOCKAGE_XMIN + (CELL_SIZE_M / 2.0) + np.arange(n_blk_cells) * CELL_SIZE_M
    blk_y_front = BLOCKAGE_YMIN + (CELL_SIZE_M / 2.0)
    blk_y_centers = np.full_like(blk_x_centers, blk_y_front, dtype=float)

    blk_ranges = []
    blk_angles = []
    for xc, yc in zip(blk_x_centers, blk_y_centers):
        r, a = pol2_range_angle(xc, yc)
        blk_ranges.append(f"{r:.3f}")
        blk_angles.append(f"{a:.2f}")
    blk_ranges_str = ",".join(blk_ranges)
    blk_angles_str = ",".join(blk_angles)

    # --- Simulation loop ---
    flat_rows: List[dict] = []
    ts_rows: List[dict] = []

    for t in range(NUM_SLOTS):
        slot_ids: List[str] = []
        slot_xs:  List[str] = []
        slot_ys:  List[str] = []
        slot_rs:  List[str] = []
        slot_as:  List[str] = []

        # Moving A
        r_a, ang_a = pol2_range_angle(xa[t], ya[t])
        if not is_occluded_by_blockage(xa[t], ya[t]):
            flat_rows.append({
                "time_slot": t, "target_id": 1, "type": "moving",
                "x_m": xa[t], "y_m": ya[t], "range_m": r_a, "angle_deg": ang_a
            })
            slot_ids.append("1")
            slot_xs.append(f"{xa[t]:.3f}")
            slot_ys.append(f"{ya[t]:.3f}")
            slot_rs.append(f"{r_a:.3f}")
            slot_as.append(f"{ang_a:.2f}")

        # Moving B
        r_b, ang_b = pol2_range_angle(xb[t], yb[t])
        if not is_occluded_by_blockage(xb[t], yb[t]):
            flat_rows.append({
                "time_slot": t, "target_id": 2, "type": "moving",
                "x_m": xb[t], "y_m": yb[t], "range_m": r_b, "angle_deg": ang_b
            })
            slot_ids.append("2")
            slot_xs.append(f"{xb[t]:.3f}")
            slot_ys.append(f"{yb[t]:.3f}")
            slot_rs.append(f"{r_b:.3f}")
            slot_as.append(f"{ang_b:.2f}")

        # Static target (always check)
        r_s, ang_s = pol2_range_angle(STATIC_POS[0], STATIC_POS[1])
        if not is_occluded_by_blockage(STATIC_POS[0], STATIC_POS[1]):
            flat_rows.append({
                "time_slot": t, "target_id": STATIC_TID, "type": "static",
                "x_m": STATIC_POS[0], "y_m": STATIC_POS[1], "range_m": r_s, "angle_deg": ang_s
            })
            slot_ids.append(str(STATIC_TID))
            slot_xs.append(f"{STATIC_POS[0]:.3f}")
            slot_ys.append(f"{STATIC_POS[1]:.3f}")
            slot_rs.append(f"{r_s:.3f}")
            slot_as.append(f"{ang_s:.2f}")

        # Aggregate per-time-slot strings
        ids_str    = ",".join(slot_ids)
        xs_str     = ",".join(slot_xs)
        ys_str     = ",".join(slot_ys)
        ranges_str = ",".join(slot_rs) if slot_rs else ""
        angles_str = ",".join(slot_as) if slot_as else ""

        # Append blockage front-face (range/angle only)
        if ranges_str:
            ranges_str = ranges_str + "," + blk_ranges_str
            angles_str = angles_str + "," + blk_angles_str
        else:
            ranges_str = blk_ranges_str
            angles_str = blk_angles_str

        ts_rows.append({
            "time_slot": t,
            "n_visible": len(slot_ids),
            "ids": ids_str,          # ONLY target ids (no blk*)
            "x_m": xs_str,
            "y_m": ys_str,
            "range_m": ranges_str,   # targets (visible) + blockage cells
            "angle_deg": angles_str, # targets (visible) + blockage cells
            "blockage_xmin": BLOCKAGE_XMIN,
            "blockage_xmax": BLOCKAGE_XMAX,
            "n_blockage_cells": n_blk_cells,
            "dt_s": DT_S
        })

    # --- Save CSVs ---
    flat_path   = OUTPUT_DIR / "targets_flat.csv"
    ts_path     = OUTPUT_DIR / "targets_timeslot.csv"
    blk_ts_path = OUTPUT_DIR / "blockage_timeslot.csv"

    pd.DataFrame(flat_rows).to_csv(flat_path, index=False, quoting=csv.QUOTE_MINIMAL)
    pd.DataFrame(ts_rows).to_csv(ts_path, index=False, quoting=csv.QUOTE_MINIMAL)

    # Blockage-only single-row timeslot CSV
    blk_row = {
        "time_slot": 0,
        "n_visible": 0,
        "ids": "",
        "x_m": "",
        "y_m": "",
        "range_m": blk_ranges_str,
        "angle_deg": blk_angles_str,
        "blockage_xmin": BLOCKAGE_XMIN,
        "blockage_xmax": BLOCKAGE_XMAX,
        "n_blockage_cells": n_blk_cells,
        "dt_s": DT_S
    }
    pd.DataFrame([blk_row]).to_csv(blk_ts_path, index=False, quoting=csv.QUOTE_MINIMAL)

    # Geometry helper CSVs
    rect_df = pd.DataFrame([{
        "xmin": BLOCKAGE_XMIN, "xmax": BLOCKAGE_XMAX,
        "ymin": BLOCKAGE_YMIN, "ymax": BLOCKAGE_YMAX,
        "width_m": (BLOCKAGE_XMAX - BLOCKAGE_XMIN),
        "height_m": (BLOCKAGE_YMAX - BLOCKAGE_YMIN),
        "center_x": (BLOCKAGE_XMIN + BLOCKAGE_XMAX)/2.0,
        "center_y": (BLOCKAGE_YMIN + BLOCKAGE_YMAX)/2.0
    }])
    rect_df.to_csv(OUTPUT_DIR / "blockage_rect.csv", index=False, quoting=csv.QUOTE_MINIMAL)

    poly_df = pd.DataFrame([
        {"vertex_idx": 0, "x_m": BLOCKAGE_XMIN, "y_m": BLOCKAGE_YMIN},
        {"vertex_idx": 1, "x_m": BLOCKAGE_XMAX, "y_m": BLOCKAGE_YMIN},
        {"vertex_idx": 2, "x_m": BLOCKAGE_XMAX, "y_m": BLOCKAGE_YMAX},
        {"vertex_idx": 3, "x_m": BLOCKAGE_XMIN, "y_m": BLOCKAGE_YMAX},
    ])
    poly_df.to_csv(OUTPUT_DIR / "blockage_poly.csv", index=False, quoting=csv.QUOTE_MINIMAL)

    # --- Plot scene overview ---
    fig, ax = plt.subplots(figsize=(12, 10))
    ax.set_title("Scene Overview (Radar @ (0,0))", fontsize=12)

    # World bounds & grid
    ax.set_xlim(WORLD_XMIN, WORLD_XMAX)
    ax.set_ylim(WORLD_YMIN, WORLD_YMAX)
    # ax.set_aspect("equal", adjustable="box")
    ax.set_aspect("auto")
    ax.grid(True, which="both", alpha=0.15)

    # Blockage rectangle
    rect = Rectangle((BLOCKAGE_XMIN, BLOCKAGE_YMIN),
                     BLOCKAGE_XMAX - BLOCKAGE_XMIN,
                     BLOCKAGE_YMAX - BLOCKAGE_YMIN,
                     facecolor="0.7", edgecolor="0.3", alpha=0.6, label="Blockage")
    ax.add_patch(rect)

    # Radar station
    ax.scatter([RADAR_X], [RADAR_Y], marker="*", color="red", s=140, label="Radar", zorder=5)

    # Static target
    ax.scatter([STATIC_POS[0]], [STATIC_POS[1]], marker="^", color="green", s=80, label=f"Static {STATIC_TID}", zorder=5)

    # Moving trajectories (full paths)
    ax.plot(xa, ya, linewidth=1.6, label="Moving A (path)")
    ax.plot(xb, yb, linewidth=1.6, label="Moving B (path)")

    # Start & end markers for moving targets
    ax.scatter([xa[0]], [ya[0]], marker="o", s=50, facecolors="none", edgecolors="C0", label="A start")
    ax.scatter([xa[-1]], [ya[-1]], marker="o", s=50, facecolors="C0", edgecolors="C0", label="A end")

    ax.scatter([xb[0]], [yb[0]], marker="s", s=50, facecolors="none", edgecolors="C1", label="B start")
    ax.scatter([xb[-1]], [yb[-1]], marker="s", s=50, facecolors="C1", edgecolors="C1", label="B end")

    ax.legend(loc="best", ncol=1, fontsize=9, framealpha=0.9)
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")

    out_fig = OUTPUT_DIR / "scene_overview.png"
    plt.savefig(out_fig, dpi=200, bbox_inches="tight")
    plt.close(fig)

    print("Written:")
    print(f"  {flat_path}")
    print(f"  {ts_path}")
    print(f"  {blk_ts_path}")
    print(f"  {OUTPUT_DIR / 'blockage_rect.csv'}")
    print(f"  {OUTPUT_DIR / 'blockage_poly.csv'}")
    print(f"  {out_fig}")

if __name__ == "__main__":
    simulate_and_save()
