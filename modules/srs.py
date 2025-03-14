import streamlit as st
from .base_module import BaseWriteUpModule
from validation_utils import FormValidator, validate_dose_fractionation

class SRSModule(BaseWriteUpModule):
    """SRS module for clinical documentation generation.
    
    This module handles the creation of documentation for stereotactic radiosurgery (SRS)
    and stereotactic radiotherapy (SRT) treatments, primarily used for brain lesions.
    """
    
    def __init__(self, config_manager):
        """Initialize the SRS module with configuration manager."""
        super().__init__(config_manager)
        
        # Brain-specific regions for SRS
        self.brain_regions = [
            "left frontal lobe", "right frontal lobe", 
            "left parietal lobe", "right parietal lobe", 
            "left temporal lobe", "right temporal lobe", 
            "left occipital lobe", "right occipital lobe",
            "cerebellum", "brainstem", "thalamus", "basal ganglia",
            "corpus callosum", "pineal region", "midbrain", "pons",
            "medulla", "left cerebellar hemisphere", "right cerebellar hemisphere",
            "left hippocampus", "right hippocampus", "optic chiasm", "sellar region"
        ]
        
        # Treatment types
        self.treatment_types = {
            "SRS": "SRS (Single Fraction)",
            "SRT": "SRT (Multiple Fractions)"
        }
        
        # Constants (previously user inputs that are now fixed)
        self.constants = {
            "mri_sequence": "T1-weighted, post Gd contrast",
            "planning_system": "BrainLAB Elements",
            "accelerator": "Versa HD",
            "tracking_system": "ExacTrac",
            "immobilization_device": "rigid aquaplast head mask",
            "ct_slice_thickness": 1.25,
            "ct_localization": True
        }
    
    def get_module_name(self):
        """Return the display name of this module."""
        return "SRS"
    
    def get_module_description(self):
        """Return a brief description of this module."""
        return "Stereotactic Radiosurgery for precise treatment of brain lesions"
    
    def get_required_fields(self):
        """Return a list of required field names for this module."""
        return ["lesions"]
    
    def render_specialized_fields(self, physician, physicist, patient_age, patient_sex, patient_details):
        """Render the specialized fields for SRS write-ups with multiple lesion support."""
        
        # Use tabs to organize the form
        basic_tab, lesions_tab = st.tabs([
            "Basic Information", "Lesions & Treatment"
        ])
        
        with basic_tab:
            # Add an information expander for SRS technique
            st.info("""
                ### Stereotactic Radiosurgery (SRS) / Stereotactic Radiotherapy (SRT)
                
                **Clinical Purpose:**  
                SRS/SRT delivers precisely-targeted radiation to intracranial lesions with millimeter 
                accuracy. SRS refers to single-fraction delivery, while SRT uses multiple fractions.
                
                **Key Benefits:**
                - Highly conformal dose distributions
                - Steep dose gradients to spare adjacent critical structures
                - Non-invasive alternative to surgical resection
                - Outpatient procedure with minimal recovery time
                
                **Common Applications:**
                - Brain metastases
                - Acoustic neuromas
                - Meningiomas
                - Arteriovenous malformations (AVMs)
                - Trigeminal neuralgia
                - Pituitary adenomas
                
                **Fractionation Selection:**
                - Single fraction (SRS): Typically for smaller lesions (<3cm) away from critical structures
                - Multi-fraction (SRT): Larger lesions or those near critical structures like optic apparatus
                """)
        
        with lesions_tab:
            # Number of lesions input
            num_lesions = st.number_input("Number of Lesions", min_value=1, max_value=10, value=1, key="num_lesions")
            
            # Initialize session state for lesions if it doesn't exist
            if 'srs_lesions' not in st.session_state:
                st.session_state.srs_lesions = [
                    {
                        'site': self.brain_regions[0],
                        'volume': 1.5,
                        'treatment_type': self.treatment_types["SRS"],
                        'dose': 18.0,
                        'fractions': 1,
                        'prescription_isodose': 80.0,
                        'ptv_coverage': 98.0,
                        'conformity_index': 1.2,
                        'gradient_index': 3.0,
                        'max_dose': 125
                    }
                ] * min(num_lesions, 1)  # Initialize with at least one lesion
            
            # Update lesions array size if number of lesions changes
            if len(st.session_state.srs_lesions) < num_lesions:
                # Add new lesions with default values
                for i in range(len(st.session_state.srs_lesions), num_lesions):
                    st.session_state.srs_lesions.append({
                        'site': self.brain_regions[0],
                        'volume': 1.5,
                        'treatment_type': self.treatment_types["SRS"],
                        'dose': 18.0,
                        'fractions': 1,
                        'prescription_isodose': 80.0,
                        'ptv_coverage': 98.0,
                        'conformity_index': 1.2,
                        'gradient_index': 3.0,
                        'max_dose': 125
                    })
            elif len(st.session_state.srs_lesions) > num_lesions:
                # Remove excess lesions
                st.session_state.srs_lesions = st.session_state.srs_lesions[:num_lesions]
            
            # Copy feature for multiple lesions
            if num_lesions > 1:
                with st.expander("Quick Copy Tool", expanded=False):
                    st.markdown("#### Copy Parameters Between Lesions")
                    copy_cols = st.columns(4)
                    with copy_cols[0]:
                        source_lesion = st.number_input("Copy from Lesion #", min_value=1, max_value=num_lesions, value=1, key="copy_source") - 1
                    with copy_cols[1]:
                        target_lesion = st.number_input("Copy to Lesion #", min_value=1, max_value=num_lesions, value=min(2, num_lesions), key="copy_target") - 1
                    with copy_cols[2]:
                        which_params = st.multiselect("Parameters to Copy", 
                                                ["All", "Dose", "Volume", "Metrics"],
                                                default=["All"],
                                                key="copy_params")
                    with copy_cols[3]:
                        if st.button("Copy Now", key="copy_button"):
                            if source_lesion != target_lesion and 0 <= source_lesion < num_lesions and 0 <= target_lesion < num_lesions:
                                if "All" in which_params or len(which_params) == 0:
                                    # Copy everything except site
                                    site = st.session_state.srs_lesions[target_lesion]['site']
                                    st.session_state.srs_lesions[target_lesion] = st.session_state.srs_lesions[source_lesion].copy()
                                    st.session_state.srs_lesions[target_lesion]['site'] = site
                                else:
                                    if "Dose" in which_params:
                                        st.session_state.srs_lesions[target_lesion]['dose'] = st.session_state.srs_lesions[source_lesion]['dose']
                                        st.session_state.srs_lesions[target_lesion]['treatment_type'] = st.session_state.srs_lesions[source_lesion]['treatment_type']
                                        st.session_state.srs_lesions[target_lesion]['fractions'] = st.session_state.srs_lesions[source_lesion]['fractions']
                                    if "Volume" in which_params:
                                        st.session_state.srs_lesions[target_lesion]['volume'] = st.session_state.srs_lesions[source_lesion]['volume']
                                    if "Metrics" in which_params:
                                        st.session_state.srs_lesions[target_lesion]['prescription_isodose'] = st.session_state.srs_lesions[source_lesion]['prescription_isodose']
                                        st.session_state.srs_lesions[target_lesion]['ptv_coverage'] = st.session_state.srs_lesions[source_lesion]['ptv_coverage']
                                        st.session_state.srs_lesions[target_lesion]['conformity_index'] = st.session_state.srs_lesions[source_lesion]['conformity_index']
                                        st.session_state.srs_lesions[target_lesion]['gradient_index'] = st.session_state.srs_lesions[source_lesion]['gradient_index']
                                        st.session_state.srs_lesions[target_lesion]['max_dose'] = st.session_state.srs_lesions[source_lesion]['max_dose']
                                    st.success(f"Copied from Lesion {source_lesion+1} to Lesion {target_lesion+1}")
            
            # Display lesion input forms
            for i in range(num_lesions):
                # Basic Input + Advanced Input tab approach for each lesion
                with st.expander(f"Lesion {i+1}", expanded=(i == 0 or num_lesions <= 3)):
                    lesion_tabs = st.tabs(["Basic Info", "Plan Metrics", "Quick Presets"])
                    
                    with lesion_tabs[0]:  # Basic Info tab
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Lesion location with custom option
                            sorted_regions = sorted(self.brain_regions) + ["Other (specify)"]
                            current_site = st.session_state.srs_lesions[i]['site']
                            
                            # Find index of current site in sorted regions
                            try:
                                site_index = sorted_regions.index(current_site)
                            except ValueError:
                                # If current site is not in the predefined list,
                                # select "Other" and we'll show it as custom
                                if current_site not in sorted_regions:
                                    site_index = len(sorted_regions) - 1  # "Other" option
                                else:
                                    site_index = 0
                            
                            selected_region = st.selectbox(
                                "Brain Region", 
                                sorted_regions,
                                index=site_index,
                                key=f"lesion_site_select_{i}"
                            )
                            
                            # If "Other" is selected, show text input for custom region
                            if selected_region == "Other (specify)":
                                # If we already have a custom value, use it as default
                                default_custom = "" if current_site in sorted_regions else current_site
                                custom_region = st.text_input(
                                    "Specify Region",
                                    value=default_custom,
                                    key=f"lesion_site_custom_{i}"
                                )
                                if custom_region:
                                    st.session_state.srs_lesions[i]['site'] = custom_region
                            else:
                                st.session_state.srs_lesions[i]['site'] = selected_region
                            
                            # Treatment type
                            treatment_options = list(self.treatment_types.values())
                            
                            # Ensure treatment_type is properly initialized
                            if 'treatment_type' not in st.session_state.srs_lesions[i] or st.session_state.srs_lesions[i]['treatment_type'] not in treatment_options:
                                st.session_state.srs_lesions[i]['treatment_type'] = self.treatment_types["SRS"]
                            
                            current_treatment = st.session_state.srs_lesions[i]['treatment_type']
                            
                            # Find index of current treatment
                            try:
                                treatment_index = treatment_options.index(current_treatment)
                            except (ValueError, TypeError):
                                # If treatment_type isn't set or is invalid, default to SRS
                                treatment_index = 0
                                st.session_state.srs_lesions[i]['treatment_type'] = self.treatment_types["SRS"]
                                
                            st.session_state.srs_lesions[i]['treatment_type'] = st.radio(
                                "Treatment Type",
                                treatment_options,
                                index=treatment_index,
                                key=f"lesion_treatment_type_{i}"
                            )
                            
                            # Show fractions input if SRT is selected
                            if st.session_state.srs_lesions[i]['treatment_type'] == self.treatment_types["SRT"]:
                                # Ensure fractions is initialized to a valid value (at least 2 for SRT)
                                if not 'fractions' in st.session_state.srs_lesions[i] or st.session_state.srs_lesions[i]['fractions'] < 2:
                                    st.session_state.srs_lesions[i]['fractions'] = 5  # Default to 5 fractions for SRT
                                
                                st.session_state.srs_lesions[i]['fractions'] = st.number_input(
                                    "Number of Fractions", 
                                    min_value=2, 
                                    max_value=10, 
                                    value=st.session_state.srs_lesions[i]['fractions'],
                                    key=f"lesion_fractions_{i}"
                                )
                            else:
                                st.session_state.srs_lesions[i]['fractions'] = 1
                        
                        with col2:
                            # Target volume for this specific lesion
                            st.session_state.srs_lesions[i]['volume'] = st.number_input(
                                "Target Volume (cc)", 
                                min_value=0.01, 
                                value=st.session_state.srs_lesions[i]['volume'],
                                step=0.1, 
                                key=f"lesion_volume_{i}"
                            )
                            
                            # Dose prescription
                            if 'treatment_type' in st.session_state.srs_lesions[i]:
                                if st.session_state.srs_lesions[i]['treatment_type'] == self.treatment_types["SRS"]:
                                    default_dose = 18.0
                                else:
                                    default_dose = 25.0
                            else:
                                default_dose = 18.0  # Default to SRS dose if no treatment type set
                            
                            # Get current dose value or use default
                            current_dose = st.session_state.srs_lesions[i].get('dose', default_dose)
                            if current_dose is None or current_dose <= 0:
                                current_dose = default_dose
                                
                            st.session_state.srs_lesions[i]['dose'] = st.number_input(
                                "Prescription Dose (Gy)", 
                                min_value=0.0, 
                                value=current_dose,
                                step=0.1, 
                                key=f"lesion_dose_{i}"
                            )
                    
                    with lesion_tabs[1]:  # Plan Metrics tab
                        metrics_cols = st.columns(2)
                        
                        with metrics_cols[0]:
                            # Prescription and coverage - use number_input for decimal precision
                            st.session_state.srs_lesions[i]['prescription_isodose'] = st.number_input(
                                "Prescription Isodose (%)", 
                                min_value=80.0, 
                                max_value=100.0, 
                                value=float(st.session_state.srs_lesions[i].get('prescription_isodose', 80.0)),
                                step=0.1,
                                format="%.1f",
                                key=f"lesion_isodose_{i}"
                            )
                            
                            st.session_state.srs_lesions[i]['ptv_coverage'] = st.number_input(
                                "PTV Coverage (%)", 
                                min_value=90.0, 
                                max_value=100.0, 
                                value=float(st.session_state.srs_lesions[i].get('ptv_coverage', 98.0)),
                                step=0.1,
                                format="%.1f",
                                key=f"lesion_coverage_{i}"
                            )
                        
                        with metrics_cols[1]:
                            # Direct text input for CI to avoid lag issues
                            ci_str = st.text_input(
                                "Conformity Index (0.01-3.0)", 
                                value=str(st.session_state.srs_lesions[i].get('conformity_index', 1.2)),
                                key=f"lesion_ci_text_{i}"
                            )
                            
                            # Convert input to float with validation
                            try:
                                new_ci = float(ci_str)
                                # Constrain to valid range
                                if 0.01 <= new_ci <= 3.0:
                                    st.session_state.srs_lesions[i]['conformity_index'] = new_ci
                                else:
                                    st.warning("Conformity Index must be between 0.01 and 3.0")
                            except ValueError:
                                st.warning("Please enter a valid number for Conformity Index")
                            
                            # Direct text input for GI to avoid lag issues
                            gi_str = st.text_input(
                                "Gradient Index (0.01-10.0)", 
                                value=str(st.session_state.srs_lesions[i].get('gradient_index', 3.0)),
                                key=f"lesion_gi_text_{i}"
                            )
                            
                            # Convert input to float with validation
                            try:
                                new_gi = float(gi_str)
                                # Constrain to valid range
                                if 0.01 <= new_gi <= 10.0:
                                    st.session_state.srs_lesions[i]['gradient_index'] = new_gi
                                else:
                                    st.warning("Gradient Index must be between 0.01 and 10.0")
                            except ValueError:
                                st.warning("Please enter a valid number for Gradient Index")
                            
                            # Use slider for max dose
                            st.session_state.srs_lesions[i]['max_dose'] = st.slider(
                                "Maximum Dose (%)", 
                                min_value=110, 
                                max_value=150, 
                                value=int(st.session_state.srs_lesions[i].get('max_dose', 125)),
                                step=1,
                                key=f"lesion_maxdose_{i}"
                            )
                    
                    with lesion_tabs[2]:  # Quick Presets tab
                        st.markdown("### Fractionation Presets")
                        
                        # SRS presets
                        st.markdown("#### SRS (Single Fraction)")
                        srs_cols = st.columns(4)
                        
                        srs_presets = [
                            {"dose": 16.0, "label": "16 Gy × 1"},
                            {"dose": 18.0, "label": "18 Gy × 1"},
                            {"dose": 20.0, "label": "20 Gy × 1"},
                            {"dose": 21.0, "label": "21 Gy × 1"}
                        ]
                        
                        for idx, preset in enumerate(srs_presets):
                            with srs_cols[idx % 4]:
                                if st.button(preset["label"], key=f"q_srs_{preset['dose']}_{i}", use_container_width=True):
                                    st.session_state.srs_lesions[i]['dose'] = preset["dose"]
                                    st.session_state.srs_lesions[i]['fractions'] = 1
                                    st.session_state.srs_lesions[i]['treatment_type'] = self.treatment_types["SRS"]
                                    st.rerun()
                        
                        # SRT presets
                        st.markdown("#### SRT (Multiple Fractions)")
                        srt_cols = st.columns(4)
                        
                        srt_presets = [
                            {"dose": 25.0, "fractions": 5, "label": "25 Gy × 5"},
                            {"dose": 27.0, "fractions": 3, "label": "27 Gy × 3"},
                            {"dose": 30.0, "fractions": 5, "label": "30 Gy × 5"},
                            {"dose": 35.0, "fractions": 5, "label": "35 Gy × 5"}
                        ]
                        
                        for idx, preset in enumerate(srt_presets):
                            with srt_cols[idx % 4]:
                                if st.button(preset["label"], key=f"q_srt_{preset['dose']}_{preset['fractions']}_{i}", use_container_width=True):
                                    st.session_state.srs_lesions[i]['dose'] = preset["dose"]
                                    st.session_state.srs_lesions[i]['fractions'] = preset["fractions"]
                                    st.session_state.srs_lesions[i]['treatment_type'] = self.treatment_types["SRT"]
                                    st.rerun()
        
        # Validation
        validator = FormValidator()
        
        # Validate lesions data
        for i, lesion in enumerate(st.session_state.srs_lesions):
            # Validate required fields
            validator.validate_required_field(lesion['site'], f"Lesion {i+1} Brain Region")
            validator.validate_required_field(lesion['volume'], f"Lesion {i+1} Volume", min_value=0.01)
            validator.validate_required_field(lesion['dose'], f"Lesion {i+1} Dose", min_value=0.1)
            
            # Clinical validation for dose/fractionation
            if lesion['dose'] > 0 and lesion['fractions'] > 0:
                is_valid, message = validate_dose_fractionation(lesion['dose'], lesion['fractions'], "brain")
                if not is_valid:
                    validator.errors.append(f"Lesion {i+1}: {message}")
                elif "warning" in message.lower():
                    validator.add_warning(f"Lesion {i+1}: {message}")
            
            # Validate volume-based dose guidelines
            if lesion['volume'] > 0 and lesion['dose'] > 0:
                if lesion['treatment_type'] == self.treatment_types["SRS"] and lesion['fractions'] == 1:
                    if lesion['volume'] > 10 and lesion['dose'] > 15:
                        validator.add_warning(f"Lesion {i+1}: Volume > 10cc with single fraction dose > 15 Gy may increase toxicity risk")
                    if lesion['volume'] > 20:
                        validator.add_warning(f"Lesion {i+1}: Lesions > 20cc are typically treated with fractionated SRT instead of single fraction SRS")
        
        # Display validation results
        validation_passed = validator.display_validation_results()
        
        # Return the specialized fields data if valid
        if validation_passed and len(st.session_state.srs_lesions) > 0:
            # Return only a shallow copy of the session state lesions to avoid circular references
            return {
                "lesions": [lesion.copy() for lesion in st.session_state.srs_lesions],
                "constants": self.constants
            }
        
        return None
    
    def generate_write_up(self, common_info, module_data):
        """Generate the SRS write-up based on common and module-specific data."""
        physician = common_info.get("physician", "")
        physicist = common_info.get("physicist", "")
        patient_details = common_info.get("patient_details", "")
        
        lesions = module_data.get("lesions", [])
        constants = module_data.get("constants", self.constants)
        
        # Create patient details with lesion summary
        if len(lesions) == 1:
            lesion_details = f"a {lesions[0]['volume']} cc lesion located in the {lesions[0]['site']}"
        else:
            # Create a detailed list of each lesion
            lesion_details = f"{len(lesions)} brain lesions: "
            lesion_list = []
            
            for lesion in lesions:
                lesion_list.append(f"a {lesion['volume']} cc lesion in the {lesion['site']}")
            
            # Join the lesion descriptions with commas and 'and' for the last one
            if len(lesion_list) > 1:
                lesion_details += ", ".join(lesion_list[:-1]) + f", and {lesion_list[-1]}"
            else:
                lesion_details += lesion_list[0]
        
        patient_details_with_lesions = f"{patient_details} with {lesion_details}"
        
        # Check if we have mixed treatment types
        treatment_types_set = set(lesion['treatment_type'] for lesion in lesions)
        
        if len(treatment_types_set) == 1:
            # Single treatment type for all lesions
            if self.treatment_types["SRS"] in treatment_types_set:
                treatment_type_text = "stereotactic radiosurgery (SRS)"
                fraction_text = "single fraction"
            else:  # SRT
                treatment_type_text = "stereotactic radiotherapy (SRT)"
                
                # Get the fractions from the first lesion (all should be the same)
                fractions = lesions[0]['fractions']
                fraction_text = f"{fractions} fractions"
        else:
            # Mixed treatment types
            treatment_type_text = "mixed SRS/SRT treatment"
            fraction_text = "mixed fractionation schedules"
        
        # Generate the write-up
        write_up = f"Dr. {physician} requested a medical physics consultation for --- for an MRI image fusion and {treatment_type_text}. "
        write_up += f"The patient is {patient_details_with_lesions}. "
        write_up += f"Dr. {physician} has elected to treat with a {treatment_type_text} technique "
        write_up += f"by means of the {constants['planning_system']} treatment planning system in conjunction with the "
        write_up += f"{constants['accelerator']} linear accelerator equipped with the {constants['tracking_system']} system.\n\n"
        
        # Second paragraph - immobilization and imaging
        write_up += f"Days before radiation delivery, a {constants['immobilization_device']} was constructed of the patient and was then "
        write_up += f"fixated onto a stereotactic carbon fiber frame base. Dr. {physician} was present to verify correct "
        write_up += f"construction of the head mask. A high resolution CT scan ({constants['ct_slice_thickness']}mm slice thickness) was then acquired. "
        
        # MRI fusion paragraph
        write_up += f"In addition, a previous high resolution MR image set ({constants['mri_sequence']} scan) was acquired. "
        write_up += f"The MR images and CT images were fused within the {constants['planning_system']} treatment planning system platform "
        write_up += f"where a rigid body fusion was performed. "
        
        # CT localization (if included)
        if constants['ct_localization']:
            write_up += f"CT images were also localized in {constants['planning_system']}. "
        
        # Approval statement
        write_up += f"Fusion and structure segmentation were reviewed by Dr. {physician} and Dr. {physicist}.\n\n"
        
        # Treatment planning section - varies based on number of lesions
        if len(lesions) == 1:
            # Single lesion case
            lesion = lesions[0]
            write_up += f"A radiotherapy treatment plan was developed to deliver the prescribed dose to the periphery of the lesion. "
            write_up += f"The treatment plan was optimized such that the prescription isodose volume geometrically matched "
            write_up += f"the planning target volume (PTV) and that the lower isodose volumes spared the healthy brain tissue. "
            write_up += f"The following table summarizes the plan parameters:\n\n"
            
            # Get fraction text specific to this lesion
            if lesion['treatment_type'] == self.treatment_types["SRS"]:
                lesion_fraction_text = "single fraction"
            else:
                lesion_fraction_text = f"{lesion['fractions']} fractions"
                
            # Table of plan parameters for single lesion
            write_up += f"| Parameter | Value |\n"
            write_up += f"|-----------|-------|\n"
            write_up += f"| Prescription Dose | {lesion['dose']} Gy in {lesion_fraction_text} |\n"
            write_up += f"| Target Volume | {lesion['volume']} cc |\n"
            write_up += f"| Location | {lesion['site']} |\n"
            write_up += f"| Prescription Isodose | {lesion['prescription_isodose']}% |\n"
            write_up += f"| PTV Coverage | {lesion['ptv_coverage']}% |\n"
            write_up += f"| Conformity Index | {lesion['conformity_index']} |\n"
            write_up += f"| Gradient Index | {lesion['gradient_index']} |\n"
            write_up += f"| Maximum Dose | {lesion['max_dose']}% |\n\n"
        else:
            # Multiple lesion case
            write_up += f"A radiotherapy treatment plan was developed to deliver the prescribed doses to the periphery of each lesion. "
            write_up += f"The treatment plan was optimized such that each prescription isodose volume geometrically matched "
            write_up += f"the corresponding planning target volume (PTV) and that the lower isodose volumes spared the healthy brain tissue. "
            write_up += f"The following table summarizes the plan parameters for each lesion:\n\n"
            
            # Table header for multiple lesions
            write_up += f"| Lesion | Location | Volume (cc) | Dose (Gy) | Fractions | Prescription Isodose | PTV Coverage | Conformity Index | Gradient Index | Max Dose |\n"
            write_up += f"|--------|----------|------------|-----------|-----------|---------------------|--------------|-----------------|--------------|----------|\n"
            
            # Add row for each lesion
            for i, lesion in enumerate(lesions):
                write_up += f"| {i+1} | {lesion['site']} | {lesion['volume']} | {lesion['dose']} | {lesion['fractions']} | {lesion['prescription_isodose']}% | "
                write_up += f"{lesion['ptv_coverage']}% | {lesion['conformity_index']} | {lesion['gradient_index']} | {lesion['max_dose']}% |\n"
            
            # Check if all fractions are the same
            fractions_set = set(lesion['fractions'] for lesion in lesions)
            treatment_types_set = set(lesion['treatment_type'] for lesion in lesions)
            
            if len(fractions_set) == 1 and len(treatment_types_set) == 1:
                # All lesions have the same fractionation
                write_up += f"\nAll lesions will be treated in {fraction_text}.\n\n"
            else:
                # Mixed fractionation
                write_up += f"\nLesions will be treated according to their individual fractionation schedules as shown in the table above.\n\n"
        
        # Closing statement
        write_up += f"Calculations and data analysis were reviewed and approved by both the prescribing radiation oncologist, "
        write_up += f"Dr. {physician}, and the radiation oncology physicist, Dr. {physicist}."
        
        return write_up
    
    # Legacy method for backward compatibility
    def render_srs_form(self):
        """Legacy method to maintain backward compatibility."""
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
        with col2:
            patient_sex = st.selectbox("Patient Sex", ["male", "female", "other"], key="srs_sex")
        
        patient_details = f"a {patient_age}-year-old {patient_sex}"
        
        # Get module-specific data
        module_data = self.render_specialized_fields(
            physician, physicist, patient_age, patient_sex, patient_details
        )
        
        # Generate button
        generate_pressed = st.button("Generate Write-Up", type="primary", key="srs_generate")
        
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