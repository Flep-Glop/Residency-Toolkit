import streamlit as st
from .templates import TemplateManager, ConfigManager

class SBRTModule:
    def __init__(self):
        """Initialize the SBRT module."""
        self.template_manager = TemplateManager()
        self.config_manager = ConfigManager()
        
        # Common treatment sites for SBRT
        self.treatment_sites = [
            "lung", "liver", "spine", "adrenal", "pancreas", 
            "kidney", "prostate", "lymph node", "bone", "oligometastasis"
        ]
        
        # Treatment machines
        self.treatment_machines = [
            "VersaHD", "TrueBeam", "Halcyon", "Ethos", "Radixact", "CyberKnife"
        ]
        
        # Common immobilization devices
        self.immobilization_devices = [
            "body fix", "vac-lok bag", "wing board", "S-frame", 
            "head and shoulder mask", "abdominal compression", "stereotactic body frame"
        ]
        
    def render_sbrt_form(self):
        """Render the form for SBRT write-ups."""
        st.subheader("SBRT Write-Up Generator")
        
        # Use tabs to organize the form
        physician_tab, patient_tab, treatment_tab, qa_tab = st.tabs([
            "Staff Information", "Patient Information", "Treatment Details", "QA Information"
        ])
        
        with physician_tab:
            # Staff information
            physician = st.selectbox("Physician Name", 
                                   self.config_manager.get_physicians(), 
                                   key="sbrt_physician")
            physicist = st.selectbox("Physicist Name", 
                                   self.config_manager.get_physicists(), 
                                   key="sbrt_physicist")
        
        with patient_tab:
            # Patient information
            col1, col2 = st.columns(2)
            
            with col1:
                patient_age = st.number_input("Patient Age", min_value=0, max_value=120, key="sbrt_age")
                patient_sex = st.selectbox("Patient Sex", ["male", "female", "other"], key="sbrt_sex")
            
            with col2:
                treatment_site = st.selectbox("Treatment Site", 
                                            sorted(self.treatment_sites),
                                            key="sbrt_site")
                
                # Option for custom site
                if treatment_site == "oligometastasis":
                    oligomet_location = st.text_input("Specify Oligometastasis Location", key="oligomet_location")
                    if oligomet_location:
                        treatment_site = f"oligometastatic {oligomet_location}"
                
            patient_details = f"a {patient_age}-year-old {patient_sex} with a {treatment_site} lesion"
        
        with treatment_tab:
            # Treatment planning details
            col1, col2 = st.columns(2)
            
            with col1:
                dose = st.number_input("Prescription Dose (Gy)", min_value=0.0, value=50.0, step=0.1, key="sbrt_dose")
                fractions = st.number_input("Number of Fractions", min_value=1, max_value=10, value=5, key="sbrt_fractions")
                
                # Motion management
                st.markdown("#### Motion Management")
                motion_management = st.multiselect(
                    "Motion Management Techniques", 
                    ["4DCT", "Abdominal Compression", "Breath Hold", "Gating", "Tracking", "None"],
                    default=["4DCT"],
                    key="motion_management"
                )
                
                # 4DCT specific options
                if "4DCT" in motion_management:
                    target_phase = st.radio(
                        "Target Phase", 
                        ["Maximum Intensity Projection (MIP)", "Average Intensity Projection (AIP)", "Specific Phase"],
                        key="target_phase"
                    )
                    
                    if target_phase == "Specific Phase":
                        specific_phase = st.slider("Phase (%)", 0, 90, 50, 10, key="specific_phase")
                        target_phase = f"{specific_phase}% phase"
            
            with col2:
                # Equipment details
                treatment_machine = st.selectbox("Treatment Machine", 
                                               self.treatment_machines,
                                               key="sbrt_machine")
                
                immobilization_device = st.selectbox("Immobilization Device", 
                                                   sorted(self.immobilization_devices),
                                                   key="sbrt_immobilization")
                
                # Treatment planning
                st.markdown("#### Treatment Planning")
                planning_technique = st.selectbox(
                    "Planning Technique",
                    ["VMAT", "IMRT", "3D Conformal", "Dynamic Conformal Arc"],
                    key="planning_technique"
                )
                
                # Image guidance
                image_guidance = st.multiselect(
                    "Image Guidance",
                    ["kV-CBCT", "MV-CBCT", "Stereoscopic X-ray", "Surface Guidance", "Fiducial Markers"],
                    default=["kV-CBCT"],
                    key="image_guidance"
                )
                
                if "Fiducial Markers" in image_guidance:
                    fiducial_type = st.text_input("Fiducial Marker Type", key="fiducial_type")
        
        with qa_tab:
            # QA Information
            col1, col2 = st.columns(2)
            
            with col1:
                # PTV coverage
                ptv_coverage = st.slider("PTV Coverage (%)", 90, 100, 95, key="ptv_coverage")
                
                # Plan quality metrics
                st.markdown("#### Plan Quality Metrics")
                pitv = st.number_input("PITV (Vpres iso / VPTV)", 
                                     min_value=0.0, 
                                     max_value=2.0, 
                                     value=1.0, 
                                     step=0.01,
                                     key="pitv")
                
                r50 = st.number_input("R50 (Vol50% pres iso / VolPTV)", 
                                    min_value=0.0, 
                                    max_value=10.0, 
                                    value=3.5, 
                                    step=0.1,
                                    key="r50")
            
            with col2:
                # QA specifics
                st.markdown("#### QA Measurements")
                qa_performed = st.checkbox("QA Performed", value=True, key="qa_performed")
                
                if qa_performed:
                    qa_method = st.selectbox(
                        "QA Method", 
                        ["ArcCHECK", "MapCHECK", "Portal Dosimetry", "Film", "Ion Chamber"],
                        key="qa_method"
                    )
                    
                    gamma_criteria = st.selectbox(
                        "Gamma Analysis Criteria",
                        ["3%/3mm", "2%/2mm", "3%/2mm", "2%/1mm"],
                        key="gamma_criteria"
                    )
                    
                    passing_rate = st.slider("Passing Rate (%)", 90, 100, 97, key="passing_rate")
        
        # Generate button
        generate_pressed = st.button("Generate Write-Up", type="primary", key="sbrt_generate")
        
        # Check if we have all required information and the button was pressed
        required_fields = [physician, physicist, patient_age, treatment_site, dose, fractions]
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
            if fractions == 0:
                missing_fields.append("Number of Fractions")
                
            for field in missing_fields:
                st.warning(f"Missing required field: {field}")
                
            return None
        
        # If all required fields are filled and button is pressed, generate the write-up
        if generate_pressed and all_fields_filled:
            # Format motion management text
            motion_text = self._format_motion_management(motion_management, target_phase if "4DCT" in motion_management else None)
            
            # Format image guidance text
            imaging_text = self._format_image_guidance(image_guidance, fiducial_type if "Fiducial Markers" in image_guidance else None)
            
            # QA text
            if qa_performed:
                qa_text = self._format_qa_text(qa_method, gamma_criteria, passing_rate)
            else:
                qa_text = "A quality assurance plan is scheduled to be delivered to verify the treatment plan accuracy."
            
            # Generate the write-up
            write_up = self._generate_sbrt_write_up(
                physician=physician,
                physicist=physicist,
                patient_details=patient_details,
                treatment_site=treatment_site,
                dose=dose,
                fractions=fractions,
                treatment_machine=treatment_machine,
                immobilization_device=immobilization_device,
                planning_technique=planning_technique,
                motion_text=motion_text,
                imaging_text=imaging_text,
                ptv_coverage=ptv_coverage,
                pitv=pitv,
                r50=r50,
                qa_text=qa_text
            )
            
            return write_up
        
        return None
    
    def _format_motion_management(self, motion_management, target_phase):
        """Format the motion management section of the write-up."""
        if not motion_management or "None" in motion_management:
            return "The patient was scanned in our CT simulator in the treatment position without specific motion management."
        
        motion_text = "The patient was scanned in our CT simulator in the treatment position. "
        
        if "4DCT" in motion_management:
            motion_text += f"A 4D kVCT simulation scan was performed with the patient immobilized to assess respiratory motion. "
            motion_text += f"Using the 4D dataset, a {target_phase} CT image set was reconstructed to generate an ITV "
            motion_text += "that encompasses the motion envelope of the target. "
        
        if "Abdominal Compression" in motion_management:
            motion_text += "Abdominal compression was applied to restrict diaphragmatic motion and reduce target movement. "
            
        if "Breath Hold" in motion_management:
            motion_text += "The patient was coached to reproducibly hold their breath during imaging and treatment to minimize respiratory motion. "
            
        if "Gating" in motion_management:
            motion_text += "Respiratory gating was employed to synchronize radiation delivery with specific phases of the breathing cycle. "
            
        if "Tracking" in motion_management:
            motion_text += "Real-time tumor tracking was implemented to dynamically follow target motion during treatment. "
            
        return motion_text
    
    def _format_image_guidance(self, image_guidance, fiducial_type):
        """Format the image guidance section of the write-up."""
        if not image_guidance:
            return "Image guidance will be performed before each treatment fraction to ensure accurate patient positioning."
        
        imaging_text = "Patient positioning verification will be performed before each treatment fraction using "
        
        guidance_descriptions = []
        
        if "kV-CBCT" in image_guidance:
            guidance_descriptions.append("kilovoltage cone-beam CT")
            
        if "MV-CBCT" in image_guidance:
            guidance_descriptions.append("megavoltage cone-beam CT")
            
        if "Stereoscopic X-ray" in image_guidance:
            guidance_descriptions.append("stereoscopic X-ray imaging")
            
        if "Surface Guidance" in image_guidance:
            guidance_descriptions.append("optical surface monitoring")
            
        if "Fiducial Markers" in image_guidance:
            if fiducial_type:
                guidance_descriptions.append(f"{fiducial_type} fiducial markers")
            else:
                guidance_descriptions.append("implanted fiducial markers")
        
        # Format the list properly with commas and "and"
        if len(guidance_descriptions) == 1:
            imaging_text += guidance_descriptions[0]
        elif len(guidance_descriptions) == 2:
            imaging_text += f"{guidance_descriptions[0]} and {guidance_descriptions[1]}"
        else:
            imaging_text += ", ".join(guidance_descriptions[:-1]) + f", and {guidance_descriptions[-1]}"
        
        imaging_text += " to ensure accurate target localization and patient positioning."
        
        return imaging_text
    
    def _format_qa_text(self, qa_method, gamma_criteria, passing_rate):
        """Format the QA section of the write-up."""
        qa_text = f"A quality assurance plan was developed and delivered to a {qa_method} phantom to verify "
        qa_text += "the accuracy of the radiation treatment plan. Measurements within the phantom were obtained "
        qa_text += "and compared against the calculated plan using gamma analysis with "
        qa_text += f"{gamma_criteria} criteria. The analysis showed a passing rate of {passing_rate}%, "
        qa_text += "indicating good agreement between the plan and measurements."
        
        return qa_text
    
    def _generate_sbrt_write_up(self, physician, physicist, patient_details, treatment_site, 
                              dose, fractions, treatment_machine, immobilization_device,
                              planning_technique, motion_text, imaging_text, ptv_coverage,
                              pitv, r50, qa_text):
        """Generate the SBRT write-up based on the inputs."""
        
        write_up = f"Dr. {physician} requested a medical physics consultation for a 4D CT simulation study "
        write_up += f"and SBRT delivery for {patient_details}. Dr. {physician} has elected to treat with a "
        write_up += "stereotactic body radiotherapy (SBRT) technique by means of the Pinnacle treatment planning "
        write_up += f"system in conjunction with the {treatment_machine} linear accelerator equipped with the "
        write_up += "kV-CBCT system.\n\n"
        
        # Motion management section
        write_up += f"{motion_text} Both the prescribing radiation oncologist and radiation oncology physicist "
        write_up += "evaluated and approved the patient setup. "
        
        if "4DCT" in motion_text:
            write_up += "Dr. {physician} segmented and approved both the PTVs and OARs.\n\n"
        else:
            write_up += "The patient was immobilized using a customized "
            write_up += f"{immobilization_device} to limit motion during treatment and aid in inter-fractional repositioning. "
            write_up += "Dr. {physician} segmented and approved both the PTVs and OARs.\n\n"
        
        # Treatment planning section
        write_up += f"In the treatment planning system, a {planning_technique} treatment plan was developed to "
        write_up += f"conformally deliver a prescribed dose of {dose} Gy in {fractions} fractions to the planning target volume. "
        write_up += "The treatment plan was inversely optimized such that the prescription isodose volume exactly matched "
        write_up += "the target volume in all three spatial dimensions and that the dose fell sharply away from the target volume. "
        write_up += f"The treatment plan covered {ptv_coverage}% of the PTV with the prescribed isodose volume. "
        write_up += f"The PITV (Vpres iso / VPTV) was {pitv:.2f} and the R50 (Vol50% pres iso / VolPTV) was {r50:.2f}. "
        write_up += "Normal tissue dose constraints for critical organs associated with the treatment site were reviewed.\n\n"
        
        # Image guidance section
        write_up += f"{imaging_text}\n\n"
        
        # QA section
        write_up += f"{qa_text} Calculations and data analysis were reviewed and approved by both the "
        write_up += f"prescribing radiation oncologist, Dr. {physician}, and the radiation oncology physicist, Dr. {physicist}."
        
        return write_up
    
    def display_write_up(self, write_up):
        """Display the generated write-up with a copy button."""
        if write_up:
            st.markdown("### Generated Write-Up")
            
            # Create a container with custom styling for better visibility
            with st.container():
                # Display in text area for viewing/editing
                st.text_area("", write_up, height=300, key="sbrt_result", label_visibility="collapsed")
                
                # Add a tooltip with copy instructions
                st.info("💡 To copy: Click inside the text box, use Ctrl+A (or Cmd+A on Mac) to select all, then Ctrl+C (or Cmd+C) to copy.")
                
                # Optional: Add download button
                st.download_button(
                    label="Download as Text File",
                    data=write_up,
                    file_name="sbrt_write_up.txt",
                    mime="text/plain"
                )