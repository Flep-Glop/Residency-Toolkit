# Replace the entire app.py file temporarily with this minimal test
import streamlit as st
# Add this import
from utils import debug_css_loading

# Set page config
st.set_page_config(
    page_title="Test Page",
    page_icon="📋"
)
# Add this at the beginning after setting the page config
debug_css_loading("assets/css/main.css")
debug_css_loading("assets/css/landing.css")
# Initialize session state
if 'show_landing_page' not in st.session_state:
    st.session_state.show_landing_page = True

# Display header to verify the app is running
st.title("Testing Page Rendering")

# Test the condition
if st.session_state.show_landing_page:
    st.write("LANDING PAGE CONTENT")
    st.write("If you can see this, the landing page condition works")
    
    # Test button
    if st.button("Toggle Page"):
        st.session_state.show_landing_page = False
        st.rerun()
else:
    st.write("OTHER PAGE CONTENT")
    st.write("If you can see this, the toggle worked")
    
    # Test button
    if st.button("Back to Landing"):
        st.session_state.show_landing_page = True
        st.rerun()