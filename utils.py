import streamlit as st
import os

# In utils.py, add this function for debugging
def debug_css_loading(css_file):
    """Test function to verify CSS loading"""
    try:
        with open(css_file, "r") as f:
            content = f.read()
            st.markdown(f"<p>Successfully loaded CSS file: {css_file}</p>", unsafe_allow_html=True)
            st.markdown(f"<p>First 50 characters: {content[:50]}...</p>", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error loading CSS: {str(e)}")

def load_css(css_file):
    """Load and inject CSS from a file"""
    try:
        with open(css_file, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"CSS file not found: {css_file}")
        return False
    return True
