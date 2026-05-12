import streamlit as st
import pandas as pd
import os

from pathlib import Path

APP_DIR = Path(__file__).parent
INPUT_FILE = APP_DIR / "ErateNCESmpnet_best_match_for_MT.csv"

df = pd.read_csv(INPUT_FILE)

OUTPUT_FILE = "ErateNCESmpnet_raterMTnts_MT.csv"

st.title("A–B Statement Match Review")

df = pd.read_csv(INPUT_FILE)

# Load existing judgments if present
if os.path.exists(OUTPUT_FILE):
    judged = pd.read_csv(OUTPUT_FILE)
    judged_ids = set(judged["A_id"])
else:
    judged = pd.DataFrame()
    judged_ids = set()

# Keep only unrated rows
remaining = df[~df["A_id"].isin(judged_ids)].reset_index(drop=True)

st.write(f"Remaining pairs to review: {len(remaining)}")

if len(remaining) == 0:
    st.success("All pairs have been reviewed.")
    st.stop()

row = remaining.iloc[0]

st.subheader(f"Reviewing {row['A_id']} vs {row['Best_B_id']}")

st.markdown("### Statement A")
st.write(row["A_statement"])

st.markdown("### Best Matching Statement B")
st.write(row["Best_B_statement"])

st.markdown("### Cosine Similarity")
st.write(round(row["cosine_similarity"], 4))

judgment = st.radio(
    "Is Statement B an acceptable match for Statement A?",
    ["Yes", "No"],
    index=None
)

notes = st.text_area("Optional notes")

if st.button("Submit judgment"):
    new_row = pd.DataFrame([{
        "A_id": row["A_id"],
        "A_statement": row["A_statement"],
        "Best_B_id": row["Best_B_id"],
        "Best_B_statement": row["Best_B_statement"],
        "cosine_similarity": row["cosine_similarity"],
        "judgment": judgment,
        "notes": notes
    }])

    if os.path.exists(OUTPUT_FILE):
        new_row.to_csv(OUTPUT_FILE, mode="a", header=False, index=False)
    else:
        new_row.to_csv(OUTPUT_FILE, index=False)

    st.success("Judgment saved. Refreshing to next pair...")
    st.rerun()

if os.path.exists(OUTPUT_FILE):
    ratings_df = pd.read_csv(OUTPUT_FILE)

    st.download_button(
        label="Download ratings CSV",
        data=ratMTgs_df.to_csv(index=False),
        file_name="ErateNCESmpnet_rater_judgments_MT.csv",
        mime="text/csv"
    )
    