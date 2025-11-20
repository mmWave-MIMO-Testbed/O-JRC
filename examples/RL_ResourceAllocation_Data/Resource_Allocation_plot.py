#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ================== 配置 ==================
CSV_PATH = Path("/home/haocheng/O-JRC/examples/RL_ResourceAllocation_Data") / "RL_log.csv"  # 修改为你的CSV路径
WINDOW     = 25                  # 滑动窗口大小
DT_SEC     = 0.1                 # 刷新周期（秒）
TOTAL_S    = 40                  # 总时长（秒）
LINE_WIDTH = 3.0                 # 线宽
COL_101    = "red"               # 101 -> 红
COL_2      = "lime"              # 2   -> 绿（更亮，黑底对比高）
COL_SENSE  = "deepskyblue"       # sensing -> 蓝（亮蓝，黑底对比高）
# ========================================

# ---------- 读入 ----------
df = pd.read_csv(CSV_PATH)

# 兼容不同列名
cols = {c.lower().strip(): c for c in df.columns}
def pick(*names):
    for n in names:
        if n in cols:
            return cols[n]
    raise KeyError(f"缺少列（候选其一即可）：{names}")

col_epoch = pick("epoch")
col_slot  = pick("slot")
col_user  = pick("user_id", "userid", "user")
col_beam  = pick("chosen_beam_id", "beam_id", "beam", "chosen_beam")
col_snr   = pick("snr", "data_snr")
col_width = pick("chosen_width_deg", "width_deg", "width")

# 排序与数组
df = df.sort_values([col_epoch, col_slot]).reset_index(drop=True)
slot_arr = df[col_slot].to_numpy()
user_arr = df[col_user].astype(int).to_numpy()
beam_arr = df[col_beam].astype(int).to_numpy()
width_arr = pd.to_numeric(df[col_width], errors="coerce").to_numpy()
snr_arr  = pd.to_numeric(df[col_snr], errors="coerce").to_numpy()

N_total = len(df)
if N_total == 0:
    raise RuntimeError("CSV 为空，无法绘图。")

# 总步数（每 0.1s 一步，最多 40s）
N_steps = min(int(TOTAL_S / DT_SEC), N_total)

# ---------- 画布 ----------
plt.style.use("dark_background")   # 黑色背景主题
fig, ax = plt.subplots(figsize=(10, 5), dpi=120)
fig.patch.set_facecolor("black")
ax.set_facecolor("black")

# 三条线缓存
x_vals = []
p101    = []
p2      = []
psense  = []

# 预建曲线（加粗 & 指定颜色）
(line_101,)   = ax.plot([], [], linewidth=LINE_WIDTH, color=COL_101,   label="Static User")
(line_2,)     = ax.plot([], [], linewidth=LINE_WIDTH, color=COL_2,     label="Moving User")
(line_sense,) = ax.plot([], [], linewidth=LINE_WIDTH, color=COL_SENSE, label="Sensing")

# 坐标轴与图注
xmin, xmax = slot_arr[:N_steps].min(), slot_arr[:N_steps].max()
ax.set_xlim(xmin, xmax)
ax.set_ylim(-0.05, 1.05)  # 上下都留空间，便于识别
ax.set_xlabel("Time slot", fontsize=16)
ax.set_ylabel(f"Proportion of Allocated Time-Slot Resources", fontsize=14)
ax.set_title(f"Time-Slot Resource Allocation")
ax.grid(True, alpha=0.25)
ax.legend(loc="upper right", fontsize=16)
plt.tight_layout()
plt.ion()  # 交互模式

# ---------- 主循环 ----------
for i in range(N_steps):
    # 当前滑动窗口 [i-WINDOW+1, i]
    w0 = max(0, i - WINDOW + 1)
    w1 = i + 1
    b_win    = beam_arr[w0:w1]
    u_win    = user_arr[w0:w1]
    wd_win   = width_arr[w0:w1]
    snr_win  = snr_arr[w0:w1]
    win_len  = w1 - w0

    # sensing 条件：
    # 1) beam==0
    # 2) (width==60) AND (snr == -10)
    mask_beam0   = (b_win == 0)
    mask_w60     = np.isclose(wd_win, 60.0, atol=1e-8, equal_nan=False)
    mask_snr_m10 = np.isclose(snr_win, -10.0, atol=1e-8, equal_nan=False)
    sense_mask   = mask_beam0 | (mask_w60 & mask_snr_m10)

    # 计数
    c_sense = int(np.count_nonzero(sense_mask))
    c_101   = int(np.count_nonzero((~sense_mask) & (u_win == 101)))
    c_2     = int(np.count_nonzero((~sense_mask) & (u_win == 2)))

    # 比例（不做归一化）
    if win_len > 0:
        p_s  = c_sense / win_len
        p_1  = c_101   / win_len
        p_2v = c_2     / win_len
    else:
        p_s = p_1 = p_2v = 0.0

    # 更新曲线
    x_vals.append(slot_arr[i])
    psense.append(p_s)
    p101.append(p_1)
    p2.append(p_2v)

    line_101.set_data(x_vals, p101)
    line_2.set_data(x_vals, p2)
    line_sense.set_data(x_vals, psense)

    # 如需滚动窗口视野，可启用下行：
    # ax.set_xlim(max(xmin, slot_arr[i] - 200), slot_arr[i] + 5)

    plt.pause(DT_SEC)

plt.ioff()
plt.show()
