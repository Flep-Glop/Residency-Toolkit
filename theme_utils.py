import streamlit as st

def inject_theme_responsive_css():
    """
    Inject CSS that automatically adapts to the current Streamlit theme.
    This sets CSS variables based on the current theme.
    """
    # Get current theme from Streamlit
    theme = st.get_option("theme.base")
    
    # Define your CSS variables for both themes
    css = """
    <style>
    :root {
        /* Light mode variables (default) */
        --background-color: #f8f9fa;
        --text-color: #2c3e50;
        --subtitle-color: #64748b;
        --card-background: #ffffff;
        --card-border: #e2e8f0;
        --card-shadow: rgba(0, 0, 0, 0.08);
        --primary-color: #3498db;
        --primary-color-rgb: 52, 152, 219;  /* Same as above, but in RGB format */
        --primary-color-hover: #2980b9;
        --secondary-background: #f1f5f9;
        --secondary-background-hover: #e0f2fe;
        --feature-background: #eaf2f8;
        --feature-text: #3498db;
        --feature-hover: #dbeafe;
        --feature-shadow: rgba(59, 130, 246, 0.15);
        --button-shadow: rgba(59, 130, 246, 0.3);
        --timeline-background: #dbeafe;
        --timeline-text: #3498db;
        
        /* Success/warning/error colors */
        --success-color: #27ae60;
        --warning-color: #f39c12;
        --error-color: #e74c3c;
    }
    
    /* Dark mode variables - applied automatically when theme is dark */
    [data-theme="dark"] {
        --background-color: #1a1a1a;
        --text-color: #f8fafc;
        --subtitle-color: #cbd5e1;
        --card-background: #2d3748;
        --card-border: #4a5568;
        --card-shadow: rgba(0, 0, 0, 0.3);
        --primary-color: #60a5fa;
        --primary-color-rgb: 96, 165, 250;  /* Same as above, but in RGB format */
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
        
        /* Success/warning/error colors for dark mode */
        --success-color: #2ecc71;
        --warning-color: #f1c40f;
        --error-color: #e74c3c;
    }
    
    /* Make Streamlit elements use our theme variables */
    .stApp {
        background-color: var(--background-color);
    }
    
    .stMarkdown p, .stMarkdown li {
        color: var(--text-color);
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
    
    <script>
        // Set the data-theme attribute on the body based on Streamlit's theme
        document.body.setAttribute('data-theme', '%s');
        
        // Add a mutation observer to maintain the theme if Streamlit rerenders components
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.addedNodes.length) {
                    document.body.setAttribute('data-theme', '%s');
                }
            });
        });
        
        observer.observe(document.body, { childList: true, subtree: true });
    </script>
    """ % (theme, theme)
    
    st.markdown(css, unsafe_allow_html=True)

def load_theme_aware_css(css_file):
    """
    Load CSS file but make it theme-aware.
    This loads your CSS files but ensures they work with theme variables.
    """
    try:
        with open(css_file, "r") as f:
            css = f.read()
            theme = st.get_option("theme.base")
            
            # Inject the theme attribute along with the CSS
            st.markdown(f"""
            <style>
            {css}
            </style>
            <script>
                document.body.setAttribute('data-theme', '{theme}');
            </script>
            """, unsafe_allow_html=True)
        return True
    except FileNotFoundError:
        st.warning(f"CSS file not found: {css_file}")
        return False