import streamlit as st
import os

def load_css(css_file):
    """Load and inject CSS from a file"""
    try:
        with open(css_file, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"CSS file not found: {css_file}")
        return False
    return True