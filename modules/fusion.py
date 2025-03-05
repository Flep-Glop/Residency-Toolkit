import streamlit as st
from .templates import TemplateManager, ConfigManager

class FusionModule:
    def __init__(self):
        """Initialize the Fusion module with registration presets and modality options."""
        self.template_manager = TemplateManager()
        self.config_manager = ConfigManager()
        
        # Mapping of lesions to anatomical regions
        self.lesion_to_region = {
            "oropharynx": "head and neck",
            "brain": "brain",
            "prostate": "pelvic",
            "endometrium": "pelvic",
            "thymus": "thoracic",
            "thorax": "thoracic",
            "brainstem": "brain",
            "orbital": "head and neck",
            "parotid": "head and neck",
            "renal": "abdominal",
            "nasal cavity": "head and neck",
            "liver": "abdominal",
            "lung": "thoracic",
            "breast": "thoracic",
            "diaphragm": "thoracic",
            "rib": "thoracic",
            "groin": "pelvic",
            "larynx": "head and neck",
            "pelvis": "pelvic"
        }
        
        # Modality options for registrations
        self.modality_options = ["MRI", "PET/CT", "CT", "CBCT"]
        
        # Registration method options
        self.registration_methods = ["Rigid", "Deformable"]
        
        # Updated registration presets
        self.registration_presets = {
            "MRI/CT": [{"primary": "CT", "secondary": "MRI", "method": "Rigid"}],
            "PET/CT rigid": [{"primary": "CT", "secondary": "PET/CT", "method": "Rigid"}],
            "PET/CT deformable": [{"primary": "CT", "secondary": "PET/CT", "method": "Deformable"}],
            "CT/CT rigid": [{"primary": "CT", "secondary": "CT", "method": "Rigid"}],
            "CT/CT deformable": [{"primary": "CT", "secondary": "CT", "method": "Deformable"}],
            "Custom": []  # For custom registration configurations
        }
    
    def render_fusion_form(self):
        """Render the enhanced form for fusion write-ups with modular registration configuration."""
        st.subheader("Enhanced Fusion Write-Up Generator")
        
        # Create tabs for Basic Info and Registration Details
        basic_tab, registration_tab = st.tabs(["Basic Information", "Registration Details"])
        
        with basic_tab:
            # Two-column layout for basic information
            col1, col2 = st.columns(2)
            
            with col1:
                # Staff information
                st.markdown("#### Staff Information")
                physician = st.selectbox("Physician Name", 
                                        self.config_manager.get_physicians(), 
                                        key="fusion_physician")
                physicist = st.selectbox("Physicist Name", 
                                        self.config_manager.get_physicists(), 
                                        key="fusion_physicist")
                
                # Patient information
                st.markdown("#### Patient Information")
                patient_age = st.number_input("Patient Age", min_value=0, max_value=120, key="fusion_age")
                patient_sex = st.selectbox("Patient Sex", ["male", "female", "other"], key="fusion_sex")
                
                # Lesion dropdown with "Other" option for custom entries
                lesion_options = sorted(list(self.lesion_to_region.keys()))
                lesion_options.append("Other (specify)")
                
                selected_lesion = st.selectbox("Lesion", lesion_options, key="fusion_lesion_selection")
                
                # If "Other" is selected, show text inputs for custom lesion and region
                if selected_lesion == "Other (specify)":
                    custom_lesion = st.text_input("Custom Lesion", key="fusion_custom_lesion")
                    
                    # Dropdown for anatomical region when custom lesion is selected
                    region_options = ["head and neck", "brain", "thoracic", "abdominal", "pelvic", "spinal"]
                    custom_region = st.selectbox("Anatomical Region", region_options, key="fusion_custom_region")
                    
                    lesion = custom_lesion if custom_lesion else "unspecified"
                    anatomical_region = custom_region
                else:
                    lesion = selected_lesion
                    # Get the anatomical region based on the selected lesion (hidden from user)
                    anatomical_region = self.lesion_to_region.get(lesion, "")
                
                patient_details = f"a {patient_age}-year-old {patient_sex} with a {lesion} lesion"
        
        with registration_tab:
            # Select registration configuration method
            st.markdown("#### Registration Configuration")
            
            # Preset selection
            preset_option = st.selectbox(
                "Registration Preset", 
                list(self.registration_presets.keys()),
                key="fusion_preset"
            )
            
            # Initialize session state for registrations if it doesn't exist
            if 'registrations' not in st.session_state:
                st.session_state.registrations = []
            
            # Load preset when selected
            if st.button("Load Preset", key="load_preset") or (preset_option != "Custom" and len(st.session_state.registrations) == 0):
                st.session_state.registrations = self.registration_presets[preset_option].copy()
            
            # Display current registrations
            st.markdown("#### Current Registrations")
            if not st.session_state.registrations:
                st.info("No registrations configured. Add a registration below or select a preset.")
            else:
                for i, reg in enumerate(st.session_state.registrations):
                    with st.container():
                        cols = st.columns([3, 3, 2, 1])
                        with cols[0]:
                            st.write(f"**Primary**: {reg['primary']}")
                        with cols[1]:
                            st.write(f"**Secondary**: {reg['secondary']}")
                        with cols[2]:
                            st.write(f"**Method**: {reg['method']}")
                        with cols[3]:
                            if st.button("🗑️", key=f"delete_{i}"):
                                st.session_state.registrations.pop(i)
                                st.rerun()
            
            # Add new registration
            st.markdown("#### Add New Registration")
            with st.container():
                cols = st.columns([3, 3, 2, 1])
                with cols[0]:
                    # Primary is always CT, so display text instead of dropdown
                    st.write("**Primary**: CT")
                    new_primary = "CT"  # Always set to CT
                with cols[1]:
                    new_secondary = st.selectbox("Secondary", self.modality_options, key="new_secondary")
                with cols[2]:
                    new_method = st.selectbox("Method", self.registration_methods, key="new_method")
                with cols[3]:
                    if st.button("➕", key="add_registration"):
                        st.session_state.registrations.append({
                            "primary": new_primary,
                            "secondary": new_secondary,
                            "method": new_method
                        })
                        st.rerun()
        
        # Generate button
        generate_pressed = st.button("Generate Write-Up", type="primary", key="fusion_generate")
        
        # Check if all required fields are filled
        required_fields = [physician, physicist, patient_age]
        # Additional validation for custom lesion
        if selected_lesion == "Other (specify)" and not custom_lesion:
            custom_lesion_filled = False
        else:
            custom_lesion_filled = True
        
        # Check if any registrations are configured
        registrations_configured = len(st.session_state.registrations) > 0
            
        all_fields_filled = all(str(field) != "" and str(field) != "0" for field in required_fields) and \
            custom_lesion_filled and registrations_configured
        
        # Show warnings for missing fields
        if generate_pressed and not all_fields_filled:
            st.error("Please fill in all required fields before generating the write-up.")
            for i, field in enumerate([physician, physicist, patient_age]):
                if str(field) == "" or str(field) == "0":
                    field_names = ["Physician Name", "Physicist Name", "Patient Age"]
                    st.warning(f"Missing required field: {field_names[i]}")
            
            # Check for custom lesion specifically
            if selected_lesion == "Other (specify)" and not custom_lesion:
                st.warning("Missing required field: Custom Lesion")
                
            # Check for registrations
            if not registrations_configured:
                st.warning("Please add at least one registration in the Registration Details tab.")
        
        # Generate write-up if all fields are filled and button is pressed
        if generate_pressed and all_fields_filled:
            # Generate fusion description text based on the registrations
            fusion_type_text = self._generate_fusion_text(st.session_state.registrations, anatomical_region, lesion)
            
            template_data = {
                "physician": physician,
                "physicist": physicist,
                "patient_details": patient_details,
                "patient_age": patient_age,
                "patient_sex": patient_sex,
                "lesion": lesion,
                "fusion_type_text": fusion_type_text
            }
            
            # Use the template file for consistent formatting
            write_up = self.template_manager.render_template("fusion", template_data)
            return write_up
        
        return None
    
    def _generate_fusion_text(self, registrations, anatomical_region, lesion):
        """Generate the fusion description text based on the configured registrations."""
        # Count registrations by modality for summary
        modality_counts = {}
        for reg in registrations:
            secondary = reg['secondary']
            if secondary in modality_counts:
                modality_counts[secondary] += 1
            else:
                modality_counts[secondary] = 1
        
        # Introduction text varies based on the number and type of registrations
        intro_text = ""
        if len(registrations) == 1:
            # Single registration
            reg = registrations[0]
            secondary = reg['secondary']
            method = reg['method'].lower()
            
            if secondary == "CT":
                intro_text = f"Another {secondary} image study that was previously acquired was imported into the Velocity software. "
            else:
                intro_text = f"A {secondary} image study that was previously acquired was imported into the Velocity software. "
                
            intro_text += f"A fusion study was created between the planning CT and the {secondary} image set. "
            
        else:
            # Multiple registrations
            modality_list = ", ".join([f"{count} {mod}" for mod, count in modality_counts.items()])
            intro_text = f"Multiple image studies including {modality_list} were imported into the Velocity software. "
            intro_text += "Fusion studies were created between the planning CT and each of the other modality image sets. "
        
        # Registration process description
        reg_text = ""
        for i, reg in enumerate(registrations):
            if i > 0:
                reg_text += "\n\n"
            
            secondary = reg['secondary']
            method = reg['method']
            
            if method == "Rigid":
                reg_text += f"The CT and {secondary} image sets were first registered using a rigid registration algorithm based on the {anatomical_region} anatomy and then refined manually. "
            else:  # Deformable
                reg_text += f"The CT and {secondary} image sets were initially aligned using a rigid registration algorithm based on the {anatomical_region} anatomy. A deformable image registration was then performed to improve registration results. "
                
            reg_text += f"The resulting registration of the fused images was verified for accuracy using anatomical landmarks such as the {lesion}."
        
        # Conclusion text
        conclusion_text = " The fused images were used to improve the identification of critical structures and targets and to accurately contour them for treatment planning."
        
        return intro_text + reg_text + conclusion_text
    
    def display_write_up(self, write_up):
        """Display the generated write-up with a copy button."""
        if write_up:
            st.markdown("### Generated Write-Up")
            
            # Create a container with custom styling for better visibility
            with st.container():
                # Display in text area for viewing/editing
                st.text_area("", write_up, height=300, key="result", label_visibility="collapsed")
                
                # Add a tooltip with copy instructions
                st.info("💡 To copy: Click inside the text box, use Ctrl+A (or Cmd+A on Mac) to select all, then Ctrl+C (or Cmd+C) to copy.")
                
                # Optional: Add download button
                st.download_button(
                    label="Download as Text File",
                    data=write_up,
                    file_name="fusion_write_up.txt",
                    mime="text/plain"
                )