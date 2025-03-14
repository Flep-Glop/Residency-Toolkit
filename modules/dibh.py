import streamlit as st
import datetime
from .templates import ConfigManager

class DIBHModule:
    """Deep Inspiration Breath Hold (DIBH) module for clinical documentation generation.
    
    This module handles the creation of documentation for DIBH treatments in radiation therapy.
    DIBH is a technique used primarily in breast cancer radiotherapy to reduce cardiac dose by
    having the patient hold their breath during treatment, which moves the heart away from the
    chest wall and treatment field.
    
    Clinical Context:
        - Primarily used for left breast treatments to reduce heart dose
        - Can also be used for other thoracic treatments to reduce respiratory motion
        - Requires specialized equipment (typically C-RAD or similar surface tracking)
        - Patients must be able to reliably hold their breath for 20-30 seconds
    
    The module provides a user interface for inputting patient and treatment details,
    validates these inputs, and generates standardized clinical documentation.
    """
    def __init__(self):
        """Initialize the DIBH module."""
        self.config_manager = ConfigManager()
    
    def render_dibh_form(self):
        """Render the form for DIBH write-ups with enhanced validation."""
        
        # Add an information expander that users can click to learn more
        with st.expander("ℹ️ About DIBH Technique", expanded=False):
            st.markdown("""
            ### Deep Inspiration Breath Hold (DIBH)
            
            **Clinical Purpose:**  
            DIBH is a technique used primarily in breast cancer radiation therapy to reduce radiation 
            dose to the heart. By having the patient hold their breath, the heart moves away from the 
            chest wall, creating distance from the treatment area and reducing cardiac exposure.
            
            **Key Benefits:**
            - Reduces mean heart dose by 25-67% in left breast treatments
            - Minimizes respiratory motion during treatment delivery
            - Can improve dose homogeneity across the target volume
            
            **Patient Selection:**
            - Most commonly used for left-sided breast cancer patients
            - Requires patient ability to hold breath for ~20 seconds
            - May also benefit patients with other thoracic treatments
            
            **Equipment Requirements:**
            - Surface monitoring system (C-RAD or similar)
            - Visual feedback system for patient breath-hold guidance
            - Image guidance for verification
            """)
        
        # Use tabs to organize the form
        basic_tab, treatment_tab, preview_tab = st.tabs([
            "Basic Information", "Treatment Details", "Preview"
        ])
        if 'dibh_last_values' not in st.session_state:
            st.session_state.dibh_last_values = {}
        
        with basic_tab:
            # Create two columns for headers
            header_col1, header_col2 = st.columns(2)
            
            with header_col1:
                st.markdown("#### Staff Information")
            
            with header_col2:
                st.markdown("#### Patient Information")
            
            # Create two columns for the form fields
            col1, col2 = st.columns(2)
            
            with col1:
                physician = st.selectbox("Physician Name", 
                                    self.config_manager.get_physicians(), 
                                    key="dibh_physician")
                
                physicist = st.selectbox("Physicist Name", 
                                    self.config_manager.get_physicists(), 
                                    key="dibh_physicist")
            
            with col2:
                patient_age = st.number_input("Patient Age", 
                                        min_value=0, 
                                        max_value=120, 
                                        key="dibh_age")
                
                patient_sex = st.selectbox("Patient Sex", 
                                        ["male", "female", "other"], 
                                        key="dibh_sex")
            
            patient_details = f"a {patient_age}-year-old {patient_sex}"
        
        with treatment_tab:
            # Treatment information
            st.markdown("#### Treatment Information")
            col1, col2 = st.columns(2)
            
            with col1:
                treatment_site = st.selectbox("Treatment Site", 
                                            ["left breast", "right breast", "diaphragm", "chest wall"], 
                                            key="dibh_site")
                
                # Add tooltip with info about DIBH
                st.info("💡 DIBH is typically used for left breast to reduce cardiac dose, but can be used for other thoracic sites.")
                
                immobilization_device = st.selectbox("Immobilization Device", 
                                                ["breast board", "wing board"], 
                                                key="dibh_immobilization")
            
            with col2:
                dose = st.number_input("Prescription Dose (Gy)", 
                                    min_value=0.0, 
                                    value=40.0, 
                                    step=0.1, 
                                    key="dibh_dose")
                
                fractions = st.number_input("Number of Fractions", 
                                        min_value=1, 
                                        value=15, 
                                        key="dibh_fractions")
                
                # Show dose per fraction calculation
                if fractions > 0:
                    dose_per_fraction = dose / fractions
                    st.text(f"Dose per fraction: {dose_per_fraction:.2f} Gy")
                    
                    # Provide guidance based on dose per fraction
                    if dose_per_fraction > 3:
                        st.warning(f"Dose per fraction ({dose_per_fraction:.2f} Gy) is higher than conventional fractionation")
                    elif dose_per_fraction < 1.5:
                        st.info(f"Dose per fraction ({dose_per_fraction:.2f} Gy) indicates hypofractionation")
        
        with preview_tab:
            # Show a preview of what the write-up will contain
            st.markdown("#### Write-Up Preview")
            st.info("This tab shows a preview of the information that will be included in your write-up.")
            
            if patient_age > 0 and treatment_site and dose > 0 and fractions > 0:
                st.markdown(f"**Patient:** {patient_age}-year-old {patient_sex}")
                st.markdown(f"**Treatment:** {treatment_site} using DIBH technique")
                st.markdown(f"**Prescription:** {dose} Gy in {fractions} fractions")
                st.markdown(f"**Staff:** Dr. {physician} (Radiation Oncologist), Dr. {physicist} (Medical Physicist)")
                st.markdown("**Procedure:** DIBH CT simulation with C-RAD positioning and gating system")
            else:
                st.warning("Complete the form fields to see a preview")
        
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
        
        # Enhanced validation when generate button is pressed
        if generate_pressed and all_fields_filled:
            validation_errors = self._validate_inputs(patient_age, treatment_site, dose, fractions)
            
            if validation_errors:
                st.error("Please address the following issues:")
                for error in validation_errors:
                    st.warning(error)
                
                # Add override option for edge cases
                if st.checkbox("Override validation (use with caution)"):
                    st.warning("You're overriding validation checks. Ensure all information is clinically appropriate.")
                    override = True
                else:
                    return None
            else:
                override = False
            
            try:
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
                
                # Log this successful generation (you could expand this for analytics)
                if not override:
                    st.session_state.setdefault('generation_log', []).append({
                        'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'module': 'DIBH',
                        'physician': physician,
                        'treatment_site': treatment_site
                    })
                
                return write_up
                
            except Exception as e:
                st.error(f"An error occurred while generating the write-up: {str(e)}")
                st.info("Please contact support if this error persists.")
                return None
        
        return None
    
    def _generate_dibh_write_up(self, physician, physicist, patient_details, treatment_site, 
                          dose, fractions, machine, scanning_system, 
                          immobilization_device):
        """Generate the DIBH write-up with enhanced content based on inputs."""
        
        # Calculate dose per fraction for use in the write-up
        dose_per_fraction = dose / fractions
        fractionation_description = "conventional fractionation" if dose_per_fraction <= 2.0 else "hypofractionated"
        
        # Add specific details based on treatment site
        if treatment_site == "left breast":
            site_specific_text = "left breast with a DIBH technique to reduce dose to the heart "
            benefit_text = "significantly reduce cardiac dose"
        elif treatment_site == "right breast":
            site_specific_text = "right breast with a DIBH technique "
            benefit_text = "minimize breathing motion during radiation delivery"
        else:
            site_specific_text = f"{treatment_site} with a DIBH technique "
            benefit_text = "minimize breathing motion during radiation delivery"
        
        write_up = f"Dr. {physician} requested a medical physics consultation for --- for a gated, DIBH treatment. "
        write_up += f"The patient is {patient_details}. Dr. {physician} has elected "
        write_up += f"to treat the {site_specific_text}to {benefit_text} "
        write_up += f"using the C-RAD positioning and gating system in conjunction with the {machine}.\n\n"
        
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
        write_up += f"prescribed dose of {dose} Gy in {fractions} fractions ({dose_per_fraction:.2f} Gy per fraction) "
        write_up += f"to the {treatment_site} using {fractionation_description}. "
        write_up += f"The delivery of the DIBH gating technique on the linear accelerator will be performed "
        write_up += f"using the C-RAD CatalystHD. The CatalystHD will be used to position the patient, "
        write_up += f"monitor intra-fraction motion, and gate the beam delivery. Verification of the patient "
        write_up += f"position will be validated with a DIBH kV-CBCT. Treatment plan calculations and delivery "
        write_up += f"procedures were reviewed and approved by the prescribing radiation oncologist, Dr. {physician}, "
        write_up += f"and the radiation oncology physicist, Dr. {physicist}."
        
        return write_up
    
    # Add this validation function to DIBHModule
    def _validate_inputs(self, patient_age, treatment_site, dose, fractions):
        """Validate DIBH form inputs with specific clinical context."""
        errors = []
        
        # Age validation
        if patient_age <= 0:
            errors.append("Patient age must be greater than 0")
        if patient_age > 100:
            errors.append("Please verify patient age (>100)")
        
        # Dose validation
        if dose <= 0:
            errors.append("Dose must be greater than 0")
        if dose < 10:
            errors.append("Dose appears unusually low for radiation therapy (<10 Gy)")
        if dose > 80:
            errors.append("Dose exceeds typical range for DIBH treatments (>80 Gy)")
        
        # Fractionation validation
        if fractions <= 0:
            errors.append("Number of fractions must be greater than 0")
        if fractions == 1 and dose > 20:
            errors.append("Single fraction treatment with high dose (>20 Gy) is unusual")
        if fractions > 40:
            errors.append("Unusually high number of fractions (>40)")
        
        # DIBH-specific validation
        if treatment_site not in ["left breast", "right breast", "diaphragm", "chest wall"]:
            errors.append(f"'{treatment_site}' is not a typical DIBH treatment site")
        
        # Dose-fractionation relationship
        dose_per_fraction = dose / fractions if fractions > 0 else 0
        if dose_per_fraction > 5 and fractions > 5:
            errors.append(f"Dose per fraction ({dose_per_fraction:.2f} Gy) is unusually high")
        
        return errors

    def display_write_up(self, write_up):
        """Display the generated write-up with enhanced features."""
        if write_up:
            st.markdown("### Generated Write-Up")
            
            # Create a container with custom styling for better visibility
            with st.container():
                # Display in text area for viewing/editing
                edited_write_up = st.text_area("", write_up, height=300, key="dibh_result", label_visibility="collapsed")
                
                # Track if user made edits
                if edited_write_up != write_up:
                    st.info("You've made edits to the generated write-up.")
                
                # Add a tooltip with copy instructions
                st.info("💡 To copy: Click inside the text box, use Ctrl+A (or Cmd+A on Mac) to select all, then Ctrl+C (or Cmd+C) to copy.")
                
                # Two-column layout for action buttons
                col1, col2 = st.columns(2)
                
                with col1:
                    # Optional: Add download button with timestamp
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    st.download_button(
                        label="Download as Text File",
                        data=edited_write_up,
                        file_name=f"dibh_write_up_{timestamp}.txt",
                        mime="text/plain"
                    )
                
                with col2:
                    # Add a button to copy to clipboard using JavaScript
                    st.markdown(
                        """
                        <script>
                        function copyToClipboard() {
                            const textArea = document.querySelector('textarea[aria-label=""]');
                            textArea.select();
                            document.execCommand('copy');
                        }
                        </script>
                        <button onclick="copyToClipboard()">Copy to Clipboard</button>
                        """,
                        unsafe_allow_html=True
                    )