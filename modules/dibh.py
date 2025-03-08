import streamlit as st
from .templates import ConfigManager

class DIBHModule:
    def __init__(self):
        """Initialize the DIBH module."""
        self.config_manager = ConfigManager()
    
    def render_dibh_form(self):
        """Render the form for DIBH write-ups."""
        st.subheader("DIBH Write-Up Generator")
        
        # Use tabs to organize the form
        basic_tab, treatment_tab = st.tabs([
            "Basic Information", "Treatment Details"
        ])
        
        with basic_tab:
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
            col1, col2 = st.columns(2)
            
            with col1:
                patient_age = st.number_input("Patient Age", min_value=0, max_value=120, key="dibh_age")
            with col2:
                patient_sex = st.selectbox("Patient Sex", ["male", "female", "other"], key="dibh_sex")
            
            patient_details = f"a {patient_age}-year-old {patient_sex}"
        
        with treatment_tab:
            # Treatment information - moved from basic tab
            st.markdown("#### Treatment Information")
            col1, col2 = st.columns(2)
            
            with col1:
                treatment_site = st.selectbox("Treatment Site", 
                                            ["left breast", "right breast", "diaphragm", "chest wall"], 
                                            key="dibh_site")
                
                immobilization_device = st.selectbox("Immobilization Device", 
                                                ["breast board", "wing board"], 
                                                key="dibh_immobilization")
            
            with col2:
                dose = st.number_input("Prescription Dose (Gy)", min_value=0.0, value=40.0, step=0.1, key="dibh_dose")
                fractions = st.number_input("Number of Fractions", min_value=1, value=15, key="dibh_fractions")
        
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
            # Default values for removed form fields
            machine = "linear accelerator" 
            scanning_system = "C-RAD"
            
            # Generate the write-up based on the inputs
            write_up = self._generate_dibh_write_up(
                physician=physician,
                physicist=physicist,
                patient_details=patient_details,
                treatment_site=treatment_site,
                dose=dose,
                fractions=fractions,
                machine=machine,
                scanning_system=scanning_system,
                immobilization_device=immobilization_device
            )
            
            return write_up
        
        return None
    
    def _generate_dibh_write_up(self, physician, physicist, patient_details, treatment_site, 
                              dose, fractions, machine, scanning_system, 
                              immobilization_device):
        """Generate the DIBH write-up based on the inputs."""
        
        write_up = f"Dr. {physician} requested a medical physics consultation for --- for a gated, DIBH treatment."
        write_up += f"The patient is {patient_details}. Dr. {physician} has elected "
        write_up += f"to treat the {treatment_site} with a DIBH technique to reduce dose to the heart "
        write_up += f"and lung and minimize breathing motion during radiation delivery using the C-RAD "
        write_up += f"positioning and gating system in conjunction with the {machine} linear accelerator.\n\n"
        
        write_up += f"Days before the initial radiation delivery, the patient was simulated in the treatment "
        write_up += f"position using a {immobilization_device} to aid in immobilization "
        write_up += f"and localization. The patient was provided instructions and coached to reproducibly "
        write_up += f"hold their breath. Using the {scanning_system} surface scanning system, a free breathing "
        write_up += f"and breath hold signal trace was established. The patient was then asked to reproduce "
        write_up += f"the breath hold pattern using visual goggles. Once the patient established a consistent "
        write_up += f"breathing pattern, a gating baseline and gating window was established. Doing so, a "
        write_up += f"DIBH CT simulation scan was then acquired. The DIBH CT simulation scan was approved "
        write_up += f"by the Radiation Oncologist, Dr. {physician}.\n\n"
        
        write_up += f"A radiation treatment plan was developed on the DIBH CT simulation to deliver a "
        write_up += f"prescribed dose of {dose} Gy in {fractions} fractions to the {treatment_site}. "
        write_up += f"The delivery of the DIBH gating technique on the linear accelerator will be performed "
        write_up += f"using the C-RAD CatalystHD. The CatalystHD will be used to position the patient, "
        write_up += f"monitor intra-fraction motion, and gate the beam delivery. Verification of the patient "
        write_up += f"position will be validated with a DIBH kV-CBCT. Treatment plan calculations and delivery "
        write_up += f"procedures were reviewed and approved by the prescribing radiation oncologist, Dr. {physician} "
        write_up += f"and the radiation oncology physicist, Dr. {physicist}."
        
        return write_up
    
    def display_write_up(self, write_up):
        """Display the generated write-up with a copy button."""
        if write_up:
            st.markdown("### Generated Write-Up")
            
            # Create a container with custom styling for better visibility
            with st.container():
                # Display in text area for viewing/editing
                st.text_area("", write_up, height=300, key="dibh_result", label_visibility="collapsed")
                
                # Add a tooltip with copy instructions
                st.info("💡 To copy: Click inside the text box, use Ctrl+A (or Cmd+A on Mac) to select all, then Ctrl+C (or Cmd+C) to copy.")
                
                # Optional: Add download button
                st.download_button(
                    label="Download as Text File",
                    data=write_up,
                    file_name="dibh_write_up.txt",
                    mime="text/plain"
                )