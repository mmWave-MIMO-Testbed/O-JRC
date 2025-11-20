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
USE_RADIAL_VELOCITY = False      # True=计算径向速度；False=全设0
INCLUDE_HEADER = True           # 写入第一行注释头

RCS_BY_ID = { "1": 1.0, "2": 40.0, "101": 0.5 }  # 各目标等效RCS（按需改）
RCS_DEFAULT_TARGET = 1.0
RCS_BLOCKAGE = 0.9              # 每个遮挡cell的等效RCS（按需改）

AUTO_BEAM_INTERVAL_S = 0.5      # 自动模式下：逐束推进间隔

# ========= 波束配置（beambook）=========
# beam_index: 0=omni；1..N 对应下述中心角，固定宽度
BEAM_WIDTH_DEG = 30.0
BEAM_CENTERS = list(range(-60, 61, 5))  # -60, -55, ..., 60  共25个
N_BEAMS = 1 + len(BEAM_CENTERS)         # 含 omni

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
    with OUT_FILE.open("w", newline="") as f:
        if INCLUDE_HEADER:
            f.write("# range_m,velocity_mps,rcs_m2,azimuth_deg\n")
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

def _rows_for_slot_all(df_ts: pd.DataFrame, idx: int,
                       prev_ranges: dict[str, float]) -> tuple[list[tuple[float, float, float, float]], dict[str, float]]:
    """
    生成“该时隙的完整行（目标+遮挡）”，供后续按波束过滤。
    返回：
      rows_all = [(range, v, rcs, angle), ...]
      curr_ranges = { id -> range }  # 仅目标
    """
    row = df_ts.iloc[idx]
    n_visible = int(row["n_visible"])
    n_blk = int(row["n_blockage_cells"])

    ids = _parse_str_list(row["ids"]) if n_visible > 0 else []
    rngs_all = _parse_float_list(row["range_m"])
    angs_all = _parse_float_list(row["angle_deg"])

    # 前 n_visible 是目标；最后 n_blk 是遮挡
    tgt_ranges = rngs_all[:n_visible]
    tgt_angles = angs_all[:n_visible]
    blk_ranges = rngs_all[-n_blk:] if n_blk > 0 else []
    blk_angles = angs_all[-n_blk:] if n_blk > 0 else []

    # 径向速度（目标）
    curr_ranges = {tid: r for tid, r in zip(ids, tgt_ranges)}
    if USE_RADIAL_VELOCITY:
        v_by_id = {tid: (curr_ranges[tid] - prev_ranges.get(tid, curr_ranges[tid])) / DT_S
                   for tid in curr_ranges}
    else:
        v_by_id = {tid: 0.0 for tid in curr_ranges}

    rows_all: list[tuple[float, float, float, float]] = []
    # 目标
    for tid, r, a in zip(ids, tgt_ranges, tgt_angles):
        rcs = RCS_BY_ID.get(tid, RCS_DEFAULT_TARGET)
        rows_all.append((r, v_by_id.get(tid, 0.0), rcs, a))
    # 遮挡（速度=0）
    rows_all.extend((r, 0.0, RCS_BLOCKAGE, a) for r, a in zip(blk_ranges, blk_angles))

    return rows_all, curr_ranges

def _apply_beam(rows_all: list[tuple[float, float, float, float]],
                beam_index: int) -> list[tuple[float, float, float, float]]:
    """
    按 beam_index 过滤：
      0 -> omni（不过滤）
      1..N -> 仅保留 |angle - center| <= width/2 的条目
    """
    if beam_index == 0:
        return rows_all
    center = BEAM_CENTERS[beam_index - 1]
    half = BEAM_WIDTH_DEG / 2.0
    def in_beam(angle: float) -> bool:
        return (angle >= center - half) and (angle <= center + half)
    return [row for row in rows_all if in_beam(row[3])]

def _print_beambook():
    print("[BEAMBOOK] index=0 -> omni")
    for i, c in enumerate(BEAM_CENTERS, start=1):
        print(f"[BEAMBOOK] index={i:2d} -> center={c:+.1f} deg, width={BEAM_WIDTH_DEG:.1f} deg")

# ========= 主流程 =========
def main():
    df_ts = pd.read_csv(TS_FILE, dtype=str, escapechar="\\")
    nslots = len(df_ts)

    print(f"[INFO] Data dir: {DATA_DIR}")
    print(f"[INFO] Loaded {nslots} time slots from {TS_FILE.name}")
    print(f"[INFO] Writing target_data.csv to {OUT_FILE}")
    print(f"[INFO] Beamforming enabled: {N_BEAMS} beams (0..{N_BEAMS-1}), width={BEAM_WIDTH_DEG} deg")
    _print_beambook()

    # 先写“仅遮挡”一次，方便对齐视图
    blk_rows = _build_blockage_rows_from_file()
    _write_target_data(blk_rows)
    user = input("[BLOCKAGE ONLY] 已写入 target_data.csv。回车进入 slot 0（q 退出）：").strip().lower()
    if user == "q":
        print("[DONE] 结束。")
        return

    # 模式：1=手动逐束推进；2=自动逐束推进
    mode = input(f"选择运行模式：1=手动逐束，2=自动逐束({AUTO_BEAM_INTERVAL_S:.1f}s)  [默认1]：").strip()
    if mode not in ("1", "2"):
        mode = "1"

    prev_ranges: dict[str, float] = {}

    try:
        for i in range(nslots):
            # 先准备该时隙的“完整行”（一次），后续逐束过滤
            rows_all, curr_ranges = _rows_for_slot_all(df_ts, i, prev_ranges)

            for b in range(N_BEAMS):
                rows_beam = _apply_beam(rows_all, b)
                _write_target_data(rows_beam)

                if b == 0:
                    desc = "omni"
                else:
                    desc = f"center={BEAM_CENTERS[b-1]:+.1f}°, width={BEAM_WIDTH_DEG:.1f}°"
                print(f"[SLOT {i}] [BEAM {b:2d}/{N_BEAMS-1:2d} {desc}] "
                      f"written {len(rows_beam)} rows to target_data.csv")

                if mode == "1":
                    user = input("  回车 -> 下一束；q -> 退出：").strip().lower()
                    if user == "q":
                        raise KeyboardInterrupt
                else:
                    time.sleep(AUTO_BEAM_INTERVAL_S)

            # 完成该时隙所有波束后，再更新 prev_ranges（确保速度跨“时隙”）
            prev_ranges = curr_ranges

    except KeyboardInterrupt:
        print("\n[INFO] 捕获到退出指令，提前结束。")

    print("[DONE] 结束。")

if __name__ == "__main__":
    main()