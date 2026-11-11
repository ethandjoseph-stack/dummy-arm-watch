"""Build data/dummy_real_show_2026-11-11.parquet: Dummy's real left arm playing its class show, with the
command AND the real position of every joint in every control cycle (30 per second).

Eight runs: five on the night of 10.11.2026 and three on the morning of 11.11.2026 (the last two are the longer,
113-second show). Only the runs named in WHAT below go in, so that a later run does not change the file by itself:
to add one, add its line there. The source is the show's own logs in the Dummy repo
(measurements/2026-11-10/show-logs and measurements/2026-11-11/show-logs, *.jsonl.gz).
Each cycle line there holds:
  target   where the show's routine wanted each joint
  sent     what the safety layer HANDS sent to the motors            -> action.<joint>
  present  the positions HANDS read just before sending that command -> state.<joint>
In all these runs HANDS changed no command (sent == target in every row), so `target` is not copied.
The lag the project is about is |action - state|, joint by joint. Degrees; the gripper is on a 0-100 scale.

Run (reads the Dummy repo, writes one file here; nothing talks to the robot):
  .venv/bin/python scripts/build_show_data.py [path to the Dummy repo, default ~/Dummy]
"""

import gzip
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "dummy_real_show_2026-11-11.parquet"
JOINTS = ["shoulder_pan", "shoulder_lift", "elbow_flex", "wrist_flex", "wrist_roll", "gripper"]
DAYS = ["2026-11-10", "2026-11-11"]
# What each run was (Dummy: measurements/2026-11-10/README.md and measurements/2026-11-11/README.md).
WHAT = {
    "20261110-221533": "first careful show, 29 steps, no sound",
    "20261110-224346": "puppet pose probe, 31 steps, no sound",
    "20261110-224959": "full show, first time with sound",
    "20261110-230253": "full show after the sound fix",
    "20261110-230757": "full show from the Desktop button",
    "20261111-055302": "full show from the Desktop button, full volume",
    "20261111-072519": "longer show (113 s), first time on the arm",
    "20261111-075325": "longer show (113 s), after the sound fix",
}


def read_run(path: Path) -> tuple[dict, list[dict]]:
    head, cycles = {}, []
    with gzip.open(path, "rt") as f:
        for line in f:
            d = json.loads(line)
            if "start" in d and not head:
                head = d
            elif "sent" in d and "present" in d and "target" in d:
                cycles.append(d)
    return head, cycles


def main() -> None:
    dummy = Path(sys.argv[1]).expanduser() if len(sys.argv) > 1 else Path.home() / "Dummy"
    found = sorted(p for day in DAYS for p in (dummy / "measurements" / day / "show-logs").glob("*.jsonl.gz"))
    logs = [p for p in found if p.name.split(".")[0] in WHAT]
    if len(logs) != len(WHAT):
        sys.exit(f"found {len(logs)} of the {len(WHAT)} show logs named in WHAT under {dummy}/measurements")
    for p in found:
        if p not in logs:
            print(f"not included (not named in WHAT): {p.name}")
    frames = []
    for i, path in enumerate(logs):
        name = path.name.split(".")[0]
        head, cycles = read_run(path)
        arm = f"{head['arm']}_arm_"
        rows = []
        for c in cycles:
            if len(c["sent"]) != len(JOINTS) or len(c["present"]) != len(JOINTS):
                continue  # a cycle that sent nothing (none in these six runs)
            assert all(c["sent"][f"{arm}{j}.pos"] == c["target"][f"{arm}{j}.pos"] for j in JOINTS), "HANDS changed a command"
            row = {"run": name, "run_index": i, "what": WHAT.get(name, ""),
                   "hands": f"new HANDS ({head['step_deg']} deg from last goal)", "t": c["t"], "step": c["step"]}
            for j in JOINTS:
                row[f"action.{j}"] = c["sent"][f"{arm}{j}.pos"]
                row[f"state.{j}"] = c["present"][f"{arm}{j}.pos"]
            rows.append(row)
        frames.append(pd.DataFrame(rows))
        print(f"{name}: {len(rows)} rows, {rows[-1]['t']:.1f} s, {WHAT.get(name, '?')}")
    df = pd.concat(frames, ignore_index=True)
    df.to_parquet(OUT, index=False)
    print(f"\n{OUT.relative_to(ROOT)}: {len(df):,} rows, {len(df.columns)} columns, "
          f"{int(df.isna().sum().sum())} empty cells, {OUT.stat().st_size / 1024:.0f} kB")
    lag = pd.DataFrame({j: (df[f"action.{j}"] - df[f"state.{j}"]).abs() for j in JOINTS})
    print(f"\nlag |action - state| over all {df.run_index.nunique()} runs:")
    print(lag.describe(percentiles=[0.5, 0.95]).loc[["50%", "95%", "max"]].round(2).to_string())


if __name__ == "__main__":
    main()
