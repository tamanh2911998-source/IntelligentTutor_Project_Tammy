import streamlit as st
import pandas as pd
import os
from practice.flyer import flyer_completion

# ==========================
# APP CONFIG
# ==========================
st.set_page_config(page_title="Adaptive Learning App", layout="wide")

# ==========================
# DEV MODE (allow testing without login)
# ==========================
DEV_MODE = True

USER_FILE = "users.csv"

if not os.path.exists(USER_FILE):
    pd.DataFrame(
        columns=["student_id", "full_name", "password"]
    ).to_csv(USER_FILE, index=False)

# ==========================
# SESSION STATE
# ==========================
for key, default in {
    "logged_in": DEV_MODE,
    "student_id": "DEV" if DEV_MODE else None,
    "full_name": "Test User" if DEV_MODE else None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ==========================
# USER FUNCTIONS
# ==========================
def load_users():
    return pd.read_csv(USER_FILE)

def save_user(student_id, full_name, password):
    df = load_users()
    df.loc[len(df)] = [student_id, full_name, password]
    df.to_csv(USER_FILE, index=False)

# ==========================
# TOP LOGIN BAR
# ==========================
def top_login_bar():
    col1, col2 = st.columns([4, 1])

    with col2:
        if not st.session_state.logged_in:
            with st.popover("🔐 Account"):
                tab1, tab2 = st.tabs(["Sign in", "Sign up"])

                # SIGN IN
                with tab1:
                    sid = st.text_input("Student ID")
                    pw = st.text_input("Password", type="password")

                    if st.button("Login"):
                        df = load_users()
                        user = df[
                            (df.student_id == sid)
                            & (df.password == pw)
                        ]

                        if not user.empty:
                            st.session_state.logged_in = True
                            st.session_state.student_id = sid
                            st.session_state.full_name = user.iloc[0]["full_name"]
                            st.rerun()
                        else:
                            st.error("Wrong ID or password")

                # SIGN UP
                with tab2:
                    new_id = st.text_input("Student ID", key="new_id")
                    new_name = st.text_input("Full name")
                    new_pw = st.text_input("Password", type="password", key="new_pw")

                    if st.button("Create account"):
                        df = load_users()

                        if new_id in df.student_id.values:
                            st.error("ID already exists")

                        elif new_id and new_name and new_pw:
                            save_user(new_id, new_name, new_pw)
                            st.success("Account created!")
                        else:
                            st.warning("Fill all fields")

        else:
            with st.popover(f"👤 {st.session_state.full_name}"):

                st.write(f"ID: {st.session_state.student_id}")

                if st.button("Logout"):
                    st.session_state.logged_in = False
                    st.session_state.student_id = None
                    st.session_state.full_name = None
                    st.rerun()

# ==========================
# TASK PLACEHOLDERS
# ==========================
def notice_task():
    st.subheader("📢 Notice Completion")
    st.info("Notice task goes here")

def leaflet_task():
    flyer_completion()

def reorder_task():
    st.subheader("🔀 Reordering Text")
    st.info("Reordering task goes here")

def info_gap_task():
    st.subheader("🧩 Information Gap Completion")
    st.info("Info-gap task goes here")

def reading_task():
    st.subheader("📘 Reading Comprehension")
    st.info("Reading task goes here")

# ==========================
# PAGES
# ==========================
def home_page():
    st.title("🏠 Adaptive English Learning App")

    if st.session_state.logged_in:
        st.success(f"Welcome {st.session_state.full_name} 👋")

    st.write("""
    • Practice exam-style tasks  
    • Learn from mistakes  
    • Track progress  
    """)

def diagnostic_page():
    st.header("🧪 Diagnostic Test")

    if not st.session_state.logged_in and not DEV_MODE:
        st.warning("👉 Please sign in to access diagnostic test")
        return

    st.info("Diagnostic test content will be added here.")

def practice_page():
    st.header("📝 Practice")

    task_type = st.radio(
        "Choose a task type",
        [
            "📢 Notice completion",
            "📄 Leaflet/Flyer completion",
            "🔀 Reordering text",
            "🧩 Information gap completion",
            "📘 Reading comprehension",
        ]
    )

    st.divider()

    if not st.session_state.logged_in and not DEV_MODE:
        st.warning("👉 Please sign in to start this task")
        return

    if task_type == "📢 Notice completion":
        notice_task()

    elif task_type == "📄 Leaflet/Flyer completion":
        leaflet_task()

    elif task_type == "🔀 Reordering text":
        reorder_task()

    elif task_type == "🧩 Information gap completion":
        info_gap_task()

    elif task_type == "📘 Reading comprehension":
        reading_task()

def progress_page():
    st.header("📊 Progress")

    if not st.session_state.logged_in and not DEV_MODE:
        st.warning("Sign in to view progress")
        return

    st.info("Progress analytics here")

def review_page():
    st.header("🔁 Review Mistakes")

    if not st.session_state.logged_in and not DEV_MODE:
        st.warning("Sign in to review mistakes")
        return

    st.info("Mistake review here")

# ==========================
# MAIN
# ==========================
top_login_bar()

if DEV_MODE:
    st.sidebar.warning("⚠ DEV MODE ON")

menu = st.sidebar.radio(
    "Navigation",
    [
        "Home",
        "Diagnostic Test",
        "Practice",
        "Progress",
        "Review Mistakes",
    ]
)

if menu == "Home":
    home_page()

elif menu == "Diagnostic Test":
    diagnostic_page()

elif menu == "Practice":
    practice_page()

elif menu == "Progress":
    progress_page()

elif menu == "Review Mistakes":
    review_page()
