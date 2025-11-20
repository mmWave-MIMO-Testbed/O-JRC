#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
import re
from typing import List, Optional, Tuple
import random

import numpy as np
import pandas as pd

from scipy.ndimage import maximum_filter, label, gaussian_filter
import os
if "MPLBACKEND" in os.environ:
    del os.environ["MPLBACKEND"]

import matplotlib.pyplot as plt



# ============== radar_chan.csv 解析 ==============
# 形如: "# MARKER, slot=0, beam=0, ts=2025-08-19 17:38:34.042"
_MARKER_RE = re.compile(
    r"#\s*MARKER,\s*slot\s*=\s*(\d+)\s*,\s*beam\s*=\s*(\d+)\s*,\s*ts\s*=\s*([^\r\n]+)",
    re.IGNORECASE,
)

# 复数对: (real,imag) 允许科学计数法
_NUM = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?"
_PAIR_RE = re.compile(rf"\(\s*({_NUM})\s*,\s*({_NUM})\s*\)")

# def _extract_radar_csi_matrix(
#     radar_csv_path: str, slot_id: int, beam_id: int, rows: int = 64, cols: int = 8
# ) -> np.ndarray:
#     """
#     从指定 (slot, beam) 段提取复数对，并组装为 rows×cols 的复数矩阵 (np.complex128)。
#     若提取到的复数个数 >= rows*cols，则截取前 rows*cols。
#     若个数为 0，则返回 shape=(0,0)。
#     若个数为 k 且 k%cols==0，但 k!=rows*cols，则按 (k/cols, cols) 形状返回。
#     其他不足情形以 0+0j 右侧补齐到 rows*cols。
#     """
#     in_block = False
#     buf: List[str] = []

#     with open(radar_csv_path, "r", encoding="utf-8", errors="ignore") as f:
#         for raw in f:
#             line = raw.strip()
#             m = _MARKER_RE.match(line)
#             if m:
#                 s = int(m.group(1)); b = int(m.group(2))
#                 in_block = (s == slot_id and b == beam_id)
#                 # 命中新的目标段 -> 清空缓冲
#                 if in_block:
#                     buf.clear()
#                 continue
#             if not in_block:
#                 continue
#             if not line or line.startswith("#"):
#                 continue
#             buf.append(line)

#     if not buf:
#         return np.empty((0, 0), dtype=np.complex128)

#     text = " ".join(buf)
#     pairs = _PAIR_RE.findall(text)
#     if not pairs:
#         return np.empty((0, 0), dtype=np.complex128)

#     comp = np.array(
#         [complex(float(r), float(i)) for (r, i) in pairs],
#         dtype=np.complex128,
#     )
#     need = rows * cols
#     n = comp.size

#     if n >= need:
#         return comp[:need].reshape(rows, cols, order="F")
#     if n > 0 and (n % cols == 0):
#         return comp.reshape(n // cols, cols, order="F")

#     # 不足且无法整除 -> 用 0+0j 补齐到 rows*cols
#     out = np.zeros(need, dtype=np.complex128)
#     out[:n] = comp
#     return out.reshape(rows, cols)

def _extract_radar_csi_matrix(
    radar_csv_path: str, slot_id: int, beam_id: int, rows: int = 64, cols: int = 8
) -> np.ndarray:
    """
    在同一 (slot_id, beam_id) 的所有 MARKER 区间内，收集“数据行”，
    随机挑一行解析为 CSI：
      - 若该行复数对数量 == rows*cols：按 (rows, cols) 列优先 reshape 返回
      - 否则若数量能被 cols 整除：按 (k//cols, cols) 列优先 reshape 返回（不截断不补零）
      - 若当前随机行不满足，换另一行继续；全部都不满足则返回空 (0,0)
    只在同一 slot/beam 内随机，不跨 slot/beam。
    """
    need = rows * cols
    candidate_lines: List[str] = []
    in_block = False

    with open(radar_csv_path, "r", encoding="utf-8", errors="ignore") as f:
        for raw in f:
            line = raw.strip()
            m = _MARKER_RE.match(line)
            if m:
                # 进入目标段后，遇到下一条 MARKER 就停止扫描（早停）
                if in_block:
                    break
                s = int(m.group(1)); b = int(m.group(2))
                in_block = (s == slot_id and b == beam_id)
                continue
            if not in_block:
                continue
            if not line or line.startswith("#"):
                continue
            candidate_lines.append(line)

    if not candidate_lines:
        return np.empty((0, 0), dtype=np.complex128)

    # 随机顺序尝试每一行，直到命中
    order = list(range(len(candidate_lines)))
    random.shuffle(order)

    # 先严格匹配 rows*cols
    for idx in order:
        pairs = _PAIR_RE.findall(candidate_lines[idx])
        if not pairs:
            continue
        comp = np.array([complex(float(r), float(i)) for (r, i) in pairs],
                        dtype=np.complex128)
        if comp.size == need:
            return comp.reshape(rows, cols, order="F")  # 列优先，和 MATLAB 对齐

    # 都不满足
    return np.empty((0, 0), dtype=np.complex128)


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
      - 若 user_id == 101 (static)，则无论传入 slot_id 为多少，统一用 slot=0 查找 comm。
      - beam_id == 0 时，只返回 radar_csi；crc/snr 为 None。
    """
    # —— 关键逻辑：static(id=101) 强制使用 slot=0 ——
    effective_slot = 0 if _is_static_user(user_id) else slot_id

    # Radar: 从 curr_slot 提取
    radar_csi = _extract_radar_csi_matrix(
        radar_csv_path, slot_id, beam_id, rows=64, cols=8
    )

    if beam_id == 0:
        return radar_csi, None, None

    # Comm: 用 effective_slot
    crc, snr = _fetch_comm_crc_snr(
        comm_csv_path, effective_slot, beam_id, user_id
    )
    return radar_csi, crc, snr

# ======== DSP: CSI -> Range-Angle Image (DFT) ========
def _csi_to_range_angle(
    csi: np.ndarray,
    *,
    Fc: float = 24e9,
    B: float = 125e6,
    dtx: float = 6.35e-3,
    interp_range: int = 16,
    interp_angle: int = 32,
    flip_lr: bool = True,
    return_db: bool = False,
    normalize: bool = True,     # 新增：是否进行最大值归一化
    eps: float = 1e-12          # 新增：避免 log(0) 的小量
):
    """
    将形如 [Nsc x (Ntx*Nrx)] 的 CSI 矩阵转换为 range-angle 图像（与 MATLAB 版本等价）。
    返回: (image, angle_bins_deg, range_bins_m)
      - image: 归一化矩阵（线性或 dB），shape = [interp_range*Nsc, interp_angle*(Ntx*Nrx)+1]
      - angle_bins_deg: 角度刻度（度）
      - range_bins_m: 距离刻度（米）
    """
    if csi.size == 0:
        return np.empty((0, 0)), np.array([]), np.array([])

    # 常量/尺寸
    # 光速
    c = 299792458.0

    Nsc, Nv = csi.shape

    fft_len_range = interp_range * Nsc
    # 关键：与 MATLAB 对齐的 +1
    fft_len_angle = interp_angle * Nv + 1

    win_r = np.hamming(Nsc)
    win_a = np.hamming(Nv)
    x = (win_r[:, None] * csi) * win_a[None, :]

    ang_profiles = np.fft.fft(x, n=fft_len_angle, axis=1)
    ang_profiles = np.fft.fftshift(ang_profiles, axes=1) / float(Nv)

    ra = np.fft.ifft(ang_profiles, n=fft_len_range, axis=0)
    ra = (fft_len_range / float(Nsc)) * ra

    mag = np.abs(ra)

    # —— 先生成 angle_bins —— 
    k = np.arange(fft_len_angle, dtype=float) - float(fft_len_angle // 2)
    s = (c / Fc) / (dtx * float(fft_len_angle)) * k
    s = np.clip(s, -1.0, 1.0)
    angle_bins = np.degrees(np.arcsin(s))

    # —— 再可选左右翻转 & 同步角度刻度 —— 
    if flip_lr:
        mag = np.fliplr(mag)
        angle_bins = np.flip(angle_bins)   # 保证列索引与角度一一对应

    # maxval = mag.max() if mag.size else 0.0
    # mag_norm = (mag / maxval) if maxval > 0 else mag
    # img = 10.0*np.log10(np.maximum(mag_norm**2, 1e-12)) if return_db else mag_norm

    # —— 是否归一化 & 是否返回 dB ——  
    maxval = mag.max() if mag.size else 0.0

    if return_db:
        if normalize:
            # 相对 dB（最大值为 0 dB）
            if maxval > 0:
                img_db = 10.0 * np.log10(np.maximum((mag / maxval) ** 2, eps))
            else:
                img_db = 10.0 * np.log10(np.maximum(mag ** 2, eps))  # 全零兜底
            img = img_db
        else:
            # 绝对 dB（功率 dB）
            img = 10.0 * np.log10(np.maximum(mag ** 2, eps))
    else:
        if normalize:
            img = (mag / maxval) if maxval > 0 else mag
        else:
            img = mag  # 原始幅度

    range_res = c / (2.0 * B)
    range_bins = np.arange(fft_len_range, dtype=float) * (range_res / float(interp_range))
    return img, angle_bins, range_bins


def query_entry_radar_image(
    slot_id: int,
    beam_id: int,
    user_id: int,
    *,
    radar_csv_path: str = "/home/haocheng/RL_Beamforming_Collaboration_UMich/demo_data/radar_chan.csv",
    comm_csv_path: str = "/home/haocheng/RL_Beamforming_Collaboration_UMich/demo_data/comm_sim.csv",
    output: str = "linear",   # "linear" 或 "db"
    Fc: float = 24e9,
    B: float = 125e6,
    dtx: float = 6.35e-3,
    interp_range: int = 16,
    interp_angle: int = 32,
    flip_lr: bool = False,
    normalize: bool = True,     # 新增：是否进行最大值归一化
):
    """
    与 query_entry 平行的接口：返回处理后的 range-angle 图像矩阵。
    返回:
      image, angle_bins, range_bins, crc, snr
    备注:
      - 仍继承 static 用户 (id=101) 强制 slot=0 的逻辑（复用 query_entry）
      - beam_id=0 时 CRC/SNR 为 None，但仍返回图像
    """
    # 先取 CSI & 通信指标（保持与现有逻辑一致）
    csi, crc, snr = query_entry(
        slot_id=slot_id,
        beam_id=beam_id,
        user_id=user_id,
        radar_csv_path=radar_csv_path,
        comm_csv_path=comm_csv_path,
    )

    # 将 CSI 转 range-angle 图像
    img, angle_bins, range_bins = _csi_to_range_angle(
        csi,
        Fc=Fc, B=B, dtx=dtx,
        interp_range=interp_range,
        interp_angle=interp_angle,
        flip_lr=flip_lr,
        return_db=(output.lower() == "db"),
        normalize=normalize,
    )
    return img, angle_bins, range_bins, crc, snr


# ======== Range-Angle Image -> World XY Grid (average pooling over cells) ========
def ra_image_to_world_grid(
    img: np.ndarray,
    angle_bins_deg: np.ndarray,
    range_bins_m: np.ndarray,
    *,
    x_min: float = -4.0,
    x_max: float = +4.0,
    y_min: float =  0.0,
    y_max: float = +10.0,
    cell_size_m: float = 0.1,
    assume_angle_from_pos_y: bool = True,  # 角度相对 +y 轴（与你之前设定一致）
    average_in_power: bool = False,        # True: 按功率平均（推荐物理意义更正确）
    input_is_db: bool = False,             # 若传入的是 img_db（dB）
    return_db: bool = False                # 返回 dB（仅当 average_in_power=True 时有意义）
):
    """
    将 range-angle 图像映射到世界坐标网格 (x,y)，对每个网格内的像素进行平均。
    参数:
      - img: 形状 [R, A]，行=range_bins，列=angle_bins；可为线性幅度或 dB
      - angle_bins_deg: [A]，列对应角度(度)。若你对图像做过左右翻转，应同步 np.flip 角度刻度！
      - range_bins_m:  [R]，行对应距离(米)
      - average_in_power:
          False: 直接平均 img 数值（img 为线性幅度时可用）
          True:  先将输入转为“功率”再平均；若 input_is_db=False 且 img 为幅度，则用 img**2
      - input_is_db:
          True 时认为 img 是 dB（例如你得到的 img_db），会先转回线性功率再平均
      - return_db:
          仅 average_in_power=True 有意义；对平均后的功率再转 dB 返回
    返回:
      grid_avg: [Ny, Nx]，每个网格的平均值（线性或 dB）
      grid_cnt: [Ny, Nx]，每个网格累积样本数
      x_centers: [Nx]，网格中心 x (m)
      y_centers: [Ny]，网格中心 y (m)
    说明:
      - 映射采用：x = r*sin(theta), y = r*cos(theta)，theta 相对 +y 轴，左负右正（与你设定一致）。
      - 不在世界范围内的像素会被忽略；没有像素落入的格子返回 NaN。
    """
    if img.size == 0 or angle_bins_deg.size == 0 or range_bins_m.size == 0:
        return (np.empty((0, 0)), np.empty((0, 0)), np.array([]), np.array([]))

    # 角度/距离网格 -> 笛卡尔坐标
    theta_rad = np.radians(angle_bins_deg)  # [A]
    r = range_bins_m                        # [R]

    # 广播到 [R, A]
    # 注意: 这里按你的定义，theta 相对 +y 轴 => (x,y) = (r*sin, r*cos)
    if not assume_angle_from_pos_y:
        # 如果你的 angle 是相对 +x 轴，则应改为 (x,y)=(r*cos, r*sin)
        raise ValueError("Current implementation assumes angle measured from +y axis.")

    X = r[:, None] * np.sin(theta_rad[None, :])  # [R, A]
    Y = r[:, None] * np.cos(theta_rad[None, :])  # [R, A]

    # 网格尺寸
    Nx = int(np.round((x_max - x_min) / cell_size_m))
    Ny = int(np.round((y_max - y_min) / cell_size_m))
    x_edges = x_min + np.arange(Nx + 1, dtype=float) * cell_size_m
    y_edges = y_min + np.arange(Ny + 1, dtype=float) * cell_size_m
    x_centers = x_min + (np.arange(Nx, dtype=float) + 0.5) * cell_size_m
    y_centers = y_min + (np.arange(Ny, dtype=float) + 0.5) * cell_size_m

    # 将像素映射到网格索引
    ix = np.floor((X - x_min) / cell_size_m).astype(np.int64)  # [R, A]
    iy = np.floor((Y - y_min) / cell_size_m).astype(np.int64)  # [R, A]

    inb = (ix >= 0) & (ix < Nx) & (iy >= 0) & (iy < Ny)
    if not inb.any():
        grid = np.full((Ny, Nx), np.nan, dtype=float)
        cnt = np.zeros((Ny, Nx), dtype=np.int64)
        return grid, cnt, x_centers, y_centers

    # 要平均的数值域
    if average_in_power:
        if input_is_db:
            # img_db = 10*log10(P_norm)，=> P_norm = 10^(img_db/10)
            val = np.power(10.0, img / 10.0)
        else:
            # img 为幅度归一化 => 功率 ~ 幅度^2
            val = np.square(img)
    else:
        # 直接平均输入（若传入的是 dB，这只是算术平均 dB，不推荐，但允许）
        val = img

    # 扁平化 + 原地累加
    ix_f = ix[inb].ravel()
    iy_f = iy[inb].ravel()
    v_f  = val[inb].ravel()
    flat_idx = (iy_f * Nx + ix_f).astype(np.int64)

    sum_grid = np.zeros(Nx * Ny, dtype=float)
    cnt_grid = np.zeros(Nx * Ny, dtype=np.int64)
    np.add.at(sum_grid, flat_idx, v_f)
    np.add.at(cnt_grid, flat_idx, 1)

    sum_grid = sum_grid.reshape(Ny, Nx)
    cnt_grid = cnt_grid.reshape(Ny, Nx)

    with np.errstate(invalid="ignore", divide="ignore"):
        avg_grid = sum_grid / cnt_grid
        avg_grid[cnt_grid == 0] = 1e-14

    # 如需以 dB 返回（仅对“功率平均”有意义）
    if average_in_power and return_db:
        # 避免 log(0)
        avg_grid = 10.0 * np.log10(np.maximum(avg_grid, 1e-12))

    return avg_grid, cnt_grid, x_centers, y_centers

def plot_world_grid(grid_avg, x_c, y_c, *, is_db=True, title=None):
    """把 (Ny,Nx) 的 grid_avg 画成 (x,y) 世界坐标热力图。"""
    if grid_avg is None or np.size(grid_avg) == 0:
        print("grid_avg is empty.")
        return

    # 根据网格中心反推边界，保证像素与物理坐标对齐
    dx = (x_c[1] - x_c[0]) if len(x_c) > 1 else 0.1
    dy = (y_c[1] - y_c[0]) if len(y_c) > 1 else 0.1
    extent = [x_c[0] - dx/2, x_c[-1] + dx/2, y_c[0] - dy/2, y_c[-1] + dy/2]

    img = np.asarray(grid_avg, dtype=float)
    m = np.ma.masked_invalid(img)  # NaN 不显示

    plt.figure(figsize=(7, 5))
    im = plt.imshow(m, extent=extent, origin='lower', aspect='auto')
    plt.xlabel('x (m)')
    plt.ylabel('y (m)')
    cb = plt.colorbar(im)
    cb.set_label('dB' if is_db else 'Power (linear)')
    if title:
        plt.title(title)
    plt.tight_layout()
    plt.show()

def image_to_xylist(
    grid: np.ndarray,
    x_centers: np.ndarray,
    y_centers: np.ndarray,
    *,
    threshold_abs: float = 0.3,
    nms_window_cells: int = 5,        # 奇数，约=2*min_distance+1
    sigma_smooth: Optional[float] = 0.0,
    mask: Optional[np.ndarray] = None,
    top_n: Optional[int] = None
) -> List[Tuple[float, float]]:
    """
    局部极大值+平台合并（取平台内最大值）。
    返回 [(x, y), ...]，按原grid强度从大到小排序。
    """
    if grid.size == 0:
        return []

    g = grid
    if sigma_smooth and sigma_smooth > 0:
        g = gaussian_filter(g, sigma=sigma_smooth)

    size = int(nms_window_cells) if nms_window_cells % 2 == 1 else int(nms_window_cells + 1)
    g_max = maximum_filter(g, size=size, mode="nearest")

    # 候选峰：与局部最大相等且超过阈值
    peaks_mask = (g == g_max) & (g >= threshold_abs)
    if mask is not None:
        peaks_mask &= mask

    # 平台（相同值连通区域）标记
    labeled, num = label(peaks_mask)
    if num == 0:
        return []

    coords = []
    for lab in range(1, num + 1):
        ys, xs = np.where(labeled == lab)
        if ys.size == 0:
            continue
        # 只保留该平台里“原grid数值最大”的那个点
        vals = grid[ys, xs]
        k = int(np.argmax(vals))
        py, px = int(ys[k]), int(xs[k])
        coords.append((float(x_centers[px]), float(y_centers[py]), float(grid[py, px])))

    # 按强度排序并裁剪
    coords.sort(key=lambda t: t[2], reverse=True)
    if top_n is not None:
        coords = coords[:top_n]

    return [(round(x, 4), round(y, 4)) for x, y, _ in coords]