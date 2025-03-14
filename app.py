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

    else:  # This is the landing page
        # Load landing-specific CSS
        load_css("assets/css/landing.css")
        
        # Clean, minimal header
        st.markdown("""
        <div class="landing-header">
            <h1>Medical Physics Residency Toolkit</h1>
            <p>Streamlining documentation for radiation oncology workflows</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Primary Card - Most important tool front and center
        st.markdown("""
        <div class="primary-card">
            <div class="card-content">
                <div class="card-icon">📝</div>
                <div class="card-text">
                    <h2>QuickWrite</h2>
                    <p>Generate standardized documentation for clinical scenarios</p>
                    <ul class="feature-list">
                        <li>DIBH Reports</li>
                        <li>Fusion Documentation</li>
                        <li>Prior Dose Analysis</li>
                        <li>Pacemaker, SBRT & SRS Documentation</li>
                    </ul>
                </div>
            </div>
            <div class="card-action" id="quickwrite-btn-container"></div>
        </div>
        """, unsafe_allow_html=True)
        
        # Place the button in the container
        button_col = st.container()
        with button_col:
            if st.button("Launch QuickWrite", key="quickwrite_btn", use_container_width=True):
                go_to_module("Quick Write")
        
        # Secondary information in collapsible sections
        with st.expander("ℹ️ About This Tool", expanded=False):
            st.markdown("""
            <div class="info-content">
                <p>The <strong>Medical Physics Residency Toolkit</strong> helps radiation oncology residents and physicists create standardized documentation efficiently.</p>
                <p>Current version: <span class="version-badge">Beta v0.9</span></p>
                <p>This toolkit streamlines workflows for common clinical scenarios, reducing documentation time and ensuring consistency.</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Bottom section with minimal visual weight
        st.markdown("""
        <div class="footer-section">
            <h3>Coming Soon</h3>
            <div class="coming-soon-grid">
                <div class="coming-soon-item">
                    <div class="soon-icon">🧠</div>
                    <div>Competency Tracker</div>
                </div>
                <div class="coming-soon-item">
                    <div class="soon-icon">📊</div>
                    <div>QA Dashboard</div>
                </div>
                <div class="coming-soon-item">
                    <div class="soon-icon">📚</div>
                    <div>Part 3 Bank</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Minimal footer with feedback option
        st.markdown("<hr class='footer-divider'>", unsafe_allow_html=True)
        
        feedback_col1, feedback_col2 = st.columns([3, 1])
        with feedback_col2:
            with st.expander("Provide Feedback", expanded=False):
                feedback_type = st.selectbox(
                    "Type", 
                    ["Bug Report", "Feature Request", "Usability", "General"]
                )
                feedback_text = st.text_area("Details", height=100)
                if st.button("Submit", use_container_width=True):
                    st.success("Thank you for your feedback!")