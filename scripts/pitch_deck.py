"""Fill the pitch slides (docs/pitch/pitch-deck.html) with their data and pictures, and make the offline copy.

  .venv/bin/python scripts/pitch_deck.py

What it writes into docs/pitch/pitch-deck.html, in place (run it again after the data changes):
  - the two charts' numbers, from data/ -> the <script id="deck-data"> block
      slide 1: the shoulder on 9.11, run 1, seconds 190-262: what the operator asked and what HANDS sent
      slide 2: the wrist roll in the dance of the 11.11 05:53 show run: the command and the real position
  - docs/pitch/assets/app_shot.png (a screenshot of the live app) -> the <img data-asset="app-shot"> on slide 4
  - docs/pitch/assets/qr_data.json (QR code of the data folder's link) -> the <path data-asset="qr-data"> on slide 3
Then it writes docs/pitch/pitch-deck-offline.html: the same page as a whole document, which opens from the disk
by a double click (pitch-deck.html itself is the body the Claude Artifact takes, with no <html> around it).
It also prints every number the slides quote, so that the text can be checked against the data.
"""

import base64
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA, PITCH = ROOT / "data", ROOT / "docs" / "pitch"
DECK, OFFLINE = PITCH / "pitch-deck.html", PITCH / "pitch-deck-offline.html"
ARM = ["shoulder_pan", "shoulder_lift", "elbow_flex", "wrist_flex", "wrist_roll"]  # the gripper is on a 0-100 scale


def chart_data() -> dict:
    teleop = pd.read_parquet(DATA / "dummy_real_teleop_2026-11-09.parquet")
    run1 = teleop[(teleop.run_index == 0) & (teleop.t >= 190) & (teleop.t <= 262)].iloc[::3]
    sent = run1["action.shoulder_lift"]
    assert sent.min() == sent.max(), "the sent goal is not one flat line in this window"
    stuck = {"t": [round(float(t) - 190, 1) for t in run1.t], "asked": [round(float(v), 1) for v in run1["leader.shoulder_lift"]],
             "sent": round(float(sent.iloc[0]), 2)}

    show = pd.read_parquet(DATA / "dummy_real_show_2026-11-11.parquet")
    dance = show[(show.run_index == 5) & (show.t >= 47.2) & (show.t <= 53.0)]
    cmd, real = dance["action.wrist_roll"], dance["state.wrist_roll"]
    lag = (cmd - real).abs()
    worst = lag.idxmax()
    note = {"x": round(float(dance.t[worst]) - 47.2, 3), "y": round(float(cmd[worst] + real[worst]) / 2, 2), "lag": round(float(lag.max()), 2)}
    return {"stuck": stuck,
            "dance": {"t": [round(float(t) - 47.2, 3) for t in dance.t], "cmd": [round(float(v), 2) for v in cmd],
                      "real": [round(float(v), 2) for v in real], "note": note}}


def print_numbers(d: dict) -> None:
    show = pd.read_parquet(DATA / "dummy_real_show_2026-11-11.parquet")
    teleop = pd.read_parquet(DATA / "dummy_real_teleop_2026-11-09.parquet")
    print("slide 1: asked", min(d["stuck"]["asked"]), "to", max(d["stuck"]["asked"]), "deg; sent", d["stuck"]["sent"], "deg the whole window")
    print("slide 2: dance, worst lag", d["dance"]["note"]["lag"], "deg at second", d["dance"]["note"]["x"], "of the window")
    speed = np.concatenate([np.abs(np.gradient(g[f"action.{j}"].to_numpy(), g["t"].to_numpy()))
                            for j in ARM for _, g in show.groupby("run_index")])
    lag = np.concatenate([(g[f"action.{j}"] - g[f"state.{j}"]).abs().to_numpy() for j in ARM for _, g in show.groupby("run_index")])
    bins = pd.cut(speed, [0, 0.5, 10, 20, 40, 80], include_lowest=True)
    print(f"slide 2: mean lag of the five arm joints by command speed (deg per second), {show.run_index.nunique()} runs:")
    print(pd.DataFrame({"speed": bins, "lag": lag}).groupby("speed", observed=True)["lag"].agg(["count", "mean", "max"]).round(2).to_string())
    slope, const = np.linalg.lstsq(np.c_[speed, np.ones_like(speed)], lag, rcond=None)[0]
    print(f"slide 2: lag = {slope:.3f} s x speed + {const:.2f} deg; correlation {np.corrcoef(speed, lag)[0, 1]:.2f}")
    worst = {j: round(float((show[f"action.{j}"] - show[f"state.{j}"]).abs().max()), 2) for j in ARM}
    print("slide 4: worst lag per arm joint in the show data:", worst)
    rows = {"sim": 8100, "public": 11939, "teleop 9.11": len(teleop), "shoulder test": 13, "show": len(show)}
    print("slide 3: rows", rows, "total", sum(rows.values()), "| recordings", 60 + 50 + teleop.run_index.nunique() + 1 + show.run_index.nunique())
    print("slide 4: show runs", show.run_index.nunique(), "| seconds of each run", [round(float(g.t.max()), 1) for _, g in show.groupby("run_index")])


def main() -> None:
    d = chart_data()
    html = DECK.read_text()
    html, n1 = re.subn(r'(<script id="deck-data" type="application/json">).*?(</script>)',
                       lambda m: m.group(1) + json.dumps(d, separators=(",", ":")) + m.group(2), html, flags=re.S)
    shot = "data:image/png;base64," + base64.b64encode((PITCH / "assets" / "app_shot.png").read_bytes()).decode()
    html, n2 = re.subn(r'(data-asset="app-shot" src=")[^"]*(")', lambda m: m.group(1) + shot + m.group(2), html)
    qr = json.loads((PITCH / "assets" / "qr_data.json").read_text())
    assert qr["modules"] == 37, "the QR code changed size: fix the viewBox on slide 3 (modules + 8)"
    html, n3 = re.subn(r'(data-asset="qr-data" d=")[^"]*(")', lambda m: m.group(1) + qr["path"] + m.group(2), html)
    assert (n1, n2, n3) == (1, 1, 1), f"a placeholder is missing in {DECK.name}: {(n1, n2, n3)}"
    DECK.write_text(html)
    OFFLINE.write_text('<!doctype html>\n<html lang="he" dir="rtl">\n<head>\n<meta charset="utf-8">\n'
                       '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
                       + html + "\n</body>\n</html>\n")
    print(f"{DECK.relative_to(ROOT)}: {len(html) / 1024:.0f} kB; {OFFLINE.relative_to(ROOT)} written\n")
    print_numbers(d)


if __name__ == "__main__":
    main()
