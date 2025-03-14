import streamlit as st
from .base_module import BaseWriteUpModule
from validation_utils import FormValidator, validate_dose_fractionation

class SBRTModule(BaseWriteUpModule):
    """SBRT module for clinical documentation generation.
    
    This module handles the creation of documentation for stereotactic body
    radiation therapy (SBRT), which delivers precisely-targeted radiation
    in fewer, higher-dose treatments than traditional therapy.
    """
    
    def __init__(self, config_manager):
        """Initialize the SBRT module with configuration manager."""
        super().__init__(config_manager)
        
        # Common treatment sites for SBRT
        self.treatment_sites = [
            "lung", "liver", "spine", "adrenal", "pancreas", 
            "kidney", "prostate", "lymph node", "bone", "oligometastasis"
        ]
    
    def get_module_name(self):
        """Return the display name of this module."""
        return "SBRT"
    
    def get_module_description(self):
        """Return a brief description of this module."""
        return "Stereotactic Body Radiation Therapy for precise high-dose treatment"
    
    def get_required_fields(self):
        """Return a list of required field names for this module."""
        return ["treatment_site", "dose", "fractions", "is_4dct", "target_volume", "ptv_coverage"]
    
    def render_specialized_fields(self, physician, physicist, patient_age, patient_sex, patient_details):
        """Render SBRT-specific input fields and return the generated data."""
        # Create tabs for Basic Info and Treatment Details
        basic_tab, treatment_tab, metrics_tab = st.tabs([
            "Basic Information", "Treatment Details", "Plan Metrics"
        ])
        
        with basic_tab:
            # Treatment site - moved from basic tab
            st.markdown("#### Treatment Site")
            treatment_site = st.selectbox("Treatment Site", 
                                        sorted(self.treatment_sites),
                                        key="sbrt_site")
            
            # Option for custom site
            if treatment_site == "oligometastasis":
                oligomet_location = st.text_input("Specify Oligometastasis Location", key="oligomet_location")
                if oligomet_location:
                    treatment_site = f"oligometastatic {oligomet_location}"
        
        with treatment_tab:
            # Treatment planning details
            st.markdown("#### Treatment Parameters")
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
        
        with metrics_tab:
            # Plan quality metrics
            st.markdown("#### Plan Quality Metrics")
            col1, col2 = st.columns(2)
            
            with col1:
                pitv = st.number_input("PITV (Vpres iso / VPTV)", 
                                    min_value=0.0, 
                                    max_value=2.0, 
                                    value=1.0, 
                                    step=0.01,
                                    key="pitv")
            
            with col2:
                r50 = st.number_input("R50 (Vol50% pres iso / VolPTV)", 
                                    min_value=0.0, 
                                    max_value=10.0, 
                                    value=3.5, 
                                    step=0.1,
                                    key="r50")
            
            # Add section for dose constraints
            st.markdown("#### Organ-at-Risk Constraints")
            
            # Dynamic constraints based on treatment site
            if treatment_site:
                constraints = self._get_dose_constraints(treatment_site)
                if constraints:
                    st.info(f"Reference constraints for {treatment_site} SBRT:")
                    for organ, limit in constraints.items():
                        st.write(f"- **{organ}**: {limit}")
                else:
                    st.info("No specific constraints available for this site.")
        
        # Validate form inputs
        validator = FormValidator()
        validator.validate_required_field(treatment_site, "Treatment Site")
        validator.validate_required_field(dose, "Prescription Dose", min_value=0.1)
        validator.validate_required_field(fractions, "Number of Fractions", min_value=1)
        validator.validate_required_field(target_volume, "Target Volume", min_value=0.01)
        
        # Clinical validation for dose/fractionation
        if dose > 0 and fractions > 0:
            is_valid, message = validate_dose_fractionation(dose, fractions, treatment_site)
            if not is_valid:
                validator.errors.append(message)
            elif "warning" in message.lower():
                validator.add_warning(message)
        
        # Display any validation errors
        validation_passed = validator.display_validation_results()
        
        # Return the specialized fields data if valid
        if validation_passed and treatment_site and dose > 0 and fractions > 0:
            # Format motion management text based on 4DCT selection
            if is_4dct == "Yes":
                motion_text = "The patient was scanned in our CT simulator in the treatment position. "
                motion_text += "A 4D kVCT simulation scan was performed with the patient immobilized to assess respiratory motion. "
                motion_text += "Using the 4D dataset, a Maximum Intensity Projection (MIP) CT image set was reconstructed to generate an ITV "
                motion_text += "that encompasses the motion envelope of the target."
            else:
                motion_text = "The patient was scanned in our CT simulator in the treatment position. "
                motion_text += "The patient was immobilized using a customized immobilization device to limit motion during treatment and aid in inter-fractional repositioning."
            
            # Standard image guidance text
            imaging_text = "Patient positioning verification will be performed before each treatment fraction using "
            imaging_text += "kilovoltage cone-beam CT to ensure accurate target localization and patient positioning."
            
            # Return module-specific data
            return {
                "treatment_site": treatment_site,
                "dose": dose,
                "fractions": fractions,
                "is_4dct": is_4dct,
                "target_volume": target_volume,
                "ptv_coverage": ptv_coverage,
                "pitv": pitv,
                "r50": r50,
                "motion_text": motion_text,
                "imaging_text": imaging_text
            }
        
        return None
    
    def generate_write_up(self, common_info, module_data):
        """Generate the SBRT write-up based on common and module-specific data."""
        physician = common_info.get("physician", "")
        physicist = common_info.get("physicist", "")
        patient_details = common_info.get("patient_details", "")
        
        treatment_site = module_data.get("treatment_site", "")
        dose = module_data.get("dose", 0)
        fractions = module_data.get("fractions", 0)
        target_volume = module_data.get("target_volume", 0)
        ptv_coverage = module_data.get("ptv_coverage", 95)
        pitv = module_data.get("pitv", 1.0)
        r50 = module_data.get("r50", 3.5)
        motion_text = module_data.get("motion_text", "")
        imaging_text = module_data.get("imaging_text", "")
        
        # Standard QA text
        qa_text = "A quality assurance plan was developed and delivered to verify "
        qa_text += "the accuracy of the radiation treatment plan. Measurements within the phantom were obtained "
        qa_text += "and compared against the calculated plan, showing good agreement between the plan and measurements."
        
        # Generate the write-up
        write_up = f"Dr. {physician} requested a medical physics consultation for --- for a 4D CT simulation study and SBRT delivery. "
        write_up += f"The patient is {patient_details}. Dr. {physician} has elected to treat with a "
        write_up += "stereotactic body radiotherapy (SBRT) technique by means of the Pinnacle treatment planning "
        write_up += "system in conjunction with the linear accelerator equipped with the "
        write_up += "kV-CBCT system.\n\n"
        
        # Motion management section
        write_up += f"{motion_text} Both the prescribing radiation oncologist and radiation oncology physicist "
        write_up += "evaluated and approved the patient setup. "
        write_up += f"Dr. {physician} segmented and approved both the PTVs and OARs.\n\n"
        
        # Treatment planning section
        write_up += "In the treatment planning system, a VMAT treatment plan was developed to "
        write_up += f"conformally deliver a prescribed dose of {dose} Gy in {fractions} fractions to the planning target volume. "
        write_up += "The treatment plan was inversely optimized such that the prescription isodose volume exactly matched "
        write_up += f"the target volume of {target_volume} cc in all three spatial dimensions and that the dose fell sharply away from the target volume. "
        write_up += f"The treatment plan covered {ptv_coverage}% of the PTV with the prescribed isodose volume. "
        write_up += f"The PITV (Vpres iso / VPTV) was {pitv} and the R50 (Vol50% pres iso / VolPTV) was {r50}. "
        write_up += "Normal tissue dose constraints for critical organs associated with the treatment site were reviewed.\n\n"
        
        # Image guidance section
        write_up += f"{imaging_text}\n\n"
        
        # QA section
        write_up += f"{qa_text} Calculations and data analysis were reviewed and approved by both the "
        write_up += f"prescribing radiation oncologist, Dr. {physician}, and the radiation oncology physicist, Dr. {physicist}."
        
        return write_up
    
    def _get_dose_constraints(self, site):
        """Get dose constraints for a specific treatment site."""
        # SBRT dose constraints based on treatment site
        constraints = {
            "lung": {
                "Spinal Cord": "Dmax < 18 Gy",
                "Esophagus": "Dmax < 27 Gy",
                "Brachial Plexus": "Dmax < 24 Gy",
                "Heart": "Dmax < 30 Gy",
                "Trachea": "Dmax < 30 Gy",
                "Great vessels": "Dmax < 39 Gy"
            },
            "liver": {
                "Liver (normal)": "V15 < 700 cc",
                "Spinal Cord": "Dmax < 18 Gy",
                "Stomach": "Dmax < 30 Gy",
                "Duodenum": "Dmax < 24 Gy",
                "Kidney": "V12 < 25%",
                "Small Bowel": "Dmax < 27 Gy"
            },
            "spine": {
                "Spinal Cord": "Dmax < 14 Gy",
                "Cauda Equina": "Dmax < 16 Gy",
                "Esophagus": "Dmax < 15 Gy",
                "Kidney": "V12 < 25%"
            },
            "pancreas": {
                "Duodenum": "Dmax < 24 Gy",
                "Stomach": "Dmax < 22 Gy",
                "Small Bowel": "Dmax < 27 Gy",
                "Kidney": "V12 < 25%",
                "Liver": "V15 < 700 cc"
            },
            "prostate": {
                "Rectum": "V36 < 1 cc",
                "Bladder": "V37 < 10 cc",
                "Urethra": "V37 < 0.5 cc",
                "Femoral Head": "V24 < 3 cc"
            }
        }
        
        # Handle oligometastasis sites
        if "oligometastatic" in site:
            base_site = site.split(" ")[1]
            # Try to find constraints for the specific oligometastasis location
            for known_site in constraints:
                if known_site in base_site:
                    return constraints[known_site]
            # Default to generic constraints if specific location not found
            return {
                "Spinal Cord": "Dmax < 18 Gy",
                "Small Bowel": "Dmax < 27 Gy",
                "Kidney": "V12 < 25%",
                "Liver": "V15 < 700 cc"
            }
        
        return constraints.get(site.lower(), {})
    
    # Legacy method for backward compatibility
    def render_sbrt_form(self):
        """Legacy method to maintain backward compatibility."""
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
        with col2:
            patient_sex = st.selectbox("Patient Sex", ["male", "female", "other"], key="sbrt_sex")
        
        patient_details = f"a {patient_age}-year-old {patient_sex}"
        
        # Get module-specific data
        module_data = self.render_specialized_fields(
            physician, physicist, patient_age, patient_sex, patient_details
        )
        
        # Generate button
        generate_pressed = st.button("Generate Write-Up", type="primary", key="sbrt_generate")
        
        # Generate write-up if button is pressed and all data is provided
        if generate_pressed and module_data:
            common_info = {
                "physician": physician,
                "physicist": physicist,
                "patient_age": patient_age,
                "patient_sex": patient_sex,
                "patient_details": patient_details
            }
            
            write_up = self.generate_write_up(common_info, module_data)
            self.display_write_up(write_up)
            return write_up
        
        return None