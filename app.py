import streamlit as st
from modules.quickwrite import QuickWriteModule
from modules.qa_bank import QABankModule  # Import the new QA Bank module

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
    /* Additional styling for QA Bank */
    .preset-card {
        border: 1px solid #e0e0e0;
        border-radius: 5px;
        padding: 10px;
        margin-bottom: 10px;
        background-color: #f5f5f5;
    }
    .test-item {
        padding: 5px 10px;
        margin: 3px 0;
        border-left: 3px solid #3498db;
        background-color: #eaf2f8;
    }
</style>
""", unsafe_allow_html=True)

# Initialize modules
quick_write = QuickWriteModule()
qa_bank = QABankModule()  # Initialize the QA Bank module

# Sidebar for navigation
st.sidebar.title("Residency Toolkit")
selected_module = st.sidebar.selectbox(
    "Select Module",
    ["Quick Write", "QA Bank", "Competency Tracker", "Part 3 Bank", "P&Ps", "Inventory"]
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
        
elif selected_module in ["Competency Tracker", "Part 3 Bank", "P&Ps", "Inventory"]:
    st.title(f"{selected_module}")
    st.info(f"The {selected_module} module is under development.")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("Medical Physics Residency Toolkit  \nDeveloped with Streamlit")