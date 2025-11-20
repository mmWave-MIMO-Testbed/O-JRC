#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Path Simulator (cells=0.1m, world 4m x 10m) + Plot — Target B moves HORIZONTALLY, keep static target
- Radar at (0,0)
- Angle: degrees in [-90, 90], measured from +y axis (left negative, right positive)
- Moving target B: moves along a straight **horizontal** line at constant y, **behind the blockage**
- Static target: retained and visible by placement (not occluded)
- One static blockage (axis-aligned rectangle); finite width
- dt = 0.1 s, record once per time slot

Outputs (same filenames):
  1) targets_flat.csv
  2) targets_timeslot.csv
  3) blockage_timeslot.csv
  4) blockage_rect.csv, blockage_poly.csv
  5) scene_overview.png

Notes:
- To guarantee B is **always occluded** by the blockage while moving horizontally, we constrain its x-range to
  |x| ≤ BLOCKAGE_XMAX * (B_Y_CONST / BLOCKAGE_YMIN) * margin. With B_Y_CONST > BLOCKAGE_YMAX, the LoS from radar to B
  necessarily crosses the rectangle y ∈ [BLOCKAGE_YMIN, BLOCKAGE_YMAX]. Adjust B_Y_CONST or the margin to change behavior.
- If you want B to sweep a **wider** horizontal range (possibly partially visible), set B_X_MIN/MAX manually and/or set
  ALWAYS_OCCLUDED = False and widen the range.
"""

import math
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
DURATION_S  = 40.0         # total duration (e.g., 40s)
NUM_SLOTS   = int(round(DURATION_S / DT_S))

# World (meters)
WORLD_XMIN, WORLD_XMAX = -4.0, +4.0   # width 8 m
WORLD_YMIN, WORLD_YMAX =  0.0, +10.0  # length 10 m

# Radar
RADAR_X, RADAR_Y = 0.0, 0.0

# Blockage rectangle (meters)
BLOCKAGE_XMIN, BLOCKAGE_XMAX = -0.4, +0.4
BLOCKAGE_YMIN, BLOCKAGE_YMAX =  4.5,  5.0   # 高度：0.5 m

# --------------------- Static target (kept) ---------------------
STATIC_TID = 101
STATIC_POS = (-1.5, 2.0)  # y=2 m, 不会被上方遮挡体挡住

# --------------------- Target B: horizontal line behind blockage ---------------------
# Constant y chosen > BLOCKAGE_YMAX so B stays "behind" the blockage from radar's perspective
B_Y_CONST = 7.0
B_SPEED   = 0.1   # m/s, horizontal speed (bounce motion)

# Always-occluded design (derive safe horizontal extent)
ALWAYS_OCCLUDED = False
MARGIN = 0.98  # safety factor
if ALWAYS_OCCLUDED:
    # ensure the LoS crosses the rectangle for any x in [B_X_MIN, B_X_MAX]
    x_abs_max = BLOCKAGE_XMAX * (B_Y_CONST / BLOCKAGE_YMIN) * MARGIN
    B_X_MIN, B_X_MAX = -x_abs_max, x_abs_max
else:
    # choose your own sweep (may be partially visible)
    B_X_MIN, B_X_MAX = -2.0, 2.0

# clip to world
B_X_MIN = max(B_X_MIN, WORLD_XMIN)
B_X_MAX = min(B_X_MAX, WORLD_XMAX)

# If desired, record occluded ground truth as well
LOG_OCCLUDED = False

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
    # inside the rectangle
    if BLOCKAGE_XMIN <= x <= BLOCKAGE_XMAX and BLOCKAGE_YMIN <= y <= BLOCKAGE_YMAX:
        return True
    # LOS test from radar to (x, y)
    return liang_barsky_segment_intersects_rect((RADAR_X, RADAR_Y), (x, y), rect)

def pol2_range_angle(x: float, y: float) -> Tuple[float, float]:
    r = math.hypot(x - RADAR_X, y - RADAR_Y)
    ang_deg = math.degrees(math.atan2(x - RADAR_X, y - RADAR_Y))
    return r, ang_deg

# --------------------- Motion planning: horizontal line ---------------------
def plan_straight_line_horizontal(x_min: float, x_max: float, y_const: float,
                                  speed: float, dt: float, num_slots: int):
    """Bounce motion along a horizontal straight line y = const between x_min and x_max."""
    assert x_max > x_min, "x_max must be greater than x_min"
    assert WORLD_YMIN <= y_const <= WORLD_YMAX, "y_const outside world bounds"

    step = speed * dt
    x = np.empty(num_slots, dtype=float)
    y = np.full(num_slots, float(y_const))

    # start at x_min, move right first
    cur = x_min
    direction = 1.0  # +1 right, -1 left
    for t in range(num_slots):
        x[t] = cur
        nxt = cur + direction * step
        if nxt > x_max:
            excess = nxt - x_max
            cur = x_max - excess
            direction = -1.0
        elif nxt < x_min:
            excess = x_min - nxt
            cur = x_min + excess
            direction = 1.0
        else:
            cur = nxt

    # clamp to world bounds just in case
    y = np.clip(y, WORLD_YMIN, WORLD_YMAX)
    x = np.clip(x, WORLD_XMIN, WORLD_XMAX)
    return x, y

# --------------------------- SIMULATE ---------------------------
def simulate_and_save():
    # --- Target B motion (straight horizontal line behind blockage) ---
    xb, yb = plan_straight_line_horizontal(B_X_MIN, B_X_MAX, B_Y_CONST,
                                           B_SPEED, DT_S, NUM_SLOTS)

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

        # Moving B only
        r_b, ang_b = pol2_range_angle(xb[t], yb[t])
        vis_b = (not is_occluded_by_blockage(xb[t], yb[t]))

        if vis_b or LOG_OCCLUDED:
            flat_rows.append({
                "time_slot": t, "target_id": 2, "type": "moving",
                "x_m": xb[t], "y_m": yb[t], "range_m": r_b, "angle_deg": ang_b,
                **({"visible": int(vis_b)} if LOG_OCCLUDED else {})
            })
        if vis_b:
            slot_ids.append("2")
            slot_xs.append(f"{xb[t]:.3f}")
            slot_ys.append(f"{yb[t]:.3f}")
            slot_rs.append(f"{r_b:.3f}")
            slot_as.append(f"{ang_b:.2f}")

        # Static target (kept)
        r_s, ang_s = pol2_range_angle(STATIC_POS[0], STATIC_POS[1])
        vis_s = (not is_occluded_by_blockage(STATIC_POS[0], STATIC_POS[1]))
        if vis_s or LOG_OCCLUDED:
            flat_rows.append({
                "time_slot": t, "target_id": STATIC_TID, "type": "static",
                "x_m": STATIC_POS[0], "y_m": STATIC_POS[1], "range_m": r_s, "angle_deg": ang_s,
                **({"visible": int(vis_s)} if LOG_OCCLUDED else {})
            })
        if vis_s:
            slot_ids.append(str(STATIC_TID))
            slot_xs.append(f"{STATIC_POS[0]:.3f}")
            slot_ys.append(f"{STATIC_POS[1]:.3f}")
            slot_rs.append(f"{r_s:.3f}")
            slot_as.append(f"{ang_s:.2f}")

        # Aggregate per-time-slot strings (append blockage front-face always)
        ids_str    = ",".join(slot_ids)
        xs_str     = ",".join(slot_xs)
        ys_str     = ",".join(slot_ys)
        ranges_str = ",".join(slot_rs) if slot_rs else ""
        angles_str = ",".join(slot_as) if slot_as else ""

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
    ax.set_title("Scene Overview (Radar @ (0,0)) — B horizontal behind blockage; static kept", fontsize=12)

    # World bounds & grid
    ax.set_xlim(WORLD_XMIN, WORLD_XMAX)
    ax.set_ylim(WORLD_YMIN, WORLD_YMAX)
    ax.set_aspect("auto")
    ax.grid(True, which="both", alpha=0.15)

    # Blockage rectangle
    rect = Rectangle((BLOCKAGE_XMIN, BLOCKAGE_YMIN),
                     BLOCKAGE_XMAX - BLOCKAGE_XMIN,
                     BLOCKAGE_YMAX - BLOCKAGE_YMIN,
                     facecolor="0.7", edgecolor="0.3", alpha=0.6, label="Blockage")
    ax.add_patch(rect)

    # Radar station
    ax.scatter([RADAR_X], [RADAR_Y], marker="*", color="red", s=180, label="Radar", zorder=5)

    # Static target
    ax.scatter([STATIC_POS[0]], [STATIC_POS[1]], marker="^", color="green", s=140, label=f"Static {STATIC_TID}", zorder=5)

    # Moving B path (horizontal line)
    ax.plot(xb, yb, linewidth=1.6, label="Moving B (horizontal)")

    # Start & end markers for B
    ax.scatter([xb[0]], [yb[0]], marker="s", s=50, facecolors="none", edgecolors="C1", label="B start")
    ax.scatter([xb[-1]], [yb[-1]], marker="s", s=50, facecolors="C1", edgecolors="C1", label="B end")

    ax.legend(loc="best", ncol=1, fontsize=9, framealpha=0.9)
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")

    out_fig = OUTPUT_DIR / "scene_overview_simple_case.png"
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
