import streamlit as st
from .templates import TemplateManager, ConfigManager

class SRSModule:
    def __init__(self):
        """Initialize the SRS module."""
        self.template_manager = TemplateManager()
        self.config_manager = ConfigManager()
        
        # Common treatment sites for SRS
        self.treatment_sites = [
            "brain metastasis", "acoustic neuroma", "meningioma", "pituitary adenoma", 
            "trigeminal neuralgia", "arteriovenous malformation", "glioma", 
            "vestibular schwannoma", "multiple brain metastases", "skull base tumor"
        ]
        
    def render_srs_form(self):
        """Render the form for SRS write-ups."""
        st.subheader("SRS Write-Up Generator")
        
        # Use condensed tabs to organize the form
        basic_tab, treatment_tab = st.tabs([
            "Basic Information", "Treatment Details"
        ])
        
        with basic_tab:
            # Staff information
            st.markdown("#### Staff Information")
            physician = st.selectbox("Physician Name", 
                                   self.config_manager.get_physicians(), 
                                   key="srs_physician")
            physicist = st.selectbox("Physicist Name", 
                                   self.config_manager.get_physicists(), 
                                   key="srs_physicist")
        
            # Patient information
            st.markdown("#### Patient Information")
            col1, col2 = st.columns(2)
            
            with col1:
                patient_age = st.number_input("Patient Age", min_value=0, max_value=120, key="srs_age")
                patient_sex = st.selectbox("Patient Sex", ["male", "female", "other"], key="srs_sex")
            
            with col2:
                treatment_site = st.selectbox("Treatment Site", 
                                            sorted(self.treatment_sites),
                                            key="srs_site")
                
                # Option for multiple mets with number specification
                if "multiple brain metastases" in treatment_site:
                    lesion_count = st.number_input("Number of Lesions", min_value=2, max_value=20, value=3, key="lesion_count")
                    treatment_site = f"{lesion_count} brain metastases"
                
                # Option for custom site
                custom_site = st.checkbox("Custom Site Description", key="custom_site")
                if custom_site:
                    custom_site_text = st.text_input("Enter Custom Site", key="custom_site_text")
                    if custom_site_text:
                        treatment_site = custom_site_text
                
            patient_details = f"a {patient_age}-year-old {patient_sex} with {treatment_site}"
        
        with treatment_tab:
            # Treatment planning details
            col1, col2 = st.columns(2)
            
            with col1:
                # SRS vs. SRT option
                treatment_type = st.radio(
                    "Treatment Type",
                    ["SRS (Single Fraction)", "SRT (Multiple Fractions)", "SRS+SRT (Combined)"],
                    key="treatment_type"
                )
                
                if treatment_type == "SRS (Single Fraction)":
                    dose = st.number_input("Prescription Dose (Gy)", min_value=0.0, value=18.0, step=0.1, key="srs_dose")
                    fractions = 1
                elif treatment_type == "SRT (Multiple Fractions)":
                    dose = st.number_input("Prescription Dose (Gy)", min_value=0.0, value=25.0, step=0.1, key="srs_dose")
                    fractions = st.number_input("Number of Fractions", min_value=2, max_value=10, value=5, key="srs_fractions")
                else:  # Combined
                    dose_srs = st.number_input("SRS Prescription Dose (Gy)", min_value=0.0, value=18.0, step=0.1, key="srs_dose_single")
                    dose_srt = st.number_input("SRT Prescription Dose (Gy)", min_value=0.0, value=25.0, step=0.1, key="srs_dose_multi")
                    fractions_srt = st.number_input("SRT Number of Fractions", min_value=2, max_value=10, value=5, key="srs_fractions_multi")
                    # For the template we'll use the SRS dose, but note both in the write-up
                    dose = dose_srs
                    fractions = 1
                
                # Target volume
                target_volume = st.number_input("Target Volume (cc)", min_value=0.01, value=3.5, step=0.1, key="target_volume")
            
            with col2:
                # Prescription isodose
                prescription_isodose = st.slider("Prescription Isodose (%)", 50, 100, 80, key="prescription_isodose")
                
                # PTV coverage
                ptv_coverage = st.slider("PTV Coverage (%)", 90, 100, 98, key="srs_ptv_coverage")
                
                # Plan quality metrics
                st.markdown("#### Plan Quality Metrics")
                conformity_index = st.number_input("Conformity Index", 
                                                min_value=0.0, 
                                                max_value=3.0, 
                                                value=1.2, 
                                                step=0.01,
                                                key="conformity_index")
                
                gradient_index = st.number_input("Gradient Index", 
                                               min_value=0.0, 
                                               max_value=10.0, 
                                               value=3.0, 
                                               step=0.1,
                                               key="gradient_index")
        
        # Generate button
        generate_pressed = st.button("Generate Write-Up", type="primary", key="srs_generate")
        
        # Check if we have all required information and the button was pressed
        required_fields = [physician, physicist, patient_age, treatment_site]
        
        # Check dose fields based on treatment type
        if treatment_type == "SRS+SRT (Combined)":
            required_fields.extend([dose_srs, dose_srt, fractions_srt])
        else:
            required_fields.append(dose)
            if treatment_type == "SRT (Multiple Fractions)":
                required_fields.append(fractions)
        
        all_fields_filled = all(str(field) != "" and str(field) != "0" for field in required_fields)
        
        # Show missing fields if any
        if generate_pressed and not all_fields_filled:
            st.error("Please fill in all required fields before generating the write-up.")
            missing_fields = []
            if not physician:
                missing_fields.append("Physician Name")
            if not physicist:
                missing_fields.append("Physicist Name")
            if patient_age == 0:
                missing_fields.append("Patient Age")
            if not treatment_site:
                missing_fields.append("Treatment Site")
                
            # Check dose fields based on treatment type
            if treatment_type == "SRS+SRT (Combined)":
                if dose_srs == 0:
                    missing_fields.append("SRS Prescription Dose")
                if dose_srt == 0:
                    missing_fields.append("SRT Prescription Dose")
                if fractions_srt == 0:
                    missing_fields.append("SRT Number of Fractions")
            else:
                if dose == 0:
                    missing_fields.append("Prescription Dose")
                if treatment_type == "SRT (Multiple Fractions)" and fractions == 0:
                    missing_fields.append("Number of Fractions")
                
            for field in missing_fields:
                st.warning(f"Missing required field: {field}")
                
            return None
        
        # If all required fields are filled and button is pressed, generate the write-up
        if generate_pressed and all_fields_filled:
            # Default values for removed form fields
            treatment_machine = "linear accelerator"
            immobilization_device = "thermoplastic mask"
            planning_technique = "VMAT"
            
            # Format treatment type
            if treatment_type == "SRS (Single Fraction)":
                treatment_type_text = "stereotactic radiosurgery (SRS)"
                dose_fractions_text = f"{dose} Gy in a single fraction"
            elif treatment_type == "SRT (Multiple Fractions)":
                treatment_type_text = "stereotactic radiotherapy (SRT)"
                dose_fractions_text = f"{dose} Gy in {fractions} fractions"
            else:  # Combined
                treatment_type_text = "combined stereotactic radiosurgery (SRS) and stereotactic radiotherapy (SRT)"
                dose_fractions_text = f"{dose_srs} Gy in a single fraction for SRS and {dose_srt} Gy in {fractions_srt} fractions for SRT"
            
            # Fixed image fusion text
            fusion_text = "Image fusion was performed with T1-weighted MRI with contrast to aid in target delineation and critical structure identification."
            
            # Fixed image guidance text
            imaging_text = "Patient positioning verification will be performed before treatment using kilovoltage cone-beam CT to ensure accurate target localization and patient positioning."
            
            # Fixed critical structure doses text
            critical_doses_text = ""
            
            # Fixed QA text
            qa_text = "A quality assurance plan was developed and delivered to verify the accuracy of the radiation treatment plan. Measurements were obtained and compared against the calculated plan, showing good agreement between the plan and measurements."
            
            # Generate the write-up
            write_up = self._generate_srs_write_up(
                physician=physician,
                physicist=physicist,
                patient_details=patient_details,
                treatment_site=treatment_site,
                treatment_type=treatment_type_text,
                dose_fractions_text=dose_fractions_text,
                treatment_machine=treatment_machine,
                immobilization_device=immobilization_device,
                planning_technique=planning_technique,
                prescription_isodose=prescription_isodose,
                target_volume=target_volume,
                ptv_coverage=ptv_coverage,
                conformity_index=conformity_index,
                gradient_index=gradient_index,
                fusion_text=fusion_text,
                imaging_text=imaging_text,
                critical_doses_text=critical_doses_text,
                qa_text=qa_text
            )
            
            return write_up
        
        return None
    
    def _generate_srs_write_up(self, physician, physicist, patient_details, treatment_site, 
                             treatment_type, dose_fractions_text, treatment_machine, 
                             immobilization_device, planning_technique, prescription_isodose,
                             target_volume, ptv_coverage, conformity_index, gradient_index,
                             fusion_text, imaging_text, critical_doses_text, qa_text):
        """Generate the SRS write-up based on the inputs."""
        
        write_up = f"Dr. {physician} requested a medical physics consultation for {patient_details}. "
        write_up += f"Dr. {physician} has elected to treat with {treatment_type} using the "
        write_up += f"{treatment_machine} and {immobilization_device} for immobilization.\n\n"
        
        # Simulation and planning section
        write_up += "The patient was scanned in our CT simulator in the treatment position using a "
        write_up += f"{immobilization_device} to ensure reproducible patient positioning and minimize motion "
        write_up += f"during treatment. {fusion_text} The acquired images were transferred to the treatment "
        write_up += "planning system for target and critical structure delineation. "
        write_up += f"Dr. {physician} segmented and approved both the target volumes and organs at risk.\n\n"
        
        # Treatment planning section
        write_up += f"A {planning_technique} treatment plan was developed to deliver a prescribed dose of "
        write_up += f"{dose_fractions_text} to the target volume. The prescription was normalized to the "
        write_up += f"{prescription_isodose}% isodose line, providing optimal target coverage while minimizing "
        write_up += f"dose to surrounding normal tissues. The target volume was {target_volume:.2f} cc and "
        write_up += f"the plan achieved {ptv_coverage}% target coverage. The conformity index was {conformity_index:.2f} "
        write_up += f"and the gradient index was {gradient_index:.2f}, indicating a highly conformal dose distribution "
        write_up += f"with a steep dose gradient. {critical_doses_text}\n\n"
        
        # Image guidance section
        write_up += f"{imaging_text}\n\n"
        
        # QA section
        write_up += f"{qa_text} The treatment plan and quality assurance results were reviewed and approved by "
        write_up += f"both the prescribing radiation oncologist, Dr. {physician}, and the radiation oncology physicist, Dr. {physicist}."
        
        return write_up
    
    def display_write_up(self, write_up):
        """Display the generated write-up with a copy button."""
        if write_up:
            st.markdown("### Generated Write-Up")
            
            # Create a container with custom styling for better visibility
            with st.container():
                # Display in text area for viewing/editing
                st.text_area("", write_up, height=300, key="srs_result", label_visibility="collapsed")
                
                # Add a tooltip with copy instructions
                st.info("💡 To copy: Click inside the text box, use Ctrl+A (or Cmd+A on Mac) to select all, then Ctrl+C (or Cmd+C) to copy.")
                
                # Optional: Add download button
                st.download_button(
                    label="Download as Text File",
                    data=write_up,
                    file_name="srs_write_up.txt",
                    mime="text/plain"
                )