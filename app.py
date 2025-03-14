import streamlit as st
from modules.quickwrite import QuickWriteModule
from utils import load_css
from theme_utils import inject_theme_responsive_css, load_theme_aware_css

# Page configuration
st.set_page_config(
    page_title="Medical Physics Residency Toolkit",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject theme-responsive CSS (this should be first before any UI is shown)
inject_theme_responsive_css()

# Load main CSS (it will now use the theme variables)
load_theme_aware_css("assets/css/main.css")

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
        # Get the write-up type from session state or URL parameter, default to DIBH if not specified
        write_up_type = st.session_state.get("active_write_up", "DIBH")
        
        # Show which module we're in
        st.title(f"{write_up_type} Write-Up Generator")
        
        # Add a dropdown to allow changing the form type
        new_write_up_type = st.sidebar.selectbox(
            "Change Write-Up Type",
            ["DIBH", "Fusion", "Prior Dose", "Pacemaker", "SBRT", "SRS"],
            index=["DIBH", "Fusion", "Prior Dose", "Pacemaker", "SBRT", "SRS"].index(write_up_type)
        )
        
        # If the user changed the type using the dropdown, update and rerun
        if new_write_up_type != write_up_type:
            st.session_state.active_write_up = new_write_up_type
            st.rerun()
        
        # Display the appropriate form based on the write_up_type
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
    # Load landing-specific CSS with theme awareness
    load_theme_aware_css("assets/css/landing.css")
    
    # Clean header with title (removed emoji)
    col1, col2 = st.columns([1, 5])
    with col2:
        st.title("Medical Physics Residency Toolkit")
        st.markdown("<p class='subtitle'>Streamlining documentation for radiation oncology workflows</p>", unsafe_allow_html=True)
    
    # Main content tabs - matching QuickWrite styling
    tools_tab, about_tab, coming_soon_tab = st.tabs([
        "Available Tools", "About", "Coming Soon"
    ])
    
    with tools_tab:
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Main tools with clear descriptions - removed feature tags that looked clickable
        st.markdown("""
        <div class='tool-card'>
            <h2>Quick Write Generator</h2>
            <p>Generate standardized clinical documentation with guided forms for DIBH, Fusion, Prior Dose, Pacemaker, SBRT, and SRS reports.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Direct navigation to specific write-up types - more condensed layout
        st.markdown("<p><strong>Quick Access:</strong> Select a write-up type to begin</p>", unsafe_allow_html=True)
        
        # Use columns for layout
        cols = st.columns(3)
        # DIBH button
        if cols[0].button("DIBH", key="dibh_direct_btn", use_container_width=True):
            st.session_state.active_write_up = "DIBH"
            go_to_module("Quick Write")
            st.rerun()
        # Fusion button
        if cols[1].button("Fusion", key="fusion_direct_btn", use_container_width=True):
            st.session_state.active_write_up = "Fusion"
            go_to_module("Quick Write")
            st.rerun()
        # Prior Dose button
        if cols[2].button("Prior Dose", key="prior_dose_direct_btn", use_container_width=True):
            st.session_state.active_write_up = "Prior Dose"
            go_to_module("Quick Write")
            st.rerun()

        # Another row for the remaining buttons
        cols = st.columns(3)
        # Pacemaker button
        if cols[0].button("Pacemaker", key="pacemaker_direct_btn", use_container_width=True):
            st.session_state.active_write_up = "Pacemaker"
            go_to_module("Quick Write")
            st.rerun()
        # SBRT button
        if cols[1].button("SBRT", key="sbrt_direct_btn", use_container_width=True):
            st.session_state.active_write_up = "SBRT"
            go_to_module("Quick Write")
            st.rerun()
        # SRS button
        if cols[2].button("SRS", key="srs_direct_btn", use_container_width=True):
            st.session_state.active_write_up = "SRS"
            go_to_module("Quick Write")
            st.rerun()
        
    with about_tab:
        st.markdown("<br>", unsafe_allow_html=True)
        
        # About section with cards for better organization
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class='info-card'>
                <h3>Purpose</h3>
                <p>The <b>Medical Physics Residency Toolkit</b> is designed to help radiation oncology residents and physicists create standardized documentation quickly and accurately, improving clinical workflow efficiency.</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class='info-card'>
                <h3>Current Version</h3>
                <p><span class='version'>Beta v0.9</span></p>
                <p>Last updated: March 2025</p>
                <p>For help or suggestions, use the feedback form below.</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Simple feedback section
        with st.expander("Provide Feedback", expanded=False):
            feedback_type = st.selectbox("Type", ["Bug Report", "Feature Request", "General Feedback"])
            feedback_text = st.text_area("Details")
            if st.button("Submit Feedback"):
                st.success("Thank you for your feedback!")
    
    with coming_soon_tab:
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Coming soon features - reduced to only first two items
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class='coming-soon-card'>
                <h3>📊 QA Dashboard</h3>
                <p>Interactive quality assurance tracking and visualization</p>
                <div class='timeline'>In development</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class='coming-soon-card'>
                <h3>📚 Rogue Resident </h3>
                <p>Rogue-like study tool to sharpen your medical physics knowledge</p>
                <div class='timeline'>In development</div>
            </div>
            """, unsafe_allow_html=True)