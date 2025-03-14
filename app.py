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

    # Update this section in app.py to replace the current landing page code

    # Replace the entire landing page section in app.py with this minimal version

    # Replace JUST the 'else' section in your original app.py with this:

else:  # This is the landing page
    # Load landing-specific CSS (keep this)
    load_css("assets/css/landing.css")
    
    # Simple header
    st.title("Medical Physics Residency Toolkit")
    st.markdown("<p class='subtitle'>Streamlining documentation for radiation oncology workflows</p>", unsafe_allow_html=True)
    
    # Add some spacing
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Main tool card
    st.markdown("""
    <div class='tool-card'>
        <h2>📝 QuickWrite</h2>
        <p>Generate professional documentation for clinical scenarios</p>
        <div class='features'>
            <span>DIBH</span>
            <span>Fusion</span>
            <span>Prior Dose</span>
            <span>Pacemaker</span>
            <span>SBRT</span>
            <span>SRS</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Placing the button outside of HTML for reliability
    if st.button("Launch QuickWrite", key="quickwrite_btn", use_container_width=True):
        go_to_module("Quick Write")
    
    # Add some spacing
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Info and coming soon sections using columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<h3>About This Tool</h3>", unsafe_allow_html=True)
        st.markdown("<p>The <b>Medical Physics Residency Toolkit</b> is designed to help radiation oncology residents and physicists create standardized documentation quickly.</p>", unsafe_allow_html=True)
        st.markdown("<p>Current version: <span class='version'>Beta v0.9</span></p>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<h3>Coming Soon</h3>", unsafe_allow_html=True)
        st.markdown("<p>📊 QA Dashboard</p>", unsafe_allow_html=True)
        st.markdown("<p>🧠 Competency Tracker</p>", unsafe_allow_html=True)
        st.markdown("<p>📚 Part 3 Bank</p>", unsafe_allow_html=True)
    
    # Simple feedback section
    st.markdown("<hr>", unsafe_allow_html=True)
    with st.expander("Provide Feedback"):
        feedback_type = st.selectbox("Type", ["Bug Report", "Feature Request", "General"])
        feedback_text = st.text_area("Details")
        if st.button("Submit Feedback"):
            st.success("Thank you for your feedback!")