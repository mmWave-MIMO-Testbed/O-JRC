#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Windowed-average SNR (live, 0.1s/step), two users (101, 2), black background.

Rules:
- Consider only rows with beam_id != 0
- Drop SNR == -10 (packet loss)
- Adjust SNR by subtracting 10 dB before averaging
- X axis: time slot (sorted)
- For each user at each slot:
    * If the user has valid sample(s) in this slot: use the slot-mean SNR (after -10).
    * If not selected in this slot: append 0 for this slot.
- Window mean at each step:
    * Mean over NON-ZERO entries in the window.
    * If all are zeros -> output -20 dB for that point.
- Two continuous lines: User 101 (red), User 2 (lime).
"""

import time
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ========== Config ==========
CSV_PATH   = Path("/home/haocheng/O-JRC/examples/RL_ResourceAllocation_Data") / "RL_log.csv"
WINDOW     = 20                  # 滑动窗口大小（slots）
# DT_SEC     = 0.2                 # 逐帧播放间隔（秒）
LINE_WIDTH = 3.0
COL_101    = "red"
COL_2      = "lime"
# ============================

# ---------- Load ----------
df = pd.read_csv(CSV_PATH)

# 列名兼容
cols = {c.lower().strip(): c for c in df.columns}
def pick(*names):
    for n in names:
        if n in cols:
            return cols[n]
    raise KeyError(f"缺少列（候选其一即可）：{names}")

col_epoch = pick("epoch")  # 仅用于排序时参照（不参与分组）
col_slot  = pick("slot")
col_user  = pick("user_id", "userid", "user")
col_beam  = pick("chosen_beam_id", "beam_id", "beam", "chosen_beam")
col_snr   = pick("snr", "data_snr")

# 类型化
df[col_slot] = pd.to_numeric(df[col_slot], errors="coerce").astype("Int64")
df[col_user] = pd.to_numeric(df[col_user], errors="coerce").astype("Int64")
df[col_beam] = pd.to_numeric(df[col_beam], errors="coerce").astype("Int64")
df[col_snr]  = pd.to_numeric(df[col_snr],  errors="coerce")

# 仅统计 beam!=0、SNR 有效、丢包剔除、两位用户
mask_valid = df[col_slot].notna() & df[col_user].notna() & df[col_beam].notna() & df[col_snr].notna()
df = df[mask_valid]
df = df[df[col_beam] != 0]
df = df[~np.isclose(df[col_snr], -10.0, atol=1e-8, equal_nan=False)]
df = df[df[col_user].isin([101, 2])]

# 若全被过滤
if df.empty:
    raise SystemExit("没有可用于统计的样本（beam!=0 且 SNR!=-10 且 user∈{101,2}）。")

# SNR 统一减 10 dB
df["_snr_adj"] = df[col_snr] - 10.0

# 计算“每个 (slot, user) 的即时平均 SNR”
slot_user_mean = (
    df.groupby([col_slot, col_user], as_index=False)["_snr_adj"]
      .mean()
)

# 构造字典：slot -> mean_snr（分用户）
g101 = slot_user_mean[slot_user_mean[col_user] == 101][[col_slot, "_snr_adj"]]
g2   = slot_user_mean[slot_user_mean[col_user] == 2][[col_slot, "_snr_adj"]]
mean_by_slot_101 = dict(zip(g101[col_slot].astype(int), g101["_snr_adj"]))
mean_by_slot_2   = dict(zip(g2[col_slot].astype(int),   g2["_snr_adj"]))

# 所有 slot（从原始 CSV 的 slot 列获取，保证时间顺序用 slot 升序）
all_slots = sorted(df[col_slot].astype(int).unique())
if not all_slots:
    raise SystemExit("没有可用于绘图的 time slot。")

TOTAL_SEC = 40.0
DT_SEC = TOTAL_SEC / max(1, len(all_slots))

# 预先把两条“window 平均曲线”离线算好（便于确定 y 轴范围 & 实时播放）
def window_series(means_by_slot: dict[int, float], slots: list[int], window: int) -> tuple[list[int], list[float]]:
    buf = []     # 最近 window 个值；有效则为该 slot 的 mean，无数据则为 0
    xs  = []
    ys  = []
    for s in slots:
        v = float(means_by_slot.get(s, 0.0))
        buf.append(v)
        if len(buf) > window:
            buf.pop(0)
        # 只对非零求平均；若全零 -> -20
        nz = [x for x in buf if x != 0.0]
        y = (float(np.mean(nz)) if len(nz) > 0 else -20.0)
        xs.append(s)
        ys.append(y)
    return xs, ys

x101, y101 = window_series(mean_by_slot_101, all_slots, WINDOW)
x2,   y2   = window_series(mean_by_slot_2,   all_slots, WINDOW)

# y 轴范围（上下留空）
all_y = np.array([*y101, *y2], dtype=float)
ymin, ymax = float(np.min(all_y)), float(np.max(all_y))
pad = max(1e-6, 0.1 * max(1.0, ymax - ymin))
ymin_plot, ymax_plot = ymin - pad, ymax + pad

# ---------- Plot ----------
plt.style.use("dark_background")
fig, ax = plt.subplots(figsize=(10, 5), dpi=120)
fig.patch.set_facecolor("black")
ax.set_facecolor("black")

(line_101,) = ax.plot([], [], color=COL_101, linewidth=LINE_WIDTH, label=f"Static User")
(line_2,)   = ax.plot([], [], color=COL_2,   linewidth=LINE_WIDTH, label=f"Moving User")

ax.set_xlim(all_slots[0], all_slots[-1])
ax.set_ylim(-10, ymax_plot)
ax.set_xlabel("Time slot", fontsize=16)
ax.set_ylabel("average SNR (dB)", fontsize=16)
ax.tick_params(axis='y', labelsize=16)
ax.tick_params(axis='x', labelsize=14)
ax.set_title("Average SNR per User", fontsize=16)
ax.grid(True, alpha=0.25)
ax.legend(loc="lower right", fontsize=16)
plt.tight_layout()
plt.ion()

# 实时播放：每 0.1s 增加一个点
x_vals = []
y101_vals = []
y2_vals = []
for i in range(len(all_slots)):
    # 追加当前 slot
    x_vals.append(all_slots[i])
    y101_vals.append(y101[i])
    y2_vals.append(y2[i])

    # 更新两条线
    line_101.set_data(x_vals, y101_vals)
    line_2.set_data(x_vals, y2_vals)

    plt.pause(DT_SEC)

plt.ioff()
plt.show()
