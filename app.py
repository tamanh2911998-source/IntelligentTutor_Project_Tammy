import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Adaptive Learning App", layout="wide")

# =========================
# FILE SETUP
# =========================
USER_FILE = "users.csv"

if not os.path.exists(USER_FILE):
    pd.DataFrame(columns=["student_id","full_name","password"]).to_csv(USER_FILE,index=False)


# =========================
# SESSION STATE
# =========================
if "student_id" not in st.session_state:
    st.session_state.student_id = None

if "full_name" not in st.session_state:
    st.session_state.full_name = None

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


# =========================
# USER FUNCTIONS
# =========================
def load_users():
    return pd.read_csv(USER_FILE)

def save_user(student_id, full_name, password):
    df = load_users()
    new_row = pd.DataFrame([[student_id, full_name, password]],
                           columns=df.columns)
    df = pd.concat([df,new_row], ignore_index=True)
    df.to_csv(USER_FILE,index=False)


# =========================
# TOP RIGHT LOGIN BAR
# =========================
def top_login_bar():

    col1, col2 = st.columns([4,1])

    with col2:

        # ===== NOT LOGIN =====
        if not st.session_state.logged_in:

            with st.popover("🔐 Account"):

                tab1, tab2 = st.tabs(["Sign in","Sign up"])

                # -------- SIGN IN --------
                with tab1:
                    login_id = st.text_input("Student ID", key="login_id")
                    login_pw = st.text_input("Password", type="password", key="login_pw")

                    if st.button("Login"):
                        df = load_users()

                        user = df[(df.student_id == login_id) &
                                  (df.password == login_pw)]

                        if not user.empty:
                            st.session_state.logged_in = True
                            st.session_state.student_id = login_id
                            st.session_state.full_name = user.iloc[0]["full_name"]
                            st.rerun()
                        else:
                            st.error("Wrong ID or password")


                # -------- SIGN UP --------
                with tab2:
                    new_id = st.text_input("Student ID", key="signup_id")
                    new_name = st.text_input("Full name", key="signup_name")
                    new_pw = st.text_input("Password", type="password", key="signup_pw")

                    if st.button("Create account"):

                        df = load_users()

                        if new_id in df.student_id.values:
                            st.error("ID already exists")

                        elif new_id and new_name and new_pw:
                            save_user(new_id,new_name,new_pw)
                            st.success("Account created!")
                        else:
                            st.warning("Fill all fields")

        # ===== LOGIN SUCCESS =====
        else:
            with st.popover(f"👤 {st.session_state.full_name}"):

                st.write(f"ID: {st.session_state.student_id}")

                if st.button("Logout"):
                    st.session_state.logged_in = False
                    st.session_state.student_id = None
                    st.session_state.full_name = None
                    st.rerun()


# =========================
# HOME PAGE
# =========================
def home_page():

    st.title("🏠 Adaptive English Learning App")

    if st.session_state.logged_in:
        st.success(f"Welcome {st.session_state.full_name} 👋")

    st.write("""
    You can:

    - Practice reading tasks  
    - Learn from mistakes  
    - Explore corpus examples  
    - Track progress  
    """)


# =========================
# PRACTICE PAGE
# =========================
def practice_page():

    st.header("📝 Practice Tasks")

    if not st.session_state.logged_in:
        st.warning("Sign in to do exercises")
        return

    task_type = st.selectbox(
        "Choose task type",
        [
            "Notice completion",
            "Leaflet/Flyer completion",
            "Reordering text",
            "Information gap completion",
            "Reading comprehension"
        ]
    )

    st.info(f"Task interface for {task_type} will appear here")


# =========================
# PROGRESS PAGE
# =========================
def progress_page():

    st.header("📊 Learning Progress")

    if not st.session_state.logged_in:
        st.warning("Sign in to view progress")
        return

    st.info("Progress analytics will appear here")


# =========================
# REVIEW PAGE
# =========================
def review_page():

    st.header("🔁 Review Mistakes")

    if not st.session_state.logged_in:
        st.warning("Sign in to review mistakes")
        return

    st.info("Mistake review will appear here")


# =========================
# MAIN APP
# =========================

top_login_bar()

menu = st.sidebar.radio(
    "Navigation",
    [
        "Home",
        "Practice",
        "Progress",
        "Review Mistakes"
    ]
)

if menu == "Home":
    home_page()

def practice_page():

    st.header("📝 Task Types")

    st.subheader("Choose a task type")

    task_type = st.radio(
        "",
        [
            "📢 Notice completion",
            "📄 Leaflet/Flyer completion",
            "🔀 Reordering text",
            "🧩 Information gap completion",
            "📘 Reading text 1",
        ]
    )

    st.divider()

    # ===== CHECK LOGIN ONLY WHEN START TASK =====

    if not st.session_state.logged_in:
        st.info("👉 Please sign in to start this task.")
        return

    # ===== SHOW TASK AFTER LOGIN =====

    if task_type == "📢 Notice completion":
        notice_task()

    elif task_type == "📄 Leaflet/Flyer completion":
        leaflet_task()

    elif task_type == "🔀 Reordering text":
        reorder_task()

    elif task_type == "🧩 Information gap completion":
        info_gap_task()

    elif task_type == "📘 Reading text 1":
        reading1_task()

elif menu == "Progress":
    progress_page()

elif menu == "Review Mistakes":
    review_page()
