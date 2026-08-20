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
        /* Main background & typography */
        .main {
            background-color: #f8f9fa;
        }
        
        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background-color: #0b192c;
        }
        [data-testid="stSidebar"] * {
            color: #ffffff !important;
        }
        [data-testid="stSidebar"] .stRadio label {
            padding: 8px 12px;
            border-radius: 6px;
            margin-bottom: 4px;
            transition: all 0.2s ease;
        }
        
        /* Metric cards */
        div[data-testid="stMetric"] {
            background-color: #ffffff;
            border-left: 5px solid #2e7d32;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        
        /* Header Banner Styling */
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
            font-weight: 500;
            margin: 0;
            font-style: italic;
        }
        
        /* Form container styling */
        .stForm {
            background-color: #ffffff;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }

        /* Dark Form Submit Button Styling */
        div.stFormSubmitButton > button {
            background-color: #0b192c !important;
            color: #ffffff !important;
            border: none !important;
            font-weight: 600 !important;
            padding: 10px 24px !important;
            border-radius: 6px !important;
            transition: background-color 0.3s ease !important;
        }
        
        div.stFormSubmitButton > button:hover {
            background-color: #2e7d32 !important;
            color: #ffffff !important;
        }
    </style>
""", unsafe_allow_html=True)

# 3. Database Initialization
DB_FILE = "welfare_system.db"

def get_connection():
    return sqlite3.connect(DB_FILE)

def init_db():
    conn = get_connection()
    c = conn.cursor()
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
    
    # Create default Admin if no users exist
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        c.execute(
            "INSERT INTO users (username, password, full_name, role, status) VALUES (?, ?, ?, ?, ?)",
            ("admin", "admin123", "System Administrator", "Admin", "Active")
        )
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

# Initialize Session State for Authentication
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
    st.markdown("""
        <div style="max-width: 450px; margin: 40px auto 10px auto; text-align: center;">
            <h2 style="color: #0b192c; font-weight: 800;">FAMILY WELFARE SYSTEM</h2>
            <h4 style="color: #2e7d32;">Traffic Police Punjab</h4>
            <p style="color: #666;">Please sign in to access the portal</p>
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

if st.sidebar.button("🚪 Logout"):
    st.session_state.authenticated = False
    st.session_state.username = ""
    st.session_state.user_role = ""
    st.session_state.full_name = ""
    st.rerun()

st.sidebar.markdown("---")

# Navigation Options based on Role
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

# 5. Clean Official Welcome Header with Larger Centered Logo
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

logo2_base64 = get_base64_image("logo2.png")
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
    
    current_month_str = datetime.now().strftime("%Y-%m")
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
    
    st.info("""
        **Welcome to the Traffic Wardens Family Welfare Portal**  
        Use the sidebar navigation menu on the left to:
        - Register new warden members and record initial deposits.
        - Submit monthly contributions (Rs. 1,000/- or higher).
        - View and export monthly paid/unpaid compliance reports.
        - Track individual payment histories and cumulative deposits.
    """)

# --- REGISTER MEMBER ---
elif menu == "👤 Register New Member":
    st.subheader("📋 Register New Warden Member")
    st.caption("Fill in particulars to add a new warden to the welfare registry.")

    with st.form("register_form", clear_on_submit=True):
        col_a, col_b = st.columns(2)
        with col_a:
            name = st.text_input("Full Name *")
            father_name = st.text_input("Father's Name *")
            belt_no = st.text_input("Belt No. (Unique ID) *")
        with col_b:
            cnic = st.text_input("CNIC Number (e.g., 35201-XXXXXXX-X) *")
            mobile = st.text_input("Mobile Number *")
            amount = st.number_input("Initial Amount Deposited (Rs.) *", min_value=1000.0, step=100.0, value=1000.0)
            submitted_date = st.date_input("Submission Date", value=datetime.today())

        submit_btn = st.form_submit_button("Submit Registration")

    if submit_btn:
        if not name or not father_name or not belt_no or not cnic or not mobile:
            st.error("Please fill in all required fields.")
        else:
            try:
                conn = get_connection()
                c = conn.cursor()
                c.execute(
                    "INSERT INTO members (belt_no, name, father_name, cnic, mobile, join_date) VALUES (?, ?, ?, ?, ?, ?)",
                    (belt_no.strip(), name.strip(), father_name.strip(), cnic.strip(), mobile.strip(), str(submitted_date))
                )
                month_year = submitted_date.strftime("%Y-%m")
                c.execute(
                    "INSERT INTO payments (belt_no, amount, payment_date, month_year) VALUES (?, ?, ?, ?)",
                    (belt_no.strip(), amount, str(submitted_date), month_year)
                )
                conn.commit()
                conn.close()
                st.success(f"Member **{name}** (Belt No: {belt_no}) successfully registered with initial deposit of Rs. {amount:,.2f}!")
            except sqlite3.IntegrityError:
                st.error("Error: Belt No or CNIC already exists in the database.")

# --- RECORD PAYMENT ---
elif menu == "💳 Record Monthly Payment":
    st.subheader("💵 Record Monthly Contribution")
    
    members_df = get_members()
    if members_df.empty:
        st.warning("No members registered yet. Please register members first.")
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
                payment_month = st.date_input("Contribution Month", value=datetime.today(), help="Select any date within target contribution month")

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
            p.payment_date AS 'Deposit Date'
        FROM payments p
        JOIN members m ON p.belt_no = m.belt_no
        WHERE p.month_year = '{target_period}'
        ORDER BY p.payment_date DESC
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
    selected_month = col_m.selectbox("Select Month", ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"], index=datetime.now().month-1)
    selected_year = col_y.number_input("Select Year", min_value=2020, max_value=2030, value=datetime.now().year)
    
    target_period = f"{selected_year}-{selected_month}"

    conn = get_connection()
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
    st.caption("Remove a registered warden member and purge their payment records permanently.")

    members_df = get_members()
    if members_df.empty:
        st.warning("No registered members found in the database.")
    else:
        member_options = {f"{row['name']} (Belt No: {row['belt_no']}) - CNIC: {row['cnic']}": row['belt_no'] for _, row in members_df.iterrows()}
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
    st.caption("Create new accounts, modify user roles, or disable/enable existing system users.")

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
                    new_password = st.text_input("New Password (leave plain to keep existing)", value=e_u_pass, type="password")
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
