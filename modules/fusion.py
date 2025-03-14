import streamlit as st
from .base_module import BaseWriteUpModule

class FusionModule(BaseWriteUpModule):
    """Fusion module for clinical documentation generation."""
    
    def __init__(self, config_manager):
        """Initialize the Fusion module with configuration manager."""
        super().__init__(config_manager)
        
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
    
    def get_module_name(self):
        """Return the display name of this module."""
        return "Fusion"
    
    def get_module_description(self):
        """Return a brief description of this module."""
        return "Image fusion for improved target delineation in radiation therapy"
    
    def get_required_fields(self):
        """Return a list of required field names for this module."""
        return ["lesion", "registrations"]
    
    def render_specialized_fields(self, physician, physicist, patient_age, patient_sex, patient_details):
        """Render Fusion-specific input fields and return the generated data."""
        # Initialize session state for registrations if it doesn't exist
        if 'registrations' not in st.session_state:
            st.session_state.registrations = []
        
        # Create tabs for Basic Info and Registration Details
        lesions_tab, registration_tab = st.tabs(["Lesion Information", "Registration Details"])
        
        with lesions_tab:
            col1, col2 = st.columns(2)
            
            with col1:
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
        
        with registration_tab:
            # Registration configuration 
            st.markdown("#### Current Registrations")
            
            # Display current registrations
            if not st.session_state.registrations:
                st.info("No registrations configured. Add a registration below.")
            else:
                # Create a container to hold all registrations
                registration_container = st.container()
                
                # Display each registration in the container
                with registration_container:
                    for i, reg in enumerate(st.session_state.registrations):
                        cols = st.columns([3, 3, 2, 1])
                        with cols[0]:
                            st.write(f"**Primary**: {reg['primary']}")
                        with cols[1]:
                            st.write(f"**Secondary**: {reg['secondary']}")
                        with cols[2]:
                            st.write(f"**Method**: {reg['method']}")
                        with cols[3]:
                            # Use a unique key for each delete button
                            if st.button("🗑️", key=f"delete_reg_{i}_{reg['secondary']}"):
                                st.session_state.registrations.pop(i)
                                st.rerun()
            
            # Add new registration
            st.markdown("#### Add New Registration")
            
            # Use a form to prevent auto-rerun
            with st.form(key="add_registration_form"):
                cols = st.columns([3, 3, 2, 1])
                with cols[0]:
                    # Primary is always CT, so display text instead of dropdown
                    st.write("**Primary**: CT")
                    new_primary = "CT"  # Always set to CT
                with cols[1]:
                    new_secondary = st.selectbox("Secondary", self.modality_options, key="new_secondary")
                with cols[2]:
                    new_method = st.selectbox("Method", self.registration_methods, key="new_method")
                
                # Add a submit button to the form
                submitted = st.form_submit_button("Add Registration")
                
                # Only process when form is submitted to prevent auto-reruns
                if submitted:
                    st.session_state.registrations.append({
                        "primary": new_primary,
                        "secondary": new_secondary,
                        "method": new_method
                    })
                    st.rerun()  # Only rerun here, after form submission
        
        # Check if all required fields are filled
        required_fields_filled = True
        
        # Additional validation for custom lesion
        if selected_lesion == "Other (specify)" and not custom_lesion:
            required_fields_filled = False
        
        # Check if any registrations are configured
        registrations_configured = len(st.session_state.registrations) > 0
        
        if not registrations_configured:
            required_fields_filled = False
        
        # If all required fields are filled, return the module data
        if required_fields_filled:
            return {
                "lesion": lesion,
                "anatomical_region": anatomical_region,
                "registrations": st.session_state.registrations
            }
        
        return None
    
    def generate_write_up(self, common_info, module_data):
        """Generate the Fusion write-up based on common and module-specific data."""
        # Implementation remains the same
        physician = common_info.get("physician", "")
        physicist = common_info.get("physicist", "")
        patient_details = common_info.get("patient_details", "")
        
        lesion = module_data.get("lesion", "")
        anatomical_region = module_data.get("anatomical_region", "")
        registrations = module_data.get("registrations", [])
        
        # Generate fusion description text based on the registrations
        fusion_type_text = self._generate_fusion_text(registrations, anatomical_region, lesion)
        
        # Generate the write-up
        write_up = f"Dr. {physician} requested a medical physics consultation for --- to perform a multimodality image fusion. "
        write_up += f"The patient is {patient_details}. "
        write_up += "The patient was scanned in our CT simulator in the treatment position. "
        write_up += "The CT study was then exported to the Velocity imaging registration software.\n\n"
        
        write_up += f"{fusion_type_text}\n\n"
        
        write_up += f"The fusion of the image sets was reviewed and approved by both the prescribing radiation oncologist, "
        write_up += f"Dr. {physician}, and the medical physicist, Dr. {physicist}."
        
        return write_up
    
    def _generate_fusion_text(self, registrations, anatomical_region, lesion):
        """Generate the fusion description text based on the configured registrations."""
        # Implementation remains the same
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