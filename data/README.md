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

## 3. ‏`dummy_real_teleop_2026-11-09.parquet` — הזרוע האמיתית של Dummy, היום הראשון

ב-9.11.2026 הזרוע השמאלית האמיתית של Dummy זזה בפעם הראשונה (teleop: מזיזים ביד את זרוע ה-leader, והזרוע של Dummy מחקה אותה דרך HANDS). זה חמש הפעלות, 30 שורות בשנייה. המקור הוא ה-logs של `dummy teleop` בפרויקט Dummy (`measurements/2026-11-09/`).

| | |
|---|---|
| הפעלות | 5 (עמודה `run`) |
| שורות | 42,468 |
| עמודות | 17: ‏`run`, `run_index`, `hands` (איזו גרסה של HANDS), `t` (שניות), `mode` (engaging / following / paused), ‏`leader.<joint>` (6, לאן המפעיל הזיז), ‏`action.<joint>` (6, מה HANDS שלח לזרוע) |
| חוסרים | 81,750 תאים: ‏`action.*` ריק ב־13,625 שורות שבהן הזרוע עצרה (`mode = paused`), כי לא נשלח שום דבר. בשאר העמודות אין חוסרים |

**שימו לב:** ב-log הזה **אין** את המיקום האמיתי (`observation.state`). יש בו מה שהמפעיל ביקש (`leader`) ומה ש-HANDS שלח (`action`). ההפרש ביניהם הוא מה ש-HANDS עצר.
**מה רואים בו:** בשלוש ההפעלות הראשונות (HANDS הישן) הכתף והמרפק לא עקבו. ‏`action.shoulder_lift` נשאר ב־‎−109.5° בזמן שה-leader עלה עד +87°. בשתי האחרונות (HANDS החדש) הם עקבו: הכתף עלתה עד +28°.

## 4. ‏`shoulder_lift_10deg_test_2026-11-09.csv` — בדיקת הכתף

הכתף בלבד, בלי HANDS: יעד של +114 ticks (‏10°) בקפיצה אחת, ואז חזרה. ‏`position_ticks` הוא המיקום האמיתי, `load_permille` הוא העומס באלפיות, ו-`status` הם דגלי התקלה של המנוע (0 = אין).
הכתף הגיעה ל־937 מתוך 939 תוך 0.3 שנייה, בעומס של 4% לכל היותר. בחזרה היא עצרה 9 ticks ‏(0.8°) לפני היעד. זה הפיגור של מפרק עם משקל, והוא בדיוק הבעיה שהפרויקט הזה מודד.

## בהמשך

ההקלטות של Dummy האמיתי (`dummy teleop --record`, שלב 2) יישמרו באותו פורמט ויתווספו לכאן.
