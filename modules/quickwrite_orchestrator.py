import streamlit as st
from .templates import ConfigManager
from .common_info_collector import collect_common_info
from .module_selector import select_modules

class QuickWriteOrchestrator:
    """Main controller for the QuickWrite workflow."""
    
    def __init__(self, modules):
        """Initialize with all required modules.
        
        Args:
            modules: Dict mapping module_id to module instance
        """
        self.config_manager = ConfigManager()
        self.modules = modules
    
    def render_workflow(self):
        """Render the entire QuickWrite workflow based on current state.
        
        Returns:
            dict: The generated write-ups, or None if not complete
        """
        # Initialize session state for workflow if needed
        if "workflow_step" not in st.session_state:
            st.session_state.workflow_step = "basic_info"
            
        # Determine the current workflow step
        current_step = st.session_state.workflow_step
        
        if current_step == "basic_info":
            return self._render_basic_info_step()
        elif current_step == "module_selection":
            return self._render_module_selection_step()
        elif current_step == "module_details":
            return self._render_module_details_step()
        elif current_step == "results":
            return self._render_results_step()
    
    def _render_basic_info_step(self):
        """Render the basic information collection step."""
        st.markdown("## Common Information")
        st.info("First, let's collect basic information that applies to all write-ups.")
        
        # Get existing data if available
        existing_data = st.session_state.get("common_info", None)
        
        # Use the common info collector
        common_info = collect_common_info(self.config_manager, existing_data)
        
        # Navigation buttons
        col1, col2 = st.columns([4, 1])
        
        with col2:
            can_proceed = common_info is not None
            if st.button("Continue", key="basic_info_continue", disabled=not can_proceed, type="primary"):
                # Save common info to session state
                st.session_state.common_info = common_info
                # Advance to next step
                st.session_state.workflow_step = "module_selection"
                # Force rerun to update the UI
                st.rerun()
        
        if not can_proceed:
            st.warning("Please fill in all required fields to continue.")
    
    def _render_module_selection_step(self):
        """Render the module selection step."""
        st.markdown("## Select Write-Up Types")
        
        # Show summary of common information with edit option
        if "common_info" in st.session_state:
            with st.expander("Common Information (click to review)", expanded=False):
                st.write(f"**Physician:** Dr. {st.session_state.common_info['physician']}")
                st.write(f"**Physicist:** Dr. {st.session_state.common_info['physicist']}")
                st.write(f"**Patient:** {st.session_state.common_info['patient_details']}")
                
                if st.button("Edit Common Information", key="edit_common_info"):
                    st.session_state.workflow_step = "basic_info"
                    st.rerun()
        
        # Get existing selections if available
        existing_selections = st.session_state.get("selected_modules", None)
        
        # Use the module selector
        selected_modules = select_modules(self.modules, existing_selections)
        
        # Navigation buttons
        col1, col2, col3 = st.columns([1, 3, 1])
        
        with col1:
            if st.button("← Back", key="module_selection_back"):
                st.session_state.workflow_step = "basic_info"
                st.rerun()
        
        with col3:
            can_proceed = len(selected_modules) > 0
            if st.button("Continue", key="module_selection_continue", disabled=not can_proceed, type="primary"):
                # Save selected modules to session state
                st.session_state.selected_modules = selected_modules
                # Initialize module data if not already present
                if "module_data" not in st.session_state:
                    st.session_state.module_data = {}
                # Advance to next step
                st.session_state.workflow_step = "module_details"
                st.rerun()
        
        if not can_proceed:
            st.warning("Please select at least one write-up type to continue.")
    
    def _render_module_details_step(self):
        """Render the module-specific details collection step."""
        st.markdown("## Module Details")
        
        # Get needed data from session state
        common_info = st.session_state.get("common_info", {})
        selected_modules = st.session_state.get("selected_modules", {})
        module_data = st.session_state.get("module_data", {})
        
        # Collect data for any uncompleted modules
        uncompleted_modules = []
        completed_modules = []
        
        for module_id, selected in selected_modules.items():
            if selected:
                # Get the module instance
                module = self.modules.get(module_id)
                if not module:
                    continue
                
                with st.expander(f"{module.get_module_name()} Details", expanded=module_id not in module_data):
                    # Render the module-specific fields
                    if module_id not in module_data:
                        # Pass common information to the module
                        result = module.render_specialized_fields(
                            common_info.get("physician", ""),
                            common_info.get("physicist", ""),
                            common_info.get("patient_age", 0),
                            common_info.get("patient_sex", ""),
                            common_info.get("patient_details", "")
                        )
                        
                        if result is not None:
                            # Save the module data
                            module_data[module_id] = result
                            # Force rerun to update UI
                            st.rerun()
                        else:
                            # Module is not complete
                            uncompleted_modules.append(module.get_module_name())
                    else:
                        # Show summary of completed module
                        st.success(f"{module.get_module_name()} details completed")
                        
                        # Add option to edit
                        if st.button(f"Edit {module.get_module_name()} Details", key=f"edit_{module_id}"):
                            # Remove this module's data to force re-rendering
                            del module_data[module_id]
                            st.rerun()
                        
                        completed_modules.append(module.get_module_name())
        
        # Update session state with any new module data
        st.session_state.module_data = module_data
        
        # Navigation buttons
        col1, col2, col3 = st.columns([1, 3, 1])
        
        with col1:
            if st.button("← Back", key="module_details_back"):
                st.session_state.workflow_step = "module_selection"
                st.rerun()
        
        with col3:
            can_proceed = len(uncompleted_modules) == 0 and len(completed_modules) > 0
            if st.button("Generate Write-Ups", key="generate_write_ups", disabled=not can_proceed, type="primary"):
                # Generate all write-ups
                results = {}
                for module_id, selected in selected_modules.items():
                    if selected and module_id in module_data:
                        # Get the module instance
                        module = self.modules.get(module_id)
                        if not module:
                            continue
                        
                        # Generate the write-up
                        write_up = module.generate_write_up(common_info, module_data[module_id])
                        if write_up:
                            results[module_id] = write_up
                
                # Save results to session state
                st.session_state.results = results
                
                # Advance to results step
                st.session_state.workflow_step = "results"
                st.rerun()
        
        if not can_proceed:
            st.warning(f"Please complete details for: {', '.join(uncompleted_modules)}")
    
    def _render_results_step(self):
        """Render the results display step."""
        st.markdown("## Generated Write-Ups")
        
        # Get results from session state
        results = st.session_state.get("results", {})
        
        if not results:
            st.error("No write-ups were generated. Please go back and try again.")
            if st.button("← Back to Module Details", key="results_back_error"):
                st.session_state.workflow_step = "module_details"
                st.rerun()
            return
        
        # Create tabs for each generated write-up
        tab_labels = []
        for module_id in results.keys():
            # Get the module instance
            module = self.modules.get(module_id)
            if module:
                tab_labels.append(module.get_module_name())
            else:
                tab_labels.append(module_id.replace('_', ' ').title())
        
        tabs = st.tabs(tab_labels)
        
        # Populate each tab with the corresponding write-up
        for i, (module_id, write_up) in enumerate(results.items()):
            with tabs[i]:
                # Get the module instance
                module = self.modules.get(module_id)
                if module:
                    # Use the module's display method
                    module.display_write_up(write_up)
                else:
                    # Fallback display method
                    st.text_area("Generated Write-Up", write_up, height=300)
                    st.download_button(
                        label="Download as Text File",
                        data=write_up,
                        file_name=f"{module_id}_write_up.txt",
                        mime="text/plain"
                    )
        
        # Navigation buttons
        col1, col2, col3 = st.columns([1, 3, 1])
        
        with col1:
            if st.button("← Back to Details", key="results_back"):
                st.session_state.workflow_step = "module_details"
                st.rerun()
        
        with col3:
            if st.button("Start New Write-Up", key="start_new", type="primary"):
                # Reset the entire workflow
                self.reset_workflow()
                st.rerun()
                
    def reset_workflow(self):
        """Reset the entire workflow."""
        for key in ['workflow_step', 'common_info', 'selected_modules', 'module_data', 'results']:
            if key in st.session_state:
                del st.session_state[key]