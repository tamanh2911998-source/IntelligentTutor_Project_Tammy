import streamlit as st
import json
import os
from datetime import datetime

# =========================
# LOAD DATA
# =========================
def load_flyer_data():
    """Load flyer_gap-fill.json data"""
    json_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "data",
        "converted data",
        "flyer_gap-fill.json"
    )
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(f"❌ Could not find data file at {json_path}")
        return None
    except json.JSONDecodeError:
        st.error("❌ Error reading JSON file")
        return None

# =========================
# INITIALIZE SESSION STATE
# =========================
def init_session_state():
    """Initialize session state for flyer practice"""
    if "flyer_questions" not in st.session_state:
        st.session_state.flyer_questions = load_flyer_data()
    
    if "flyer_current_q" not in st.session_state:
        st.session_state.flyer_current_q = 0
    
    if "flyer_answers" not in st.session_state:
        st.session_state.flyer_answers = {}
    
    if "flyer_submitted" not in st.session_state:
        st.session_state.flyer_submitted = False
    
    if "flyer_score" not in st.session_state:
        st.session_state.flyer_score = None

# =========================
# FLYER COMPLETION TASK
# =========================
def flyer_completion():
    """Main flyer completion MCQ practice"""
    
    init_session_state()
    
    st.subheader("📄 Leaflet/Flyer Completion")
    st.write("Fill in the blanks with the correct options. Read the passage carefully and choose the best answer.")
    
    # Load questions
    questions = st.session_state.flyer_questions
    
    if questions is None or len(questions) == 0:
        st.error("❌ No questions available")
        return
    
    # Display progress
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Question", f"{st.session_state.flyer_current_q + 1}/{len(questions)}")
    with col2:
        answered = len(st.session_state.flyer_answers)
        st.metric("Answered", f"{answered}/{len(questions)}")
    with col3:
        if st.session_state.flyer_score is not None:
            percentage = (st.session_state.flyer_score / len(questions)) * 100
            st.metric("Score", f"{st.session_state.flyer_score}/{len(questions)}", f"{percentage:.0f}%")
    
    st.divider()
    
    # Get current question
    current_q = st.session_state.flyer_current_q
    question = questions[current_q]
    
    # Display question content
    st.write(f"**Topic:** {question['topic']}")
    st.write(f"**Question ID:** {question['id']}")
    
    # Display the passage with blanks
    st.write("**Passage:**")
    st.text(question['question_text'])
    
    st.write("---")
    
    # Display options
    st.write("**Choose the correct answer:**")
    
    # Create radio buttons for options
    option_key = f"q_{current_q}"
    
    # Retrieve stored answer if it exists
    current_answer = st.session_state.flyer_answers.get(option_key)
    
    selected_option = st.radio(
        "Options:",
        options=question['options'],
        index=question['options'].index(current_answer) if current_answer else 0,
        key=option_key
    )
    
    st.write("---")
    
    # Store answer
    st.session_state.flyer_answers[option_key] = selected_option
    
    # Navigation buttons
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("⬅️ Previous", disabled=(current_q == 0)):
            st.session_state.flyer_current_q -= 1
            st.rerun()
    
    with col2:
        if st.button("Next ➡️", disabled=(current_q == len(questions) - 1)):
            st.session_state.flyer_current_q += 1
            st.rerun()
    
    with col3:
        if st.button("Jump to..."):
            st.session_state.show_jump_dialog = True
    
    with col4:
        if st.button("📤 Submit Answers"):
            if len(st.session_state.flyer_answers) == len(questions):
                st.session_state.flyer_submitted = True
                st.rerun()
            else:
                st.warning(f"⚠️ Please answer all {len(questions)} questions before submitting")
    
    # Show jump dialog
    if st.session_state.get("show_jump_dialog", False):
        st.divider()
        jump_q = st.selectbox(
            "Jump to question:",
            range(len(questions)),
            format_func=lambda i: f"Question {i+1} (ID: {questions[i]['id']})"
        )
        if st.button("Go"):
            st.session_state.flyer_current_q = jump_q
            st.session_state.show_jump_dialog = False
            st.rerun()
    
    # Show results if submitted
    if st.session_state.flyer_submitted:
        st.divider()
        show_results(questions)

# =========================
# SHOW RESULTS
# =========================
def show_results(questions):
    """Display results and feedback"""
    
    st.header("📊 Results & Feedback")
    
    score = 0
    results = []
    
    for i, question in enumerate(questions):
        user_answer = st.session_state.flyer_answers.get(f"q_{i}")
        correct_answer = question['correct_answer']
        is_correct = user_answer == correct_answer
        
        if is_correct:
            score += 1
        
        results.append({
            "question_id": question['id'],
            "topic": question['topic'],
            "user_answer": user_answer,
            "correct_answer": correct_answer,
            "is_correct": is_correct,
            "error_type": question['error_type']
        })
    
    # Store score
    st.session_state.flyer_score = score
    
    # Show overall score
    percentage = (score / len(questions)) * 100
    
    if percentage >= 80:
        st.success(f"🎉 Excellent! Score: {score}/{len(questions)} ({percentage:.0f}%)")
    elif percentage >= 60:
        st.info(f"👍 Good job! Score: {score}/{len(questions)} ({percentage:.0f}%)")
    else:
        st.warning(f"💪 Keep practicing! Score: {score}/{len(questions)} ({percentage:.0f}%)")
    
    st.divider()
    
    # Show detailed feedback for each question
    st.subheader("Detailed Feedback")
    
    for idx, result in enumerate(results):
        with st.expander(f"Question {idx + 1} (ID: {result['question_id']}) - {result['topic']}", 
                        expanded=False):
            
            if result['is_correct']:
                st.success("✅ Correct!")
            else:
                st.error("❌ Incorrect")
            
            st.write(f"**Your answer:** {result['user_answer']}")
            st.write(f"**Correct answer:** {result['correct_answer']}")
            st.write(f"**Error type:** {result['error_type']}")
            
            # Show the question again for reference
            question = questions[idx]
            st.write(f"**Passage:** {question['question_text'][:200]}...")
    
    st.divider()
    
    # Action buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Retake this practice"):
            st.session_state.flyer_current_q = 0
            st.session_state.flyer_answers = {}
            st.session_state.flyer_submitted = False
            st.session_state.flyer_score = None
            st.rerun()
    
    with col2:
        if st.button("📈 Back to Practice Menu"):
            # This will be handled by main app
            st.info("Redirecting to practice menu...")
