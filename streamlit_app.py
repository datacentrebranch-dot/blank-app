import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Family Welfare System - Traffic Wardens",
    page_icon="🛡️",
    layout="wide"
)

# Custom CSS for styling
st.markdown("""
    <style>
        .main-title {
            color: #0A2540;
            text-align: center;
            font-size: 2.2rem;
            font-weight: bold;
            margin-top: 10px;
        }
        .sub-title {
            color: #4CAF50;
            text-align: center;
            font-size: 1.2rem;
            margin-bottom: 30px;
        }
    </style>
""", unsafe_allow_html=True)

# Main Landing / Welcome Layout
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    # Display Logo Centered
    st.image("logo.png", use_container_width=True)
    st.markdown('<div class="main-title">FAMILY WELFARE SYSTEM</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">FOR TRAFFIC WARDENS</div>', unsafe_allow_html=True)

st.divider()

# Sidebar Navigation
st.sidebar.image("logo.png", width=120)
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Welfare Requests", "Family Registration", "Support & Contact"])

# Page Content
if page == "Home":
    st.header("Welcome to the Support Portal")
    st.write(
        "This platform is dedicated to serving traffic wardens and their families, providing access "
        "to welfare benefits, registration, and administrative support."
    )
    
    # Quick Action Metrics/Cards
    m1, m2, m3 = st.columns(3)
    m1.metric(label="Registered Families", value="1,240")
    m2.metric(label="Active Assistance Plans", value="85")
    m3.metric(label="Resolved Claims", value="312")

elif page == "Welfare Requests":
    st.header("Submit / Track Welfare Requests")
    st.info("Select a service to apply for welfare support.")

elif page == "Family Registration":
    st.header("Register Dependent Family Members")
    st.text_input("Warden Service ID")
    st.text_input("Dependent Name")

elif page == "Support & Contact":
    st.header("Helpdesk & Support")
    st.write("For urgent inquiries, reach out to the administrative desk.")
