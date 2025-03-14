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
        st.title("Quick Write Generator")
        
        # Sub-module selection for Quick Write
        default_index = 0
        if "active_write_up" in st.session_state:
            try:
                options = ["DIBH", "Fusion", "Prior Dose", "Pacemaker", "SBRT", "SRS"]
                default_index = options.index(st.session_state.active_write_up)
            except ValueError:
                pass
                
        write_up_type = st.sidebar.selectbox(
            "Select Write-Up Type",
            ["DIBH", "Fusion", "Prior Dose", "Pacemaker", "SBRT", "SRS"],
            index=default_index
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
        
        # Use a container with flex display for the buttons
        st.markdown("""
        <div class="quick-access-container">
            <button class="quick-access-button" data-type="DIBH">DIBH</button>
            <button class="quick-access-button" data-type="Fusion">Fusion</button>
            <button class="quick-access-button" data-type="Prior Dose">Prior Dose</button>
            <button class="quick-access-button" data-type="Pacemaker">Pacemaker</button>
            <button class="quick-access-button" data-type="SBRT">SBRT</button>
            <button class="quick-access-button" data-type="SRS">SRS</button>
        </div>
        """, unsafe_allow_html=True)
        
        # Initialize write-up selection from query params
        if "write_up_type" in st.query_params:
            write_up_type = st.query_params["write_up_type"]
            # Clear the parameter after reading it
            st.query_params.clear()
            # Navigate to QuickWrite with the selected write-up type
            go_to_module("Quick Write")
            st.session_state.active_write_up = write_up_type
            st.rerun()
        
        # JavaScript to handle the custom buttons
        st.markdown("""
        <script>
            // Function to set query param and reload
            function navigateToWriteUp(writeUpType) {
                const url = new URL(window.location.href);
                url.searchParams.set('write_up_type', writeUpType);
                window.location.href = url.toString();
            }
            
            // Add click listeners to all quick access buttons
            document.querySelectorAll('.quick-access-button').forEach(button => {
                button.addEventListener('click', function(e) {
                    e.preventDefault();
                    const writeUpType = this.getAttribute('data-type');
                    navigateToWriteUp(writeUpType);
                });
            });
        </script>
        """, unsafe_allow_html=True)
        
        # Main launch button
        if st.button("Launch QuickWrite", key="quickwrite_btn", use_container_width=True):
            go_to_module("Quick Write")
    
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