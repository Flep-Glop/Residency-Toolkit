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

# Update the 'else' section in app.py (the landing page part)
else:  # This is the landing page
    # Load landing-specific CSS
    load_css("assets/css/landing.css")
    
    # Add theme detection
    theme = st.get_option("theme.base")
    st.markdown(f"""
    <script>
        document.documentElement.setAttribute('data-theme', '{theme}');
    </script>
    """, unsafe_allow_html=True)
    
    # Clean header with logo and title
    col1, col2 = st.columns([1, 5])
    with col1:
        st.markdown("# 📋")
    with col2:
        st.title("Medical Physics Residency Toolkit")
        st.markdown("<p class='subtitle'>Streamlining documentation for radiation oncology workflows</p>", unsafe_allow_html=True)
    
    # Main content tabs - matching QuickWrite styling
    tools_tab, about_tab, coming_soon_tab = st.tabs([
        "Available Tools", "About", "Coming Soon"
    ])
    
    with tools_tab:
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Main tools with clear descriptions
        st.markdown("""
        <div class='tool-card'>
            <h2>Quick Write Generator</h2>
            <p>Generate standardized clinical documentation with guided forms</p>
            <div class='features' id='quickwrite-features'>
                <span>DIBH</span>
                <span>Fusion</span>
                <span>Prior Dose</span>
                <span>Pacemaker</span>
                <span>SBRT</span>
                <span>SRS</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Direct navigation to specific write-up types - more condensed layout
        st.markdown("<p>Quick Access:</p>", unsafe_allow_html=True)
        
        # Use a container with flex display for the buttons
        st.markdown("""
        <div class="quick-access-container">
            <a href="#" class="quick-access-button" data-type="DIBH">DIBH</a>
            <a href="#" class="quick-access-button" data-type="Fusion">Fusion</a>
            <a href="#" class="quick-access-button" data-type="Prior Dose">Prior Dose</a>
            <a href="#" class="quick-access-button" data-type="Pacemaker">Pacemaker</a>
            <a href="#" class="quick-access-button" data-type="SBRT">SBRT</a>
            <a href="#" class="quick-access-button" data-type="SRS">SRS</a>
        </div>
        """, unsafe_allow_html=True)
        
        # Hidden buttons that will be triggered by JavaScript
        for write_up_type in ["DIBH", "Fusion", "Prior Dose", "Pacemaker", "SBRT", "SRS"]:
            if st.button(f"Go to {write_up_type}", key=f"{write_up_type.lower().replace(' ', '_')}_btn", visible=False):
                go_to_module("Quick Write")
                st.session_state.active_write_up = write_up_type
        
        # JavaScript to connect the custom buttons to the hidden Streamlit buttons
        st.markdown("""
        <script>
            // Function to click the corresponding hidden button
            function clickHiddenButton(writeUpType) {
                // Find the hidden button and click it
                const buttonId = writeUpType.toLowerCase().replace(' ', '_') + '_btn';
                const button = document.querySelector(`button[kind="secondary"][data-testid="baseButton-secondary"]:has(div:contains("Go to ${writeUpType}"))`);
                if (button) button.click();
            }
            
            // Add click listeners to all quick access buttons
            document.querySelectorAll('.quick-access-button').forEach(button => {
                button.addEventListener('click', function(e) {
                    e.preventDefault();
                    const writeUpType = this.getAttribute('data-type');
                    clickHiddenButton(writeUpType);
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
        
        # Coming soon features in a more visual format
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class='coming-soon-card'>
                <h3>📊 QA Dashboard</h3>
                <p>Interactive quality assurance tracking and visualization</p>
                <div class='timeline'>Coming in Q2 2025</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            st.markdown("""
            <div class='coming-soon-card'>
                <h3>📚 Part 3 Question Bank</h3>
                <p>Practice questions for board certification preparation</p>
                <div class='timeline'>Coming in Q3 2025</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class='coming-soon-card'>
                <h3>🧠 Competency Tracker</h3>
                <p>Track and document clinical competencies for residency programs</p>
                <div class='timeline'>Coming in Q2 2025</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            st.markdown("""
            <div class='coming-soon-card'>
                <h3>📱 Mobile Support</h3>
                <p>Fully responsive design for on-the-go documentation</p>
                <div class='timeline'>Coming in Q4 2025</div>
            </div>
            """, unsafe_allow_html=True)