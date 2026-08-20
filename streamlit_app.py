import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os

# Page Configuration
st.set_page_config(
    page_title="Family Welfare System - Traffic Wardens",
    page_icon="🛡️",
    layout="wide"
)

# Custom Styling
st.markdown("""
    <style>
        .main-title {
            color: #0A2540;
            text-align: center;
            font-size: 2.2rem;
            font-weight: bold;
        }
        .sub-title {
            color: #4CAF50;
            text-align: center;
            font-size: 1.2rem;
            margin-bottom: 20px;
        }
    </style>
""", unsafe_allow_html=True)

IMAGE_PATH = "logo.png"

# ==========================================
# DATABASE SETUP & HELPER FUNCTIONS
# ==========================================
DB_FILE = "welfare_system.db"

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()
    # Table for Warden Members
    c.execute('''
        CREATE TABLE IF NOT EXISTS members (
            belt_no TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            father_name TEXT NOT NULL,
            cnic TEXT UNIQUE NOT NULL,
            mobile TEXT NOT NULL,
            join_date DATE NOT NULL
        )
    ''')
    # Table for Monthly Payments
    c.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            belt_no TEXT NOT NULL,
            amount REAL NOT NULL,
            payment_date DATE NOT NULL,
            month_year TEXT NOT NULL,
            FOREIGN KEY (belt_no) REFERENCES members (belt_no)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Fetch all members list
def get_members():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM members ORDER BY name ASC", conn)
    conn.close()
    return df

# ==========================================
# HEADER & SIDEBAR LOGO
# ==========================================
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if os.path.exists(IMAGE_PATH):
        st.image(IMAGE_PATH, use_container_width=True)
    st.markdown('<div class="main-title">FAMILY WELFARE SYSTEM</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">FOR TRAFFIC WARDENS</div>', unsafe_allow_html=True)

st.divider()

# Navigation
st.sidebar.title("Welfare Menu")
menu = st.sidebar.radio(
    "Select Action",
    [
        "Register New Member", 
        "Record Monthly Payment", 
        "Monthly Payment Report", 
        "Unpaid Defaulters Report", 
        "Individual Member Ledger"
    ]
)

# ==========================================
# 1. REGISTER NEW MEMBER
# ==========================================
if menu == "Register New Member":
    st.header("📋 Register New Warden Member")
    st.info("Enter warden particulars and initial contribution.")

    with st.form("register_form", clear_on_submit=True):
        col_a, col_b = st.columns(2)
        with col_a:
            name = st.text_input("Full Name *")
            father_name = st.text_input("Father's Name *")
            belt_no = st.text_input("Belt No. (Unique ID) *")
        with col_b:
            cnic = st.text_input("CNIC Number (e.g., 35201-XXXXXXX-X) *")
            mobile = st.text_input("Mobile Number *")
            amount = st.number_input("Initial Amount Deposited (Rs.) *", min_value=1000.0, step=500.0, value=1000.0)
            submitted_date = st.date_input("Submission Date", value=datetime.today())

        submit_btn = st.form_submit_button("Register Member")

    if submit_btn:
        if not name or not father_name or not belt_no or not cnic or not mobile:
            st.error("Please fill in all required fields marked with *")
        else:
            try:
                conn = get_connection()
                c = conn.cursor()
                
                # Insert Member
                c.execute(
                    "INSERT INTO members (belt_no, name, father_name, cnic, mobile, join_date) VALUES (?, ?, ?, ?, ?, ?)",
                    (belt_no.strip(), name.strip(), father_name.strip(), cnic.strip(), mobile.strip(), str(submitted_date))
                )
                
                # Record initial payment
                month_year = submitted_date.strftime("%Y-%m")
                c.execute(
                    "INSERT INTO payments (belt_no, amount, payment_date, month_year) VALUES (?, ?, ?, ?)",
                    (belt_no.strip(), amount, str(submitted_date), month_year)
                )
                
                conn.commit()
                conn.close()
                st.success(f"Member **{name}** (Belt No: {belt_no}) successfully registered with initial payment of Rs. {amount:,.2f}!")
            except sqlite3.IntegrityError as e:
                st.error("Error: Belt No or CNIC already exists in the system!")

# ==========================================
# 2. RECORD MONTHLY PAYMENT
# ==========================================
elif menu == "Record Monthly Payment":
    st.header("💵 Record Monthly Contribution")
    
    members_df = get_members()
    if members_df.empty:
        st.warning("No members registered yet. Please register members first.")
    else:
        # Create dropdown options with Name and Belt No
        member_options = {f"{row['name']} (Belt No: {row['belt_no']})": row['belt_no'] for _, row in members_df.iterrows()}
        selected_display = st.selectbox("Select Member *", list(member_options.keys()))
        selected_belt_no = member_options[selected_display]

        with st.form("payment_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                payment_amount = st.number_input("Amount Deposited (Rs.) *", min_value=1000.0, step=500.0, value=1000.0)
                payment_date = st.date_input("Submission Date", value=datetime.today())
            with c2:
                # Select target month/year for contribution
                payment_month = st.date_input("Contribution Month", value=datetime.today(), help="Pick any date in the target month")

            submit_payment = st.form_submit_button("Record Payment")

        if submit_payment:
            target_month_year = payment_month.strftime("%Y-%m")
            conn = get_connection()
            c = conn.cursor()
            
            c.execute(
                "INSERT INTO payments (belt_no, amount, payment_date, month_year) VALUES (?, ?, ?, ?)",
                (selected_belt_no, payment_amount, str(payment_date), target_month_year)
            )
            conn.commit()
            conn.close()
            st.success(f"Payment of Rs. {payment_amount:,.2f} recorded for {selected_display} for month {target_month_year}.")

# ==========================================
# 3. MONTHLY PAYMENT REPORT (PAID)
# ==========================================
elif menu == "Monthly Payment Report":
    st.header("📊 Paid Contributions Report")
    
    # Select Month & Year
    col_m, col_y = st.columns(2)
    selected_month = col_m.selectbox("Select Month", ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"], index=datetime.now().month-1)
    selected_year = col_y.number_input("Select Year", min_value=2020, max_value=2030, value=datetime.now().year)
    
    target_period = f"{selected_year}-{selected_month}"
    
    conn = get_connection()
    query = f"""
        SELECT 
            m.belt_no AS 'Belt No',
            m.name AS 'Name',
            m.father_name AS 'Father Name',
            m.mobile AS 'Mobile No',
            p.amount AS 'Amount Paid (Rs.)',
            p.payment_date AS 'Submission Date'
        FROM payments p
        JOIN members m ON p.belt_no = m.belt_no
        WHERE p.month_year = '{target_period}'
        ORDER BY p.payment_date DESC
    """
    df_paid = pd.read_sql_query(query, conn)
    conn.close()

    st.subheader(f"Members Who Deposited Funds for {target_period}")
    if not df_paid.empty:
        st.dataframe(df_paid, use_container_width=True)
        st.metric("Total Collection for Month", f"Rs. {df_paid['Amount Paid (Rs.)'].sum():,.2f}")
        
        # Download Button
        csv = df_paid.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Paid Report (CSV)", csv, f"Paid_Report_{target_period}.csv", "text/csv")
    else:
        st.info(f"No payment records found for {target_period}.")

# ==========================================
# 4. UNPAID DEFAULTERS REPORT
# ==========================================
elif menu == "Unpaid Defaulters Report":
    st.header("⚠️ Pending Contributions Report")
    
    col_m, col_y = st.columns(2)
    selected_month = col_m.selectbox("Select Month", ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"], index=datetime.now().month-1)
    selected_year = col_y.number_input("Select Year", min_value=2020, max_value=2030, value=datetime.now().year)
    
    target_period = f"{selected_year}-{selected_month}"

    conn = get_connection()
    # Query members who DO NOT have a record in payments for selected month_year
    query = f"""
        SELECT 
            m.belt_no AS 'Belt No',
            m.name AS 'Name',
            m.father_name AS 'Father Name',
            m.cnic AS 'CNIC',
            m.mobile AS 'Mobile No',
            m.join_date AS 'Registration Date'
        FROM members m
        WHERE m.belt_no NOT IN (
            SELECT belt_no FROM payments WHERE month_year = '{target_period}'
        )
        ORDER BY m.name ASC
    """
    df_unpaid = pd.read_sql_query(query, conn)
    conn.close()

    st.subheader(f"Members Who Have NOT Deposited Funds for {target_period}")
    if not df_unpaid.empty:
        st.dataframe(df_unpaid, use_container_width=True)
        st.error(f"Total Pending Defaulters: {len(df_unpaid)} Wardens")
        
        # Download Button
        csv = df_unpaid.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Defaulters List (CSV)", csv, f"Defaulters_{target_period}.csv", "text/csv")
    else:
        st.success(f"🎉 Great news! All registered members have submitted their contributions for {target_period}.")

# ==========================================
# 5. INDIVIDUAL MEMBER LEDGER
# ==========================================
elif menu == "Individual Member Ledger":
    st.header("👤 Individual Member Payment History")
    
    members_df = get_members()
    if members_df.empty:
        st.warning("No members registered yet.")
    else:
        member_options = {f"{row['name']} (Belt No: {row['belt_no']})": row['belt_no'] for _, row in members_df.iterrows()}
        selected_display = st.selectbox("Select Member to View Ledger", list(member_options.keys()))
        selected_belt_no = member_options[selected_display]

        conn = get_connection()
        # Member Info
        member_info = pd.read_sql_query(f"SELECT * FROM members WHERE belt_no = '{selected_belt_no}'", conn).iloc[0]
        
        # Payment History
        history_df = pd.read_sql_query(f"""
            SELECT 
                month_year AS 'Contribution Month',
                amount AS 'Amount Paid (Rs.)',
                payment_date AS 'Deposit Date'
            FROM payments 
            WHERE belt_no = '{selected_belt_no}'
            ORDER BY payment_date DESC
        """, conn)
        conn.close()

        # Display Member Summary Card
        st.markdown("---")
        c1, c2, c3 = st.columns(3)
        c1.write(f"**Name:** {member_info['name']}")
        c1.write(f"**Father's Name:** {member_info['father_name']}")
        c2.write(f"**Belt No:** {member_info['belt_no']}")
        c2.write(f"**CNIC:** {member_info['cnic']}")
        c3.write(f"**Mobile:** {member_info['mobile']}")
        c3.write(f"**Joined Date:** {member_info['join_date']}")
        st.markdown("---")

        st.subheader("Payment History Records")
        if not history_df.empty:
            st.dataframe(history_df, use_container_width=True)
            total_deposited = history_df['Amount Paid (Rs.)'].sum()
            st.metric("Total Cumulative Contribution", f"Rs. {total_deposited:,.2f}")
            
            # Download Ledger CSV
            csv = history_df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Member Ledger (CSV)", csv, f"Ledger_{selected_belt_no}.csv", "text/csv")
        else:
            st.info("No payment history found for this member.")
