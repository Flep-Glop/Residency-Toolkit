import streamlit as st
from modules.quickwrite import QuickWriteModule
from modules.qa_bank import QABankModule
from modules.pnp import PnPModule
from modules.inventory import InventoryModule
from modules.game import GameModule  # Import the game module

# Page configuration
st.set_page_config(
    page_title="Medical Physics Residency Toolkit",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
qa_bank = QABankModule()
pnp_module = PnPModule()
inventory_module = InventoryModule()
game_module = GameModule()  # Initialize the Game module

# Set up session state for navigation
if 'show_landing_page' not in st.session_state:
    st.session_state.show_landing_page = True
if 'active_module' not in st.session_state:
    st.session_state.active_module = None

# Functions to navigate
def go_to_module(module_name):
    st.session_state.show_landing_page = False
    st.session_state.active_module = module_name

def go_to_landing_page():
    st.session_state.show_landing_page = True
    st.session_state.active_module = None

# Sidebar for navigation when not on landing page
if not st.session_state.show_landing_page:
    st.sidebar.title("Residency Toolkit")
    
    # Back to Home button
    if st.sidebar.button("← Back to Home"):
        go_to_landing_page()
    
    # Module selector
    selected_module = st.sidebar.selectbox(
        "Select Module",
        ["Quick Write", "QA Bank", "P&Ps", "Inventory", "Residency Game", "Competency Tracker", "Part 3 Bank"]
    )
    
    # Switch to the selected module if changed
    if selected_module != st.session_state.active_module:
        st.session_state.active_module = selected_module
        st.rerun()

# Main content area
if st.session_state.show_landing_page:
    # Simple title banner
    st.markdown("""
    <div style="text-align:center; padding:20px; margin-bottom:30px;">
        <h1 style="margin-bottom:10px;">Medical Physics Residency Toolkit</h1>
        <p>Tools and resources to enhance your training experience</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Define module data
    modules = [
        {
            "id": "quick_write",
            "name": "Quick Write",
            "description": "Generate professional documentation for common clinical scenarios",
            "icon": "📝",
            "implemented": True
        },
        {
            "id": "qa_bank",
            "name": "QA Bank",
            "description": "Access and organize quality assurance procedures",
            "icon": "🧪",
            "implemented": True
        },
        {
            "id": "pnp",
            "name": "Policies & Procedures",
            "description": "Review department policies and standard procedures",
            "icon": "📑",
            "implemented": True
        },
        {
            "id": "inventory",
            "name": "Inventory",
            "description": "Track equipment, usage, and training status",
            "icon": "🔍",
            "implemented": True
        },
        {
            "id": "game",
            "name": "Residency Game",
            "description": "Test your knowledge with an interactive learning game",
            "icon": "🎮",
            "implemented": True
        },
        {
            "id": "competency",
            "name": "Competency Tracker",
            "description": "Monitor your progress toward residency milestones",
            "icon": "📊",
            "implemented": False
        },
        {
            "id": "part3",
            "name": "Part 3 Bank",
            "description": "Prepare for board examinations with practice questions",
            "icon": "🎓",
            "implemented": False
        }
    ]
    
    # Display only implemented modules
    implemented_modules = [m for m in modules if m["implemented"]]
    
    # Create a grid layout with 3 columns
    cols = st.columns(3)
    
    # Display modules in columns with explicit buttons
    for i, module in enumerate(implemented_modules):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="module-card">
                <div class="module-icon">{module['icon']}</div>
                <div class="module-title">{module['name']}</div>
                <div class="module-desc">{module['description']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Regular button with clear text
            if st.button(f"Open {module['name']}", key=f"btn_{module['id']}"):
                go_to_module(module['name'])
            
else:
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

    elif active_module == "QA Bank":
        # Render the QA Bank module UI
        qa_bank.render_qa_bank()

    elif active_module == "P&Ps":
        # Render the P&Ps module UI
        pnp_module.render_pp_module()

    elif active_module == "Inventory":
        # Render the Inventory module UI
        inventory_module.render_inventory_module()

    elif active_module == "Residency Game":
        # Render the Game module UI
        game_module.render_game_module()
            
    elif active_module in ["Competency Tracker", "Part 3 Bank"]:
        st.title(f"{active_module}")
        st.info(f"The {active_module} module is under development.")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("Medical Physics Residency Toolkit  \nDeveloped with Streamlit")