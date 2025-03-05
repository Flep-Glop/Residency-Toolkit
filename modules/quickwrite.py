import streamlit as st
from .templates import TemplateManager, ConfigManager
from .fusion import FusionModule
from .prior_dose import PriorDoseModule
from .pacemaker import PacemakerModule
from .sbrt import SBRTModule

class QuickWriteModule:
    def __init__(self):
        """Initialize the Quick Write module."""
        self.template_manager = TemplateManager()
        self.config_manager = ConfigManager()
        self.fusion_module = FusionModule()
        self.prior_dose_module = PriorDoseModule()
        self.pacemaker_module = PacemakerModule()
        self.sbrt_module = SBRTModule()
        
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
        """Delegate to the FusionModule for enhanced fusion write-ups."""
        return self.fusion_module.render_fusion_form()
    
    def render_prior_dose_form(self):
        """Delegate to the PriorDoseModule for prior dose write-ups."""
        return self.prior_dose_module.render_prior_dose_form()
    
    def render_pacemaker_form(self):
        """Delegate to the PacemakerModule for pacemaker write-ups."""
        return self.pacemaker_module.render_pacemaker_form()
    
    def render_sbrt_form(self):
        """Delegate to the SBRTModule for SBRT write-ups."""
        return self.sbrt_module.render_sbrt_form()
    
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