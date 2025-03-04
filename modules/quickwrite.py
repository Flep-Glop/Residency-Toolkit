import streamlit as st
from .templates import TemplateManager, ConfigManager

class QuickWriteModule:
    def __init__(self):
        """Initialize the Quick Write module."""
        self.template_manager = TemplateManager()
        self.config_manager = ConfigManager()
        
        # Mapping of lesions to anatomical regions for the fusion form
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
        
    def render_dibh_form(self):
        """Render the form for DIBH write-ups."""
        st.subheader("DIBH Write-Up Generator")
        
        # Two-column layout for efficient use of space
        col1, col2 = st.columns(2)
        
        with col1:
            # Staff information
            st.markdown("#### Staff Information")
            physician = st.selectbox("Physician Name", 
                                    self.config_manager.get_physicians(), 
                                    key="dibh_physician")
            physicist = st.selectbox("Physicist Name", 
                                    self.config_manager.get_physicists(), 
                                    key="dibh_physicist")
            
            # Patient information
            st.markdown("#### Patient Information")
            patient_age = st.number_input("Patient Age", min_value=0, max_value=120, key="dibh_age")
            patient_sex = st.selectbox("Patient Sex", ["male", "female", "other"], key="dibh_sex")
            patient_details = f"a {patient_age}-year-old {patient_sex}"
        
        with col2:
            # Treatment information
            st.markdown("#### Treatment Information")
            treatment_site = st.selectbox("Treatment Site", 
                                          ["left breast", "right breast", "diaphragm", "chest wall"], 
                                          key="dibh_site")
            
            # Determine breast side based on selection
            breast_side = ""
            if "breast" in treatment_site or "chest wall" in treatment_site:
                breast_side = treatment_site.split()[0]
            
            dose = st.number_input("Prescription Dose (Gy)", min_value=0.0, value=40.0, key="dibh_dose")
            fractions = st.number_input("Number of Fractions", min_value=1, value=15, key="dibh_fractions")
            
            # Equipment information
            machine = st.selectbox("Treatment Machine", ["VersaHD", "TrueBeam", "Halcyon"], key="dibh_machine")
            scanning_system = st.selectbox("Scanning System", ["Sentinel", "Catalyst"], key="dibh_scanning")
            immobilization_device = st.selectbox("Immobilization Device", 
                                                ["breast board", "wing board", "vac-lok bag"], 
                                                key="dibh_immobilization")
        
        # Generate button
        generate_pressed = st.button("Generate Write-Up", type="primary", key="dibh_generate")
        
        # Check if we have all required information and the button was pressed
        required_fields = [physician, physicist, patient_age, treatment_site, dose, fractions]
        all_fields_filled = all(str(field) != "" and str(field) != "0" for field in required_fields)
        
        # Show missing fields if any
        if generate_pressed and not all_fields_filled:
            st.error("Please fill in all required fields before generating the write-up.")
            for i, field in enumerate([physician, physicist, patient_age, treatment_site, dose, fractions]):
                if str(field) == "" or str(field) == "0":
                    field_names = ["Physician Name", "Physicist Name", "Patient Age", 
                                  "Treatment Site", "Prescription Dose", "Number of Fractions"]
                    st.warning(f"Missing required field: {field_names[i]}")
            return None
        
        # If all required fields are filled and button is pressed, generate the write-up
        if generate_pressed and all_fields_filled:
            template_data = {
                "physician": physician,
                "physicist": physicist,
                "patient_details": patient_details,
                "treatment_site": treatment_site,
                "breast_side": breast_side,
                "dose": dose,
                "fractions": fractions,
                "machine": machine,
                "scanning_system": scanning_system,
                "immobilization_device": immobilization_device
            }
            
            write_up = self.template_manager.render_template("dibh", template_data)
            return write_up
        
        return None

    def render_fusion_form(self):
        """Render the form for fusion write-ups."""
        st.subheader("Fusion Write-Up Generator")
        
        # Two-column layout
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
        
        with col2:
            # Fusion information
            st.markdown("#### Fusion Information")
            fusion_type = st.selectbox("Fusion Type", 
                                    ["CT Only", "CT+PET", "CT+MRI", "Multiple Modalities"], 
                                    key="fusion_type")
            
            # Registration method
            registration_method = st.selectbox("Registration Method",
                                            ["Rigid", "Deformable"],
                                            key="fusion_reg_method")
            
            # Show different options based on fusion type
            if fusion_type == "CT Only":
                fusion_type_text = """Another CT image study that was previously acquired was also imported into the Velocity software. A fusion study between the CT sim and the previous CT image set was created. The fusion study was initially registered using a non-deformable registration algorithm based on the {anatomical_region} anatomy and refined manually. {deformable_text}The resulting registration of the fused images was verified for accuracy using anatomical landmarks such as the {lesion}. The fused images were used in order to improve the identification of the critical structures and targets and to accurately contour them."""
                
            elif fusion_type == "CT+PET":
                fusion_type_text = """A PET/CT image study that was previously acquired was also transferred to the Velocity software. A fusion study was then created using the two CT images. The CT image sets were first registered using a non-deformable registration algorithm based on the {anatomical_region} anatomy and then refined manually. {deformable_text}The resulting registration of the fused images was verified for accuracy using anatomical landmarks such as the {lesion} and utilized to register the standard uptake values from the PET image to the treatment planning CT. The fused images were used to facilitate the segmentation of targets for the patient's treatment with external beam radiotherapy."""
                
            elif fusion_type == "CT+MRI":
                fusion_type_text = """An MRI study that was previously acquired was also transferred to the Velocity software. A fusion study between the CT and MRI image set was created. The CT and MRI image sets were first registered using a non-deformable registration algorithm based on the {anatomical_region} anatomy and then refined manually. {deformable_text}The resulting registration of the fused images was verified for accuracy using anatomical landmarks such as the {lesion}. The fused images were used to improve the identification of the critical structures and targets and to accurately contour them."""
                
            else:  # Multiple Modalities
                fusion_type_text = """Multiple image studies including CT, MRI, and PET/CT were transferred to the Velocity software. Fusion studies were created between the primary CT simulation and each of the other modalities. The image sets were first registered using a non-deformable registration algorithm based on the {anatomical_region} anatomy and then refined manually. {deformable_text}The resulting registrations of the fused images were verified for accuracy using anatomical landmarks such as the {lesion}. The fused images were used to improve the identification of the critical structures and targets and to accurately contour them."""
            
            # Deformable text based on registration method
            deformable_text = "A deformable image registration was then performed to improve registration results. " if registration_method == "Deformable" else ""
            
            # Anatomical region is now handled behind the scenes
            # No visible indicator is shown to the user
        
        # Generate button
        generate_pressed = st.button("Generate Write-Up", type="primary", key="fusion_generate")
        
        # Check if all required fields are filled
        required_fields = [physician, physicist, patient_age]
        # Additional validation for custom lesion
        if selected_lesion == "Other (specify)" and not custom_lesion:
            custom_lesion_filled = False
        else:
            custom_lesion_filled = True
            
        all_fields_filled = all(str(field) != "" and str(field) != "0" for field in required_fields) and custom_lesion_filled
        
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
            return None
        
        # Generate write-up if all fields are filled and button is pressed
        if generate_pressed and all_fields_filled:
            # Format the fusion type text with the actual values
            formatted_fusion_text = fusion_type_text.format(
                anatomical_region=anatomical_region,
                deformable_text=deformable_text,
                lesion=lesion
            )
            
            template_data = {
                "physician": physician,
                "physicist": physicist,
                "patient_details": patient_details,
                "patient_age": patient_age,
                "patient_sex": patient_sex,
                "lesion": lesion,
                "fusion_type_text": formatted_fusion_text
            }
            
            # Use the template file for consistent formatting
            write_up = self.template_manager.render_template("fusion", template_data)
            return write_up
        
        return None
    
    
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
                    file_name="write_up.txt",
                    mime="text/plain"
                )