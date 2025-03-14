import streamlit as st

def inject_theme_responsive_css():
    """
    Inject CSS that forces dark mode regardless of system theme settings.
    """
    # Define dark mode CSS variables
    css = """
    <style>
    /* Apply dark mode variables to all possible theme states */
    :root, [data-theme="light"], [data-theme="dark"], [data-theme="None"] {
        /* Dark mode variables */
        --background-color: #1a1a1a;
        --text-color: #f8fafc;
        --subtitle-color: #cbd5e1;
        --card-background: #2d3748;
        --card-border: #4a5568;
        --card-shadow: rgba(0, 0, 0, 0.3);
        --primary-color: #60a5fa;
        --primary-color-rgb: 96, 165, 250;
        --primary-color-hover: #93c5fd;
        --secondary-background: #374151;
        --secondary-background-hover: #4b5563;
        --feature-background: #374151;
        --feature-text: #93c5fd;
        --feature-hover: #4b5563;
        --feature-shadow: rgba(147, 197, 253, 0.3);
        --button-shadow: rgba(147, 197, 253, 0.4);
        --timeline-background: #2a4365;
        --timeline-text: #93c5fd;
        
        /* Success/warning/error colors */
        --success-color: #2ecc71;
        --warning-color: #f1c40f;
        --error-color: #e74c3c;
    }
    
    /* Force dark styles on Streamlit elements */
    .stApp {
        background-color: var(--background-color) !important;
    }
    
    .stMarkdown p, .stMarkdown li {
        color: var(--text-color) !important;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-color) !important;
    }
    
    /* Success/info/warning/error message styling */
    [data-baseweb="message-container"] [kind="info"] {
        background-color: var(--feature-background) !important;
    }
    
    [data-baseweb="message-container"] [kind="success"] {
        background-color: rgba(46, 204, 113, 0.2) !important;
    }
    
    [data-baseweb="message-container"] [kind="warning"] {
        background-color: rgba(241, 196, 15, 0.2) !important;
    }
    
    [data-baseweb="message-container"] [kind="error"] {
        background-color: rgba(231, 76, 60, 0.2) !important;
    }
    </style>
    """
    
    # Apply the CSS
    st.markdown(css, unsafe_allow_html=True)
    
    # Add separate JavaScript to set the data-theme attribute
    js = """
    <script>
        // Always set dark theme
        document.body.setAttribute('data-theme', 'dark');
        
        // Use a mutation observer to ensure theme consistency
        const observer = new MutationObserver(() => {
            document.body.setAttribute('data-theme', 'dark');
        });
        
        observer.observe(document.body, { childList: true, subtree: true });
    </script>
    """
    
    # Apply the JavaScript
    st.markdown(js, unsafe_allow_html=True)

def load_theme_aware_css(css_file):
    """
    Load CSS file with forced dark theme.
    """
    try:
        with open(css_file, "r") as f:
            css = f.read()
            
            # Just load the CSS without theme handling
            st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
            
            # Then add a script to enforce dark mode
            js = """
            <script>
                document.body.setAttribute('data-theme', 'dark');
            </script>
            """
            st.markdown(js, unsafe_allow_html=True)
        return True
    except FileNotFoundError:
        st.warning(f"CSS file not found: {css_file}")
        return False