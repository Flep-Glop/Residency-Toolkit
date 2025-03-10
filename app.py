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
    
    /* Landing page styles */
    .landing-container {
        text-align: center;
        padding: 40px 20px;
        max-width: 800px;
        margin: 0 auto;
    }
    
    .feature-card {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.15);
    }
    
    .feature-card h3 {
        margin-bottom: 10px;
        color: #3498db;
    }
    
    .feature-icon {
        font-size: 2em;
        margin-bottom: 10px;
    }
    
    .welcome-header {
        margin: 30px 0;
    }

    /* Module cards for landing page */
    .module-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
        gap: 20px;
        margin: 30px 0;
    }
    
    .module-card {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        transition: transform 0.2s, box-shadow 0.2s;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    
    .module-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.15);
    }
    
    .module-icon {
        font-size: 2.5em;
        margin-bottom: 15px;
    }
    
    .module-title {
        font-size: 1.2em;
        font-weight: bold;
        margin-bottom: 10px;
    }
    
    .module-desc {
        margin-bottom: 20px;
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
    # Landing page content
    st.markdown("""
    <div class="landing-container">
        <h1 class="welcome-header">Welcome to the Medical Physics Residency Toolkit</h1>
        <p>A comprehensive suite of tools designed to enhance your residency experience and learning.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature highlights
    st.markdown("## Toolkit Features")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📝</div>
            <h3>Documentation Tools</h3>
            <p>Generate professional writeups for common clinical scenarios, QA procedures, and more.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🎮</div>
            <h3>Interactive Learning</h3>
            <p>Test your knowledge with the Residency Game and track your progress.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <h3>Resource Management</h3>
            <p>Track inventory, manage QA procedures, and organize your resources effectively.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📚</div>
            <h3>Knowledge Base</h3>
            <p>Access a comprehensive library of policies, procedures, and reference materials.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Available modules
    st.markdown("## Available Modules")
    
    st.markdown("""
    <div class="module-grid">
        <div class="module-card">
            <div>
                <div class="module-icon">📋</div>
                <div class="module-title">Quick Write Generator</div>
                <div class="module-desc">Create professional clinical documentation for common scenarios.</div>
            </div>
            <button onclick="document.dispatchEvent(new CustomEvent('quickwrite_click'))" class="st-emotion-cache-19rxjzo eczjsme11">Open Module</button>
        </div>
        
        <div class="module-card">
            <div>
                <div class="module-icon">🧪</div>
                <div class="module-title">QA Bank</div>
                <div class="module-desc">Organize and access quality assurance procedures and templates.</div>
            </div>
            <button onclick="document.dispatchEvent(new CustomEvent('qabank_click'))" class="st-emotion-cache-19rxjzo eczjsme11">Open Module</button>
        </div>
        
        <div class="module-card">
            <div>
                <div class="module-icon">📑</div>
                <div class="module-title">Policies & Procedures</div>
                <div class="module-desc">Review department policies and standard operating procedures.</div>
            </div>
            <button onclick="document.dispatchEvent(new CustomEvent('pnp_click'))" class="st-emotion-cache-19rxjzo eczjsme11">Open Module</button>
        </div>
        
        <div class="module-card">
            <div>
                <div class="module-icon">🔍</div>
                <div class="module-title">Inventory Tracker</div>
                <div class="module-desc">Manage equipment, track usage history, and monitor training status.</div>
            </div>
            <button onclick="document.dispatchEvent(new CustomEvent('inventory_click'))" class="st-emotion-cache-19rxjzo eczjsme11">Open Module</button>
        </div>
        
        <div class="module-card">
            <div>
                <div class="module-icon">🎮</div>
                <div class="module-title">Residency Game</div>
                <div class="module-desc">Test your knowledge with an interactive learning game.</div>
            </div>
            <button onclick="document.dispatchEvent(new CustomEvent('game_click'))" class="st-emotion-cache-19rxjzo eczjsme11">Open Module</button>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # JavaScript to handle button clicks
    st.markdown("""
    <script>
    document.addEventListener('quickwrite_click', function() {
        window.parent.postMessage({
            type: 'streamlit:setComponentValue',
            value: 'Quick Write'
        }, '*');
    });
    
    document.addEventListener('qabank_click', function() {
        window.parent.postMessage({
            type: 'streamlit:setComponentValue',
            value: 'QA Bank'
        }, '*');
    });
    
    document.addEventListener('pnp_click', function() {
        window.parent.postMessage({
            type: 'streamlit:setComponentValue',
            value: 'P&Ps'
        }, '*');
    });
    
    document.addEventListener('inventory_click', function() {
        window.parent.postMessage({
            type: 'streamlit:setComponentValue',
            value: 'Inventory'
        }, '*');
    });
    
    document.addEventListener('game_click', function() {
        window.parent.postMessage({
            type: 'streamlit:setComponentValue',
            value: 'Residency Game'
        }, '*');
    });
    </script>
    """, unsafe_allow_html=True)
    
    # Real buttons that work with Streamlit
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if st.button("Quick Write", key="qw_btn"):
            go_to_module("Quick Write")
    
    with col2:
        if st.button("QA Bank", key="qa_btn"):
            go_to_module("QA Bank")
    
    with col3:
        if st.button("P&Ps", key="pp_btn"):
            go_to_module("P&Ps")
    
    with col4:
        if st.button("Inventory", key="inv_btn"):
            go_to_module("Inventory")
    
    with col5:
        if st.button("Residency Game", key="game_btn"):
            go_to_module("Residency Game")

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