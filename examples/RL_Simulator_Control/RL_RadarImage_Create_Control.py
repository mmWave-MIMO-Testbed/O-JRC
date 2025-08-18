#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import pandas as pd
import csv
import time

# ========= 路径配置 =========
DATA_DIR = Path("/home/haocheng/O-JRC/examples/RL_ResourceAllocation_Data")
TS_FILE  = DATA_DIR / "targets_timeslot.csv"
BLK_FILE = DATA_DIR / "blockage_timeslot.csv"
OUT_FILE = DATA_DIR / "target_data.csv"

# ========= 参数配置 =========
DT_S = 0.1                      # 与生成器一致
USE_RADIAL_VELOCITY = True      # True=计算径向速度；False=全设0
INCLUDE_HEADER = True           # 写入第一行注释头
RCS_BY_ID = { "1": 1.0, "2": 60.0, "101":1.6 }  # 各目标的等效RCS（可按需改）
RCS_DEFAULT_TARGET = 1.0
RCS_BLOCKAGE = 0.8              # 每个遮挡cell的等效RCS（可按需改）
AUTO_INTERVAL_S = 0.5  # 自动模式下的步进间隔（秒）

# ========= 工具函数 =========
def _strip_quotes_and_unescape(s: str) -> str:
    """去掉首尾双引号、还原 '\,' -> ','；空/NaN返回空字符串"""
    if pd.isna(s):
        return ""
    s = str(s)
    if len(s) >= 2 and s[0] == '"' and s[-1] == '"':
        s = s[1:-1]
    # 兼容我们可能用过的 QUOTE_NONE + escapechar="\\"
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
    with OUT_FILE.open("w", newline="") as f:
        # 直接写一行注释头（包含逗号），避免 csv.writer 触发转义问题
        if INCLUDE_HEADER:
            f.write("# range_m,velocity_mps,rcs_m2,azimuth_deg\n")

        # 数值行用 csv.writer；禁止引号，但提供 escapechar 以防将来某字段带逗号
        w = csv.writer(f, delimiter=",", quoting=csv.QUOTE_NONE, escapechar="\\")
        for r, v, rcs, a in rows:
            w.writerow([f"{r:.3f}", f"{v:.3f}", f"{rcs:.4f}", f"{a:.2f}"])

def _build_blockage_rows_from_file() -> list[tuple[float, float, float, float]]:
    dfb = pd.read_csv(BLK_FILE, dtype=str, escapechar="\\")
    if dfb.empty:
        return []
    row = dfb.iloc[0]
    rngs = _parse_float_list(row["range_m"])
    angs = _parse_float_list(row["angle_deg"])
    return [(r, 0.0, RCS_BLOCKAGE, a) for r, a in zip(rngs, angs)]

def _build_rows_for_slot(df_ts: pd.DataFrame, idx: int,
                         prev_ranges: dict[str, float]) -> tuple[list[tuple[float, float, float, float]], dict[str, float]]:
    row = df_ts.iloc[idx]
    n_visible = int(row["n_visible"])
    n_blk = int(row["n_blockage_cells"])

    # 解析列表列
    ids = _parse_str_list(row["ids"]) if n_visible > 0 else []
    rngs_all = _parse_float_list(row["range_m"])
    angs_all = _parse_float_list(row["angle_deg"])

    # 切分为：前 n_visible 是目标；最后 n_blk 是遮挡 cells
    tgt_ranges = rngs_all[:n_visible]
    tgt_angles = angs_all[:n_visible]
    blk_ranges = rngs_all[-n_blk:] if n_blk > 0 else []
    blk_angles = angs_all[-n_blk:] if n_blk > 0 else []

    # 计算径向速度
    curr_ranges = {tid: r for tid, r in zip(ids, tgt_ranges)}
    if USE_RADIAL_VELOCITY:
        v_by_id = {tid: (curr_ranges[tid] - prev_ranges.get(tid, curr_ranges[tid])) / DT_S for tid in curr_ranges}
    else:
        v_by_id = {tid: 0.0 for tid in curr_ranges}

    rows: list[tuple[float, float, float, float]] = []
    # 先写目标
    for tid, r, a in zip(ids, tgt_ranges, tgt_angles):
        rcs = RCS_BY_ID.get(tid, RCS_DEFAULT_TARGET)
        rows.append((r, v_by_id.get(tid, 0.0), rcs, a))
    # 再写遮挡（速度=0）
    rows.extend((r, 0.0, RCS_BLOCKAGE, a) for r, a in zip(blk_ranges, blk_angles))

    return rows, curr_ranges

# ========= 交互循环 =========
def main():
    # 读入 timeslot 表（兼容有/无引号，有反斜杠转义都行）
    df_ts = pd.read_csv(TS_FILE, dtype=str, escapechar="\\")
    nslots = len(df_ts)

    print(f"[INFO] Data dir: {DATA_DIR}")
    print(f"[INFO] Loaded {nslots} time slots from {TS_FILE.name}")
    print(f"[INFO] Writing target_data.csv to {OUT_FILE}")

    # Step 0：先写 blockage only
    blk_rows = _build_blockage_rows_from_file()
    _write_target_data(blk_rows)
    input("[BLOCKAGE ONLY] 已写入 target_data.csv。按回车进入 slot 0（q 退出）：")
    prev_ranges: dict[str, float] = {}

    # 模式选择：1=手动(回车推进)；2=自动(每 AUTO_INTERVAL_S 秒推进)
    mode = input(f"选择运行模式：1=手动回车，2=自动{AUTO_INTERVAL_S:.1f}s推进  [默认1]：").strip()
    if mode not in ("1", "2"):
        mode = "1"

    # Step 1..N：逐时隙
    try:
        for i in range(nslots):
            rows, prev_ranges = _build_rows_for_slot(df_ts, i, prev_ranges)
            _write_target_data(rows)

            if mode == "1":
                user = input(f"[SLOT {i}] 已写入 target_data.csv。回车 -> 下一时隙；q -> 退出：").strip().lower()
                if user == "q":
                    break
            else:
                print(f"[SLOT {i}] 已写入 target_data.csv。（自动模式，{AUTO_INTERVAL_S:.1f}s 后继续）")
                time.sleep(AUTO_INTERVAL_S)

    except KeyboardInterrupt:
        print("\n[INFO] 捕获到 Ctrl+C，提前结束。")

    print("[DONE] 结束。")

if __name__ == "__main__":
    main()
