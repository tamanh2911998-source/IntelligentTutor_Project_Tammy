import streamlit as st
import pandas as pd

# Set page layout to wide
st.set_page_config(layout="wide")

# Initialize session state for question index
if "q_idx" not in st.session_state:
    st.session_state.q_idx = 0

# Load data with error handling
try:
    df = pd.read_csv("advertisement_gap-fill.csv")
except FileNotFoundError:
    st.error("advertisement_gap-fill.csv file not found. Please ensure the file is in the correct directory.")
    df = None

# Sidebar Navigation
st.sidebar.title("Study Zone")

# Validate required columns
required_cols = ["question", "correct_answer"]
if df is not None:
    missing_cols = [c for c in required_cols if c not in df.columns]
    if missing_cols:
        st.error(f"Missing required column(s) in CSV: {', '.join(missing_cols)}. Please update the CSV.")
        df = None

if df is not None:
    # Filtering: prefer 'error_type' if present, otherwise offer a fallback
    if "error_type" in df.columns:
        error_types = df["error_type"].dropna().unique().tolist()
        error_types = ["All"] + error_types if len(error_types) > 0 else ["All"]
        selected_error_type = st.sidebar.selectbox("Filter by Error Type:", error_types)
        if selected_error_type == "All":
            filtered_df = df.reset_index(drop=True)
        else:
            filtered_df = df[df["error_type"] == selected_error_type].reset_index(drop=True)
    else:
        st.sidebar.warning("Column 'error_type' not found — providing alternate filtering options.")
        cols_for_filter = ["No filter"] + df.columns.tolist()
        pick_col = st.sidebar.selectbox("Pick a column to filter (optional):", cols_for_filter)
        if pick_col == "No filter":
            filtered_df = df.reset_index(drop=True)
        else:
            vals = df[pick_col].dropna().unique().tolist()
            vals = ["All"] + vals if len(vals) > 0 else ["All"]
            selected_val = st.sidebar.selectbox(f"Filter {pick_col} by:", vals)
            if selected_val == "All":
                filtered_df = df.reset_index(drop=True)
            else:
                filtered_df = df[df[pick_col] == selected_val].reset_index(drop=True)

    # Reset Progress button
    if st.sidebar.button("Reset Progress"):
        st.session_state.q_idx = 0
        st.experimental_rerun()

    # Main Layout - Two columns
    col_quiz, col_feedback = st.columns([2, 1])

    # Column 1: Quiz Section
    with col_quiz:
        if len(filtered_df) > 0:
            # Get current question index
            current_idx = min(st.session_state.q_idx, len(filtered_df) - 1)
            current_question = filtered_df.iloc[current_idx]

            st.subheader(f"Question {current_idx + 1} of {len(filtered_df)}")
            st.write(current_question.get("question", "(No question text found)."))

            # Radio buttons for options (A-D)
            user_choice = st.radio(
                "Select your answer:",
                options=["A", "B", "C", "D"],
                key=f"answer_{current_idx}"
            )

            # Submit Answer and Next Question buttons with unique keys
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Submit Answer", key=f"submit_{current_idx}"):
                    correct_answer = str(current_question.get("correct_answer", "")).strip()
                    if user_choice == correct_answer:
                        st.success("✓ Correct! Well done!")
                    else:
                        st.error(f"✗ Wrong! The correct answer is {correct_answer}")
            with col2:
                if st.button("Next Question", key=f"next_{current_idx}"):
                    if current_idx < len(filtered_df) - 1:
                        st.session_state.q_idx += 1
                        st.experimental_rerun()
                    else:
                        st.info("You've completed all questions in this category!")
        else:
            st.warning("No questions available for the selected filter.")

    # Column 2: Feedback Section
    with col_feedback:
        st.subheader("Ms. Tammy's Diagnosis")
        st.info("Waiting for your answer to analyze...")
else:
    st.error("Unable to load the application. Please check the data file and required columns.")
