"""Build data/dummy_real_edge_2026-11-11.parquet: the 35 edge tests of 11.11.2026 on Dummy's real left arm.

Each test is a short routine that takes the arm to one edge: the range of a joint, the top speed, fast swings,
load against gravity, a long stand, a ten-minute run, the show's keys, and the class show itself with no voice.
They ran between 11:14 and 12:08 (R019-R053 in the Dummy repo's measurements/RUNS.md; what each one does and what
it found: measurements/2026-11-11/edge/README.md there). The source is the tests' own logs,
measurements/2026-11-11/edge-logs/*.jsonl.gz, and manifest.ndjson next to them, which names the test of each log.
Only the tests up to LAST go in, so that a later test does not change the file by itself.

Each control cycle (30 per second) becomes one row:
  target   where the test's routine wanted each joint                 -> target.<joint>
  sent     what the safety layer HANDS sent to the motors             -> action.<joint>
  present  the positions HANDS read just before sending that command  -> state.<joint>
  load     how hard each motor pushed, in percent of its full force   -> load.<joint>   (the sign is the direction)
  ma       the current each motor drew, in milliamperes               -> current.<joint>
`action` differs from `target` only where HANDS held a joint (a stall) or eased the arm back in after a pause.
The lag the project is about is |action - state|, joint by joint. Degrees; the gripper is on a 0-100 scale.
The current's unit (6.5 mA a step) is from Feetech's table and was not checked against a meter.

Run (reads the Dummy repo, writes one file here; nothing talks to the robot):
  .venv/bin/python scripts/build_edge_data.py [path to the Dummy repo, default ~/Dummy]
"""

import gzip
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "dummy_real_edge_2026-11-11.parquet"
JOINTS = ["shoulder_pan", "shoulder_lift", "elbow_flex", "wrist_flex", "wrist_roll", "gripper"]
LOGS = Path("measurements") / "2026-11-11" / "edge-logs"
FIRST, LAST, TESTS = "20261111-111409", "20261111-120630", 35


def main() -> None:
    dummy = Path(sys.argv[1]).expanduser() if len(sys.argv) > 1 else Path.home() / "Dummy"
    manifest = [json.loads(line) for line in (dummy / LOGS / "manifest.ndjson").read_text().splitlines() if line.strip()]
    tests = [m for m in manifest if FIRST <= m["stamp"] <= LAST]
    for m in manifest:
        if m not in tests:
            print(f"not included (after {LAST}): {m['stamp']} {m['test']}")
    if len(tests) != TESTS:
        sys.exit(f"found {len(tests)} of the {TESTS} edge tests in {dummy / LOGS / 'manifest.ndjson'}")
    frames = []
    for i, m in enumerate(tests):
        rows = []
        with gzip.open(dummy / LOGS / f"{m['stamp']}.jsonl.gz", "rt") as f:
            for line in f:
                c = json.loads(line)
                if "sent" not in c or "present" not in c:
                    continue  # the run's first line, a health line (heat and volts), a key, or the summary
                row = {"run": m["stamp"], "run_index": i, "test": m["test"], "t": c["t"], "step": c["step"], "mode": c["mode"]}
                for column, key, ending in (("target", "target", ".pos"), ("action", "sent", ".pos"), ("state", "present", ".pos"),
                                            ("load", "load", ""), ("current", "ma", "")):
                    for j in JOINTS:
                        row[f"{column}.{j}"] = c[key][f"left_arm_{j}{ending}"]
                rows.append(row)
        frames.append(pd.DataFrame(rows))
        held = ", HANDS held: " + " ".join(m["stalled"]) if m["stalled"] else ""
        print(f"{m['stamp']} {m['test']}: {len(rows)} rows, {rows[-1]['t']:.1f} s{held}")
    df = pd.concat(frames, ignore_index=True)
    df.to_parquet(OUT, index=False)
    print(f"\n{OUT.relative_to(ROOT)}: {len(df):,} rows, {len(df.columns)} columns, {df.run_index.nunique()} runs, "
          f"{int(df.isna().sum().sum())} empty cells, {OUT.stat().st_size / 1024:.0f} kB, {df.groupby('run_index').t.max().sum() / 60:.1f} minutes")
    changed = pd.concat([(df[f"action.{j}"] != df[f"target.{j}"]) for j in JOINTS], axis=1).any(axis=1)
    print(f"rows where HANDS sent something else than the routine's target: {int(changed.sum())} "
          f"(in {sorted(df[changed].test.unique())})")
    lag = pd.DataFrame({j: (df[f"action.{j}"] - df[f"state.{j}"]).abs() for j in JOINTS})
    print("\nlag |action - state|:")
    print(lag.describe(percentiles=[0.5, 0.95]).loc[["50%", "95%", "max"]].round(2).to_string())
    print("\nthe largest push and current of each motor:")
    print(pd.DataFrame({"load %": [df[f"load.{j}"].abs().max() for j in JOINTS],
                        "current mA": [df[f"current.{j}"].abs().max() for j in JOINTS]}, index=JOINTS).round(1).to_string())


if __name__ == "__main__":
    main()
