# import streamlit as st
# import sqlite3
# import hashlib

# # --- Initialize Session State ---
# if "logged_in" not in st.session_state:
#     st.session_state["logged_in"] = False
# if "user_name" not in st.session_state:
#     st.session_state["user_name"] = ""
# if "user_email" not in st.session_state:
#     st.session_state["user_email"] = ""

# # --- CSS Styling ---
# st.markdown(
#     """
#     <style>
#     .title {
#         font-size: 36px !important;
#         color: #4CAF50;
#         text-align: center;
#     }
#     .stButton>button {
#         background-color: #4CAF50;
#         color: white;
#         font-size: 18px;
#         border-radius: 10px;
#     }
#     .stTextInput>div>div>input {
#         border-radius: 10px;
#     }
#     </style>
#     """,
#     unsafe_allow_html=True
# )

# def hash_password(password):
#     return hashlib.sha256(password.encode()).hexdigest()

# def authenticate_user(email, password):
#     conn = sqlite3.connect("users.db")
#     c = conn.cursor()
#     c.execute("SELECT * FROM users WHERE email=? AND password=?", 
#               (email, hash_password(password)))
#     user = c.fetchone()
#     conn.close()
#     return user

# # --- Login Page ---
# st.markdown('<p class="title">🔐 Login to Your Account</p>', unsafe_allow_html=True)

# with st.form("login_form"):
#     email = st.text_input("📧 Email", placeholder="Enter your email")
#     password = st.text_input("🔑 Password", type="password", placeholder="Enter your password")
#     submit = st.form_submit_button("Login")

# if submit:
#     user = authenticate_user(email, password)
#     if user:
#         st.session_state["logged_in"] = True
#         st.session_state["user_name"] = user[1]
#         st.session_state["user_email"] = user[2]
#         st.success(f"✅ Welcome, {user[1]}!")

#         # Correct way to navigate to another page
#         st.button("➡ Go to Monitoring", on_click=lambda: st.switch_page("monitor.py"))
#     else:
#         st.error("❌ Invalid credentials. Please try again.")
import streamlit as st
import sqlite3
import hashlib

# --- CSS Styling ---
st.markdown(
    """
    <style>
    body {
        background-color: #f0f2f6;
    }
    .title {
        font-size: 36px !important;
        color: #4CAF50;
        text-align: center;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        font-size: 18px;
        border-radius: 10px;
    }
    .stTextInput>div>div>input {
        border-radius: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Database Connection ---
conn = sqlite3.connect("users.db")
c = conn.cursor()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate_user(email, password):
    c.execute("SELECT * FROM users WHERE email=? AND password=?", 
              (email, hash_password(password)))
    return c.fetchone()

# --- Login Page ---
st.markdown('<p class="title">🔐 Login to Your Account</p>', unsafe_allow_html=True)

with st.form("login_form"):
    email = st.text_input("📧 Email", placeholder="Enter your email")
    password = st.text_input("🔑 Password", type="password", placeholder="Enter your password")
    submit = st.form_submit_button("Login")

if submit:
    user = authenticate_user(email, password)
    if user:
        st.session_state["logged_in"] = True
        st.session_state["user_name"] = user[1]
        st.success(f"✅ Welcome, {user[1]}!")
        st.page_link("pages/monitor.py", label="➡ Go to Monitoring")
    else:
        st.error("❌ Invalid credentials. Please try again.")

conn.close()
