import streamlit as st
from .templates import ConfigManager

class SRSModule:
    def __init__(self):
        """Initialize the SRS module."""
        self.config_manager = ConfigManager()
        
        # Common treatment sites for SRS
        self.treatment_sites = [
            "brain metastasis", "acoustic neuroma", "meningioma", "pituitary adenoma", 
            "trigeminal neuralgia", "arteriovenous malformation", "glioma", 
            "vestibular schwannoma", "multiple brain metastases", "skull base tumor"
        ]
        
        # Treatment delivery systems
        self.treatment_systems = {
            "planning_systems": ["BrainLAB Elements", "Pinnacle", "Eclipse", "RayStation"],
            "accelerators": ["Versa HD", "TrueBeam", "Elekta Infinity", "CyberKnife"],
            "tracking_systems": ["ExacTrac", "Vision RT", "Catalyst HD", "X-ray imaging"]
        }
        
        # Immobilization devices
        self.immobilization_devices = [
            "rigid aquaplast head mask", 
            "thermoplastic mask", 
            "frameless stereotactic mask system",
            "SRS frame"
        ]
        
    def render_srs_form(self):
        """Render the form for SRS write-ups."""
        st.subheader("SRS Write-Up Generator")
        
        # Use tabs to organize the form
        basic_tab, treatment_tab, planning_tab = st.tabs([
            "Basic Information", "Treatment Details", "Planning Systems"
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
                
                # Target volume
                target_volume = st.number_input("Target Volume (cc)", min_value=0.01, value=1.5, step=0.1, key="target_volume")
            
            patient_details = f"a {patient_age}-year-old {patient_sex} with a {target_volume} cc lesion located in the {treatment_site}"
        
        with treatment_tab:
            # Treatment planning details
            col1, col2 = st.columns(2)
            
            with col1:
                # SRS vs. SRT option
                treatment_type = st.radio(
                    "Treatment Type",
                    ["SRS (Single Fraction)", "SRT (Multiple Fractions)"],
                    key="treatment_type"
                )
                
                if treatment_type == "SRS (Single Fraction)":
                    dose = st.number_input("Prescription Dose (Gy)", min_value=0.0, value=18.0, step=0.1, key="srs_dose")
                    fractions = 1
                else:  # SRT (Multiple Fractions)
                    dose = st.number_input("Prescription Dose (Gy)", min_value=0.0, value=25.0, step=0.1, key="srs_dose")
                    fractions = st.number_input("Number of Fractions", min_value=2, max_value=10, value=5, key="srs_fractions")
                
                # Image fusion options
                include_fusion = st.checkbox("Include MRI Fusion", value=True, key="include_fusion")
                if include_fusion:
                    mri_sequence = st.selectbox("MRI Sequence", 
                                              ["T1-weighted, post Gd contrast", "T2-weighted", "FLAIR", "DWI"], 
                                              key="mri_sequence")
            
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
                                               
                # Maximum dose
                max_dose = st.number_input("Maximum Dose (%)", 
                                         min_value=100, 
                                         max_value=200, 
                                         value=125, 
                                         step=1,
                                         key="max_dose")
        
        with planning_tab:
            col1, col2 = st.columns(2)
            
            with col1:
                planning_system = st.selectbox("Treatment Planning System", 
                                            self.treatment_systems["planning_systems"],
                                            key="planning_system")
                
                accelerator = st.selectbox("Linear Accelerator", 
                                         self.treatment_systems["accelerators"],
                                         key="accelerator")
                
                tracking_system = st.selectbox("Tracking/Positioning System", 
                                            self.treatment_systems["tracking_systems"],
                                            key="tracking_system")
            
            with col2:
                immobilization_device = st.selectbox("Immobilization Device", 
                                                   self.immobilization_devices,
                                                   key="immobilization_device")
                
                ct_slice_thickness = st.number_input("CT Slice Thickness (mm)", 
                                                  min_value=0.5, 
                                                  max_value=3.0, 
                                                  value=1.25, 
                                                  step=0.25,
                                                  key="ct_slice_thickness")
                
                # CT localization checkbox
                ct_localization = st.checkbox("CT Localization in Planning System", 
                                           value=True,
                                           key="ct_localization")
        
        # Generate button
        generate_pressed = st.button("Generate Write-Up", type="primary", key="srs_generate")
        
        # Check if we have all required information and the button was pressed
        required_fields = [physician, physicist, patient_age, treatment_site, dose]
        
        # Check fractions field based on treatment type
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
            if dose == 0:
                missing_fields.append("Prescription Dose")
            if treatment_type == "SRT (Multiple Fractions)" and fractions == 0:
                missing_fields.append("Number of Fractions")
                
            for field in missing_fields:
                st.warning(f"Missing required field: {field}")
                
            return None
        
        # If all required fields are filled and button is pressed, generate the write-up
        if generate_pressed and all_fields_filled:
            # Format treatment type
            if treatment_type == "SRS (Single Fraction)":
                treatment_type_text = "stereotactic radiosurgery (SRS)"
                fraction_text = "single fraction"
            else:  # SRT (Multiple Fractions)
                treatment_type_text = "stereotactic radiotherapy (SRT)"
                fraction_text = f"{fractions} fractions"
            
            # Generate the write-up
            write_up = self._generate_srs_write_up(
                physician=physician,
                physicist=physicist,
                patient_details=patient_details,
                treatment_site=treatment_site,
                treatment_type=treatment_type_text,
                fraction_text=fraction_text,
                dose=dose,
                fractions=fractions,
                planning_system=planning_system,
                accelerator=accelerator,
                tracking_system=tracking_system,
                immobilization_device=immobilization_device,
                ct_slice_thickness=ct_slice_thickness,
                include_fusion=include_fusion,
                mri_sequence=mri_sequence if include_fusion else "",
                ct_localization=ct_localization,
                prescription_isodose=prescription_isodose,
                ptv_coverage=ptv_coverage,
                conformity_index=conformity_index,
                gradient_index=gradient_index,
                max_dose=max_dose,
                target_volume=target_volume
            )
            
            return write_up
        
        return None
    
    def _generate_srs_write_up(self, physician, physicist, patient_details, treatment_site, 
                             treatment_type, fraction_text, dose, fractions, planning_system, 
                             accelerator, tracking_system, immobilization_device, ct_slice_thickness,
                             include_fusion, mri_sequence, ct_localization, prescription_isodose,
                             ptv_coverage, conformity_index, gradient_index, max_dose, target_volume):
        """Generate the SRS write-up based on the inputs, following the requested format."""
        
        # First paragraph - consultation request
        fusion_text = "an MRI image fusion and " if include_fusion else ""
        write_up = f"Dr. {physician} requested a medical physics consultation for --- for {fusion_text}{treatment_type}. "
        write_up += f"The patient is {patient_details}. "
        write_up += f"Dr. {physician} has elected to treat with a {treatment_type} technique "
        write_up += f"by means of the {planning_system} treatment planning system in conjunction with the "
        write_up += f"{accelerator} linear accelerator equipped with the {tracking_system} system.\n\n"
        
        # Second paragraph - immobilization and imaging
        write_up += f"Days before radiation delivery, a {immobilization_device} was constructed of the patient and was then "
        write_up += f"fixated onto a stereotactic carbon fiber frame base. Dr. {physician} was present to verify correct "
        write_up += f"construction of the head mask. A high resolution CT scan ({ct_slice_thickness}mm slice thickness) was then acquired. "
        
        # MRI fusion paragraph (if included)
        if include_fusion:
            write_up += f"In addition, a previous high resolution MR image set ({mri_sequence} scan) was acquired. "
            write_up += f"The MR images and CT images were fused within the {planning_system} treatment planning system platform "
            write_up += f"where a rigid body fusion was performed. "
        
        # CT localization (if included)
        if ct_localization:
            write_up += f"CT images were also localized in {planning_system}. "
        
        # Approval statement
        write_up += f"Fusion and structure segmentation were reviewed by Dr. {physician} and Dr. {physicist}.\n\n"
        
        # Treatment planning section
        write_up += f"A radiotherapy treatment plan was developed to deliver the prescribed dose to the periphery of the lesion. "
        write_up += f"The treatment plan was optimized such that the prescription isodose volume geometrically matched "
        write_up += f"the planning target volume (PTV) and that the lower isodose volumes spared the healthy brain tissue. "
        write_up += f"The following table summarizes the plan parameters:\n\n"
        
        # Table of plan parameters
        write_up += f"| Parameter | Value |\n"
        write_up += f"|-----------|-------|\n"
        write_up += f"| Prescription Dose | {dose} Gy in {fraction_text} |\n"
        write_up += f"| Target Volume | {target_volume} cc |\n"
        write_up += f"| Prescription Isodose | {prescription_isodose}% |\n"
        write_up += f"| PTV Coverage | {ptv_coverage}% |\n"
        write_up += f"| Conformity Index | {conformity_index} |\n"
        write_up += f"| Gradient Index | {gradient_index} |\n"
        write_up += f"| Maximum Dose | {max_dose}% |\n\n"
        
        # Closing statement
        write_up += f"Calculations and data analysis were reviewed and approved by both the prescribing radiation oncologist, "
        write_up += f"Dr. {physician}, and the radiation oncology physicist, Dr. {physicist}."
        
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