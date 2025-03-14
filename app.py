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

    else:  # Landing page
        # Load CSS
        load_css("assets/css/landing.css")
        
        # Title and subtitle - pure Streamlit, no custom HTML
        st.title("Medical Physics Residency Toolkit")
        st.write("Streamlining documentation for radiation oncology workflows")
        
        # Main card using pure Streamlit
        st.markdown("---")
        st.subheader("📝 QuickWrite")
        st.write("Generate standardized documentation for clinical scenarios")
        
        # Features as simple text
        st.write("Features: DIBH Reports, Fusion Documentation, Prior Dose Analysis, Pacemaker & SBRT Reports")
        
        # Launch button
        if st.button("Launch QuickWrite", type="primary", use_container_width=True):
            go_to_module("Quick Write")
        
        # About this tool
        st.markdown("---")
        with st.expander("About This Tool"):
            st.write("The Medical Physics Residency Toolkit helps radiation oncology residents and physicists create standardized documentation efficiently.")
            st.write("Current version: Beta v0.9")
        
        # Coming soon
        st.markdown("---")
        st.subheader("Coming Soon")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write("🧠 Competency Tracker")
        with col2:
            st.write("📊 QA Dashboard")
        with col3:
            st.write("📚 Part 3 Bank")