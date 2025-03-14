import streamlit as st
from modules.quickwrite import QuickWriteModule
from utils import load_css

# Page configuration
st.set_page_config(
    page_title="Medical Physics Residency Toolkit",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load main CSS (always loaded)
load_css("assets/css/main.css")

# Initialize session state variables
if 'show_landing_page' not in st.session_state:
    st.session_state.show_landing_page = True
if 'active_module' not in st.session_state:
    st.session_state.active_module = None

# Navigation functions
def go_to_module(module_name):
    st.session_state.show_landing_page = False
    st.session_state.active_module = module_name

def go_to_landing_page():
    st.session_state.show_landing_page = True
    st.session_state.active_module = None

# Initialize modules
quick_write = QuickWriteModule()

# Sidebar for navigation when not on landing page
if not st.session_state.show_landing_page:
    st.sidebar.title("Residency Toolkit")
    
    # Back to Home button
    if st.sidebar.button("← Back to Home"):
        go_to_landing_page()
    
    # Module selector
    visible_modules = ["Quick Write"]
    
    selected_module = st.sidebar.selectbox(
        "Select Module",
        visible_modules
    )
    
    # Switch to the selected module if changed
    if selected_module != st.session_state.active_module:
        st.session_state.active_module = selected_module
        st.rerun()

    # Display selected module content
    active_module = st.session_state.active_module
    
    if active_module == "Quick Write":
        st.title("Quick Write Generator")
        
        # Sub-module selection for Quick Write
        write_up_type = st.sidebar.selectbox(
            "Select Write-Up Type",
            ["DIBH", "Fusion", "Prior Dose", "Pacemaker", "SBRT", "SRS"]
        )
        
        # Display the appropriate form based on selection
        if write_up_type == "DIBH":
            write_up = quick_write.render_dibh_form()
            quick_write.dibh_module.display_write_up(write_up)
        elif write_up_type == "Fusion":
            write_up = quick_write.render_fusion_form()
            quick_write.fusion_module.display_write_up(write_up)
        elif write_up_type == "Prior Dose":
            write_up = quick_write.render_prior_dose_form()
            quick_write.prior_dose_module.display_write_up(write_up)
        elif write_up_type == "Pacemaker":
            write_up = quick_write.render_pacemaker_form()
            quick_write.pacemaker_module.display_write_up(write_up)
        elif write_up_type == "SBRT":
            write_up = quick_write.render_sbrt_form()
            quick_write.sbrt_module.display_write_up(write_up)
        elif write_up_type == "SRS":
            write_up = quick_write.render_srs_form()
            quick_write.srs_module.display_write_up(write_up)
        else:
            st.info(f"The {write_up_type} write-up type is under development.")

    elif active_module in ["Competency Tracker", "Part 3 Bank"]:
        st.title(f"{active_module}")
        st.info(f"The {active_module} module is under development.")

else:  # This is the landing page
    # Load landing-specific CSS
    load_css("assets/css/landing.css")
    
    # Header section with gradient background
    st.markdown("""
    <div class="landing-header">
        <h1>Medical Physics Residency Toolkit</h1>
        <p>Streamlining documentation for clinical workflows in radiation oncology</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Main tools section
    st.markdown("## Available Tools")
    
    # Use columns for tool modules
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📝 QuickWrite")
        st.markdown("""
        Generate professional documentation for DIBH, Fusion, Prior Dose, 
        Pacemaker, SBRT, and SRS clinical scenarios.
        """)
        if st.button("Launch QuickWrite", key="quickwrite_btn", use_container_width=True):
            go_to_module("Quick Write")
    
    with col2:
        st.markdown("### 🔍 Coming Soon")
        st.markdown("""
        More tools are under development! We're working on additional features 
        to help streamline your clinical workflows.
        """)
        st.button("In Development", disabled=True, use_container_width=True)
    
    # About section in a card
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class="info-card">
        <h3>About This Tool <span class="version-badge">Beta v0.9</span></h3>
        <p>The <strong>Medical Physics Residency Toolkit</strong> is designed to help radiation oncology 
        residents and physicists create standardized, professional documentation quickly and efficiently.</p>
        
        <p>This toolkit streamlines workflows for common clinical scenarios, reducing documentation time and 
        ensuring consistency. Current functionality focuses on template-based report generation.</p>
        
        <p>This tool is under active development, and we welcome your feedback to improve future versions.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Feedback section
    with st.expander("📝 Provide Feedback", expanded=False):
        st.markdown("""
        <div class="feedback-card">
            Help us improve the toolkit by sharing your experience and suggestions!
        </div>
        """, unsafe_allow_html=True)
        
        feedback_type = st.selectbox(
            "Feedback Type", 
            ["Bug Report", "Feature Request", "Usability Issue", "General Feedback"]
        )
        
        feedback_text = st.text_area(
            "Your Feedback", 
            height=100, 
            placeholder="Please describe your experience, issues, or suggestions..."
        )
        
        if st.button("Submit Feedback", use_container_width=True):
            # In a full implementation, send this feedback to a database or email
            st.success("Thank you for your feedback! We'll use it to improve the tool.")