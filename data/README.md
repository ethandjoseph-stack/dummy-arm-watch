# הנתונים

שני קבצים באותו פורמט (LeRobotDataset v3, ‏30 שורות בשנייה). בכל שורה: לאן כל אחד מ-6 המפרקים של הזרוע **התבקש** ללכת (`action`), ואיפה הוא **באמת** (`observation.state`), במעלות.
המפרקים, באותו סדר בשתי העמודות: `shoulder_pan`, `shoulder_lift`, `elbow_flex`, `wrist_flex`, `wrist_roll`, `gripper`.

## 1. ‏`dummy_sim_point.parquet` — הנתונים של Dummy

הקלטות הדגמה של המיומנות "point at the red cube" על הזרוע הימנית של Dummy, בסימולציה (MuJoCo), דרך שכבת הבטיחות HANDS. נוצרו בפרויקט Dummy ב-24.10.2026 (`scripts/sim_skill.py collect --episodes 60`), ועליהן אומן מודל ACT שהצליח ב-19 מתוך 20 ניסיונות.
התיאור המלא של ה-dataset: `dummy_sim_point_info.json`.

| | |
|---|---|
| הקלטות | 60 |
| שורות | 8,100 |
| עמודות | `action` (6), `observation.state` (6), `timestamp`, `frame_index`, `episode_index`, `index`, `task_index` |
| חוסרים | 0 |

## 2. ‏`so101_pickplace.parquet` — זרוע SO-101 אמיתית

ה-dataset הציבורי **lerobot/svla_so101_pickplace** מ-Hugging Face (רישיון Apache-2.0): זרוע SO-101 אמיתית, משימת הרם-והנח. בסימולציה הפיגור לא גדל מעבר ל-1.2°, ולכן צריך גם נתונים של זרוע אמיתית, שבה הפיגור מגיע עד 36°.

- עמוד ה-dataset: https://huggingface.co/datasets/lerobot/svla_so101_pickplace
- הורדה ישירה (0.4 MB): https://huggingface.co/datasets/lerobot/svla_so101_pickplace/resolve/main/data/chunk-000/file-000.parquet

| | |
|---|---|
| הקלטות | 50 |
| שורות | 11,939 |
| עמודות | אותן עמודות כמו ב-1 |
| חוסרים | 0 |

הסרטונים של המצלמות לא נמצאים כאן, והפרויקט לא צריך אותם.

## בהמשך

ההקלטות של Dummy האמיתי (`dummy teleop --record`, שלב 2) יישמרו באותו פורמט ויתווספו לכאן.
