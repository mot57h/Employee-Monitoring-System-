# import streamlit as st
# import sqlite3
# import pandas as pd

# # --- CSS Styling ---
# st.markdown(
#     """
#     <style>
#     .title {
#         font-size: 36px !important;
#         color: #4B0082;
#         text-align: center;
#     }
#     .stDataFrame {
#         border-radius: 10px;
#         overflow: hidden;
#     }
#     </style>
#     """,
#     unsafe_allow_html=True
# )

# # --- Database Connection ---
# conn = sqlite3.connect("users.db")

# st.markdown('<p class="title">👥 Employee Directory</p>', unsafe_allow_html=True)

# df = pd.read_sql_query("SELECT id, name, email FROM users", conn)
# st.dataframe(df.style.set_properties(**{"border-radius": "10px"}))

# conn.close()



import streamlit as st
import sqlite3
import pandas as pd
import smtplib
import ssl
from email.message import EmailMessage
import os

# --- Database Connection ---
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()

st.title("👥 Employee Directory")

# Function to Fetch Employee Data
def fetch_employee_data():
    return pd.read_sql_query("SELECT id, name, email FROM users", conn)

# Function to Export Employee Data to Excel
def export_to_excel(df):
    file_path = "employees.xlsx"
    df.to_excel(file_path, index=False)
    return file_path

# Function to Send Email with Updated Excel
def send_email_with_attachment(receiver_email):
    sender_email = "gauthamshetty379@gmail.com"  # Change this
    sender_password = "dhdm orxt sqyy yazq"  # Use an app password for security
    subject = "Updated Employee List"
    body = "Attached is the latest employee data."

    # Export to Excel
    file_path = export_to_excel(fetch_employee_data())

    # Ensure file exists before sending
    if not os.path.exists(file_path):
        st.error("Error: Excel file not found.")
        return

    # Create Email
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg.set_content(body)

    # Attach Excel File
    with open(file_path, "rb") as f:
        msg.add_attachment(f.read(), maintype="application", subtype="octet-stream", filename="employees.xlsx")

    # Send Email
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        st.success("📧 Employee list sent to the owner!")
    except Exception as e:
        st.error(f"Failed to send email: {e}")

# Check for new employees
if "last_employee_count" not in st.session_state:
    st.session_state.last_employee_count = cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0]

current_count = cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0]

if current_count > st.session_state.last_employee_count:
    owner_email = "shettygautham71@gmail.com"  # Change this
    send_email_with_attachment(owner_email)
    st.session_state.last_employee_count = current_count  # Update count

# Display Employee Table
df = fetch_employee_data()
st.dataframe(df)
