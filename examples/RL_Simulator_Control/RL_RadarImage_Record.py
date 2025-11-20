#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RL_RadarImage_Record.py

Purpose
-------
Per time slot, iterate beams b=0..N_BEAMS-1 (0 = omni). For each beam:
  1) Update target_data.csv for the beam's angular coverage (incl. blockage)
  2) Append a marker line to radar_chan.csv indicating (slot, beam)
  3) Trigger GNU Radio to generate TEN packets via data_interface.write_packet_data
     (each trigger causes the flowgraph to produce a radar channel entry)

Notes
-----
- Assumes GNU Radio flowgraph watches packet_data.csv; any rewrite triggers one packet.
- The radar_chan.csv is assumed to be appended by the flowgraph; this script inserts
  a comment marker line BEFORE the 10 packets so downstream parsing can group by
  (slot, beam).
- Uses the same beambook definition as RL_RadarImage_Create_Control_Beamforming.py.
- If your beambook differs, edit BEAM_WIDTH_DEG / BEAM_CENTERS below.

Edit paths if needed.
"""

from __future__ import annotations

from pathlib import Path
from datetime import datetime
import time
import csv
import pandas as pd

# External interface to the GNU Radio flowgraph
import data_interface as DI  # requires data_interface.py in PYTHONPATH

# ========= 路径配置 =========
# Adjust DATA_DIR to your environment
DATA_DIR = Path("/home/haocheng/O-JRC/examples/RL_ResourceAllocation_Data")
TS_FILE   = DATA_DIR / "targets_timeslot.csv"      # 输入：场景按时隙的目标/遮挡（由你的模拟器生成）
BLK_FILE  = DATA_DIR / "blockage_timeslot.csv"     # 输入：遮挡角度/距离（可选）
TARGET_OUT_FILE = DATA_DIR / "target_data.csv"     # 输出：给雷达仿真器的目标列表（随束变化）
RADAR_CHAN_FILE = DATA_DIR / "radar_chan.csv"      # 输出：GNU Radio写入的通道数据（我们会先写入 marker）
PACKET_DATA_FILE= DATA_DIR / "packet_data.csv"     # 触发 GNU Radio 的信号文件（每写一次 -> 1 个包）
PACKET_LOG_FILE = DATA_DIR / "packet_log.csv"      # 可选：我们自己的触发日志

# ========= 参数配置 =========
DT_S = 0.1                        # 与时隙生成一致（仅用于速度估计）
USE_RADIAL_VELOCITY = False       # True=径向速度差分；False=全0
INCLUDE_HEADER = True             # target_data.csv 的表头注释

BLOCKAGE_ONLY_ONESHOT = False    #Blockage only on first slot

# RCS 配置（按需修改）
RCS_BY_ID = { "1": 1.0, "2": 40.0, "101": 0.5 }
RCS_DEFAULT_TARGET = 1.0
RCS_BLOCKAGE = 0.9

# 当束内没有任何目标时，注入一个极低RCS的“虚拟目标”，以保证雷达图像可生成
DUMMY_TARGET_RANGE_M = 11.0
DUMMY_TARGET_RCS_M2  = 1e-4

# # Beam 配置：index=0 -> omni，其余使用中心角+固定宽度窗口
# BEAM_WIDTH_DEG = 30.0
# BEAM_CENTERS = list(range(-60, 61, 5))  # -60, -55, ..., 60  (25 beams)
# N_BEAMS = 1 + len(BEAM_CENTERS)

# --- Beam book config ---
OMNI_ID = 0
OMNI_WIDTH_DEG = 360.0  # 仅占位，表示全向
# 从 -60 到 60，每 10 度一个中心
BEAM_CENTERS = list(range(-60, 61, 10))           # [-60, -50, ..., 60]
# 每个中心对应这三种宽度
BEAM_WIDTHS  = [20.0, 40.0, 60.0]
# BEAM_WIDTHS = [180.0]  # test: 全部用 omnidirectional
# 展平后的 beam book：
# id=0 预留给 OMNI；其余按 (center, width) 的笛卡尔积顺序排列：
# 例如 id=1:(-60,10), id=2:(-60,30), id=3:(-60,50), id=4:(-50,10), ...
BEAM_BOOK = [(None, OMNI_WIDTH_DEG)] + [(c, w) for c in BEAM_CENTERS for w in BEAM_WIDTHS]

N_BEAMS = len(BEAM_BOOK)  # = 1 + 13*3 = 40

# 触发配置：每束发多少包、间隔多久
PACKETS_PER_BEAM = 50
PACKET_INTERVAL_S = 0.08         # 两次触发之间的间隔
MARKER_SETTLE_S   = 0.1         # 写 marker 后给文件系统/其它进程一点缓冲

# 触发包参数（根据你的Flowgraph需要调整）
TRIGGER_PACKET_TYPE = 1          # 1=NDP, 2=DATA（示例）
TRIGGER_PACKET_SIZE = 10        # 字节数（示例）

# ========= 工具函数 =========
def _strip_quotes_and_unescape(s: str) -> str:
    if pd.isna(s):
        return ""
    s = str(s)
    if len(s) >= 2 and s[0] == '"' and s[-1] == '"':
        s = s[1:-1]
    return s.replace("\\,", ",")


def _parse_float_list(cell: str) -> list[float]:
    s = _strip_quotes_and_unescape(cell).strip()
    if not s:
        return []
    return [float(x) for x in s.split(",") if x != ""]


def _parse_str_list(cell: str) -> list[str]:
    s = _strip_quotes_and_unescape(cell).strip()
    if not s:
        return []
    return [x for x in s.split(",") if x != ""]


def _write_target_data(rows: list[tuple[float, float, float, float]]):
    """rows: [(range, vel, rcs, angle), ...] -> target_data.csv"""
    with TARGET_OUT_FILE.open("w", newline="") as f:
        if INCLUDE_HEADER:
            f.write("# range_m,velocity_mps,rcs_m2,azimuth_deg\n")
        w = csv.writer(f, delimiter=",", quoting=csv.QUOTE_NONE, escapechar="\\")
        for r, v, rcs, a in rows:
            w.writerow([f"{r:.3f}", f"{v:.3f}", f"{rcs:.4f}", f"{a:.2f}"])


def _build_blockage_rows_from_file() -> list[tuple[float, float, float, float]]:
    if not BLK_FILE.exists():
        return []
    dfb = pd.read_csv(BLK_FILE, dtype=str, escapechar="\\")
    if dfb.empty:
        return []
    row = dfb.iloc[0]
    rngs = _parse_float_list(row.get("range_m", ""))
    angs = _parse_float_list(row.get("angle_deg", ""))
    return [(r, 0.0, RCS_BLOCKAGE, a) for r, a in zip(rngs, angs)]


def _rows_for_slot_all(df_ts: pd.DataFrame, idx: int,
                       prev_ranges: dict[str, float]) -> tuple[list[tuple[float, float, float, float]], dict[str, float]]:
    """
    生成“该时隙完整行（目标+遮挡）”，供后续按波束过滤。
    返回：
      rows_all = [(range, v, rcs, angle), ...]
      curr_ranges = { id -> range }  # 仅目标
    """
    row = df_ts.iloc[idx]
    n_visible = int(row["n_visible"]) if "n_visible" in row else 0
    n_blk = int(row["n_blockage_cells"]) if "n_blockage_cells" in row else 0

    ids = _parse_str_list(row["ids"]) if n_visible > 0 else []
    rngs_all = _parse_float_list(row["range_m"]) if "range_m" in row else []
    angs_all = _parse_float_list(row["angle_deg"]) if "angle_deg" in row else []

    # 前 n_visible 是目标；最后 n_blk 是遮挡
    tgt_ranges = rngs_all[:n_visible]
    tgt_angles = angs_all[:n_visible]
    blk_ranges = rngs_all[-n_blk:] if n_blk > 0 else []
    blk_angles = angs_all[-n_blk:] if n_blk > 0 else []

    curr_ranges = {tid: r for tid, r in zip(ids, tgt_ranges)}
    if USE_RADIAL_VELOCITY:
        v_by_id = {tid: (curr_ranges[tid] - prev_ranges.get(tid, curr_ranges[tid])) / DT_S
                   for tid in curr_ranges}
    else:
        v_by_id = {tid: 0.0 for tid in curr_ranges}

    rows_all: list[tuple[float, float, float, float]] = []
    for tid, r, a in zip(ids, tgt_ranges, tgt_angles):
        rcs = RCS_BY_ID.get(tid, RCS_DEFAULT_TARGET)
        rows_all.append((r, v_by_id.get(tid, 0.0), rcs, a))

    rows_all.extend((r, 0.0, RCS_BLOCKAGE, a) for r, a in zip(blk_ranges, blk_angles))
    return rows_all, curr_ranges

def _beam_params(beam_index: int) -> tuple[float | None, float]:
    """
    返回 (center_deg, width_deg)。OMNI 为 (None, 360.0)。
    """
    if not (0 <= beam_index < len(BEAM_BOOK)):
        raise ValueError(f"beam_index {beam_index} out of range (0..{len(BEAM_BOOK)-1})")
    return BEAM_BOOK[beam_index]

def _apply_beam(
    rows_all: list[tuple[float, float, float, float]],
    beam_index: int
) -> list[tuple[float, float, float, float]]:
    """
    按 beam_index 过滤：
      0 -> omni（不过滤）
      1..N -> 仅保留 |angle - center| <= width/2 的条目
    """
    center, width = _beam_params(beam_index)

    # 0 或任意被配置为“全向”的束：不过滤
    if beam_index == 0 or center is None or width >= 61.0:
        return rows_all

    half = 0.5 * float(width)
    lo, hi = float(center) - half, float(center) + half

    def in_beam(angle: float) -> bool:
        return lo <= angle <= hi

    return [row for row in rows_all if in_beam(row[3])]


# def _ensure_min_one_target(
#     rows_beam: list[tuple[float, float, float, float]],
#     beam_index: int
# ) -> list[tuple[float, float, float, float]]:
#     """若束内无任何“目标”（只存在遮挡或完全为空），追加一个极低RCS的虚拟目标。
#     目标与遮挡的区分依据：遮挡的RCS固定为 RCS_BLOCKAGE。
#     """
#     has_target = any(abs(rcs - RCS_BLOCKAGE) > 1e-12 for (_, _, rcs, _) in rows_beam)
#     if has_target:
#         return rows_beam

#     center, _ = _beam_params(beam_index)
#     ang = 0.0 if (center is None) else float(center)

#     return rows_beam + [(float(DUMMY_TARGET_RANGE_M), 0.0, float(DUMMY_TARGET_RCS_M2), ang)]

def _ensure_min_one_target(
    rows_beam: list[tuple[float, float, float, float]],
    beam_index: int
) -> list[tuple[float, float, float, float]]:
    """
    若束内完全为空，则追加一个极低 RCS 的虚拟目标。
    不再区分目标/遮挡；只要有任何条目（包括遮挡），就原样返回。
    """
    if rows_beam:  # 既有目标也可能只有遮挡；都算“有东西”
        return rows_beam

    center, _ = _beam_params(beam_index)
    ang = 0.0 if (center is None) else float(center)
    return rows_beam + [(float(DUMMY_TARGET_RANGE_M), 0.0, float(DUMMY_TARGET_RCS_M2), ang)]

def _append_radar_chan_marker(slot_idx: int, beam_idx: int):
    """在 radar_chan.csv 末尾追加一个注释行，用于标记以下数据属于哪个 (slot, beam)。"""
    RADAR_CHAN_FILE.parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    line = f"# MARKER, slot={slot_idx}, beam={beam_idx}, ts={stamp}\n"
    with RADAR_CHAN_FILE.open("a", encoding="utf-8") as f:
        f.write(line)


def _trigger_one_packet(packet_type: int, packet_size: int):
    ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]  # e.g. 22:10:39.001
    pkt = DI.PacketData(ts, packet_type, packet_size)
    # 1) 写触发文件（覆盖写，供Flowgraph检测）
    DI.write_packet_data(pkt, str(PACKET_DATA_FILE))
    # # 2) 可选：写我们自己的包日志（追加）
    # try:
    #     DI.write_packet_log(pkt, str(PACKET_LOG_FILE))
    # except Exception:
    #     pass


# ========= 主流程 =========
def main():
    print(f"[INFO] Data dir: {DATA_DIR}")
    print(f"[INFO] Timeslot file: {TS_FILE}")
    print(f"[INFO] Radar chan file: {RADAR_CHAN_FILE}")
    print(f"[INFO] Packet data file (trigger): {PACKET_DATA_FILE}")
    #print(f"[INFO] Beamforming: N_BEAMS={N_BEAMS} (0=omni, 1..{N_BEAMS-1} centers), width={BEAM_WIDTH_DEG} deg")
    print(f"[INFO] Beamforming: N_BEAMS={N_BEAMS} "
          f"(0=omni, {len(BEAM_CENTERS)} centers × {len(BEAM_WIDTHS)} widths)")


    if not TS_FILE.exists():
        raise FileNotFoundError(f"Missing timeslot file: {TS_FILE}")

    df_ts = pd.read_csv(TS_FILE, dtype=str, escapechar="\\")
    blk_ts = pd.read_csv(BLK_FILE, dtype=str, escapechar="\\")
    nslots = len(df_ts)
    print(f"[INFO] Loaded {nslots} time slots")

    prev_ranges: dict[str, float] = {}

#-----Read blockage only -----------
    if BLOCKAGE_ONLY_ONESHOT:
        # 只跑一次：slot=0, beam=0；写 marker 后触发 1 个 packet，然后退出
        slot = 0
        beam = 0
        # 1) 预构建该时隙的完整行（block-only 数据源在 blk_ts 中）
        rows_all, curr_ranges = _rows_for_slot_all(blk_ts, slot, prev_ranges)

        # 2) 依束筛选（beam=0），并写 target_data.csv 供雷达仿真器读取
        rows_beam = _apply_beam(rows_all, beam)
        rows_beam = _ensure_min_one_target(rows_beam, beam)
        _write_target_data(rows_beam)

        # 3) 在 radar_chan.csv 写入 MARKER（slot=0, beam=0）
        _append_radar_chan_marker(slot, beam)
        time.sleep(MARKER_SETTLE_S)

        # 4) 触发 10 个包；GNU Radio 将为该包产生一行/多行通道数据
        for _ in range(10):
            _trigger_one_packet(TRIGGER_PACKET_TYPE, TRIGGER_PACKET_SIZE)
            time.sleep(PACKET_INTERVAL_S)

        print(f"[BLOCKAGE-ONLY] wrote marker slot={slot}, "
              f"beam={beam} and triggered 10 packets. rows_in_beam={len(rows_beam)}")
        return


    for slot in range(nslots):
        # 1) 预构建该时隙的完整行
        rows_all, curr_ranges = _rows_for_slot_all(df_ts, slot, prev_ranges)

        for b in range(N_BEAMS):
            # 2) 依束筛选目标+遮挡，并写 target_data.csv 供雷达仿真器读取
            rows_beam = _apply_beam(rows_all, b)
            rows_beam = _ensure_min_one_target(rows_beam, b)
            _write_target_data(rows_beam)

            # 3) 在 radar_chan.csv 里写入 marker，标记即将产生的 10 条通道数据
            _append_radar_chan_marker(slot, b)
            time.sleep(MARKER_SETTLE_S)

            # 4) 触发 10 个包；GNU Radio 将为每个包产生一行/多行通道数据
            for k in range(PACKETS_PER_BEAM):
                # _write_target_data(rows_beam)
                _trigger_one_packet(TRIGGER_PACKET_TYPE, TRIGGER_PACKET_SIZE)
                time.sleep(PACKET_INTERVAL_S)

            print(f"[SLOT {slot}] [BEAM {b:2d}/{N_BEAMS-1:2d}] rows_in_beam={len(rows_beam)} -> triggered {PACKETS_PER_BEAM} packets")

        # 仅在完成该时隙所有波束后更新 prev_ranges（速度估计按时隙）
        prev_ranges = curr_ranges

    print("[DONE] All slots processed.")


if __name__ == "__main__":
    time.sleep(2)  # 等待文件系统稳定
    main()
