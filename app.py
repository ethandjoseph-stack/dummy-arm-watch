"""Dummy Arm Watch — first app (M1): project name, project sentence and the first rows of the data."""

from pathlib import Path

import pandas as pd
import streamlit as st

DATA = Path(__file__).parent / "data"
JOINTS = ["shoulder_pan", "shoulder_lift", "elbow_flex", "wrist_flex", "wrist_roll", "gripper"]
DATASETS = {
    "Dummy (סימולציה)": DATA / "dummy_sim_point.parquet",
    "זרוע SO-101 אמיתית": DATA / "so101_pickplace.parquet",
}


@st.cache_data
def load(path: Path) -> pd.DataFrame:
    """One row per frame (30 per second): where each joint was told to go and where it really is."""
    raw = pd.read_parquet(path)
    raw = raw.rename(columns={"observation_state": "observation.state"})  # web copy: no dot in the name (fastparquet)
    command = pd.DataFrame(raw["action"].tolist(), columns=[f"{j}_cmd" for j in JOINTS])
    actual = pd.DataFrame(raw["observation.state"].tolist(), columns=[f"{j}_pos" for j in JOINTS])
    return pd.concat([raw[["episode_index", "frame_index", "timestamp"]], command, actual], axis=1)


st.set_page_config(page_title="Dummy Arm Watch", page_icon="🦾")
st.markdown(  # Hebrew text reads right to left
    "<style>h3, .stMarkdown, .stAlert {direction: rtl; text-align: right;}</style>",
    unsafe_allow_html=True,
)
st.title("🦾 Dummy Arm Watch")
st.subheader("הזרוע של Dummy מפגרת אחרי הפקודה? האפליקציה תראה איפה, ותחזה מתי.")

st.markdown(
    "**משפט הפרויקט:** בוני רובוטים ביתיים עם זרועות SO-101, כמו Dummy, לא יודעים "
    "מתי מפרק בזרוע מפגר אחרי הפקודה (שוקע, נתקע או עמוס) עד שמיומנות נכשלת, "
    "ואנחנו נבנה דשבורד שמשתמש בהקלטות ההדגמה של הזרוע ובמודל רגרסיה "
    "שחוזה את הפיגור של כל מפרק."
)

st.info("בקרוב: דשבורד + מודל")

for name, path in DATASETS.items():
    df = load(path)
    st.markdown(
        f"**{name}:** {df['episode_index'].nunique()} הקלטות, "
        f"{len(df):,} שורות (30 בשנייה), {len(df.columns)} עמודות."
    )
    st.dataframe(df.head(5))

st.markdown("**טעימה מהדשבורד:** הכתף (`shoulder_lift`) בהקלטה הראשונה של הזרוע האמיתית. הפער בין הקווים הוא הפיגור.")
first = load(DATASETS["זרוע SO-101 אמיתית"]).query("episode_index == 0")
st.line_chart(
    first.set_index("timestamp")[["shoulder_lift_cmd", "shoulder_lift_pos"]].rename(
        columns={"shoulder_lift_cmd": "פקודה", "shoulder_lift_pos": "מיקום אמיתי"}
    ),
    color=["#4C9BE8", "#F5C518"],  # blue = command, Dummy's yellow = where the arm really is
    x_label="שניות",
    y_label="מעלות",
)
