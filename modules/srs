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
        
        # Treatment machines
        self.treatment_machines = [
            "VersaHD", "TrueBeam", "Gamma Knife", "CyberKnife", "Radixact", "Ethos"
        ]
        
        # Common immobilization devices
        self.immobilization_devices = [
            "thermoplastic mask", "head frame", "frameless mask system",
            "BrainLAB mask", "SRS frame", "double-shell positioning system"
        ]
        
    def render_srs_form(self):
        """Render the form for SRS write-ups."""
        st.subheader("SRS Write-Up Generator")
        
        # Use tabs to organize the form
        physician_tab, patient_tab, treatment_tab, qa_tab = st.tabs([
            "Staff Information", "Patient Information", "Treatment Details", "QA Information"
        ])
        
        with physician_tab:
            # Staff information
            physician = st.selectbox("Physician Name", 
                                   self.config_manager.get_physicians(), 
                                   key="srs_physician")
            physicist = st.selectbox("Physicist Name", 
                                   self.config_manager.get_physicists(), 
                                   key="srs_physicist")
        
        with patient_tab:
            # Patient information
            col1, col2 = st.columns(2)
            
            with col1:
                patient_age = st.number_input("Patient Age", min_value=0, max_value=120, key="srs_age")
                patient_sex = st.selectbox("Patient Sex", ["male", "female", "other"], key="srs_sex")
            
            with col2:
                treatment_site = st.selectbox("Treatment Site", 
                                            sorted(self.treatment_sites),
                                            key="srs_site")
                
                # Option for multiple mets
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
                # Single vs. multi-fraction
                is_single_fraction = st.radio(
                    "Treatment Fractionation",
                    ["Single Fraction (SRS)", "Multiple Fractions (SRT)"],
                    key="is_single_fraction"
                )
                
                if is_single_fraction == "Single Fraction (SRS)":
                    dose = st.number_input("Prescription Dose (Gy)", min_value=0.0, value=18.0, step=0.5, key="srs_dose")
                    fractions = 1
                else:
                    dose = st.number_input("Prescription Dose (Gy)", min_value=0.0, value=25.0, step=0.5, key="srs_dose")
                    fractions = st.number_input("Number of Fractions", min_value=2, max_value=10, value=5, key="srs_fractions")
                
                # Target volume
                target_volume = st.number_input("Target Volume (cc)", min_value=0.01, value=3.5, step=0.1, key="target_volume")
                
                # Prescription isodose
                prescription_isodose = st.slider("Prescription Isodose (%)", 50, 100, 80, key="prescription_isodose")
                
            with col2:
                # Equipment details
                treatment_machine = st.selectbox("Treatment Machine", 
                                               self.treatment_machines,
                                               key="srs_machine")
                
                immobilization_device = st.selectbox("Immobilization Device", 
                                                   sorted(self.immobilization_devices),
                                                   key="srs_immobilization")
                
                # Treatment planning
                planning_technique = st.selectbox(
                    "Planning Technique",
                    ["VMAT", "Dynamic Conformal Arc", "Cones", "IMRT", "HyperArc"],
                    key="srs_planning_technique"
                )
                
                # Image fusion
                image_fusion = st.multiselect(
                    "Image Fusion",
                    ["MRI T1 with contrast", "MRI T1 without contrast", "MRI T2", "MRI FLAIR", "CT", "PET/CT"],
                    default=["MRI T1 with contrast"],
                    key="image_fusion"
                )
                
                # Image guidance
                image_guidance = st.multiselect(
                    "Image Guidance",
                    ["kV-CBCT", "MV-CBCT", "Stereoscopic X-ray", "Surface Guidance"],
                    default=["kV-CBCT"],
                    key="srs_image_guidance"
                )
        
        with qa_tab:
            # QA Information
            col1, col2 = st.columns(2)
            
            with col1:
                # Conformity metrics
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
                
                ptv_coverage = st.slider("PTV Coverage (%)", 90, 100, 98, key="srs_ptv_coverage")
            
            with col2:
                # QA specifics
                st.markdown("#### QA Measurements")
                qa_performed = st.checkbox("QA Performed", value=True, key="srs_qa_performed")
                
                if qa_performed:
                    qa_method = st.selectbox(
                        "QA Method", 
                        ["SRS MapCHECK", "Film", "Pinpoint Ion Chamber", "SRS ArcCHECK", "Polymer Gel"],
                        key="srs_qa_method"
                    )
                    
                    gamma_criteria = st.selectbox(
                        "Gamma Analysis Criteria",
                        ["3%/1mm", "2%/2mm", "3%/2mm", "2%/1mm", "1%/1mm"],
                        index=4,
                        key="srs_gamma_criteria"
                    )
                    
                    passing_rate = st.slider("Passing Rate (%)", 90, 100, 98, key="srs_passing_rate")
                    
                # Critical structures
                st.markdown("#### Critical Structure Doses")
                include_critical_doses = st.checkbox("Include Critical Structure Doses", value=False, key="include_critical_doses")
                
                if include_critical_doses:
                    brain_stem_dose = st.number_input("Brain Stem Max Dose (Gy)", 
                                                    min_value=0.0, 
                                                    max_value=25.0, 
                                                    value=12.0, 
                                                    step=0.1,
                                                    key="brain_stem_dose")
                    
                    optic_chiasm_dose = st.number_input("Optic Chiasm Max Dose (Gy)", 
                                                      min_value=0.0, 
                                                      max_value=25.0, 
                                                      value=8.0, 
                                                      step=0.1,
                                                      key="optic_chiasm_dose")
                    
                    optic_nerve_dose = st.number_input("Optic Nerve Max Dose (Gy)", 
                                                     min_value=0.0, 
                                                     max_value=25.0, 
                                                     value=8.0, 
                                                     step=0.1,
                                                     key="optic_nerve_dose")
        
        # Generate button
        generate_pressed = st.button("Generate Write-Up", type="primary", key="srs_generate")
        
        # Check if we have all required information and the button was pressed
        required_fields = [physician, physicist, patient_age, treatment_site, dose]
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
            if dose == 0:
                missing_fields.append("Prescription Dose")
                
            for field in missing_fields:
                st.warning(f"Missing required field: {field}")
                
            return None
        
        # If all required fields are filled and button is pressed, generate the write-up
        if generate_pressed and all_fields_filled:
            # Format treatment type
            treatment_type = "stereotactic radiosurgery (SRS)" if is_single_fraction == "Single Fraction (SRS)" else "stereotactic radiotherapy (SRT)"
            
            # Format image fusion text
            fusion_text = self._format_image_fusion(image_fusion)
            
            # Format image guidance text
            imaging_text = self._format_image_guidance(image_guidance)
            
            # Format critical structure doses
            critical_doses_text = ""
            if include_critical_doses:
                critical_doses_text = self._format_critical_doses(brain_stem_dose, optic_chiasm_dose, optic_nerve_dose)
            
            # QA text
            if qa_performed:
                qa_text = self._format_qa_text(qa_method, gamma_criteria, passing_rate)
            else:
                qa_text = "A quality assurance plan is scheduled to be delivered to verify the treatment plan accuracy."
            
            # Generate the write-up
            write_up = self._generate_srs_write_up(
                physician=physician,
                physicist=physicist,
                patient_details=patient_details,
                treatment_site=treatment_site,
                treatment_type=treatment_type,
                dose=dose,
                fractions=fractions,
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
    
    def _format_image_fusion(self, image_fusion):
        """Format the image fusion section of the write-up."""
        if not image_fusion:
            return "Planning was performed using the simulation CT images."
        
        fusion_text = "Image fusion was performed with "
        
        fusion_descriptions = []
        
        if "MRI T1 with contrast" in image_fusion:
            fusion_descriptions.append("T1-weighted MRI with contrast")
            
        if "MRI T1 without contrast" in image_fusion:
            fusion_descriptions.append("T1-weighted MRI without contrast")
            
        if "MRI T2" in image_fusion:
            fusion_descriptions.append("T2-weighted MRI")
            
        if "MRI FLAIR" in image_fusion:
            fusion_descriptions.append("FLAIR MRI")
            
        if "CT" in image_fusion and len(image_fusion) > 1:  # Only add if there are other modalities
            fusion_descriptions.append("diagnostic CT")
            
        if "PET/CT" in image_fusion:
            fusion_descriptions.append("PET/CT")
        
        # Format the list properly with commas and "and"
        if len(fusion_descriptions) == 1:
            fusion_text += fusion_descriptions[0]
        elif len(fusion_descriptions) == 2:
            fusion_text += f"{fusion_descriptions[0]} and {fusion_descriptions[1]}"
        else:
            fusion_text += ", ".join(fusion_descriptions[:-1]) + f", and {fusion_descriptions[-1]}"
        
        fusion_text += " to aid in target delineation and critical structure identification."
        
        return fusion_text
    
    def _format_image_guidance(self, image_guidance):
        """Format the image guidance section of the write-up."""
        if not image_guidance:
            return "Image guidance will be performed before treatment to ensure accurate patient positioning."
        
        imaging_text = "Patient positioning verification will be performed before treatment using "
        
        guidance_descriptions = []
        
        if "kV-CBCT" in image_guidance:
            guidance_descriptions.append("kilovoltage cone-beam CT")
            
        if "MV-CBCT" in image_guidance:
            guidance_descriptions.append("megavoltage cone-beam CT")
            
        if "Stereoscopic X-ray" in image_guidance:
            guidance_descriptions.append("stereoscopic X-ray imaging")
            
        if "Surface Guidance" in image_guidance:
            guidance_descriptions.append("optical surface monitoring")
        
        # Format the list properly with commas and "and"
        if len(guidance_descriptions) == 1:
            imaging_text += guidance_descriptions[0]
        elif len(guidance_descriptions) == 2:
            imaging_text += f"{guidance_descriptions[0]} and {guidance_descriptions[1]}"
        else:
            imaging_text += ", ".join(guidance_descriptions[:-1]) + f", and {guidance_descriptions[-1]}"
        
        imaging_text += " to ensure accurate target localization and patient positioning."
        
        return imaging_text
    
    def _format_critical_doses(self, brain_stem_dose, optic_chiasm_dose, optic_nerve_dose):
        """Format the critical structure doses section of the write-up."""
        doses_text = "\n\nMaximum doses to critical structures were as follows: "
        doses_text += f"brain stem {brain_stem_dose:.1f} Gy, "
        doses_text += f"optic chiasm {optic_chiasm_dose:.1f} Gy, "
        doses_text += f"and optic nerves {optic_nerve_dose:.1f} Gy. "
        doses_text += "All critical structure doses were within protocol-specified constraints."
        
        return doses_text
    
    def _format_qa_text(self, qa_method, gamma_criteria, passing_rate):
        """Format the QA section of the write-up."""
        qa_text = f"A quality assurance plan was developed and delivered to a {qa_method} to verify "
        qa_text += "the accuracy of the radiation treatment plan. Measurements were obtained "
        qa_text += "and compared against the calculated plan using gamma analysis with "
        qa_text += f"{gamma_criteria} criteria. The analysis showed a passing rate of {passing_rate}%, "
        qa_text += "indicating excellent agreement between the plan and measurements."
        
        return qa_text
    
    def _generate_srs_write_up(self, physician, physicist, patient_details, treatment_site, 
                             treatment_type, dose, fractions, treatment_machine, 
                             immobilization_device, planning_technique, prescription_isodose,
                             target_volume, ptv_coverage, conformity_index, gradient_index,
                             fusion_text, imaging_text, critical_doses_text, qa_text):
        """Generate the SRS write-up based on the inputs."""
        
        # Determine treatment string based on fractions
        if fractions == 1:
            dose_fractions_text = f"{dose} Gy in a single fraction"
        else:
            dose_fractions_text = f"{dose} Gy in {fractions} fractions"
        
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