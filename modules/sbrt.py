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
        
    def render_sbrt_form(self):
        """Render the form for SBRT write-ups."""
        st.subheader("SBRT Write-Up Generator")
        
        # Use condensed tabs to organize the form
        basic_tab, treatment_tab = st.tabs([
            "Basic Information", "Treatment Details"
        ])
        
        with basic_tab:
            # Staff information
            st.markdown("#### Staff Information")
            physician = st.selectbox("Physician Name", 
                                   self.config_manager.get_physicians(), 
                                   key="sbrt_physician")
            physicist = st.selectbox("Physicist Name", 
                                   self.config_manager.get_physicists(), 
                                   key="sbrt_physicist")
        
            # Patient information
            st.markdown("#### Patient Information")
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
                
                # Simplified motion management - just 4DCT yes/no
                is_4dct = st.radio(
                    "Use 4DCT for motion management?",
                    ["Yes", "No"],
                    key="is_4dct"
                )
            
            with col2:
                # Target volume
                target_volume = st.number_input("Target Volume (cc)", min_value=0.01, value=3.5, step=0.1, key="target_volume")
                
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
            # Default values for removed form fields
            treatment_machine = "linear accelerator"
            immobilization_device = "custom immobilization device"
            planning_technique = "VMAT"
            
            # Format motion management text based on 4DCT selection
            if is_4dct == "Yes":
                motion_text = "The patient was scanned in our CT simulator in the treatment position. "
                motion_text += "A 4D kVCT simulation scan was performed with the patient immobilized to assess respiratory motion. "
                motion_text += "Using the 4D dataset, a Maximum Intensity Projection (MIP) CT image set was reconstructed to generate an ITV "
                motion_text += "that encompasses the motion envelope of the target."
            else:
                motion_text = "The patient was scanned in our CT simulator in the treatment position without specific motion management. "
                motion_text += "The patient was immobilized using a customized immobilization device to limit motion during treatment and aid in inter-fractional repositioning."
            
            # Standard image guidance text
            imaging_text = "Patient positioning verification will be performed before each treatment fraction using "
            imaging_text += "kilovoltage cone-beam CT to ensure accurate target localization and patient positioning."
            
            # Standard QA text
            qa_text = "A quality assurance plan was developed and delivered to verify "
            qa_text += "the accuracy of the radiation treatment plan. Measurements within the phantom were obtained "
            qa_text += "and compared against the calculated plan, showing good agreement between the plan and measurements."
            
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
                qa_text=qa_text,
                target_volume=target_volume
            )
            
            return write_up
        
        return None
    
    def _generate_sbrt_write_up(self, physician, physicist, patient_details, treatment_site, 
                              dose, fractions, treatment_machine, immobilization_device,
                              planning_technique, motion_text, imaging_text, ptv_coverage,
                              pitv, r50, qa_text, target_volume):
        """Generate the SBRT write-up based on the inputs."""
        
        write_up = f"Dr. {physician} requested a medical physics consultation for a 4D CT simulation study "
        write_up += f"and SBRT delivery for {patient_details}. Dr. {physician} has elected to treat with a "
        write_up += "stereotactic body radiotherapy (SBRT) technique by means of the Pinnacle treatment planning "
        write_up += f"system in conjunction with the {treatment_machine} equipped with the "
        write_up += "kV-CBCT system.\n\n"
        
        # Motion management section
        write_up += f"{motion_text} Both the prescribing radiation oncologist and radiation oncology physicist "
        write_up += "evaluated and approved the patient setup. "
        write_up += "Dr. {physician} segmented and approved both the PTVs and OARs.\n\n"
        
        # Treatment planning section
        write_up += f"In the treatment planning system, a {planning_technique} treatment plan was developed to "
        write_up += f"conformally deliver a prescribed dose of {dose} Gy in {fractions} fractions to the planning target volume. "
        write_up += "The treatment plan was inversely optimized such that the prescription isodose volume exactly matched "
        write_up += f"the target volume of {target_volume:.2f} cc in all three spatial dimensions and that the dose fell sharply away from the target volume. "
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