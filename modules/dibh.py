import streamlit as st
from datetime import datetime
from .base_module import BaseWriteUpModule

class DIBHModule(BaseWriteUpModule):
    """Deep Inspiration Breath Hold (DIBH) module for clinical documentation generation.
    
    This module handles the creation of documentation for DIBH treatments in radiation therapy.
    DIBH is a technique used primarily in breast cancer radiotherapy to reduce cardiac dose by
    having the patient hold their breath during treatment, which moves the heart away from the
    chest wall and treatment field.
    """
    
    def get_module_name(self):
        """Return the display name of this module."""
        return "DIBH"
    
    def get_module_description(self):
        """Return a brief description of this module."""
        return "Deep Inspiration Breath Hold technique for reducing cardiac dose in radiation therapy"
    
    def get_required_fields(self):
        """Return a list of required field names for this module."""
        return ["treatment_site", "dose", "fractions", "immobilization_device"]
    
    def render_specialized_fields(self, physician, physicist, patient_age, patient_sex, patient_details):
        """Render DIBH-specific input fields and return the generated data."""
        
        # Add an information box instead of an expander to avoid nesting issues
        st.info("""
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
        treatment_tab, preview_tab = st.tabs([
            "Treatment Details", "Preview"
        ])
        
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
        
        # Generate button for standalone use
        generate_pressed = st.button("Generate Write-Up", type="primary", key="dibh_generate")
        
        # Check if we have all required information
        all_fields_filled = all([
            treatment_site != "", 
            dose > 0, 
            fractions > 0, 
            immobilization_device != ""
        ])
        
        # Show missing fields if any
        if generate_pressed and not all_fields_filled:
            st.error("Please fill in all required fields before generating the write-up.")
            for field, value in [
                ("Treatment Site", treatment_site),
                ("Prescription Dose", dose),
                ("Number of Fractions", fractions),
                ("Immobilization Device", immobilization_device)
            ]:
                if not value or value == 0:
                    st.warning(f"Missing required field: {field}")
            return None
        
        # If all required fields are filled, return the module data
        if all_fields_filled:
            # Enhanced validation when generate button is pressed
            if generate_pressed:
                validation_errors = self._validate_inputs(patient_age, treatment_site, dose, fractions)
                
                if validation_errors:
                    st.error("Please address the following issues:")
                    for error in validation_errors:
                        st.warning(error)
                    
                    # Add override option for edge cases
                    if st.checkbox("Override validation (use with caution)"):
                        st.warning("You're overriding validation checks. Ensure all information is clinically appropriate.")
                    else:
                        return None
            
            # Return the collected module-specific data
            return {
                "treatment_site": treatment_site,
                "dose": dose,
                "fractions": fractions,
                "immobilization_device": immobilization_device,
                "dose_per_fraction": dose / fractions if fractions > 0 else 0
            }
        
        return None
    
    def generate_write_up(self, common_info, module_data):
        """Generate the DIBH write-up based on common and module-specific data."""
        physician = common_info.get("physician", "")
        physicist = common_info.get("physicist", "")
        patient_details = common_info.get("patient_details", "")
        
        treatment_site = module_data.get("treatment_site", "")
        dose = module_data.get("dose", 0)
        fractions = module_data.get("fractions", 0)
        immobilization_device = module_data.get("immobilization_device", "")
        
        # Default values for fixed parameters
        machine = "linear accelerator" 
        scanning_system = "C-RAD"
        
        # Calculate dose per fraction for use in the write-up
        dose_per_fraction = dose / fractions if fractions > 0 else 0
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
    
    def render_dibh_form(self):
        """Legacy compatibility method for standalone operation."""
        # Staff information
        st.markdown("#### Staff Information")
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
        
        # Get module-specific data
        module_data = self.render_specialized_fields(
            physician, physicist, patient_age, patient_sex, patient_details
        )
        
        # Generate write-up if all data is provided
        if module_data:
            common_info = {
                "physician": physician,
                "physicist": physicist,
                "patient_age": patient_age,
                "patient_sex": patient_sex,
                "patient_details": patient_details
            }
            
            write_up = self.generate_write_up(common_info, module_data)
            return write_up
        
        return None
    
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