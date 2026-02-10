import streamlit as st
import json
import os


# =========================
# LOAD DATA
# =========================
def load_flyer_data():

    json_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "data",
        "converted data",
        "flyer_gap-fill.json"
    )

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)

    except Exception as e:
        st.error(f"Error loading flyer data: {e}")
        return []


# =========================
# SESSION STATE
# =========================
def init_session():

    if "flyer_data" not in st.session_state:
        st.session_state.flyer_data = load_flyer_data()

    if "flyer_passage_index" not in st.session_state:
        st.session_state.flyer_passage_index = 0

    if "flyer_answers" not in st.session_state:
        st.session_state.flyer_answers = {}

    if "flyer_submitted" not in st.session_state:
        st.session_state.flyer_submitted = False


# =========================
# MAIN PAGE
# =========================
def flyer_completion():

    init_session()

    data = st.session_state.flyer_data

    if not data:
        st.warning("No flyer data found")
        return

    p_index = st.session_state.flyer_passage_index
    passage = data[p_index]

    st.subheader("📄 Leaflet / Flyer Completion")

    st.write(f"### Topic: {passage['topic']}")

    # ---------- PASSAGE ----------
    st.markdown("### Passage")
    st.write(passage["passage_text"])

    st.divider()

    # ---------- QUESTIONS ----------
    st.markdown("### Fill in each blank")

    for q in passage["questions"]:

        blank = q["blank"]
        key = f"p{p_index}_b{blank}"

        st.markdown(f"#### Blank ({blank})")

        previous_answer = st.session_state.flyer_answers.get(key)

        selected = st.radio(
            label="Choose answer:",
            options=q["options"],
            index=q["options"].index(previous_answer)
            if previous_answer in q["options"]
            else None,
            key=key
        )

        if selected:
            st.session_state.flyer_answers[key] = selected

    st.divider()

    # ---------- NAVIGATION ----------
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("⬅ Previous Passage") and p_index > 0:
            st.session_state.flyer_passage_index -= 1
            st.session_state.flyer_submitted = False
            st.rerun()

    with col2:
        if st.button("Submit Answers"):
            st.session_state.flyer_submitted = True
            st.rerun()

    with col3:
        if st.button("Next Passage ➡") and p_index < len(data) - 1:
            st.session_state.flyer_passage_index += 1
            st.session_state.flyer_submitted = False
            st.rerun()

    # ---------- FEEDBACK ----------
    if st.session_state.flyer_submitted:
        show_feedback(passage, p_index)


# =========================
# FEEDBACK
# =========================
def show_feedback(passage, p_index):

    st.header("📊 Feedback")

    total = len(passage["questions"])
    correct_count = 0

    for q in passage["questions"]:

        blank = q["blank"]
        key = f"p{p_index}_b{blank}"

        user_answer = st.session_state.flyer_answers.get(key)
        correct_answer = q["correct_answer"]

        with st.expander(f"Blank {blank}"):

            if user_answer == correct_answer:
                st.success("✅ Correct")
                correct_count += 1
            else:
                st.error("❌ Incorrect")

            st.write("Your answer:", user_answer)
            st.write("Correct answer:", correct_answer)

            if "error_type" in q:
                st.write("Error type:", q["error_type"])

    st.success(f"Score: {correct_count}/{total}")

    if st.button("🔄 Retry"):
        # Clear answers for this passage only
        for q in passage["questions"]:
            key = f"p{p_index}_b{q['blank']}"
            st.session_state.flyer_answers.pop(key, None)

        st.session_state.flyer_submitted = False
        st.rerun()


# =========================
# RUN
# =========================
if __name__ == "__main__":
    flyer_completion()
