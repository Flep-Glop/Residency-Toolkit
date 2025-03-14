import streamlit as st

def select_modules(modules, existing_selections=None):
    """Allow selection of which write-up modules to generate with improved UI stability.
    
    Args:
        modules: Dict of module_id -> module_instance
        existing_selections: Optional dict of module_id -> boolean for pre-selection
        
    Returns:
        dict: The selected module IDs mapped to True
    """
    st.write("Check all write-up types you want to generate:")
    
    # Initialize selections with existing data or empty dict
    selections = {}
    if existing_selections:
        selections = existing_selections.copy()
    
    # Create a cleaner UI with columns
    cols = st.columns(2)
    
    # Simple module selection without complex overlays
    for i, (module_id, module) in enumerate(modules.items()):
        # Determine if this module was previously selected
        default = existing_selections.get(module_id, False) if existing_selections else False
        
        # Alternate between columns
        col = cols[i % 2]
        
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
        
        # Create a clean container with proper spacing
        with col:
            with st.container():
                # Create a simple header with icon
                st.markdown(f"### {icon} {module.get_module_name()}")
                
                # Add description
                st.write(module.get_module_description())
                
                # Simple checkbox without help icon
                selected = st.checkbox(
                    f"Include this write-up",
                    value=default,
                    key=f"select_{module_id}"
                )
                
                # Store selection
                selections[module_id] = selected
                
                # Add separator for clarity
                st.markdown("---")
    
    # Provide visual feedback based on selections
    selected_count = sum(1 for v in selections.values() if v)
    
    if selected_count > 0:
        st.success(f"You've selected {selected_count} write-up type{'s' if selected_count > 1 else ''}.")
    
    # Show a summary of selected modules
    if any(selections.values()):
        st.markdown("### Selected Write-Up Types")
        for module_id, selected in selections.items():
            if selected:
                module = modules[module_id]
                st.markdown(f"- **{module.get_module_name()}**: {module.get_module_description()}")
    
    return {k: v for k, v in selections.items() if v}