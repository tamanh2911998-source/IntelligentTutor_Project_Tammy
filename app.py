import streamlit as st
import pandas as pd

# Page configuration
st.set_page_config(layout="wide")

# Initialize session state
if "q_idx" not in st.session_state:
    st.session_state.q_idx = 0
if "df" not in st.session_state:
    st.session_state.df = None
if "selected_error_type" not in st.session_state:
    st.session_state.selected_error_type = None
if "filtered_df" not in st.session_state:
    st.session_state.filtered_df = None
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "feedback" not in st.session_state:
    st.session_state.feedback = None

# Load data
try:
    df = pd.read_csv("de_thi.csv")
    st.session_state.df = df
except FileNotFoundError:
    st.warning("⚠️ de_thi.csv file not found. Please ensure the file is in the working directory.")
    st.session_state.df = None

# Sidebar Navigation
st.sidebar.title("Ms. Tammy's Study Zone")

if st.session_state.df is not None:
    # Get unique error types for filtering
    error_types = ["All Questions"] + sorted(st.session_state.df["error_type"].unique().tolist())
    
    selected_error = st.sidebar.selectbox(
        "Filter by Error Type:",
        error_types,
        key="error_filter"
    )
    
    # Filter dataframe based on selected error type
    if selected_error == "All Questions":
        st.session_state.filtered_df = st.session_state.df.copy()
    else:
        st.session_state.filtered_df = st.session_state.df[st.session_state.df["error_type"] == selected_error].reset_index(drop=True)
    
    # Reset Progress button
    if st.sidebar.button("🔄 Reset Progress"):
        st.session_state.q_idx = 0
        st.session_state.submitted = False
        st.session_state.feedback = None
        st.rerun()
    
    # Main layout
    col_quiz, col_feedback = st.columns([2, 1])
    
    # Quiz Column
    with col_quiz:
        if len(st.session_state.filtered_df) == 0:
            st.error("No questions available for the selected error type.")
        else:
            # Ensure q_idx doesn't exceed available questions
            if st.session_state.q_idx >= len(st.session_state.filtered_df):
                st.session_state.q_idx = len(st.session_state.filtered_df) - 1
            
            current_question = st.session_state.filtered_df.iloc[st.session_state.q_idx]
            
            # Display question number and content
            st.subheader(f"Question {st.session_state.q_idx + 1} of {len(st.session_state.filtered_df)}")
            st.write(current_question["question"])
            
            # Display error type
            st.caption(f"Error Type: {current_question['error_type']}")
            
            # Radio buttons for answer options
            user_answer = st.radio(
                "Select your answer:",
                ["A", "B", "C", "D"],
                key=f"answer_{st.session_state.q_idx}"
            )
            
            # Submit Answer button
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("✓ Submit Answer", key=f"submit_{st.session_state.q_idx}"):
                    st.session_state.submitted = True
                    correct_answer = current_question["correct"]
                    
                    if user_answer == correct_answer:
                        st.session_state.feedback = {
                            "correct": True,
                            "message": "✅ Excellent! Your answer is correct!"
                        }
                    else:
                        st.session_state.feedback = {
                            "correct": False,
                            "message": f"❌ Incorrect! The correct answer is {correct_answer}."
                        }
                    st.rerun()
            
            # Next Question button
            with col2:
                if st.button("→ Next Question", key=f"next_{st.session_state.q_idx}"):
                    st.session_state.q_idx += 1
                    st.session_state.submitted = False
                    st.session_state.feedback = None
                    st.rerun()
    
    # Feedback Column
    with col_feedback:
        st.subheader("Ms. Tammy's Diagnosis")
        feedback_container = st.container(border=True)
        
        with feedback_container:
            if st.session_state.feedback:
                if st.session_state.feedback["correct"]:
                    st.success(st.session_state.feedback["message"])
                else:
                    st.error(st.session_state.feedback["message"])
            else:
                st.info("Waiting for your answer to analyze...")

else:
    st.error("Unable to load the application. Please check if de_thi.csv is available.")
