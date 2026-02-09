import streamlit as st
import pandas as pd
from pathlib import Path


def load_data(path: str):
    try:
        df = pd.read_csv(path)
        return df
    except Exception:
        return None


def init_session_state():
    if 'q_idx' not in st.session_state:
        st.session_state.q_idx = 0
    if 'submitted' not in st.session_state:
        st.session_state.submitted = False
    if 'last_feedback' not in st.session_state:
        st.session_state.last_feedback = "Waiting for your answer to analyze..."


def main():
    st.set_page_config(layout='wide')

    init_session_state()

    data_path = Path('Advertisement gap-fill.csv')
    df = load_data(data_path)

    # Sidebar
    with st.sidebar:
        st.title('Study Zone')

        if df is None:
            st.warning('Dataset not found or failed to load.')
            error_types = []
        else:
            error_types = []
            if 'error_type' in df.columns:
                error_types = sorted(df['error_type'].dropna().unique().tolist())
        selected_error = st.selectbox('Filter by error type', options=['All'] + error_types)

        if st.button('Reset Progress'):
            st.session_state.q_idx = 0
            st.session_state.submitted = False
            st.session_state.last_feedback = "Waiting for your answer to analyze..."

    # Filter questions
    if df is None or df.empty:
        st.error('No questions available. Please add advertisement_gap-fill.csv to the app folder.')
        return

    if selected_error and selected_error != 'All' and 'error_type' in df.columns:
        filtered = df[df['error_type'] == selected_error].reset_index(drop=True)
    else:
        filtered = df.reset_index(drop=True)

    if filtered.empty:
        st.info('No questions match the selected filter.')
        return

    # Ensure q_idx is within range
    if st.session_state.q_idx < 0:
        st.session_state.q_idx = 0
    if st.session_state.q_idx >= len(filtered):
        st.session_state.q_idx = len(filtered) - 1

    # Main layout: two columns
    col_quiz, col_feedback = st.columns([2, 1])

    # Question display and controls
    with col_quiz:
        q = filtered.loc[st.session_state.q_idx]

        question_text = q.get('question') or q.get('Question') or q.get('prompt') or 'Question text not found.'
        st.markdown(f"**Question {st.session_state.q_idx + 1}/{len(filtered)}:** {question_text}")

        # Determine option columns (try common names)
        options = []
        option_labels = ['A', 'B', 'C', 'D']
        # prefer columns named 'A','B','C','D' or lowercase
        for label in option_labels:
            if label in filtered.columns:
                options.append(q[label])
            elif label.lower() in filtered.columns:
                options.append(q[label.lower()])
            # handle columns like 'Option A' or 'Option A'
            elif f'Option {label}' in filtered.columns:
                options.append(q[f'Option {label}'])
            elif f'Option {label}' .lower() in [c.lower() for c in filtered.columns]:
                # find matching column case-insensitively
                match = [c for c in filtered.columns if c.lower() == f'option {label}'.lower()]
                if match:
                    options.append(q[match[0]])

        # fallback: try columns named optionA..D or choices
        if not options:
            for col_name in ['optionA', 'optionB', 'optionC', 'optionD', 'choice1', 'choice2', 'choice3', 'choice4']:
                if col_name in filtered.columns:
                    options.append(q[col_name])
        # final fallback: try any four columns beyond question/error_type/correct
        if not options:
            candidate_cols = [c for c in filtered.columns if c not in ('question', 'Question', 'prompt', 'error_type', 'correct')]
            for c in candidate_cols[:4]:
                options.append(q[c])

        # Clean options and ensure four entries
        options = [str(o) for o in options if pd.notna(o)]
        while len(options) < 4:
            options.append('N/A')

        choice = st.radio('Choose an answer', options=options, key='choice_radio')

        submit = st.button('Submit Answer')
        next_q = st.button('Next Question')

        if submit:
            st.session_state.submitted = True
            # Determine correct answer
            # Check common correct/answer column names
            if 'correct' in filtered.columns:
                correct_raw = q.get('correct')
            elif 'Correct Answer' in filtered.columns:
                correct_raw = q.get('Correct Answer')
            elif 'answer' in filtered.columns:
                correct_raw = q.get('answer')
            elif 'Answer' in filtered.columns:
                correct_raw = q.get('Answer')
            else:
                correct_raw = None
            correct_text = None
            if correct_raw is not None and pd.notna(correct_raw):
                correct_s = str(correct_raw).strip()
                # If correct given as letter A-D, map to option text
                if correct_s.upper() in option_labels:
                    idx = option_labels.index(correct_s.upper())
                    if idx < len(options):
                        correct_text = options[idx]
                else:
                    # otherwise assume correct contains the exact option text
                    correct_text = correct_s

            # Compare
            is_correct = False
            if correct_text is not None:
                is_correct = (choice.strip() == str(correct_text).strip())
            else:
                # If no correct provided, compare to a column named 'answer' or 'Answer'
                alt = q.get('answer') or q.get('Answer')
                if pd.notna(alt):
                    is_correct = (choice.strip() == str(alt).strip())

            if is_correct:
                st.success('Correct!')
                st.session_state.last_feedback = 'Great job — that looks correct.'
            else:
                st.error('Incorrect. Try reviewing the options.')
                feedback = 'That answer is not correct. Keep practicing!'
                if correct_text:
                    feedback += f" The correct answer was: {correct_text}"
                st.session_state.last_feedback = feedback

        if next_q:
            st.session_state.q_idx = min(st.session_state.q_idx + 1, len(filtered) - 1)
            st.session_state.submitted = False
            st.session_state.last_feedback = "Waiting for your answer to analyze..."

    # Feedback column
    with col_feedback:
        st.header("Ms. Tammy's Diagnosis")
        st.write(st.session_state.last_feedback)


if __name__ == '__main__':
    main()
