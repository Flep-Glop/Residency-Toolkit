import streamlit as st
from modules.quickwrite import QuickWriteModule
from modules.qa_bank import QABankModule
from modules.pnp import PnPModule
from modules.inventory import InventoryModule
from modules.game import GameModule  # Import the new game module

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

# Sidebar for navigation
st.sidebar.title("Residency Toolkit")
selected_module = st.sidebar.selectbox(
    "Select Module",
    ["Quick Write", "QA Bank", "P&Ps", "Inventory", "Residency Game", "Competency Tracker", "Part 3 Bank"]
)

# Display selected module content
if selected_module == "Quick Write":
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

elif selected_module == "QA Bank":
    # Render the QA Bank module UI
    qa_bank.render_qa_bank()

elif selected_module == "P&Ps":
    # Render the P&Ps module UI
    pnp_module.render_pp_module()

elif selected_module == "Inventory":
    # Render the Inventory module UI
    inventory_module.render_inventory_module()

elif selected_module == "Residency Game":
    # Render the Game module UI
    game_module.render_game_module()
        
elif selected_module in ["Competency Tracker", "Part 3 Bank"]:
    st.title(f"{selected_module}")
    st.info(f"The {selected_module} module is under development.")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("Medical Physics Residency Toolkit  \nDeveloped with Streamlit")