#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
import re
from typing import List, Optional, Tuple

import numpy as np
import pandas as pd

# ============== radar_chan.csv 解析 ==============
# 形如: "# MARKER, slot=0, beam=0, ts=2025-08-19 17:38:34.042"
_MARKER_RE = re.compile(
    r"#\s*MARKER,\s*slot\s*=\s*(\d+)\s*,\s*beam\s*=\s*(\d+)\s*,\s*ts\s*=\s*([^\r\n]+)",
    re.IGNORECASE,
)

# 复数对: (real,imag) 允许科学计数法
_NUM = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?"
_PAIR_RE = re.compile(rf"\(\s*({_NUM})\s*,\s*({_NUM})\s*\)")

def _extract_radar_csi_matrix(
    radar_csv_path: str, slot_id: int, beam_id: int, rows: int = 64, cols: int = 8
) -> np.ndarray:
    """
    从指定 (slot, beam) 段提取复数对，并组装为 rows×cols 的复数矩阵 (np.complex128)。
    若提取到的复数个数 >= rows*cols，则截取前 rows*cols。
    若个数为 0，则返回 shape=(0,0)。
    若个数为 k 且 k%cols==0，但 k!=rows*cols，则按 (k/cols, cols) 形状返回。
    其他不足情形以 0+0j 右侧补齐到 rows*cols。
    """
    in_block = False
    buf: List[str] = []

    with open(radar_csv_path, "r", encoding="utf-8", errors="ignore") as f:
        for raw in f:
            line = raw.strip()
            m = _MARKER_RE.match(line)
            if m:
                s = int(m.group(1)); b = int(m.group(2))
                in_block = (s == slot_id and b == beam_id)
                # 命中新的目标段 -> 清空缓冲
                if in_block:
                    buf.clear()
                continue
            if not in_block:
                continue
            if not line or line.startswith("#"):
                continue
            buf.append(line)

    if not buf:
        return np.empty((0, 0), dtype=np.complex128)

    text = " ".join(buf)
    pairs = _PAIR_RE.findall(text)
    if not pairs:
        return np.empty((0, 0), dtype=np.complex128)

    comp = np.array(
        [complex(float(r), float(i)) for (r, i) in pairs],
        dtype=np.complex128,
    )
    need = rows * cols
    n = comp.size

    if n >= need:
        return comp[:need].reshape(rows, cols)
    if n > 0 and (n % cols == 0):
        return comp.reshape(n // cols, cols)

    # 不足且无法整除 -> 用 0+0j 补齐到 rows*cols
    out = np.zeros(need, dtype=np.complex128)
    out[:n] = comp
    return out.reshape(rows, cols)

# ============== comm_sim.csv 解析 ==============
# 你的 comm_sim.csv 头: slot,id,beam,CRC,SNR
# 但仍做鲁棒匹配，兼容大小写/空格/下划线/别名
_COL_CANDIDATES = {
    "slot": ["slot", "time_slot", "timeslot", "slot_id"],
    "beam": ["beam", "beam_id"],
    "user": ["id", "target_id", "tid", "user", "user_id", "ue", "ue_id"],
    "crc":  ["crc", "crc_flag", "crc_ok", "crcpass"],
    "snr":  ["snr", "snr_db", "snr_est", "snrest", "snr_estimate"],
}

def _normalize(s: str) -> str:
    return "".join(ch for ch in s.lower() if ch.isalnum())

def _resolve_col(df: pd.DataFrame, key: str) -> Optional[str]:
    cols = list(df.columns)
    lower_map = {c.lower(): c for c in cols}
    norm_map  = {_normalize(c): c for c in cols}

    for cand in _COL_CANDIDATES[key]:
        if cand.lower() in lower_map:
            return lower_map[cand.lower()]
    for cand in _COL_CANDIDATES[key]:
        cn = _normalize(cand)
        if cn in norm_map:
            return norm_map[cn]
    for cand in _COL_CANDIDATES[key]:
        cn = _normalize(cand)
        for c in cols:
            if cn in _normalize(c) or _normalize(c) in cn:
                return c
    if key == "user":
        for c in cols:
            if ("user" in c.lower()) or (re.search(r"\bue\b", c.lower())):
                return c
    return None

def _mask_eq(series: pd.Series, val) -> pd.Series:
    s_num = pd.to_numeric(series, errors="coerce")
    if not s_num.isna().all():
        v_num = pd.to_numeric(pd.Series([val]), errors="coerce").iloc[0]
        return s_num == v_num
    return series.astype(str).str.strip() == str(val)

def _fetch_comm_crc_snr(
    comm_csv_path: str, slot_id: int, beam_id: int, user_id: int
) -> Tuple[Optional[int], Optional[float]]:
    df = pd.read_csv(comm_csv_path, engine="python")

    slot_col = _resolve_col(df, "slot")
    beam_col = _resolve_col(df, "beam")
    user_col = _resolve_col(df, "user")
    crc_col  = _resolve_col(df, "crc")
    snr_col  = _resolve_col(df, "snr")

    if slot_col is None or beam_col is None:
        raise ValueError(
            f"comm_sim.csv 缺少必要列（已找到: slot={slot_col}, beam={beam_col}, user={user_col}）。"
        )

    q = _mask_eq(df[slot_col], slot_id) & _mask_eq(df[beam_col], beam_id)
    if user_col is not None:
        q = q & _mask_eq(df[user_col], user_id)
    else:
        print(f"[WARN] 未识别到 user/id 列，按 slot+beam 过滤。现有列: {list(df.columns)}")

    sub = df.loc[q]
    if sub.empty:
        return None, None

    pick = sub.sample(n=1).iloc[0]  # 多条随机一条
    crc = int(pick[crc_col]) if (crc_col in df.columns and pd.notna(pick[crc_col])) else None
    snr = float(pick[snr_col]) if (snr_col in df.columns and pd.notna(pick[snr_col])) else None
    return crc, snr

def _is_static_user(user_id) -> bool:
    """
    判断是否为 static 用户 (id=101)。
    允许传入 int 或 str，两者都能识别。
    """
    try:
        return int(str(user_id).strip()) == 101
    except Exception:
        return str(user_id).strip().lower() == "101"


# ============== 对外接口 ==============
def query_entry(
    slot_id: int,
    beam_id: int,
    user_id: int,
    radar_csv_path: str = "/home/haocheng/RL_Beamforming_Collaboration_UMich/demo_data/radar_chan.csv",
    comm_csv_path: str = "/home/haocheng/RL_Beamforming_Collaboration_UMich/demo_data/comm_sim.csv",
) -> Tuple[np.ndarray, Optional[int], Optional[float]]:
    """
    返回:
      radar_csi: 复数矩阵，优先 64×8
      crc, snr : 对应 comm 记录
    规则补充：
      - 若 user_id == 101 (static)，则无论传入 slot_id 为多少，统一用 slot=0 查找 radar/comm。
      - beam_id == 0 时，只返回 radar_csi；crc/snr 为 None。
    """
    # —— 关键逻辑：static(id=101) 强制使用 slot=0 ——
    effective_slot = 0 if _is_static_user(user_id) else slot_id

    # Radar: 从 effective_slot 提取
    radar_csi = _extract_radar_csi_matrix(
        radar_csv_path, effective_slot, beam_id, rows=64, cols=8
    )

    if beam_id == 0:
        return radar_csi, None, None

    # Comm: 也用 effective_slot
    crc, snr = _fetch_comm_crc_snr(
        comm_csv_path, effective_slot, beam_id, user_id
    )
    return radar_csi, crc, snr