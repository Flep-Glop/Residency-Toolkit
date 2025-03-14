import streamlit as st
from modules.quickwrite import QuickWriteModule

# Page configuration
st.set_page_config(
    page_title="Medical Physics Residency Toolkit",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables
if 'show_landing_page' not in st.session_state:
    st.session_state.show_landing_page = True
if 'active_module' not in st.session_state:
    st.session_state.active_module = None

# Make sure your navigation functions are defined:
def go_to_module(module_name):
    st.session_state.show_landing_page = False
    st.session_state.active_module = module_name

def go_to_landing_page():
    st.session_state.show_landing_page = True
    st.session_state.active_module = None

# Custom CSS for better appearance
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    h1, h2, h3 {
        color: #2c3e50;
    }
    .stButton button {
        background-color: #3498db;
        color: white;
    }
    .stButton button:hover {
        background-color: #2980b9;
    }
    
    /* Module card styles */
    .module-card {
        padding: 20px;
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        text-align: center;
        cursor: pointer;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .module-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.15);
    }
    .module-icon {
        font-size: 3em;
        margin-bottom: 10px;
    }
    .module-title {
        font-weight: bold;
        margin-bottom: 10px;
    }
    .module-desc {
        font-size: 0.9em;
    }
    
    /* Additional styling for P&P and other modules */
    .checklist-item {
        padding: 8px 15px;
        margin: 5px 0;
        border-left: 3px solid #3498db;
        background-color: #eaf2f8;
    }
    .objective-box {
        background-color: #f9f9f9;
        border-left: 3px solid #27ae60;
        padding: 10px;
        margin-bottom: 15px;
    }
    .frequency-box {
        background-color: #f9f9f9;
        border-left: 3px solid #e74c3c;
        padding: 10px;
        margin-bottom: 15px;
    }
    /* Inventory-specific styling */
    .equipment-card {
        background-color: #f9f9f9;
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 15px;
        margin-bottom: 15px;
    }
    .equipment-available {
        background-color: #d4edda;
        border-left: 3px solid #28a745;
        padding: 5px 10px;
    }
    .equipment-unavailable {
        background-color: #f8d7da;
        border-left: 3px solid #dc3545;
        padding: 5px 10px;
    }
    .training-status {
        background-color: #e2f0fb;
        border-left: 3px solid #3498db;
        padding: 5px 10px;
    }
    /* Print-specific styling */
    @media print {
        .stButton, .stSidebar, header {
            display: none !important;
        }
        .main .block-container {
            max-width: 100% !important;
            padding-top: 0px !important;
        }
    }
</style>
""", unsafe_allow_html=True)

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
        # Add a more sophisticated CSS for the landing page
        st.markdown("""
        <style>
            /* Landing page specific styling */
            .landing-container {
                padding: 20px;
                max-width: 1200px;
                margin: 0 auto;
            }
            .landing-header {
                text-align: center;
                background: linear-gradient(to right, #2c3e50, #3498db, #2c3e50);
                color: white;
                padding: 2rem;
                border-radius: 15px;
                margin-bottom: 2rem;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            }
            .landing-header h1 {
                color: white;
                font-size: 2.5rem;
                margin-bottom: 0.5rem;
            }
            .landing-header p {
                font-size: 1.2rem;
                opacity: 0.9;
            }
            .landing-card {
                background-color: white;
                border-radius: 12px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.05);
                padding: 25px;
                margin-bottom: 25px;
                transition: transform 0.2s, box-shadow 0.2s;
            }
            .landing-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 8px 15px rgba(0,0,0,0.1);
            }
            .landing-card h3 {
                color: #2c3e50;
                margin-top: 0;
                border-bottom: 2px solid #f0f0f0;
                padding-bottom: 10px;
            }
            .module-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-top: 30px;
            }
            .module-tile {
                background: white;
                border-radius: 12px;
                padding: 25px;
                text-align: center;
                box-shadow: 0 4px 8px rgba(0,0,0,0.05);
                transition: all 0.3s ease;
                height: 100%;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
            }
            .module-tile:hover {
                transform: translateY(-5px);
                box-shadow: 0 8px 20px rgba(0,0,0,0.1);
                border-bottom: 3px solid #3498db;
            }
            .module-icon {
                font-size: 2.5rem;
                margin-bottom: 15px;
                color: #3498db;
            }
            .module-title {
                color: #2c3e50;
                font-weight: bold;
                margin-bottom: 10px;
                font-size: 1.2rem;
            }
            .module-description {
                color: #7f8c8d;
                font-size: 0.9rem;
                margin-bottom: 15px;
                flex-grow: 1;
            }
            .module-button {
                margin-top: 10px;
            }
            .version-badge {
                display: inline-block;
                background-color: #3498db;
                color: white;
                padding: 5px 10px;
                border-radius: 20px;
                font-size: 0.8rem;
                margin-left: 10px;
            }
            .cta-button {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 12px 25px;
                border-radius: 50px;
                font-size: 1.1rem;
                cursor: pointer;
                transition: all 0.3s ease;
                display: block;
                width: 100%;
                text-align: center;
                text-decoration: none;
            }
            .cta-button:hover {
                background-color: #2980b9;
                transform: scale(1.03);
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }
            .feedback-card {
                border-left: 4px solid #3498db;
                background-color: #f8f9fa;
                padding: 15px;
                border-radius: 0 8px 8px 0;
            }
        </style>
        """, unsafe_allow_html=True)
        
        # Header section with gradient background
        st.markdown("""
        <div class="landing-header">
            <h1>Medical Physics Residency Toolkit</h1>
            <p>Streamlining documentation for clinical workflows in radiation oncology</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Top modules grid
        st.markdown("## Available Tools")
        
        # Use columns to create a responsive grid for modules
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="module-tile">
                <div class="module-icon">📝</div>
                <div class="module-title">QuickWrite</div>
                <div class="module-description">
                    Generate professional documentation for DIBH, Fusion, Prior Dose, 
                    Pacemaker, SBRT, and SRS clinical scenarios.
                </div>
                <button class="cta-button" onclick="document.querySelector('[key=launch_quickwrite]').click()">
                    Launch QuickWrite
                </button>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="module-tile">
                <div class="module-icon">🔍</div>
                <div class="module-title">Coming Soon</div>
                <div class="module-description">
                    More tools are under development! We're working on additional features 
                    to help streamline your clinical workflows.
                </div>
                <div class="module-button">
                    <span style="color: #7f8c8d; font-style: italic;">In Development</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # About section in a card
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div class="landing-card">
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
            
            col1, col2, col3 = st.columns([2,1,2])
            with col2:
                if st.button("Submit Feedback", use_container_width=True):
                    # In a full implementation, send this feedback to a database or email
                    st.success("Thank you for your feedback! We'll use it to improve the tool.")
        
        # Hidden button for JavaScript to click
        if st.button("Launch QuickWrite", key="launch_quickwrite", visible=False):
            go_to_module("Quick Write")