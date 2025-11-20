#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
beam_controller.py

桥接：RL 决策  ->  GNU Radio 动作
- 监听 data/comm_log.csv（可选 data/radar_log.csv）；
- 基于上一时隙状态调用 RL policy 输出 (angle_deg, width_deg)；
- 按 beambook 贴合并得到 beam_id；
- 追加写入 data/beam_cmd.csv 供 GNU Radio 读取执行；
- 同时写 data/packet_data.csv 触发 NDP/DATA（沿用你现有的记录方式）。

假设本文件与 RL 模块 (algorithm_ppo.py, RL_Main_Control.py 等) 在同一目录。
数据目录位于父目录的 data/ 下（与你现有实现一致）。
"""

from __future__ import annotations
import os
import sys
import csv
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import numpy as np

# ---------------- Paths ----------------
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR  = os.path.dirname(CURRENT_DIR)
DATA_DIR    = os.path.join(PARENT_DIR, "data")

RADAR_LOG_PATH   = os.path.join(DATA_DIR, "radar_log.csv")    # 输入：GNU Radio 写
COMM_LOG_PATH    = os.path.join(DATA_DIR, "comm_log.csv")     # 输入：GNU Radio 写
PACKET_DATA_PATH = os.path.join(DATA_DIR, "packet_data.csv")  # 输出：控制触发包
RADAR_DATA_PATH = os.path.join(PARENT_DIR, 'data', 'radar_data.csv')
MODEL_PATH       = os.path.join(CURRENT_DIR, "checkpoint_ppo", "actor_critic_v3.pth")

os.makedirs(DATA_DIR, exist_ok=True)

# 让 RL 模块可导入（要求本脚本与 RL 源码在同一目录）
sys.path.append(CURRENT_DIR)

# ==== 依赖你的 RL 模块 ====
try:
    from algorithm_ppo import RLAlgorithmPPO   # 你的实现
except Exception as e:
    RLAlgorithmPPO = None
    print(f"[WARN] 无法导入 RLAlgorithmPPO：{e}. 将使用安全回退策略。")

# 你已有工具（可选）：如果 policy 需要坐标列表/网格，可按需接入
try:
    from RL_Main_Control import image_to_xylist  # 用不到也没关系
except Exception:
    image_to_xylist = None

# 你已有 data_interface（重用你现有的 CSV 读写工具）
try:
    import data_interface
except Exception as e:
    data_interface = None
    print(f"[WARN] 未找到 data_interface 模块：{e}. 将使用本地 CSV 读取逻辑。")


# ---------------- RL / Beam config ----------------
EPOCHS   = 1            # 实时控制场景通常不停机；这里留 1 epoch，内部按时隙循环
N_SLOTS  = 400          # 与你的规则一致
TIMEOUT_S = 0.2         # 没有新 comm 数据的超时阈值

OMNI_WIDTH_THRESHOLD_DEG: float = 60.1
DEFAULT_BEAM_WIDTH_DEG:   float = 30.0

OMNI_BEAM_ID: int = 0
OMNI_WIDTH_DEG: float = 360.0
BEAM_CENTERS = list(range(-60, 61, 10))   # [-60..60], step 10
BEAM_WIDTHS  = [20.0, 40.0, 60.0]
BEAM_BOOK: list[tuple[float | None, float]] = (
    [(None, OMNI_WIDTH_DEG)] + [(c, w) for c in BEAM_CENTERS for w in BEAM_WIDTHS]
)
PARAMS_TO_ID = {p: i for i, p in enumerate(BEAM_BOOK)}

def clamp(x: float, lo: float, hi: float) -> float:
    return float(max(lo, min(hi, x)))

def pick_beam_id(angle_deg: float, width_deg: float) -> tuple[int, float, float]:
    """policy 输出 -> beambook；返回 (beam_id, used_center, used_width)"""
    a = clamp(float(angle_deg), -60.0, 60.0)
    w = float(width_deg)
    if w > OMNI_WIDTH_THRESHOLD_DEG:
        return OMNI_BEAM_ID, a, w
    nearest_center = min(BEAM_CENTERS, key=lambda c: abs(c - a))
    nearest_width  = min(BEAM_WIDTHS,  key=lambda x: abs(x - w))
    beam_id = PARAMS_TO_ID[(nearest_center, nearest_width)]
    return int(beam_id), float(nearest_center), float(nearest_width)


# ---------------- I/O helpers ----------------
def _append_csv_row(path: str, fieldnames: list[str], row: dict) -> None:
    is_new = not os.path.exists(path) or os.path.getsize(path) == 0
    with open(path, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        if is_new:
            w.writeheader()
        w.writerow(row)

@dataclass
class CommRow:
    timestamp: str
    packet_type: int
    data_snr: float
    CRC: int
    throughput: float

def _load_latest_comm() -> Optional[CommRow]:
    """读取你当前使用的 comm_log.csv 的最新一行。
    若存在 data_interface.load_comm_data 则优先复用；否则本地粗略解析。
    """
    if data_interface is not None and hasattr(data_interface, "load_comm_data"):
        obj = data_interface.load_comm_data(COMM_LOG_PATH)
        if obj is None:
            return None
        # 你的 CommData 字段：timestamp, packet_type, data_snr, CRC, throughput 等
        return CommRow(
            timestamp=str(getattr(obj, "timestamp", "")),
            packet_type=int(getattr(obj, "packet_type", 0) or 0),
            data_snr=float(getattr(obj, "data_snr", 0.0) or 0.0),
            CRC=int(getattr(obj, "CRC", 0) or 0),
            throughput=float(getattr(obj, "throughput", 0.0) or 0.0),
        )

    # fallback：直接读 CSV 最后一行
    if not os.path.exists(COMM_LOG_PATH) or os.path.getsize(COMM_LOG_PATH) == 0:
        return None
    try:
        with open(COMM_LOG_PATH, "r") as f:
            last = None
            for line in f:
                last = line
        if last is None:
            return None
        # 你自己的 comm_log.csv 列序如有不同，请在此调整解析
        parts = [p.strip() for p in last.split(",")]
        # 示例: timestamp, packet_type, ..., data_snr, CRC, throughput
        ts = parts[0]
        pkt_type = int(parts[1])
        data_snr = float(parts[3])
        crc = int(parts[4])
        thr = float(parts[5])
        return CommRow(ts, pkt_type, data_snr, crc, thr)
    except Exception:
        return None


# 写入 GNU Radio 读取的命令 CSV
BEAM_CMD_FIELDS = [
    "timestamp", "epoch", "slot", "user_id",
    "policy_angle_deg", "policy_width_deg",
    "chosen_center_deg", "chosen_width_deg", "beam_id",
    "reason"  # "new-data" or "timeout"
]

def write_beam_cmd(*, epoch: int, slot: int, user_id: int,
                   policy_angle_deg: float, policy_width_deg: float,
                   chosen_center_deg: float, chosen_width_deg: float,
                   beam_id: int, reason: str) -> None:
    """
    直接把“贴合后的中心角 chosen_center_deg”写入 radar_data.csv，
    供 GNU Radio 端作为 beamforming angle 使用。
    其余字段（width/beam_id/原因）若需要可另行写 debug 日志，不再生成 beam_cmd.csv。
    """
    ts = datetime.now().strftime("%H:%M:%S") + ':' + datetime.now().strftime("%f")[:3]

    # RadarData 的 5 个形参: (timestamp, peak_power, snr_est, range_val, angle_val)
    # 这里只需 angle_val 控制波束；其它占位给 0/None 即可（不影响切束）
    rd = data_interface.RadarData(
        ts,
        0.0,                             # peak_power 占位
        0.0,                             # snr_est   占位（或写入最近一次 comm_snr 也行）
        3.0,                             # range_val 占位（若你的 flowgraph 不用就写 0）
        float(chosen_center_deg)         # ★ 用贴合后的中心角来切束 ★
    )
    data_interface.write_radar_data(rd, RADAR_DATA_PATH)

    # 如需保留调试信息，可在这里顺便打一行打印/写你原先的 row（不再落盘到 beam_cmd.csv）
    # print(f"[beam_cmd] ep={epoch} slot={slot} uid={user_id} "
    #       f"policy=({policy_angle_deg:.1f},{policy_width_deg:.1f}) "
    #       f"chosen=({chosen_center_deg:.1f},{chosen_width_deg:.1f}) "
    #       f"beam_id={beam_id} reason={reason}")

# 触发包（沿用你的 data_interface）
def write_packet(packet_type: int, packet_size: int = 300) -> None:
    if data_interface is not None and hasattr(data_interface, "PacketData") and hasattr(data_interface, "write_packet_data"):
        now = datetime.now()
        ts = now.strftime("%H:%M:%S") + ":" + now.strftime("%f")[:3]
        pkt = data_interface.PacketData(ts, packet_type, packet_size)
        data_interface.write_packet_data(pkt, PACKET_DATA_PATH)
        return
    # fallback：写一个最小 CSV（如果 GNU Radio 端用你自己的 writer，则此分支可忽略）
    fields = ["timestamp", "packet_type", "packet_size"]
    ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    row = dict(timestamp=ts, packet_type=int(packet_type), packet_size=int(packet_size))
    _append_csv_row(PACKET_DATA_PATH, fields, row)


# ---------------- Controller main loop ----------------
@dataclass
class LoopState:
    pre_user_id: int
    pre_beam_angle: float
    pre_beam_width: float
    pre_comm_snr: float

def main():
    # 1) RL 初始化
    if RLAlgorithmPPO is not None:
        try:
            algo = RLAlgorithmPPO(num_users=2, load_checkpoint=True, checkpoint_path=MODEL_PATH)
            use_rl = True
            print("[INFO] RLAlgorithmPPO 已加载。")
        except Exception as e:
            print(f"[WARN] 加载 RL 模型失败：{e}. 将使用安全回退。")
            algo = None
            use_rl = False
    else:
        algo = None
        use_rl = False

    # 2) 初始状态
    state = LoopState(
        pre_user_id=101,               # 若需两用户调度，可接入你的 make_user_schedule
        pre_beam_angle=0.0,
        pre_beam_width=DEFAULT_BEAM_WIDTH_DEG,
        pre_comm_snr=0.0,
    )

    last_comm_ts: Optional[str] = None

    for ep in range(EPOCHS):
        print(f"[Epoch {ep+1}/{EPOCHS}] Controller started.")
        t_start = time.time()
        for slot in range(N_SLOTS):
            slot_begin = time.time()

            while True:
                time.sleep(0.01)
                comm = _load_latest_comm()
                now = time.time()
                reason = None

                # 是否有新数据
                has_new_comm = (comm is not None and comm.timestamp and comm.timestamp != last_comm_ts)
                timeout = (now - slot_begin) >= TIMEOUT_S

                if has_new_comm:
                    # 更新状态
                    last_comm_ts = comm.timestamp
                    state.pre_comm_snr = float(comm.data_snr)
                    reason = "new-data"
                elif timeout:
                    # 超时使用上一次 SNR（或回退 -10）
                    if not np.isfinite(state.pre_comm_snr):
                        state.pre_comm_snr = -10.0
                    reason = "timeout"
                else:
                    continue  # 既没新数据也未超时 -> 继续等

                # 3) 决策
                if use_rl and algo is not None:
                    try:
                        angle_deg, width_deg = algo.policy(
                            train=False,
                            time_slot_idx=slot,
                            pre_beam_angle=state.pre_beam_angle,
                            pre_beam_width=state.pre_beam_width,
                            pre_user_idx=state.pre_user_id,
                            pre_radar_matrix=None,      # 实机可接入你的网格/CSI，这里置 None/不用
                            pre_radar_list=None,
                            pre_obs_matrix=None,        # 可接入障碍物世界栅格
                            comm_snr=state.pre_comm_snr,
                            cur_user_idx=state.pre_user_id  # 如启用调度可换成当前 user
                        )
                        angle_deg = float(angle_deg) if np.isfinite(angle_deg) else 0.0
                        width_deg = float(width_deg) if np.isfinite(width_deg) else DEFAULT_BEAM_WIDTH_DEG
                    except Exception as e:
                        print(f"[WARN] RL policy 运行失败（slot={slot}）：{e}. 使用回退。")
                        angle_deg = state.pre_beam_angle
                        width_deg = DEFAULT_BEAM_WIDTH_DEG
                else:
                    # 回退策略：保持上次角度、固定宽度
                    angle_deg = state.pre_beam_angle
                    width_deg = DEFAULT_BEAM_WIDTH_DEG

                beam_id, used_center, used_width = pick_beam_id(angle_deg, width_deg)

                # 4) 写命令给 GNU Radio
                write_beam_cmd(
                    epoch=ep, slot=slot, user_id=state.pre_user_id,
                    policy_angle_deg=angle_deg, policy_width_deg=width_deg,
                    chosen_center_deg=used_center, chosen_width_deg=used_width,
                    beam_id=beam_id, reason=reason
                )

                # 5) 触发一次发包：beam_id==0(OMNI) -> NDP(1)，否则 DATA(2)
                pkt_type = 1 if beam_id == OMNI_BEAM_ID else 2  # OMNI_BEAM_ID 通常为 0
                write_packet(packet_type=pkt_type, packet_size=100)

                # 6) 更新状态 -> 下一时隙
                state.pre_beam_angle = used_center
                state.pre_beam_width = used_width
                # 用户调度如需可在此处更新 state.pre_user_id

                break  # 结束本时隙，进入下一个 slot

        print(f"[Epoch {ep+1}] 完成。")

if __name__ == "__main__":
    main()
