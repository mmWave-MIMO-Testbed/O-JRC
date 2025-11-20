#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RL_RadarImage_Replay_From_Log.py

按 RL_log.csv 的 (epoch, slot) → chosen_beam_id 回放：
- 每个 time slot：
    1) 从 targets_timeslot.csv 构建“全量行”（目标+遮挡）
    2) 仅对日志里的 chosen_beam_id 过滤并写 target_data.csv
    3) 写 # MARKER(slot, beam) 到 radar_chan.csv
    4) 触发 PACKETS_PER_SLOT 个包（默认 3 个）：
         - 若 BEAM0_IS_NDP=True：beam_id==0 → NDP(1)，否则 DATA(2)
         - 否则使用固定 TRIGGER_PACKET_TYPE
"""

from __future__ import annotations
from pathlib import Path
from datetime import datetime
import time, csv
import pandas as pd

# ---- 依赖你的 data_interface ----
import data_interface as DI

# ========= 路径 =========
DATA_DIR = Path("/home/haocheng/O-JRC/examples/RL_ResourceAllocation_Data")
TS_FILE   = DATA_DIR / "targets_timeslot.csv"
BLK_FILE  = DATA_DIR / "blockage_timeslot.csv"   # 可选，不强依赖
TARGET_OUT_FILE  = DATA_DIR / "target_data.csv"
RADAR_CHAN_FILE  = DATA_DIR / "radar_chan.csv"
PACKET_DATA_FILE = DATA_DIR / "packet_data.csv"
# RL 日志
RL_LOG_PATH = DATA_DIR / "RL_log.csv"

# ========= 播放参数 =========
REPLAY_EPOCH = "last"    # "last" 或者一个整数（例如 0,1,2...）
PACKETS_PER_SLOT = 3     # ★ 每个 time slot 只发 3 个包
PACKET_INTERVAL_S = 0.05
MARKER_SETTLE_S   = 0.08

# 发包策略
BEAM0_IS_NDP = False      # True: beam_id==0 -> NDP(1) 否则 DATA(2)
TRIGGER_PACKET_TYPE = 1  # 当 BEAM0_IS_NDP=False 时使用的固定类型（1=NDP, 2=DATA）
TRIGGER_PACKET_SIZE = 50

# ========= Beambook =========
OMNI_ID = 0
OMNI_WIDTH_DEG = 360.0
BEAM_CENTERS = list(range(-60, 61, 10))           # 13
BEAM_WIDTHS  = [20.0, 40.0, 60.0]                 # 3
BEAM_BOOK = [(None, OMNI_WIDTH_DEG)] + [(c, w) for c in BEAM_CENTERS for w in BEAM_WIDTHS]
N_BEAMS  = len(BEAM_BOOK)  # 40

# ========= 工具 =========
def _strip_quotes_and_unescape(s: str) -> str:
    if pd.isna(s): return ""
    s = str(s)
    if len(s) >= 2 and s[0] == '"' and s[-1] == '"': s = s[1:-1]
    return s.replace("\\,", ",")

def _parse_float_list(cell: str) -> list[float]:
    s = _strip_quotes_and_unescape(cell).strip()
    if not s: return []
    return [float(x) for x in s.split(",") if x != ""]

def _parse_str_list(cell: str) -> list[str]:
    s = _strip_quotes_and_unescape(cell).strip()
    if not s: return []
    return [x for x in s.split(",") if x != ""]

def _rows_for_slot_all(df_ts: pd.DataFrame, idx: int) -> list[tuple[float,float,float,float]]:
    """
    返回该 slot 的 'rows_all': [(range, vel, rcs, angle), ...]
    此处 velocity 设为 0（回放无需估计速度）
    遮挡行位于末尾（按你的 timeslot 格式）
    """
    row = df_ts.iloc[idx]
    n_visible = int(row["n_visible"]) if "n_visible" in row else 0
    n_blk = int(row["n_blockage_cells"]) if "n_blockage_cells" in row else 0

    ids  = _parse_str_list(row["ids"]) if n_visible > 0 else []
    rngs = _parse_float_list(row.get("range_m", ""))
    angs = _parse_float_list(row.get("angle_deg", ""))

    tgt_ranges = rngs[:n_visible]
    tgt_angles = angs[:n_visible]
    blk_ranges = rngs[-n_blk:] if n_blk > 0 else []
    blk_angles = angs[-n_blk:] if n_blk > 0 else []

    RCS_BY_ID = { "1": 1.0, "2": 40.0, "101": 0.5 }
    RCS_DEFAULT_TARGET = 1.0
    RCS_BLOCKAGE = 0.9

    rows_all: list[tuple[float,float,float,float]] = []
    for tid, r, a in zip(ids, tgt_ranges, tgt_angles):
        rcs = RCS_BY_ID.get(tid, RCS_DEFAULT_TARGET)
        rows_all.append((r, 0.0, rcs, a))
    rows_all.extend((r, 0.0, RCS_BLOCKAGE, a) for r, a in zip(blk_ranges, blk_angles))
    return rows_all

def _beam_params(beam_index: int) -> tuple[float|None, float]:
    if not (0 <= beam_index < len(BEAM_BOOK)):
        raise ValueError(f"beam_index {beam_index} out of range (0..{len(BEAM_BOOK)-1})")
    return BEAM_BOOK[beam_index]

def _apply_beam(rows_all: list[tuple[float,float,float,float]], beam_index: int
) -> list[tuple[float,float,float,float]]:
    center, width = _beam_params(beam_index)
    if beam_index == 0 or center is None or width >= 61.0:
        return rows_all
    half = 0.5 * float(width)
    lo, hi = float(center) - half, float(center) + half
    return [row for row in rows_all if lo <= row[3] <= hi]

def _ensure_min_one(rows_beam: list[tuple[float,float,float,float]], beam_index: int
) -> list[tuple[float,float,float,float]]:
    if rows_beam:
        return rows_beam
    # 没有目标/遮挡时加一个虚拟弱目标，保证雷达图像能生成
    DUMMY_TARGET_RANGE_M = 11.0
    DUMMY_TARGET_RCS_M2  = 1e-4
    center, _ = _beam_params(beam_index)
    ang = 0.0 if (center is None) else float(center)
    return [(float(DUMMY_TARGET_RANGE_M), 0.0, float(DUMMY_TARGET_RCS_M2), ang)]

def _write_target_data(rows):
    with TARGET_OUT_FILE.open("w", newline="") as f:
        f.write("# range_m,velocity_mps,rcs_m2,azimuth_deg\n")
        w = csv.writer(f, delimiter=",", quoting=csv.QUOTE_NONE, escapechar="\\")
        for r, v, rcs, a in rows:
            w.writerow([f"{r:.3f}", f"{v:.3f}", f"{rcs:.4f}", f"{a:.2f}"])

def _append_marker(slot_idx: int, beam_idx: int):
    RADAR_CHAN_FILE.parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    with RADAR_CHAN_FILE.open("a", encoding="utf-8") as f:
        f.write(f"# MARKER, slot={slot_idx}, beam={beam_idx}, ts={stamp}\n")

def _trigger_one_packet(packet_type: int, packet_size: int):
    ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    pkt = DI.PacketData(ts, packet_type, packet_size)
    DI.write_packet_data(pkt, str(PACKET_DATA_FILE))

def _load_replay_plan(path: Path, epoch_sel="last") -> dict[int, int]:
    """
    返回 {slot -> chosen_beam_id}，若 epoch_sel='last' 则取最大 epoch。
    """
    if not path.exists() or path.stat().st_size == 0:
        raise FileNotFoundError(f"RL log not found or empty: {path}")
    df = pd.read_csv(path)
    required = {"epoch","slot","chosen_beam_id"}
    if not required.issubset(set(df.columns)):
        raise ValueError(f"RL log缺列，至少需要: {required}")
    if epoch_sel == "last":
        ep = int(df["epoch"].max())
    else:
        ep = int(epoch_sel)
    df_ep = df[df["epoch"] == ep].copy()
    if df_ep.empty:
        raise ValueError(f"指定的 epoch={ep} 在 RL log 中没有数据")
    # 按 slot 升序
    df_ep.sort_values("slot", inplace=True)
    plan = {}
    for _, r in df_ep.iterrows():
        try:
            s = int(r["slot"])
            b = int(r["chosen_beam_id"])
            plan[s] = b
        except Exception:
            pass
    return plan

# ========= 主流程 =========
def main():
    print(f"[INFO] Data dir: {DATA_DIR}")
    print(f"[INFO] Timeslot file: {TS_FILE}")
    print(f"[INFO] Radar chan file: {RADAR_CHAN_FILE}")
    print(f"[INFO] RL log: {RL_LOG_PATH}")

    if not TS_FILE.exists():
        raise FileNotFoundError(f"Missing timeslot file: {TS_FILE}")
    df_ts = pd.read_csv(TS_FILE, dtype=str, escapechar="\\")

    plan = _load_replay_plan(RL_LOG_PATH, epoch_sel=REPLAY_EPOCH)
    nslots = len(df_ts)
    print(f"[INFO] Loaded {nslots} slots from timeslot; replay slots present in log: {len(plan)}")

    for slot in range(nslots):
        if slot not in plan:
            print(f"[WARN] slot {slot} 不在 RL log（跳过）")
            continue

        beam_id = int(plan[slot])
        beam_id = 0 # test: 全部用 omnidirectional
        if not (0 <= beam_id < N_BEAMS):
            print(f"[WARN] slot {slot} 的 beam_id={beam_id} 非法（跳过）")
            continue

        # 1) 该 slot 的全量行 -> 只对 beam_id 过滤
        rows_all = _rows_for_slot_all(df_ts, slot)
        rows_beam = _apply_beam(rows_all, beam_id)
        rows_beam = _ensure_min_one(rows_beam, beam_id)

        # 2) 写 target_data.csv
        _write_target_data(rows_beam)

        # # 3) 写 MARKER（包含 slot, beam）
        # _append_marker(slot, beam_id)
        # time.sleep(MARKER_SETTLE_S)

        # 4) 触发本 slot 的 3 个包
        if BEAM0_IS_NDP:
            pkt_type = 1 if beam_id == OMNI_ID else 2
        else:
            pkt_type = TRIGGER_PACKET_TYPE

        for _ in range(PACKETS_PER_SLOT):
            _trigger_one_packet(pkt_type, TRIGGER_PACKET_SIZE)
            time.sleep(PACKET_INTERVAL_S)

        print(f"[SLOT {slot:03d}] beam_id={beam_id:02d} -> rows={len(rows_beam)}; packets={PACKETS_PER_SLOT} ({'NDP' if pkt_type==1 else 'DATA'})")

    print("[DONE] Replay finished.")

if __name__ == "__main__":
    time.sleep(5)
    main()
