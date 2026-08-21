import os
import sqlite3
import base64
import pandas as pd
from datetime import datetime
import streamlit as st

# 1. Page Config
st.set_page_config(
    page_title="Family Welfare System - Traffic Police Punjab",
    page_icon="🛡️",
    layout="wide"
)

# 2. Custom CSS Styling
st.markdown("""
    <style>
        .main { background-color: #f8f9fa; }
        
        [data-testid="stSidebar"] > div:first-child {
            display: flex;
            flex-direction: column;
            height: 100vh;
        }
        [data-testid="stSidebar"] { background-color: #0b192c; }
        [data-testid="stSidebar"] * { color: #ffffff !important; }
        
        [data-testid="stSidebar"] div.stButton > button {
            background-color: #162a45 !important;
            color: #ffffff !important;
            border: 1px solid #2e7d32 !important;
            width: 100% !important;
            border-radius: 6px !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
        }
        [data-testid="stSidebar"] div.stButton > button:hover {
            background-color: #2e7d32 !important;
            color: #ffffff !important;
        }
        
        div[data-testid="stMetric"] {
            background-color: #ffffff;
            border-left: 5px solid #2e7d32;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        
        .header-container {
            background-color: #ffffff;
            padding: 25px 20px;
            border-radius: 10px;
            text-align: center;
            border-bottom: 4px solid #2e7d32;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            margin-bottom: 25px;
        }
        .main-title {
            color: #0b192c;
            font-size: 2.3rem;
            font-weight: 800;
            letter-spacing: 1px;
            margin: 0;
            text-transform: uppercase;
        }
        .dept-title {
            color: #2e7d32;
            font-size: 1.4rem;
            font-weight: 700;
            margin-top: 5px;
            margin-bottom: 8px;
        }
        .tagline-text {
            color: #555555;
            font-size: 1rem;
            font-style: italic;
        }
        .stForm {
            background-color: #ffffff;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }
        div.stFormSubmitButton > button {
            background-color: #0b192c !important;
            color: #ffffff !important;
            border: none !important;
            font-weight: 600 !important;
            padding: 10px 24px !important;
            border-radius: 6px !important;
            width: 100% !important;
        }
        div.stFormSubmitButton > button:hover {
            background-color: #2e7d32 !important;
            color: #ffffff !important;
        }
    </style>
""", unsafe_allow_html=True)

# Helper function to get base64 image strings
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

# 3. Database Initialization & Automated Excel Data Migration
DB_FILE = "welfare_system.db"
EXCEL_FILE = "old record database.xlsx"

def get_connection():
    return sqlite3.connect(DB_FILE)

def migrate_excel_data():
    if not os.path.exists(EXCEL_FILE):
        return

    try:
        df_raw = pd.read_excel(EXCEL_FILE, sheet_name='Sheet1 (2)')
        df_raw.columns = df_raw.iloc[0].values
        df_members = df_raw[1:169].reset_index(drop=True)

        df_members['Belt #'] = df_members['Belt #'].astype(str).str.strip()
        df_members['Name '] = df_members['Name '].astype(str).str.strip()
        df_members['Ph. #'] = df_members['Ph. #'].astype(str).str.strip().replace('nan', '')

        clean_members = df_members[
            df_members['Belt #'].notna() & 
            (df_members['Belt #'] != 'nan') & 
            (df_members['Name '] != 'TOTAL')
        ].copy()

        conn = get_connection()
        c = conn.cursor()

        # Insert members
        for _, row in clean_members.iterrows():
            belt_no = row['Belt #']
            name = row['Name ']
            phone = row['Ph. #'] if row['Ph. #'] else 'N/A'
            c.execute("""
                INSERT OR IGNORE INTO members (belt_no, name, father_name, cnic, mobile, join_date)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (belt_no, name, 'N/A', f"CNIC-{belt_no}", phone, "2025-12-01"))

        # Map monthly columns to dates
        month_map = {
            'December ': '2025-12',
            'January ': '2026-01',
            'February': '2026-02',
            'March': '2026-03',
            'April': '2026-04',
            'May': '2026-05',
            'June': '2026-06',
            'JULY': '2026-07',
            'AUG': '2026-08'
        }

        # Insert monthly payment logs
        for _, row in clean_members.iterrows():
            belt_no = row['Belt #']
            for col_name, month_yr in month_map.items():
                val = pd.to_numeric(row[col_name], errors='coerce')
                if pd.notna(val) and val > 0:
                    c.execute("""
                        INSERT INTO payments (belt_no, amount, payment_date, month_year)
                        VALUES (?, ?, ?, ?)
                    """, (belt_no, float(val), f"{month_yr}-01", month_yr))

        conn.commit()
        conn.close()
    except Exception as e:
        print("Data migration notice:", e)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS members (
            belt_no TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            father_name TEXT,
            cnic TEXT,
            mobile TEXT,
            join_date DATE
        )
    ''')
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
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT NOT NULL,
            status TEXT NOT NULL
        )
    ''')
    
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        c.execute(
            "INSERT INTO users (username, password, full_name, role, status) VALUES (?, ?, ?, ?, ?)",
            ("admin", "admin123", "System Administrator", "Admin", "Active")
        )
    
    # Check if members table is empty, then trigger automatic Excel migration
    c.execute("SELECT COUNT(*) FROM members")
    if c.fetchone()[0] == 0:
        conn.commit()
        conn.close()
        migrate_excel_data()
    else:
        conn.commit()
        conn.close()

init_db()

def get_members():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM members ORDER BY name ASC", conn)
    conn.close()
    return df

def get_users():
    conn = get_connection()
    df = pd.read_sql_query("SELECT username, full_name, role, status FROM users ORDER BY username ASC", conn)
    conn.close()
    return df

# Initialize Session State
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "user_role" not in st.session_state:
    st.session_state.user_role = ""
if "full_name" not in st.session_state:
    st.session_state.full_name = ""

# --- LOGIN SCREEN ---
if not st.session_state.authenticated:
    logo_base64 = get_base64_image("logo.png")
    header_logo_html = f'<img src="data:image/png;base64,{logo_base64}" style="height: 110px; margin-bottom: 12px; display: block; margin-left: auto; margin-right: auto;">' if logo_base64 else ''

    st.markdown(f"""
        <div class="header-container">
            {header_logo_html}
            <div class="main-title">FAMILY WELFARE SYSTEM</div>
            <div class="dept-title">Traffic Police Punjab</div>
            <div class="tagline-text">A Digital Welfare & Financial Management Portal for Traffic Wardens</div>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.2, 1])

    with col2:
        st.markdown("""
            <div style="text-align: center; margin-bottom: 15px;">
                <h3 style="color: #0b192c; font-weight: 700; margin-bottom: 0px;">🔐 System Login Portal</h3>
                <p style="color: #666666; font-size: 0.95rem;">Enter your credentials to access the portal</p>
            </div>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            login_user = st.text_input("Username")
            login_pass = st.text_input("Password", type="password")
            login_submit = st.form_submit_button("Sign In")

        if login_submit:
            conn = get_connection()
            c = conn.cursor()
            c.execute("SELECT username, password, full_name, role, status FROM users WHERE username = ?", (login_user.strip(),))
            user_row = c.fetchone()
            conn.close()

            if user_row:
                u_name, u_pass, f_name, u_role, u_status = user_row
                if u_pass == login_pass:
                    if u_status == "Disabled":
                        st.error("This user account has been disabled. Please contact an Administrator.")
                    else:
                        st.session_state.authenticated = True
                        st.session_state.username = u_name
                        st.session_state.full_name = f_name
                        st.session_state.user_role = u_role
                        st.rerun()
                else:
                    st.error("Invalid Username or Password.")
            else:
                st.error("Invalid Username or Password.")

    st.stop()

# 4. Sidebar Navigation
IMAGE_PATH = "logo.png"

if os.path.exists(IMAGE_PATH):
    sb_col1, sb_col2, sb_col3 = st.sidebar.columns([1, 2, 1])
    with sb_col2:
        st.image(IMAGE_PATH, use_container_width=True)

st.sidebar.markdown("<h3 style='text-align: center;'>🛡️ Welfare Portal</h3>", unsafe_allow_html=True)
st.sidebar.markdown(f"**User:** {st.session_state.full_name} ({st.session_state.user_role})")
st.sidebar.markdown("---")

nav_options = [
    "🏠 Home Dashboard", 
    "👤 Register New Member", 
    "💳 Record Monthly Payment", 
    "📊 Paid Monthly Report", 
    "⚠️ Unpaid Defaulters List", 
    "🔍 Individual Ledger"
]

if st.session_state.user_role == "Admin":
    nav_options.append("🗑️ Manage & Delete Member")
    nav_options.append("⚙️ User Administration")

menu = st.sidebar.radio("Navigation Menu", nav_options)

# Bottom Logout Button
bottom_container = st.sidebar.container()
with bottom_container:
    st.sidebar.markdown("<br><br>", unsafe_allow_html=True)
    if st.sidebar.button("🚪 Logout"):
        st.session_state.authenticated = False
        st.session_state.username = ""
        st.session_state.user_role = ""
        st.session_state.full_name = ""
        st.rerun()

# 5. Clean Official Welcome Header
logo2_base64 = get_base64_image("logo2.png") or get_base64_image("logo.png")
logo_html = f'<img src="data:image/png;base64,{logo2_base64}" style="height: 120px; margin-bottom: 15px; display: block; margin-left: auto; margin-right: auto;">' if logo2_base64 else ''

st.markdown(f"""
    <div class="header-container">
        {logo_html}
        <div class="main-title">FAMILY WELFARE SYSTEM</div>
        <div class="dept-title">Traffic Police Punjab</div>
        <div class="tagline-text">A Digital Welfare & Financial Management Portal for Traffic Wardens</div>
    </div>
""", unsafe_allow_html=True)

# 6. Page Routing

# --- HOME DASHBOARD ---
if menu == "🏠 Home Dashboard":
    st.subheader("📌 System Overview & Quick Summary")
    
    current_month_str = "2026-08"
    conn = get_connection()
    
    total_members = pd.read_sql_query("SELECT COUNT(*) as cnt FROM members", conn).iloc[0]['cnt']
    total_collected = pd.read_sql_query("SELECT SUM(amount) as total FROM payments", conn).iloc[0]['total'] or 0.0
    monthly_collected = pd.read_sql_query(f"SELECT SUM(amount) as total FROM payments WHERE month_year = '{current_month_str}'", conn).iloc[0]['total'] or 0.0
    paid_count = pd.read_sql_query(f"SELECT COUNT(DISTINCT belt_no) as cnt FROM payments WHERE month_year = '{current_month_str}'", conn).iloc[0]['cnt']
    defaulters_count = max(0, total_members - paid_count)
    
    conn.close()

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Registered Wardens", f"{total_members:,}")
    m2.metric("Total Fund Reserve", f"Rs. {total_collected:,.0f}")
    m3.metric(f"Collection ({current_month_str})", f"Rs. {monthly_collected:,.0f}")
    m4.metric(f"Pending Defaulters ({current_month_str})", f"{defaulters_count} Wardens")

    st.markdown("<br>", unsafe_allow_html=True)
    st.success("✅ **Excel Records Loaded:** All historical records from `old record database.xlsx` have been imported into the active database!")

# --- REGISTER MEMBER ---
elif menu == "👤 Register New Member":
    st.subheader("📋 Register New Warden Member")

    with st.form("register_form", clear_on_submit=True):
        col_a, col_b = st.columns(2)
        with col_a:
            name = st.text_input("Full Name *")
            father_name = st.text_input("Father's Name")
            belt_no = st.text_input("Belt No. (Unique ID) *")
        with col_b:
            cnic = st.text_input("CNIC Number")
            mobile = st.text_input("Mobile Number")
            amount = st.number_input("Initial Deposit (Rs.) *", min_value=1000.0, step=100.0, value=1000.0)
            submitted_date = st.date_input("Submission Date", value=datetime.today())

        submit_btn = st.form_submit_button("Submit Registration")

    if submit_btn:
        if not name or not belt_no:
            st.error("Please provide both Full Name and Belt Number.")
        else:
            try:
                conn = get_connection()
                c = conn.cursor()
                c.execute(
                    "INSERT INTO members (belt_no, name, father_name, cnic, mobile, join_date) VALUES (?, ?, ?, ?, ?, ?)",
                    (belt_no.strip(), name.strip(), father_name.strip() or 'N/A', cnic.strip() or 'N/A', mobile.strip() or 'N/A', str(submitted_date))
                )
                month_year = submitted_date.strftime("%Y-%m")
                c.execute(
                    "INSERT INTO payments (belt_no, amount, payment_date, month_year) VALUES (?, ?, ?, ?)",
                    (belt_no.strip(), amount, str(submitted_date), month_year)
                )
                conn.commit()
                conn.close()
                st.success(f"Member **{name}** (Belt No: {belt_no}) successfully registered!")
            except sqlite3.IntegrityError:
                st.error("Error: Belt No already exists in the database.")

# --- RECORD PAYMENT ---
elif menu == "💳 Record Monthly Payment":
    st.subheader("💵 Record Monthly Contribution")
    
    members_df = get_members()
    if members_df.empty:
        st.warning("No members registered yet.")
    else:
        member_options = {f"{row['name']} (Belt No: {row['belt_no']})": row['belt_no'] for _, row in members_df.iterrows()}
        selected_display = st.selectbox("Select Warden Member *", list(member_options.keys()))
        selected_belt_no = member_options[selected_display]

        with st.form("payment_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                payment_amount = st.number_input("Amount Deposited (Rs.) *", min_value=1000.0, step=100.0, value=1000.0)
                payment_date = st.date_input("Deposit Date", value=datetime.today())
            with c2:
                payment_month = st.date_input("Contribution Month", value=datetime.today())

            submit_payment = st.form_submit_button("Save Payment Record")

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
            st.success(f"Payment of Rs. {payment_amount:,.2f} recorded for {selected_display} for period {target_month_year}.")

# --- PAID REPORT ---
elif menu == "📊 Paid Monthly Report":
    st.subheader("📊 Submitted Funds Report")
    
    col_m, col_y = st.columns(2)
    selected_month = col_m.selectbox("Select Month", ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"], index=7)
    selected_year = col_y.number_input("Select Year", min_value=2020, max_value=2030, value=2026)
    
    target_period = f"{selected_year}-{selected_month}"
    
    conn = get_connection()
    query = f"""
        SELECT 
            m.belt_no AS 'Belt No',
            m.name AS 'Name',
            m.mobile AS 'Mobile No',
            p.amount AS 'Amount Paid (Rs.)',
            p.payment_date AS 'Deposit Date'
        FROM payments p
        JOIN members m ON p.belt_no = m.belt_no
        WHERE p.month_year = '{target_period}'
        ORDER BY m.name ASC
    """
    df_paid = pd.read_sql_query(query, conn)
    conn.close()

    if not df_paid.empty:
        st.dataframe(df_paid, use_container_width=True)
        st.metric("Total Monthly Collection", f"Rs. {df_paid['Amount Paid (Rs.)'].sum():,.2f}")
        csv = df_paid.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Export Paid List (CSV)", csv, f"Paid_Report_{target_period}.csv", "text/csv")
    else:
        st.info(f"No deposits recorded for period {target_period}.")

# --- UNPAID DEFAULTERS LIST ---
elif menu == "⚠️ Unpaid Defaulters List":
    st.subheader("⚠️ Pending Contribution Defaulters")
    
    col_m, col_y = st.columns(2)
    selected_month = col_m.selectbox("Select Month", ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"], index=7)
    selected_year = col_y.number_input("Select Year", min_value=2020, max_value=2030, value=2026)
    
    target_period = f"{selected_year}-{selected_month}"

    conn = get_connection()
    query = f"""
        SELECT 
            m.belt_no AS 'Belt No',
            m.name AS 'Name',
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

    if not df_unpaid.empty:
        st.dataframe(df_unpaid, use_container_width=True)
        st.error(f"Total Pending Defaulters: {len(df_unpaid)} Wardens")
        csv = df_unpaid.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Export Defaulters List (CSV)", csv, f"Defaulters_{target_period}.csv", "text/csv")
    else:
        st.success(f"All members have deposited their welfare funds for {target_period}.")

# --- INDIVIDUAL LEDGER ---
elif menu == "🔍 Individual Ledger":
    st.subheader("👤 Individual Warden Deposit History")
    
    members_df = get_members()
    if members_df.empty:
        st.warning("No members registered yet.")
    else:
        member_options = {f"{row['name']} (Belt No: {row['belt_no']})": row['belt_no'] for _, row in members_df.iterrows()}
        selected_display = st.selectbox("Select Warden", list(member_options.keys()))
        selected_belt_no = member_options[selected_display]

        conn = get_connection()
        member_info = pd.read_sql_query(f"SELECT * FROM members WHERE belt_no = '{selected_belt_no}'", conn).iloc[0]
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

        st.markdown("---")
        c1, c2, c3 = st.columns(3)
        c1.write(f"**Name:** {member_info['name']}")
        c1.write(f"**Father's Name:** {member_info['father_name']}")
        c2.write(f"**Belt No:** {member_info['belt_no']}")
        c2.write(f"**CNIC:** {member_info['cnic']}")
        c3.write(f"**Mobile:** {member_info['mobile']}")
        c3.write(f"**Registration Date:** {member_info['join_date']}")
        st.markdown("---")

        if not history_df.empty:
            st.dataframe(history_df, use_container_width=True)
            st.metric("Total Cumulative Contribution", f"Rs. {history_df['Amount Paid (Rs.)'].sum():,.2f}")
            csv = history_df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Export Member Ledger (CSV)", csv, f"Ledger_{selected_belt_no}.csv", "text/csv")
        else:
            st.info("No deposit history found for this member.")

# --- MANAGE & DELETE MEMBER (ADMIN ONLY) ---
elif menu == "🗑️ Manage & Delete Member" and st.session_state.user_role == "Admin":
    st.subheader("🗑️ Delete Warden Record")

    members_df = get_members()
    if members_df.empty:
        st.warning("No registered members found in the database.")
    else:
        member_options = {f"{row['name']} (Belt No: {row['belt_no']})": row['belt_no'] for _, row in members_df.iterrows()}
        selected_display = st.selectbox("Select Warden to Remove *", list(member_options.keys()))
        selected_belt_no = member_options[selected_display]

        conn = get_connection()
        member_info = pd.read_sql_query(f"SELECT * FROM members WHERE belt_no = '{selected_belt_no}'", conn).iloc[0]
        conn.close()

        st.warning(f"⚠️ **Warning:** You are selecting **{member_info['name']}** (Belt No: **{member_info['belt_no']}**) for permanent removal.")
        
        confirm = st.checkbox("I confirm that I want to delete this warden and all associated payment history.")
        
        if st.button("Permanently Delete Member", type="primary"):
            if confirm:
                conn = get_connection()
                c = conn.cursor()
                c.execute("DELETE FROM payments WHERE belt_no = ?", (selected_belt_no,))
                c.execute("DELETE FROM members WHERE belt_no = ?", (selected_belt_no,))
                conn.commit()
                conn.close()
                st.success(f"Member **{member_info['name']}** (Belt No: {selected_belt_no}) has been deleted.")
                st.rerun()
            else:
                st.error("Please check the confirmation box to proceed with deletion.")

# --- USER ADMINISTRATION (ADMIN ONLY) ---
elif menu == "⚙️ User Administration" and st.session_state.user_role == "Admin":
    st.subheader("⚙️ System User Administration")

    tab1, tab2 = st.tabs(["👤 Existing Users", "➕ Create New User"])

    with tab1:
        st.markdown("#### **Active System Users**")
        users_df = get_users()
        st.dataframe(users_df, use_container_width=True)

        st.markdown("---")
        st.markdown("#### **Modify or Disable User Account**")
        
        user_list = users_df['username'].tolist()
        selected_user = st.selectbox("Select User to Modify", user_list)

        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT username, password, full_name, role, status FROM users WHERE username = ?", (selected_user,))
        target_user = c.fetchone()
        conn.close()

        if target_user:
            with st.form("edit_user_form"):
                e_u_name, e_u_pass, e_f_name, e_role, e_status = target_user
                
                col1, col2 = st.columns(2)
                with col1:
                    new_full_name = st.text_input("Full Name", value=e_f_name)
                    new_password = st.text_input("New Password", value=e_u_pass, type="password")
                with col2:
                    new_role = st.selectbox("Role", ["Admin", "Operator"], index=0 if e_role == "Admin" else 1)
                    new_status = st.selectbox("Account Status", ["Active", "Disabled"], index=0 if e_status == "Active" else 1)

                update_btn = st.form_submit_button("Update User Profile")

            if update_btn:
                conn = get_connection()
                c = conn.cursor()
                c.execute(
                    "UPDATE users SET full_name = ?, password = ?, role = ?, status = ? WHERE username = ?",
                    (new_full_name.strip(), new_password, new_role, new_status, selected_user)
                )
                conn.commit()
                conn.close()
                st.success(f"User **{selected_user}** successfully updated!")
                st.rerun()

    with tab2:
        st.markdown("#### **Register New System User**")
        with st.form("create_user_form", clear_on_submit=True):
            col_a, col_b = st.columns(2)
            with col_a:
                new_username = st.text_input("Username *")
                new_full_name = st.text_input("Full Name *")
                new_password = st.text_input("Password *", type="password")
            with col_b:
                new_role = st.selectbox("User Role *", ["Operator", "Admin"])
                new_status = st.selectbox("Initial Status *", ["Active", "Disabled"])

            create_btn = st.form_submit_button("Create User Account")

        if create_btn:
            if not new_username or not new_full_name or not new_password:
                st.error("Please fill in all required fields.")
            else:
                try:
                    conn = get_connection()
                    c = conn.cursor()
                    c.execute(
                        "INSERT INTO users (username, password, full_name, role, status) VALUES (?, ?, ?, ?, ?)",
                        (new_username.strip().lower(), new_password, new_full_name.strip(), new_role, new_status)
                    )
                    conn.commit()
                    conn.close()
                    st.success(f"User account **{new_username}** ({new_role}) successfully created!")
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error(f"Error: Username '{new_username}' already exists.")
