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

if df is not None:
    # Get unique error types for filtering
    error_types = df["error_type"].unique().tolist()
    selected_error_type = st.sidebar.selectbox("Filter by Error Type:", error_types)
    
    # Filter questions by selected error type
    filtered_df = df[df["error_type"] == selected_error_type].reset_index(drop=True)
    
    # Reset Progress button
    if st.sidebar.button("Reset Progress"):
        st.session_state.q_idx = 0
        st.rerun()
    
    # Main Layout - Two columns
    col_quiz, col_feedback = st.columns([2, 1])
    
    # Column 1: Quiz Section
    with col_quiz:
        if len(filtered_df) > 0:
            # Get current question index
            current_idx = min(st.session_state.q_idx, len(filtered_df) - 1)
            current_question = filtered_df.iloc[current_idx]
            
            st.subheader(f"Question {current_idx + 1} of {len(filtered_df)}")
            st.write(current_question["question"])
            
            # Radio buttons for options
            user_choice = st.radio(
                "Select your answer:",
                options=["A", "B", "C", "D"],
                key=f"answer_{current_idx}"
            )
            
            # Submit Answer button
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Submit Answer"):
                    correct_answer = current_question["correct_answer"]
                    
                    if user_choice == correct_answer:
                        st.success("✓ Correct! Well done!")
                    else:
                        st.error(f"✗ Wrong! The correct answer is {correct_answer}")
            
            # Next Question button
            with col2:
                if st.button("Next Question"):
                    if current_idx < len(filtered_df) - 1:
                        st.session_state.q_idx += 1
                        st.rerun()
                    else:
                        st.info("You've completed all questions in this category!")
        else:
            st.warning("No questions available for the selected error type.")
    
    # Column 2: Feedback Section
    with col_feedback:
        st.subheader("Ms. Tammy's Diagnosis")
        st.info("Waiting for your answer to analyze...")
else:
    st.error("Unable to load the application. Please check the data file.")
