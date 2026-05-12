import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime

# -----------------------------
# File paths
# -----------------------------
APP_DIR = Path(__file__).parent

INPUT_FILE = APP_DIR / "ErateNCESmpnet_best_match_for_each_A_MT.csv"
OUTPUT_FILE = APP_DIR / "ErateNCESmpnet_rater_judgments_MT.csv"

# -----------------------------
# Page setup
# -----------------------------
st.title("A–B Statement Match Review")

# -----------------------------
# Load input file
# -----------------------------
df = pd.read_csv(INPUT_FILE)

# -----------------------------
# Load existing judgments
# -----------------------------
if OUTPUT_FILE.exists():
    judged = pd.read_csv(OUTPUT_FILE)
    judged_ids = set(judged["A_id"].astype(str))
else:
    judged = pd.DataFrame()
    judged_ids = set()

# -----------------------------
# Show download button if any ratings exist
# -----------------------------
if OUTPUT_FILE.exists():
    ratings_df = pd.read_csv(OUTPUT_FILE)

    st.download_button(
        label="Download ratings CSV",
        data=ratings_df.to_csv(index=False),
        file_name="ErateNCESmpnet_rater_judgments_MT.csv",
        mime="text/csv"
    )

# -----------------------------
# Identify remaining unrated rows
# -----------------------------
df["A_id"] = df["A_id"].astype(str)
remaining = df[~df["A_id"].isin(judged_ids)].reset_index(drop=True)

st.write(f"Remaining pairs to review: {len(remaining)}")

# Stop safely if complete
if len(remaining) == 0:
    st.success("All pairs have been reviewed.")
    st.stop()

# -----------------------------
# Display next pair
# -----------------------------
row = remaining.iloc[0]

st.subheader(f"Reviewing {row['A_id']} vs {row['Best_B_id']}")

st.markdown("### Statement A")
st.write(row["A_statement"])

st.markdown("### Best Matching Statement B")
st.write(row["Best_B_statement"])

st.markdown("### Cosine Similarity")
st.write(round(float(row["cosine_similarity"]), 4))

judgment = st.radio(
    "Is Statement B an acceptable match for Statement A?",
    ["Yes", "No"],
    index=None
)

notes = st.text_area("Optional notes")

# -----------------------------
# Save judgment
# -----------------------------
if st.button("Submit judgment"):

    if judgment is None:
        st.warning("Please select Yes or No before submitting.")
        st.stop()

    new_row = pd.DataFrame([{
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "A_id": row["A_id"],
        "A_statement": row["A_statement"],
        "Best_B_id": row["Best_B_id"],
        "Best_B_statement": row["Best_B_statement"],
        "cosine_similarity": row["cosine_similarity"],
        "judgment": judgment,
        "notes": notes
    }])

    if OUTPUT_FILE.exists():
        new_row.to_csv(OUTPUT_FILE, mode="a", header=False, index=False)
    else:
        new_row.to_csv(OUTPUT_FILE, index=False)

    st.success("Judgment saved. Loading next pair...")
    st.rerun()
