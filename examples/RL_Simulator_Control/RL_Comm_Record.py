#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RL_Comm_Sim_Record.py

Flow
----
For every time slot `t` in targets_flat.csv:
  1) STATIC target
     - Read static target's (range, angle) once at the beginning and send via UDP (same as comm_target_sim). Do NOT resend in later slots.
     - **Only at the first slot where static is detected**, iterate beams **b = 1..N_BEAMS** (no omni) to collect comm (10 packets/beam). Later slots **skip** static beam loop.
  2) MOVING target
     - If moving position exists at slot t: send it via UDP, then iterate beams **b = 1..N_BEAMS** (no omni) and send TEN packets per beam; after each packet, read CRC & data_SNR and append to comm_sim.csv.
     - If missing (occluded): for **EACH beam b = 1..N_BEAMS**, append **TEN rows** with CRC=0 and SNR=-10 (no-comm sentinel).

Assumptions
----------
- UDP host/port match comm_target_sim (127.0.0.1:52002) and payload is PMT dict
  with keys 'theta_deg' and 'distance_m'.
- data_interface.py provides write_packet_data, load_comm_data, write_radar_data,
  and the RadarData/PacketData classes.
- targets_flat.csv provides columns: slot (or time_slot), id, type (static/moving),
  range_m, angle_deg. Angle convention: degrees in [-90, 90] from +y axis.

Edit paths and constants below to match your env.
"""

from __future__ import annotations

import csv
import math
import socket
from pathlib import Path
from datetime import datetime
from time import sleep
from typing import Dict, List, Tuple, Optional

import pandas as pd
import numpy as np
import time

# PMT dict serialization for UDP (same as comm_target_sim)
import pmt

# Interface to flowgraph files
import data_interface as DI  # RadarData, PacketData, load_comm_data, write_* APIs

# ================== PATHS & IO CONFIG ==================
# Simulator inputs
SIM_DIR = Path("/home/haocheng/O-JRC/examples/RL_ResourceAllocation_Data")
TARGETS_FLAT_FILE = SIM_DIR / "targets_flat.csv"   # time-flattened targets

# Flowgraph watched files (adjust to your FG setup)
FG_DIR = Path("/home/haocheng/O-JRC/examples/data")
RADAR_DATA_CSV = FG_DIR / "radar_data.csv"         # DI.write_radar_data writes here
PACKET_DATA_CSV = FG_DIR / "packet_data.csv"       # DI.write_packet_data triggers here
COMM_LOG_CSV    = FG_DIR / "comm_log.csv"          # FG appends comm results here

# Our output
COMM_SIM_CSV    = SIM_DIR / "comm_sim.csv"         # columns: slot,id,beam,CRC,SNR

# UDP target channel (must match your comm_target_sim)
UDP_HOST = "127.0.0.1"
UDP_PORT = 52002

# # ================== BEAMBOOK ==================
# # Beam ids: 1..N map to centers below (no omni)
# BEAM_WIDTH_DEG = 20.0
# BEAM_CENTERS = list(range(-60, 61, 5))    # -60,-55,...,60  (25 beams)
# N_BEAMS = len(BEAM_CENTERS)

# ================== BEAMBOOK ==================
# 0 -> omni，其余：center∈[-60..60], step=10；width∈{10,30,50}
OMNI_ID = 0
OMNI_WIDTH_DEG = 360.0
BEAM_CENTERS = list(range(-60, 61, 10))   # [-60,-50,...,60]
BEAM_WIDTHS  = [20.0, 40.0, 60.0]

# 展平后的 beambook：id=0 是 omni；其余按 (center,width) 的笛卡尔积顺序
BEAM_BOOK = [(None, OMNI_WIDTH_DEG)] + [(c, w) for c in BEAM_CENTERS for w in BEAM_WIDTHS]
N_BEAMS = len(BEAM_BOOK)  # = 1 + 13*3 = 40

def _beam_params(beam_index: int) -> tuple[float | None, float]:
    if not (0 <= beam_index < N_BEAMS):
        raise ValueError(f"beam_index {beam_index} out of range (0..{N_BEAMS-1})")
    return BEAM_BOOK[beam_index]

# ================== PACKET CONFIG ==================
PACKETS_PER_BEAM = 50
TRIGGER_PACKET_TYPE = 2   # 1=NDP, 2=DATA
TRIGGER_PACKET_SIZE = 100
PACKET_INTERVAL_S  = 0.08  # spacing between packets
READ_DELAY_S       = 0.08  # small delay before reading comm_log

# ================== DEBUG / CONTROL ==================
# Limit how many slots to process (None => all). Useful for quick sanity checks.
LIMIT_SLOTS: Optional[int] = None
# Print progress per beam
VERBOSE = True
# # Comm log read gating (ensure we read NEW entry per packet)
# COMM_READ_TIMEOUT_S = 1.0      # max seconds to wait for a new comm_log line
# COMM_POLL_INTERVAL_S = 0.01    # polling interval while waiting

# ================== HELPERS ==================

def _now_ts_hms_ms() -> str:
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]


def _ensure_comm_sim_header(path: Path):
    if not path.exists() or path.stat().st_size == 0:
        with path.open("w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["slot", "id", "beam", "CRC", "SNR"])  # header


def _append_comm_row(slot: int, tid: str, beam: int, crc: int, snr: float):
    with COMM_SIM_CSV.open("a", newline="") as f:
        w = csv.writer(f)
        w.writerow([slot, tid, beam, crc, f"{snr:.4f}"])


# def _deg_from_xy(x: float, y: float) -> float:
#     """Angle measured from +y axis, left(-), right(+), in degrees [-90,90]."""
#     # standard atan2(y, x) gives angle from +x; we need from +y
#     ang_rad = math.atan2(x, y)  # swap to measure from +y
#     ang_deg = math.degrees(ang_rad)
#     # clamp for numeric noise
#     return max(-90.0, min(90.0, ang_deg))


# def _range_from_xy(x: float, y: float) -> float:
#     return math.hypot(x, y)


def _load_targets_flat() -> pd.DataFrame:
    if not TARGETS_FLAT_FILE.exists() or TARGETS_FLAT_FILE.stat().st_size == 0:
        raise FileNotFoundError(f"Missing or empty targets_flat.csv: {TARGETS_FLAT_FILE}")
    df = pd.read_csv(TARGETS_FLAT_FILE, dtype=str, comment="#")
    # normalize column names
    df.columns = [c.strip() for c in df.columns]
    rename = {
        "time_slot": "slot", "t": "slot",
        "target_id": "id",
        "theta_deg": "angle_deg",
    }
    for k, v in list(rename.items()):
        if k in df.columns:
            df.rename(columns={k: v}, inplace=True)
    required = ["slot", "id", "type", "range_m", "angle_deg"]
    for col in required:
        if col not in df.columns:
            raise ValueError(f"targets_flat.csv missing required column: {col}")
    df["slot"] = df["slot"].astype(int)
    df["type"] = df["type"].str.strip().str.lower()
    df["range_m"] = df["range_m"].astype(float)
    df["angle_deg"] = df["angle_deg"].astype(float)
    return df


def _send_udp_target(theta_deg: float, distance_m: float):
    d = pmt.make_dict()
    d = pmt.dict_add(d, pmt.intern('theta_deg'),  pmt.from_double(float(theta_deg)))
    d = pmt.dict_add(d, pmt.intern('distance_m'), pmt.from_double(float(distance_m)))
    payload = pmt.serialize_str(d)
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.sendto(payload, (UDP_HOST, UDP_PORT))


def _trigger_packet():
    pkt = DI.PacketData(_now_ts_hms_ms(), TRIGGER_PACKET_TYPE, TRIGGER_PACKET_SIZE)
    DI.write_packet_data(pkt, str(PACKET_DATA_CSV))


def _write_beam_meta(range_m: float, beam_center_deg: float):
    rd = DI.RadarData(_now_ts_hms_ms(), 0.0, 0.0, float(range_m), float(beam_center_deg))
    DI.write_radar_data(rd, str(RADAR_DATA_CSV))


# def _wait_new_comm(last_ts: Optional[str]):
#     """Poll comm_log via DI.load_comm_data until timestamp changes or timeout.
#     Returns CommData or None on timeout/err.
#     """
#     deadline = time.time() + COMM_READ_TIMEOUT_S
#     while time.time() < deadline:
#         try:
#             c = DI.load_comm_data(str(COMM_LOG_CSV))
#         except Exception:
#             c = None
#         if c is not None:
#             ts = getattr(c, "timestamp", None)
#             if ts != last_ts:
#                 return c
#         sleep(COMM_POLL_INTERVAL_S)
#     return None


# ================== MAIN ==================

def main():
    df = _load_targets_flat()
    slots: List[int] = sorted(df["slot"].unique().tolist())
    if LIMIT_SLOTS is not None:
        slots = slots[:LIMIT_SLOTS]

    #print(f"[INFO] Loaded {len(slots)} slots | N_BEAMS={N_BEAMS} | packets/beam={PACKETS_PER_BEAM}", flush=True)
    print(
    f"[INFO] Loaded {len(slots)} slots | N_BEAMS={N_BEAMS} (0=omni, using 1..{N_BEAMS-1}) "
    f"| packets/beam={PACKETS_PER_BEAM}",
    flush=True)
    print(f"[INFO] SIM_DIR={SIM_DIR}")
    print(f"[INFO] FG_DIR={FG_DIR}")
    print(f"[INFO] OUTPUT={COMM_SIM_CSV}")

    # Precompute the set of moving IDs (if any) to use when slot is occluded
    moving_ids_overall = df.loc[df["type"].isin(["moving","move","m"]) , "id"].unique().tolist()

    _ensure_comm_sim_header(COMM_SIM_CSV)

    static_udp_sent = False
    static_beams_done = False

    # track the latest comm_log timestamp we've seen; used to detect NEW entries
    last_comm_ts: Optional[str] = None

    for slot in slots:
        if VERBOSE:
            print(f"[SLOT {slot}] start", flush=True)
        df_slot = df[df["slot"] == slot]

        # ---- STATIC ----
        df_static = df_slot[df_slot["type"].isin(["static","s","stat"])]
        static_row: Optional[pd.Series] = df_static.iloc[0] if len(df_static) > 0 else None
        if static_row is not None:
            s_id = str(static_row["id"]) if "id" in static_row else "static"
            s_rng = float(static_row["range_m"])  # meters
            s_ang = float(static_row["angle_deg"])  # degrees
            # 1) inform FG of target position via UDP (only once at the beginning)
            if not static_udp_sent:
                _send_udp_target(theta_deg=s_ang, distance_m=s_rng)
                if VERBOSE:
                    print(f"[SLOT {slot}] static UDP sent: id={s_id}, r={s_rng:.2f}m, a={s_ang:.1f}°", flush=True)
                static_udp_sent = True
            # 2) iterate beams and collect comm ONLY ONCE (first encountered slot)
            if not static_beams_done:
                for b in range(1, N_BEAMS):
                    # beam_center = float(BEAM_CENTERS[b-1])
                    center, _ = _beam_params(b)       # b>=1 时 center 一定非 None
                    beam_center = float(center if center is not None else 0.0)
                    _write_beam_meta(range_m=s_rng, beam_center_deg=beam_center)
                    for _ in range(PACKETS_PER_BEAM):
                        _trigger_packet()
                        time.sleep(READ_DELAY_S)  # wait for FG to write comm_log
                        try:
                            c = DI.load_comm_data(str(COMM_LOG_CSV))
                        except Exception:
                            c = None
                        ts = getattr(c, "timestamp", None) if c is not None else None
                        if (c is None) or (ts == last_comm_ts):
                            _append_comm_row(slot, s_id, b, 0, -10.0)
                        else:
                            _append_comm_row(slot, s_id, b, int(c.CRC), float(c.data_snr))
                            last_comm_ts = ts
                        sleep(PACKET_INTERVAL_S)
                static_beams_done = True
        else:
            # no static this slot; do nothing for static
            pass
        # ---- MOVING ----
        df_moving = df_slot[df_slot["type"].isin(["moving","move","m"])]
        if len(df_moving) > 0:
            m_row = df_moving.iloc[0]
            m_id = str(m_row["id"]) if "id" in m_row else "moving"
            m_rng = float(m_row["range_m"])  # meters
            m_ang = float(m_row["angle_deg"])  # degrees
            # send moving position for this slot
            _send_udp_target(theta_deg=m_ang, distance_m=m_rng)
            # per-beam loop with packets
            for b in range(1, N_BEAMS):
                # beam_center = float(BEAM_CENTERS[b-1])
                center, _ = _beam_params(b)       # b>=1 时 center 一定非 None
                beam_center = float(center if center is not None else 0.0)
                _write_beam_meta(range_m=m_rng, beam_center_deg=beam_center)
                last_ts: Optional[str] = None  # 仅用于与上一次读到的时间戳比较
                for _ in range(PACKETS_PER_BEAM):
                    _trigger_packet()
                    time.sleep(READ_DELAY_S)  # wait for FG to write comm_log
                    try:
                        c = DI.load_comm_data(str(COMM_LOG_CSV))
                    except Exception:
                        c = None
                    ts = getattr(c, "timestamp", None) if c is not None else None
                    if (c is not None) and (ts != last_ts):
                        _append_comm_row(slot, m_id, b, int(c.CRC), float(c.data_snr))
                        last_ts = ts
                    else:
                        _append_comm_row(slot, m_id, b, 0, -10.0)
                    sleep(PACKET_INTERVAL_S)
        else:
            # occluded -> for EACH beam, write TEN sentinel rows (CRC=0,SNR=-10)
            # try choose a stable ID if unique overall
            occl_id = "moving"
            moving_ids_overall = df.loc[df["type"].isin(["moving","move","m"]) , "id"].unique().tolist()
            if len(moving_ids_overall) == 1:
                occl_id = str(moving_ids_overall[0])
            for b in range(1, N_BEAMS):
                for _ in range(PACKETS_PER_BEAM):
                    _append_comm_row(slot, occl_id, b, 0, -10.0)

    print("[DONE] COMM sim collection written to:", COMM_SIM_CSV, flush=True)


if __name__ == "__main__":
    time.sleep(2)  # wait for FS to settle
    main()
