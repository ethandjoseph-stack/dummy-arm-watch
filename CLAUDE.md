# Dummy Arm Watch

Course project (וייב קודינג עם קלוד, Ariel, semester A 2026/27). A Streamlit app about a SO-101 robot arm, the arm of the home robot Dummy.

- **Goal:** show where each joint of the arm lags behind its command, and predict that lag before a move.
- **Data:** two LeRobot parquet files in `data/`, 30 fps, `action` = commanded position of 6 joints, `observation.state` = measured position (degrees). `dummy_sim_point.parquet`: Dummy's own demos in MuJoCo (60 episodes, 8,100 rows; lag clipped at 1.2°). `so101_pickplace.parquet`: public real SO-101 arm, `lerobot/svla_so101_pickplace` (50 episodes, 11,939 rows; lag up to 36°). Details in `data/README.md`. Later: Dummy's real recordings (`dummy teleop --record`), same format. The robot itself lives in the separate repo ~/Dummy.
- **Model (M3):** regression. Target = lag of a joint, `|action − state|` (first `shoulder_lift`). Features = commanded positions, commanded speed (change between frames), the other joints. Split by episode, never by row (leakage). KPI: MAE in degrees.
- **Files:** `app.py` (the app), `data/` (data + where it comes from), `requirements.txt` (pinned), `README.md` (project definition, in Hebrew).

## Rules
- The operator works alone and must understand every change: explain in plain Hebrew, one step at a time.
- Keep `requirements.txt` pinned. No keys or passwords in the repo.
- Run `streamlit run app.py` and check it before every `git push`.
