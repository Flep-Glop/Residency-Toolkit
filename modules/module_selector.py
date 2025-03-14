import streamlit as st

def select_modules(modules, existing_selections=None):
    """Allow selection of which write-up modules to generate with enhanced visual feedback.
    
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
        transition: transform 0.2s, box-shadow 0.2s;
        position: relative;
    }
    .module-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 4px 12px var(--card-shadow);
    }
    .module-card.selected {
        border: 2px solid var(--primary-color);
        box-shadow: 0 0 8px rgba(var(--primary-color-rgb), 0.4);
    }
    .module-title {
        font-weight: bold;
        margin-bottom: 6px;
        color: var(--text-color);
    }
    .module-description {
        font-size: 0.9em;
        color: var(--subtitle-color);
        margin-bottom: 12px;
    }
    .module-checkbox {
        margin-top: 8px;
    }
    .module-icon {
        position: absolute;
        top: 12px;
        right: 12px;
        font-size: 1.2em;
        color: var(--primary-color);
    }
    .module-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.8em;
        margin-top: 8px;
        background-color: rgba(var(--primary-color-rgb), 0.1);
        color: var(--primary-color);
    }
    .tooltip-icon {
        color: var(--subtitle-color);
        font-size: 0.8em;
        cursor: help;
        margin-left: 4px;
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
        
        # Module-specific icon
        icon = "📄"  # Default icon
        if module.get_module_name() == "DIBH":
            icon = "🫁"
        elif module.get_module_name() == "Fusion":
            icon = "🔄"
        elif module.get_module_name() == "Prior Dose":
            icon = "📊"
        elif module.get_module_name() == "Pacemaker":
            icon = "⚡"
        elif module.get_module_name() == "SBRT":
            icon = "🎯"
        elif module.get_module_name() == "SRS":
            icon = "🧠"
            
        # Required fields as a badge
        required_fields = module.get_required_fields()
        fields_display = f"{len(required_fields)} fields required"
            
        # Create card container with selection status
        card_class = "module-card selected" if default else "module-card"
        
        st.markdown(f"""
        <div class="{card_class}" id="card-{module_id}">
            <div class="module-icon">{icon}</div>
            <div class="module-title">{module.get_module_name()}</div>
            <div class="module-description">{module.get_module_description()}</div>
            <div class="module-badge">{fields_display}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Add the checkbox (we can't do this purely in HTML)
        selected = st.checkbox(
            f"Select {module.get_module_name()}",
            value=default,
            key=f"select_{module_id}"
        )
        
        # Apply custom styling to the checkbox container
        st.markdown("""
        <style>
        /* Target the most recently added checkbox */
        .stCheckbox:last-child {
            margin-top: -40px; /* Move checkbox up to overlay with card */
            margin-left: 16px;
            position: relative;
            z-index: 10;
        }
        </style>
        """, unsafe_allow_html=True)
        
        selections[module_id] = selected
        
        # Add tooltip with more detailed information
        with st.expander(f"About {module.get_module_name()}", expanded=False):
            st.write(f"**Module Name:** {module.get_module_name()}")
            st.write(f"**Description:** {module.get_module_description()}")
            st.write(f"**Required Fields:** {', '.join(required_fields)}")
            
            # Example cases for each module type
            if module.get_module_name() == "DIBH":
                st.info("Typically used for left breast radiation therapy to reduce cardiac dose.")
                st.write("**Example case:** Left breast cancer patient requiring radiation therapy with cardiac protection.")
            elif module.get_module_name() == "Fusion":
                st.info("Used when multiple imaging modalities need to be combined for target delineation.")
                st.write("**Example case:** Head and neck cancer patient with PET/CT fusion for target volume definition.")
            elif module.get_module_name() == "Prior Dose":
                st.info("Important for retreatment cases to evaluate cumulative dose to critical structures.")
                st.write("**Example case:** Patient with recurrent disease requiring evaluation of previous radiation exposure.")
            elif module.get_module_name() == "Pacemaker":
                st.info("Critical for patients with cardiac implantable electronic devices receiving radiation therapy.")
                st.write("**Example case:** Patient with pacemaker requiring thoracic or nearby radiation treatment.")
            elif module.get_module_name() == "SBRT":
                st.info("Used for precise high-dose radiation to extracranial targets in fewer fractions.")
                st.write("**Example case:** Patient with early-stage lung cancer treated with stereotactic body radiation therapy.")
            elif module.get_module_name() == "SRS":
                st.info("Specialized for precise single or few-fraction radiation to intracranial targets.")
                st.write("**Example case:** Patient with brain metastases treated with stereotactic radiosurgery.")
    
    # Close the grid container
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Provide visual feedback based on selections
    selected_count = sum(1 for v in selections.values() if v)
    
    if selected_count == 0:
        st.warning("Please select at least one write-up type to continue.")
    else:
        st.success(f"You've selected {selected_count} write-up type{'s' if selected_count > 1 else ''}.")
    
    # Filter to only selected modules
    selected_modules = {k: v for k, v in selections.items() if v}
    
    # Show a summary of selected modules
    if selected_modules:
        st.markdown("### Selected Write-Up Types")
        cols = st.columns(len(selected_modules) or 1)
        for i, (module_id, _) in enumerate(selected_modules.items()):
            module = modules[module_id]
            with cols[i]:
                st.markdown(f"**{module.get_module_name()}**")
                st.caption(module.get_module_description())
    
    return selected_modules