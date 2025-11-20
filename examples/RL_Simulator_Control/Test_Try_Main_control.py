#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
from RL_Main_Control import query_entry_radar_image
from RL_Main_Control import ra_image_to_world_grid
from RL_Main_Control import plot_world_grid
from RL_Main_Control import image_to_xylist

import numpy as np
import os


BASE_DIR = "/home/haocheng/RL_Beamforming_Collaboration_UMich/demo_data_2"
RADAR_CSV = os.path.join(BASE_DIR, "radar_chan.csv")
COMM_CSV  = os.path.join(BASE_DIR, "comm_sim.csv")

# 显示控制
PRINT_FULL   = True   # True -> 打印完整 CSI；False -> 只预览前 N 行
PREVIEW_ROWS = 1

SHOW_RADAR_HEATMAP: bool = True

# —— 三个输出变量（全局保存）——
OUT_RADAR_CSI = None   # np.ndarray(complex128), 通常 64x8
OUT_CRC       = None   # int 或 None
OUT_SNR       = None   # float 或 None

def main(slot_id: int | None = None,
         beam_id: int | None = None,
         user_id: int | None = None,
         radar_csv_path: str = RADAR_CSV,
         comm_csv_path: str = COMM_CSV,
         print_result: bool = True):
    """
    调用 query_entry 并：
      - 返回 (radar_csi, crc, snr)
      - 将其保存到全局变量 OUT_RADAR_CSI / OUT_CRC / OUT_SNR
    如任一 id 参数为 None，则走交互式输入。
    """
    global OUT_RADAR_CSI, OUT_CRC, OUT_SNR

    try:
        if slot_id is None:
            slot_id = int(input("Time slot id (0..399): ").strip())
        if beam_id is None:
            beam_id = int(input("Beam id 0-39(0=omni): ").strip())
        if user_id is None:
            user_id = int(input("User id: 101 for static, 2 for moving:").strip())
    except ValueError:
        print("输入必须是整数。")
        return None, None, None

    # radar_csi, crc, snr = query_entry_radar_image(
    #     slot_id=slot_id,
    #     beam_id=beam_id,
    #     user_id=user_id,
    #     radar_csv_path=radar_csv_path,
    #     comm_csv_path=comm_csv_path,
    # )
    img, ang_deg, rng_m, _, snr = query_entry_radar_image(
        slot_id=slot_id,
        beam_id=beam_id,
        user_id=user_id,
        radar_csv_path=radar_csv_path,
        comm_csv_path=comm_csv_path,
        flip_lr=False,
        output="linear",
        normalize=False            # 最大值归一化
    )

    grid_avg, grid_cnt, x_c, y_c = ra_image_to_world_grid(
        img, ang_deg, rng_m,
        x_min=-4.0, x_max=+4.0, y_min=0.0, y_max=10.0,
        cell_size_m=0.1,
        average_in_power=True,   # 用功率平均
        input_is_db=False,
        return_db=False,           # 想以 dB 查看平均结果
    )

    cur_radar = grid_avg
    angle_bin = x_c
    range_bin = y_c

    coordsList = image_to_xylist(grid=cur_radar, x_centers=x_c, y_centers=y_c,
                                    threshold_abs=2e-10,
                                    nms_window_cells=5,        # 奇数，约=2*min_distance+1
                                    sigma_smooth=0.0,
                                )
    print(f"coordsList: {coordsList}")

    # print(f"Grid avg shape: {grid_avg.shape}, x_c: {x_c}, y_c: {y_c}")
    if SHOW_RADAR_HEATMAP:
        plot_world_grid(cur_radar, angle_bin, range_bin, is_db=False,
        title=f"World-grid heatmap")

    # 保存到全局变量
    OUT_RADAR_CSI = grid_avg
    OUT_SNR = snr

    if print_result:
        print(f"\n[Result] slot={slot_id}, beam={beam_id}, user={user_id}")
        print(f"SNR: {'NONE' if snr is None else snr}")

        if grid_avg is None or (isinstance(grid_avg, np.ndarray) and grid_avg.size == 0):
            print("RADAR_CSI: []")
        else:
            print(f"RADAR_CSI shape: {grid_avg.shape} (complex128)")
            if PRINT_FULL:
                with np.printoptions(suppress=True, linewidth=200):
                    print(grid_avg)
            else:
                rows_to_show = grid_avg.shape[0] if grid_avg.ndim == 1 else min(PREVIEW_ROWS, grid_avg.shape[0])
                with np.printoptions(suppress=True, linewidth=200):
                    print(grid_avg if grid_avg.ndim == 1 else grid_avg[:rows_to_show])

    return grid_avg, OUT_SNR


if __name__ == "__main__":
    # 直接运行脚本 -> 走交互式输入与默认路径
    main()
