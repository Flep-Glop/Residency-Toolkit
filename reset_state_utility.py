import streamlit as st

def add_reset_button(location="sidebar"):
    """Add a reset button to clear session state for debugging.
    
    Args:
        location: Where to place the button - "sidebar" or "main"
    """
    if location == "sidebar":
        with st.sidebar:
            st.markdown("### Developer Options")
            if st.button("🔄 Reset Application State", key="dev_reset"):
                for key in list(st.session_state.keys()):
                    if key != "developer_mode":  # Preserve developer mode setting
                        del st.session_state[key]
                st.success("Application state has been reset!")
                st.rerun()
    else:
        # Add a small button in the main interface
        if st.button("🔄 Reset", key="dev_reset_main"):
            for key in list(st.session_state.keys()):
                if key != "developer_mode":  # Preserve developer mode setting
                    del st.session_state[key]
            st.success("Application state has been reset!")
            st.rerun()