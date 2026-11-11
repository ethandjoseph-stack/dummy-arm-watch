# Dummy Arm Watch

Course project (וייב קודינג עם קלוד, Ariel, semester A 2026/27). A Streamlit app about a SO-101 robot arm, the arm of the home robot Dummy.

- **Goal:** show where each joint of the arm lags behind its command, and predict that lag before a move.
- **Data:** six files in `data/`, all 30 rows per second, degrees (the gripper is on a 0–100 scale). Details, column by column, in `data/README.md`. The robot itself lives in the separate repo ~/Dummy.
  - `dummy_sim_point.parquet` and `so101_pickplace.parquet`: LeRobot format, `action` = commanded position of the 6 joints, `observation.state` = measured position, each a list of 6 in one cell. The first is Dummy's own demos in MuJoCo (60 episodes, 8,100 rows; lag clipped at 1.2°). The second is a public real SO-101 arm, `lerobot/svla_so101_pickplace` (50 episodes, 11,939 rows; lag up to 36°).
  - `dummy_real_teleop_2026-11-09.parquet`: Dummy's real arm on its first day (5 runs, 42,468 rows). One column per joint: `leader.<joint>` = what the operator asked, `action.<joint>` = what the safety layer HANDS sent. **No measured position.** `action.*` is empty while `mode` is `paused` (81,750 empty cells). `t` counts cycles / 30, it is not a clock.
  - `shoulder_lift_10deg_test_2026-11-09.csv`: one 10° step of the shoulder without HANDS (13 rows).
  - `dummy_real_show_2026-11-11.parquet`: Dummy's real arm playing its show by itself (10 runs, 23,781 rows, no empty cells). `action.<joint>` and **`state.<joint>` = the measured position**: the first Dummy file with the model's target. Gentle motion with no load (lag up to 8°), and the runs repeat the same routines.
  - `dummy_real_edge_2026-11-11.parquet`: 35 edge tests on Dummy's real arm, 11.11.2026 (35 runs, 67,876 rows, no empty cells): the range of each joint, the top speed, fast swings, load against the arm's own weight, a 3-minute stand, a 10-minute run. One test per run (`test`). `target.<joint>` = what the test's routine asked, `action.<joint>` = what HANDS sent (differs from `target` in 238 rows: a stall hold or the ease-in after a pause), **`state.<joint>` = the measured position**, `load.<joint>` = the motor's push in percent, `current.<joint>` = its current in mA. Scripted motion with an empty gripper (lag up to 10°). With the show file: 91,657 rows of Dummy's arm that hold the measured position.
- **Model (M3):** regression. Target = lag of a joint, `|action − state|` (first `shoulder_lift`). Features = commanded positions, commanded speed (change between frames), the other joints. Split by episode, never by row (leakage). KPI: MAE in degrees.
- **Files:** `app.py` (the app), `data/` (data + where it comes from), `requirements.txt` (pinned), `README.md` (project definition, in Hebrew), `docs/pitch.md` + `docs/pitch/` (the M1 pitch of 11.11.2026), `scripts/` (`build_show_data.py` and `build_edge_data.py` build the show and the edge-tests data files from Dummy's logs; `pitch_deck.py` fills the pitch slides and prints their numbers).

## Rules
- The operator works alone and must understand every change: explain in plain Hebrew, one step at a time.
- Keep `requirements.txt` pinned. No keys or passwords in the repo.
- Run `streamlit run app.py` and check it before every `git push`.
