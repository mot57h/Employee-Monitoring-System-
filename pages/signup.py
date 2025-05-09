import streamlit as st
import sqlite3
import hashlib

# --- CSS Styling ---
st.markdown(
    """
    <style>
    .title {
        font-size: 36px !important;
        color: #1E90FF;
        text-align: center;
    }
    .stButton>button {
        background-color: #1E90FF;
        color: white;
        font-size: 18px;
        border-radius: 10px;
        width: 100%;
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

def register_user(name, email, password):
    try:
        c.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", 
                  (name, email, hash_password(password)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

# --- Signup Page ---
st.markdown('<p class="title">📝 Create an Account</p>', unsafe_allow_html=True)

with st.form("signup_form"):
    name = st.text_input("👤 Full Name", placeholder="Enter your full name")
    email = st.text_input("📧 Email", placeholder="Enter your email")
    password = st.text_input("🔑 Password", type="password", placeholder="Create a password")
    submit = st.form_submit_button("Sign Up")

if submit:
    if register_user(name, email, password):
        st.success("✅ Account created successfully! You can now log in.")
        st.page_link("pages/login.py", label="➡ Go to Login")
    else:
        st.error("❌ Email already exists. Please use a different one.")

conn.close()
