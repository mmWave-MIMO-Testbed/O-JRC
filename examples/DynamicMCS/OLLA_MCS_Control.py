#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
单链路 OLLA + EMA + 滞回 + 连击 的自适应 MCS 控制循环

主流程：
1) 初始化路径、默认值与 OLLA/EMA 状态；
2) 循环从 comm_log.csv 读取最新一条通信数据 data_interface.load_comm_data；
3) 每当检测到新包(timestamp 变化):
   - 按 CRC(ACK/NACK) 更新 OLLA 的 Δ（delta_db）；
   - 将 “data_snr + Δ” 经 EMA 平滑得到 snr_ema；
   - 基于当前 MCS 的滞回阈值 + 连击规则，决定是否升/降档；
   - 限速（每秒最多若干次变档）；
   - 若变更，则写 mcs_ctrl.csv 来触发MCS变更；
4) 周期性将 Δ 的直方图中位数保存为 Δ_ini*（轻量热启动），下次进程重启可直接使用；
5) 循环持续写 packet_data.csv 触发生成信号（即使没有新 comm 数据）。

NOTE:
- 仅三个 MCS 档（1 for BPSK /3 for QPSK/5 for 16-QAM），如需更多档位需扩展GNU-Radio's dynamic modulation blocks；
- 目前“超时视为 NACK”，如果不需要等待则关闭（waiting for ACK, 空口效率低） ；
- data_interface 需提供以下函数/类：
    - RadarData, CommData, PacketData, MCS_ctrl_data
    - write_radar_data, write_mcs_ctrl_data, write_packet_data, load_comm_data
"""

import os
import time
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import List, Tuple 
# from collections import deque  # 若不使用窗口法，可移除
import data_interface

# --------------direction of path --------------
current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)
parent_dir = os.path.dirname(current_dir)
print(parent_dir)

radar_log_path      = os.path.join(parent_dir, 'data', 'radar_log.csv')     # read: radar log
comm_log_path       = os.path.join(parent_dir, 'data', 'comm_log.csv')      # read: comm log
radar_data_path     = os.path.join(parent_dir, 'data', 'radar_data.csv')    # write: radar log
packet_data_path    = os.path.join(parent_dir, 'data', 'packet_data.csv')   # write：send packet
mcs_data_path       = os.path.join(parent_dir, 'data', 'mcs_ctrl.csv')      # write: MCS

# ---------------- OLLA configs ----------------
# OLLA：ACK 轻微往下，NACK 大幅往上，从而逼近目标 BLER
# Up 0.8, Down 0.04 is 5% BLER
# up 0.8, Down 0.08 is 10% BLER
# 目标 BLER
TARGET_BLER = 0.1  # BLER 10% 
DELTA_UP = 1.0      # 步长基准（数值影响收敛快慢）
DELTA_DOWN = DELTA_UP * TARGET_BLER / (1.0 - TARGET_BLER)
# DELTA_UP   = 0.8      # dB, NACK 步长（抬高 Δ，等效降低目标 SNR 要求）
# DELTA_DOWN = 0.08      # dB, ACK 步长（降低 Δ）
DELTA_MIN, DELTA_MAX = -20.0, 20.0  # Δ 截断范围，避免发散
BIN_SIZE   = 0.1
NUM_BINS   = int((DELTA_MAX - DELTA_MIN) / BIN_SIZE) + 1

GLOBAL_DELTA_FILE = os.path.join(parent_dir, "data", "global_delta_ini.txt")  # 轻量热启动：持久化 Δ_ini*
HEATUP_THRESHOLD  = 200   # 累计 ACK+NACK 达到阈值后，才认为直方图稳定可写入 Δ_ini*
HEATUP_INTERVAL_S = 120   # 两次写 Δ_ini* 的最小间隔(s)

def load_global_delta_ini(path: str = GLOBAL_DELTA_FILE) -> float:
    """从文件读取 Δ_ini*；若不存在或异常，返回 0.0"""
    try:
        return float(Path(path).read_text())
    except Exception:
        return 0.0

def push_hist(delta_db: float, hist_bins: List[int]) -> None:
    """将当前 Δ 计入直方图，用于估计中位数作为 Δ_ini*"""
    idx = int(round((delta_db - DELTA_MIN) / BIN_SIZE))
    idx = max(0, min(NUM_BINS - 1, idx))
    hist_bins[idx] += 1

def median_from_hist(hist_bins: List[int]) -> float:
    """由直方图估计中位数 Δ；样本为空时返回 0.0"""
    cdf = np.cumsum(np.array(hist_bins, dtype=int))
    if cdf[-1] == 0:
        return 0.0
    half = cdf[-1] // 2  # 下中位（与 // 一致）
    idx = np.searchsorted(cdf, half)
    return float(DELTA_MIN + idx * BIN_SIZE)

# ------------------EMA + 滞回 + 连击---------------------
# 1) EMA 平滑 SNR（抑制抖动）
# 2) 滞回区间（避免频繁抖动上下档）
# 3) 连击门槛（需要连续满足多次才触发变档）
ALPHA = 0.2         # EMA 平滑系数（0.1~0.3 常见）
UP_HYST = 1.5       # 升档滞回(dB)：SNR_ema > hi + UP_HYST 才考虑升档
DOWN_HYST = 1.0     # 降档滞回(dB)：SNR_ema < lo - DOWN_HYST 才考虑降档
UP_STREAK_REQ = 3   # 连续满足升档条件的次数
DOWN_STREAK_REQ = 1 # 连续满足降档条件的次数

# ------------------------------------------------------

def mcs_lower_upper_thresholds(mcs: int) -> Tuple[float, float]:
    """
    返回当前 MCS 档位的 (lo, hi) 阈值 (dB)，用于滞回判断。
    - lo：维持该档的下阈值
    - hi：维持该档的上阈值
    示例：仅 1/3/5 三档；若扩展，对每档给出合理区间。
    """
    if mcs == 1:   return ( 0.0, 14.0)   # 1档维持区间
    if mcs == 3:   return ( 12.0, 20.0)  # 3档维持区间
    if mcs == 5:   return ( 18.0, 99.0)  # 5档维持区间（给定一个大的上限值）
    # fallback 保证值合理
    return (-1.0, 99.0)

# -------------------- 主函数参数 -------------------------
current_time = '22:10:39.001'
peak_power   = 0.01
snr_est      = 0.0
range_val    = 3
angle_val    = 0    # beamforming angle
packet_type  = 2    # 1 for NDP, 2 for Data
packet_size  = 300
test_packet_type = 2
last_data_timestamp = None

# 初始 MCS 档位 BPSK
mcs_modulation = 1

# ------------- 单链路 OLLA state ----------------------
delta_db   = load_global_delta_ini()  # 轻量热启动：上次学习到的 Δ_ini*
hist_bins  = [0] * NUM_BINS           # Δ 的直方图
ack_cnt    = 0
nack_cnt   = 0
last_heatup_save_ts = time.time() - HEATUP_INTERVAL_S  # 允许尽快写一次 Δ_ini*

# ---------------- EMA/滞回/连击状态 --------------------------------
snr_ema = delta_db  # 用 Δ_ini* 作为 EMA 初值（更贴近当前链路）
consec_up = 0
consec_down = 0
last_change_ts = 0.0  # 上次 MCS 变更时间（用于限速）

# CHANGE: 升档冷却（降档后禁止立刻升回）
COOLDOWN_S = 0.5  # 降档后冷却时间(s)
last_downgrade_ts = 0.0
# ------------------- 初始化数据对象 ----------------------
# radar初始化
test_radar = data_interface.RadarData(current_time, peak_power, snr_est, range_val, angle_val)
data_interface.write_radar_data(test_radar, radar_data_path)

# comm初始化
test_comm = data_interface.CommData(current_time, 0, packet_type, snr_est, snr_est, 1, 0, 0)

# packet初始化
test_packet = data_interface.PacketData(current_time, packet_type, packet_size)

# mcs ctrl初始化
test_mcs = data_interface.MCS_ctrl_data(mcs_modulation)
data_interface.write_mcs_ctrl_data(test_mcs, mcs_data_path)
print(f"[Init] MCS = {mcs_modulation} | Δ_ini = {delta_db:.2f} dB")

# -------------------主函数------------------------
print("Start recording")
time.sleep(5)  # 等待系统稳定
previous_time = time.time()
start_time    = time.time()
total_time    = time.time()
end_time_s    = 120  # 测试持续时长（秒）

# DEBUG 开关 默认False
DEBUG_PRINT = True

while total_time - start_time <= end_time_s:

    time.sleep(0.01)  # 采样周期 ~10ms
    current_dt = datetime.now()
    now_time = time.time()

    # 期望 load_comm_data 返回 None 或最新一条 CommData
    test_comm = data_interface.load_comm_data(comm_log_path)
    time_diff = now_time - previous_time  # 用于超时判断

    # ------- 没有新数据仍然写 packet 以产生新的packet -------------
    if test_comm is None:
        test_packet.timestamp   = current_dt.strftime("%H:%M:%S") + ':' + current_dt.strftime("%f")[:3]
        test_packet.packet_size = packet_size
        data_interface.write_packet_data(test_packet, packet_data_path)
        previous_time = now_time
        total_time = time.time()
        continue

    # -----------读到数据update packet state----------------
    test_packet.timestamp   = current_dt.strftime("%H:%M:%S") + ':' + current_dt.strftime("%f")[:3]
    test_packet.packet_type = test_packet_type
    test_packet.packet_size = packet_size

    # -------------------有新数据-------------------
    if last_data_timestamp != test_comm.timestamp:
        last_data_timestamp = test_comm.timestamp

        # -------- OLLA 更新：按 CRC（1=ACK, 0=NACK）调整 Δ --------
        crc_ok = int(test_comm.CRC)  # 1=ACK, 0=NACK
        if crc_ok == 0:
            delta_db += DELTA_UP    # NACK：提高 Δ（更保守）
            nack_cnt += 1
        else:
            delta_db -= DELTA_DOWN  # ACK：降低 Δ（更激进）
            ack_cnt  += 1

        # 对 Δ 做截断，避免偶发抖动导致值外溢
        delta_db = max(DELTA_MIN, min(DELTA_MAX, delta_db))
        push_hist(delta_db, hist_bins)  # 计入直方图，用于后续 Δ_ini* 估计

        # -------- EMA 平滑 + 滞回 + 连击 判定 --------
        # 有效 SNR = 观测 data_snr + OLLA 偏置 Δ
        # snr_eff = float(test_comm.data_snr) + delta_db
        snr_eff = float(test_comm.data_snr) - delta_db  # ← 关键行
        # EMA：抑制突发抖动
        snr_ema = (1.0 - ALPHA) * snr_ema + ALPHA * snr_eff

        # 依据当前 MCS 的维持区间判断是否需要升/降档（带滞回 & 连击）
        lo, hi = mcs_lower_upper_thresholds(mcs_modulation)
        target_mcs = mcs_modulation

        # 升档条件：SNR_ema 足够高（高于上阈 + 滞回），并且连续多次满足
        if snr_ema > (hi + UP_HYST):
            consec_up += 1
            consec_down = 0
            if consec_up >= UP_STREAK_REQ:
                target_mcs = min(5, mcs_modulation + 2)  # 每次最多升一档（0→2→4）
                consec_up = 0

        # 降档条件：SNR_ema 足够低（低于下阈 - 滞回），并且连续多次满足
        elif snr_ema < (lo - DOWN_HYST):
            consec_down += 1
            consec_up = 0
            if consec_down >= DOWN_STREAK_REQ:
                target_mcs = max(0, mcs_modulation - 2)  # 每次最多降一档（4→2→0）
                consec_down = 0

        else:
            # 处于维持区间：清空连击计数
            consec_up = consec_down = 0

        # -------- 限速（避免在短时内反复跳变）--------
                # CHANGE: 升档冷却（刚降过不许马上升回）
        if target_mcs != mcs_modulation:
            if (time.time() - last_downgrade_ts) < COOLDOWN_S:
                target_mcs = mcs_modulation

        # if target_mcs != mcs_modulation:
        #     if (now_time - last_change_ts) < (1.0 / MAX_STEP_PER_SEC):
        #         # 未达到最小间隔，则本轮不变更
        #         target_mcs = mcs_modulation

        # -------- 应用变更：写 MCS 控制文件 --------
        if target_mcs != mcs_modulation:
            old = mcs_modulation
            mcs_modulation = target_mcs
            last_change_ts = now_time
            test_mcs.mcs_type = mcs_modulation
            data_interface.write_mcs_ctrl_data(test_mcs, mcs_data_path)
            
            # 记录变化时间用于冷却
            if mcs_modulation != old:     # 记录变化MCS节点
                last_downgrade_ts = now_time

            if DEBUG_PRINT:
                print(f"[{datetime.now().isoformat()}] "
                      f"CRC={crc_ok} Δ={delta_db:.2f}dB "
                      f"SNR(obs)={float(test_comm.data_snr):.1f}dB "
                      f"SNR_eff(EMA)={snr_ema:.1f}dB → MCS {old}→{mcs_modulation}")

        previous_time = now_time

    # ------------ 超时（可选）：把超时当作 NACK --------------
    # Waiting for ACK (会降低空口效率)
    # 若超时多为上层/调度原因而非链路问题，建议禁用此分支
    elif time_diff >= 0.2:
        previous_time = now_time
        delta_db += DELTA_UP
        delta_db = max(DELTA_MIN, min(DELTA_MAX, delta_db))
        nack_cnt += 1
        push_hist(delta_db, hist_bins)
        if DEBUG_PRINT:
            print("Comm time-out (treated as NACK)")

    # --------更新packet--------------
    data_interface.write_packet_data(test_packet, packet_data_path)

    # ---------- 单链路轻量热启动：样本达到阈值后周期性写 Δ_ini* -------------
    # 只有当累计样本足够 && 距离上次写入超过最小间隔，才会更新
    if (ack_cnt + nack_cnt) >= HEATUP_THRESHOLD and (time.time() - last_heatup_save_ts) > HEATUP_INTERVAL_S:
        delta_ini_star = median_from_hist(hist_bins)
        Path(GLOBAL_DELTA_FILE).write_text(f"{delta_ini_star:.2f}")
        last_heatup_save_ts = time.time()
        if DEBUG_PRINT:
            print(f"[{datetime.now().isoformat()}] Updated Δ_ini* = {delta_ini_star:.2f} dB")

    total_time = time.time()

