import streamlit as st

def select_modules(modules, existing_selections=None):
    """Allow selection of which write-up modules to generate.
    
    Args:
        modules: Dict of module_id -> module_instance
        existing_selections: Optional dict of module_id -> boolean for pre-selection
        
    Returns:
        dict: The selected module IDs mapped to True
    """
    st.write("Check all write-up types you need to generate:")
    
    # Create a visually appealing card layout for options
    st.markdown("""
    <style>
    .module-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: 16px;
        margin-top: 1rem;
    }
    .module-card {
        padding: 16px;
        border: 1px solid var(--card-border);
        border-radius: 8px;
        background-color: var(--card-background);
    }
    .module-title {
        font-weight: bold;
        margin-bottom: 6px;
    }
    .module-description {
        font-size: 0.9em;
        color: var(--subtitle-color);
        margin-bottom: 12px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Start the grid container
    st.markdown('<div class="module-grid">', unsafe_allow_html=True)
    
    selections = {}
    
    # Display modules in a responsive grid
    for module_id, module in modules.items():
        # Determine if this module was previously selected
        default = existing_selections.get(module_id, False) if existing_selections else False
        
        # Create HTML for card - we'll need to add the checkbox separately
        st.markdown(f"""
        <div class="module-card" id="card-{module_id}">
            <div class="module-title">{module.get_module_name()}</div>
            <div class="module-description">{module.get_module_description()}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Add the checkbox (we can't do this purely in HTML)
        selected = st.checkbox(
            f"Include {module.get_module_name()}",
            value=default,
            key=f"select_{module_id}"
        )
        
        selections[module_id] = selected
    
    # Close the grid container
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Filter to only selected modules
    return {k: v for k, v in selections.items() if v}