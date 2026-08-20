import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os

# ==========================================
# PAGE CONFIGURATION & STYLING
# ==========================================
st.set_page_config(
    page_title="Family Welfare System - Traffic Wardens",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for UI Enhancement
st.markdown("""
    <style>
        /* Global Styles */
        .stApp {
            background-color: #F8FAFC;
        }
        
        /* Hero Welcome Banner */
        .hero-card {
            background: linear-gradient(135deg, #0A2540 0%, #103B66 100%);
            border-radius: 16px;
            padding: 30px;
            color: white;
            text-align: center;
            box-shadow: 0 10px 25px rgba(10, 37, 64, 0.15);
            margin-bottom: 25px;
        }
        .hero-title {
            font-size: 2.2rem;
            font-weight: 800;
            letter-spacing: 1px;
            margin-bottom: 5px;
            color: #FFFFFF;
        }
        .hero-subtitle {
            font-size: 1.1rem;
            color: #4CAF50;
            font-weight: 600;
            letter-spacing: 2px;
            text-transform: uppercase;
        }
        
        /* Metric Card Styling */
        .metric-box {
            background: #FFFFFF;
            border-radius: 12px;
            padding: 20px;
            border-left: 5px solid #0A2540;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            text-align: center;
        }
        .metric-value {
            font-size: 1.8rem;
            font-weight: 700;
            color: #0A2540;
        }
        .metric-label {
            font-size: 0.9rem;
            color: #64748B;
            font-weight: 600;
            text-transform: uppercase;
        }
        
        /* Sidebar Navigation Styling */
        [data-testid="stSidebar"] {
            background-color: #0F172A !important;
        }
        [data-testid="stSidebar"] * {
            color: #F8FAFC !important;
        }
        .sidebar-header {
            text-align: center;
            padding: 10px 0;
            font-weight: bold;
            font-size: 1.2rem;
            color: #4CAF50 !important;
            border-bottom: 1px solid #334155;
            margin-bottom: 15px;
        }
        
        /* Custom Button Styling */
        .stButton>button {
            background-color: #0A2540;
            color: white !important;
            border-radius: 8px;
            font-weight: 600;
            border: none;
            padding: 10px 24px;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            background-color: #4CAF50;
            color: white !important;
            transform: translateY(-2px);
        }

        /* Card Container */
        .content-card {
            background-color: #FFFFFF;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.04);
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
    conn.commit()
    conn.close()

init_db()

def get_members():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM members ORDER BY name ASC", conn)
    conn.close()
    return df

# ==========================================
# SIDEBAR NAVIGATION
# ==========================================
with st.sidebar:
    # Sidebar Logo
    if os.path.exists(IMAGE_PATH):
        st.image(IMAGE_PATH, width=140)
    
    st.markdown('<div class="sidebar-header">🛡️ WELFARE PORTAL</div>', unsafe_allow_html=True)
    
    # Navigation Radio with Colorful Icons
    menu = st.radio(
        "MAIN NAVIGATION",
        [
            "🏠 Home Dashboard",
            "👤 Register Member", 
            "💳 Record Payment", 
            "🟢 Monthly Paid Report", 
            "🔴 Defaulters Report", 
            "📜 Individual Ledger"
        ]
    )

# Current Month Year
current_month_str = datetime.now().strftime("%Y-%m")

# ==========================================
# 1. HOME DASHBOARD (WELCOME SCREEN)
# ==========================================
if menu == "🏠 Home Dashboard":
    # Centered Medium-Sized Logo Header
    logo_col1, logo_col2, logo_col3 = st.columns([1.5, 2, 1.5])
    with logo_col2:
        if os.path.exists(IMAGE_PATH):
            st.image(IMAGE_PATH, width=280)
    
    # Hero Welcome Card
    st.markdown("""
        <div class="hero-card">
            <div class="hero-title">FAMILY WELFARE SYSTEM</div>
            <div class="hero-subtitle">TRAFFIC WARDENS WELFARE FUND</div>
        </div>
    """, unsafe_allow_html=True)

    # Fetch Quick Statistics
    conn = get_connection()
    total_members = pd.read_sql_query("SELECT COUNT(*) as cnt FROM members", conn).iloc[0]['cnt']
    total_fund = pd.read_sql_query("SELECT SUM(amount) as total FROM payments", conn).iloc[0]['total'] or 0.0
    monthly_collection = pd.read_sql_query(f"SELECT SUM(amount) as total FROM payments WHERE month_year = '{current_month_str}'", conn).iloc[0]['total'] or 0.0
    
    paid_count_this_month = pd.read_sql_query(f"SELECT COUNT(DISTINCT belt_no) as cnt FROM payments WHERE month_year = '{current_month_str}'", conn).iloc[0]['cnt']
    defaulters_this_month = total_members - paid_count_this_month
    conn.close()

    # Stat Cards Row
    m1, m2, m3, m4 = st.columns(4)
    
    with m1:
        st.markdown(f"""
            <div class="metric-box" style="border-left-color: #0A2540;">
                <div class="metric-label">👥 Active Members</div>
                <div class="metric-value">{total_members}</div>
            </div>
        """, unsafe_allow_html=True)

    with m2:
        st.markdown(f"""
            <div class="metric-box" style="border-left-color: #2E7D32;">
                <div class="metric-label">💰 Total Fund Collected</div>
                <div class="metric-value">Rs. {total_fund:,.0f}</div>
            </div>
        """, unsafe_allow_html=True)

    with m3:
        st.markdown(f"""
            <div class="metric-box" style="border-left-color: #0288D1;">
                <div class="metric-label">📅 {datetime.now().strftime('%b %Y')} Collection</div>
                <div class="metric-value">Rs. {monthly_collection:,.0f}</div>
            </div>
        """, unsafe_allow_html=True)

    with m4:
        st.markdown(f"""
            <div class="metric-box" style="border-left-color: #D32F2F;">
                <div class="metric-label">⚠️ Pending Defaulters</div>
                <div class="metric-value">{defaulters_this_month}</div>
            </div>
        """, unsafe_allow_html=True)

    st.write("")
    st.write("")

    # System Overview Card
    st.markdown("""
        <div class="content-card">
            <h3 style="color: #0A2540; margin-top:0;">🛡️ Welcome to the Warden Family Welfare Management System</h3>
            <p style="color: #475569; font-size: 1.05rem; line-height: 1.6;">
                This system facilitates traffic wardens in maintaining their mutual welfare fund. Each member contributes a fixed monthly amount (Rs. 1000/- or above) to support fellow officers and their families during emergencies, healthcare needs, and social welfare programs.
            </p>
            <hr style="border: 0; border-top: 1px solid #E2E8F0; margin: 15px 0;">
            <h4 style="color: #0A2540;">Quick Actions Checklist:</h4>
            <ul>
                <li><strong>Add New Officers:</strong> Use <i>👤 Register Member</i> to add new joiners and log initial deposits.</li>
                <li><strong>Monthly Collection:</strong> Record monthly fund deposits via <i>💳 Record Payment</i>.</li>
                <li><strong>Track Compliance:</strong> Instantly check paid vs. defaulter lists under <i>🟢 Monthly Paid Report</i> and <i>🔴 Defaulters Report</i>.</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# 2. REGISTER NEW MEMBER
# ==========================================
elif menu == "👤 Register Member":
    st.subheader("👤 Register New Warden Member")
    st.write("Enter warden details and initial fund contribution.")

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

        submit_btn = st.form_submit_button("Submit Registration")

    if submit_btn:
        if not name or not father_name or not belt_no or not cnic or not mobile:
            st.error("⚠️ Please fill in all required fields marked with *")
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
                st.success(f"✅ Member **{name}** (Belt No: {belt_no}) successfully registered with Rs. {amount:,.2f}!")
            except sqlite3.IntegrityError:
                st.error("❌ Error: A member with this Belt No or CNIC already exists in the database!")

# ==========================================
# 3. RECORD MONTHLY PAYMENT
# ==========================================
elif menu == "💳 Record Payment":
    st.subheader("💳 Record Monthly Contribution")
    
    members_df = get_members()
    if members_df.empty:
        st.warning("⚠️ No members registered yet. Please register members first.")
    else:
        member_options = {f"{row['name']} (Belt No: {row['belt_no']})": row['belt_no'] for _, row in members_df.iterrows()}
        selected_display = st.selectbox("Select Member *", list(member_options.keys()))
        selected_belt_no = member_options[selected_display]

        with st.form("payment_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                payment_amount = st.number_input("Amount Deposited (Rs.) *", min_value=1000.0, step=500.0, value=1000.0)
                payment_date = st.date_input("Submission Date", value=datetime.today())
            with c2:
                payment_month = st.date_input("Contribution Target Month", value=datetime.today())

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
            st.success(f"✅ Payment of **Rs. {payment_amount:,.2f}** recorded for **{selected_display}** for month **{target_month_year}**.")

# ==========================================
# 4. MONTHLY PAID REPORT
# ==========================================
elif menu == "🟢 Monthly Paid Report":
    st.subheader("🟢 Monthly Contribution Report (Paid List)")
    
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

    if not df_paid.empty:
        st.dataframe(df_paid, use_container_width=True)
        st.success(f"💰 Total Collection for {target_period}: **Rs. {df_paid['Amount Paid (Rs.)'].sum():,.2f}**")
        
        csv = df_paid.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download CSV Report", csv, f"Paid_Report_{target_period}.csv", "text/csv")
    else:
        st.info(f"ℹ️ No payment records found for target month: {target_period}.")

# ==========================================
# 5. UNPAID DEFAULTERS REPORT
# ==========================================
elif menu == "🔴 Defaulters Report":
    st.subheader("🔴 Pending Contributions Report (Defaulters List)")
    
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
        st.error(f"⚠️ Total Defaulters for {target_period}: **{len(df_unpaid)} Wardens**")
        
        csv = df_unpaid.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Defaulters List (CSV)", csv, f"Defaulters_{target_period}.csv", "text/csv")
    else:
        st.success(f"🎉 Excellent! All registered members have submitted their funds for {target_period}.")

# ==========================================
# 6. INDIVIDUAL MEMBER LEDGER
# ==========================================
elif menu == "📜 Individual Ledger":
    st.subheader("📜 Individual Member Statement & History")
    
    members_df = get_members()
    if members_df.empty:
        st.warning("⚠️ No members registered yet.")
    else:
        member_options = {f"{row['name']} (Belt No: {row['belt_no']})": row['belt_no'] for _, row in members_df.iterrows()}
        selected_display = st.selectbox("Select Member", list(member_options.keys()))
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

        # Member Details Card
        st.markdown(f"""
            <div class="content-card">
                <h4 style="color: #0A2540; margin-top:0;">👤 Member Particulars</h4>
                <div style="display: flex; justify-content: space-between; flex-wrap: wrap;">
                    <div><strong>Name:</strong> {member_info['name']}<br><strong>Father's Name:</strong> {member_info['father_name']}</div>
                    <div><strong>Belt No:</strong> {member_info['belt_no']}<br><strong>CNIC:</strong> {member_info['cnic']}</div>
                    <div><strong>Mobile:</strong> {member_info['mobile']}<br><strong>Joined Date:</strong> {member_info['join_date']}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        if not history_df.empty:
            st.dataframe(history_df, use_container_width=True)
            total_deposited = history_df['Amount Paid (Rs.)'].sum()
            st.success(f"Total Cumulative Contribution: **Rs. {total_deposited:,.2f}**")
            
            csv = history_df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Member Ledger (CSV)", csv, f"Ledger_{selected_belt_no}.csv", "text/csv")
        else:
            st.info("No payment history found for this member.")
```

### Key Improvements Made:
1. **Centered & Scaled Logo:** The logo is centered on the home dashboard with a medium width (`width=280`), eliminating raw oversized images.
2. **Hero Banner & Metrics Grid:** Created a dark navy & green hero card (`FAMILY WELFARE SYSTEM`) alongside real-time statistical cards (Active Members, Total Fund, Current Month Collection, Defaulters Count).
3. **Colorful Sidebar Navigation:** Replaced the plain radio menu with colorful, icon-rich menu options (`🏠 Home Dashboard`, `👤 Register Member`, `💳 Record Payment`, `🟢 Monthly Paid Report`, `🔴 Defaulters Report`, `📜 Individual Ledger`).
4. **Professional UI Color Palette:** Aligned fonts, margins, card containers, and button hovering actions with the navy blue and emerald green theme from your logo.
