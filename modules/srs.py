import streamlit as st
from .templates import ConfigManager

class SRSModule:
    def __init__(self):
        """Initialize the SRS module with brain-specific regions."""
        self.config_manager = ConfigManager()
        
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
        
    def render_srs_form(self):
        """Render the form for SRS write-ups with multiple lesion support."""
        st.subheader("SRS Write-Up Generator")
        
        # Use tabs to organize the form
        basic_tab, lesions_tab = st.tabs([
            "Basic Information", "Lesions & Treatment"
        ])
        
        with basic_tab:
            # Staff information
            st.markdown("#### Staff Information")
            physician = st.selectbox("Physician Name", 
                                self.config_manager.get_physicists(), 
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
        
        with lesions_tab:
            # Target volume - moved from Basic tab
            col1, col2 = st.columns(2)
            with col1:
                # Number of lesions input
                num_lesions = st.number_input("Number of Lesions", min_value=1, max_value=10, value=1, key="num_lesions")
            
            with col2:
                # Target volume moved here from Basic tab
                target_volume = st.number_input("Target Volume (cc)", min_value=0.01, value=3.5, step=0.1, key="target_volume")
            
            # Initialize session state for lesions if it doesn't exist
            if 'lesions' not in st.session_state:
                st.session_state.lesions = [
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
            if len(st.session_state.lesions) < num_lesions:
                # Add new lesions with default values
                for i in range(len(st.session_state.lesions), num_lesions):
                    st.session_state.lesions.append({
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
            elif len(st.session_state.lesions) > num_lesions:
                # Remove excess lesions
                st.session_state.lesions = st.session_state.lesions[:num_lesions]
            
            # Copy feature
            if num_lesions > 1:
                st.markdown("#### Quick Copy")
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
                                site = st.session_state.lesions[target_lesion]['site']
                                st.session_state.lesions[target_lesion] = st.session_state.lesions[source_lesion].copy()
                                st.session_state.lesions[target_lesion]['site'] = site
                            else:
                                if "Dose" in which_params:
                                    st.session_state.lesions[target_lesion]['dose'] = st.session_state.lesions[source_lesion]['dose']
                                    st.session_state.lesions[target_lesion]['treatment_type'] = st.session_state.lesions[source_lesion]['treatment_type']
                                    st.session_state.lesions[target_lesion]['fractions'] = st.session_state.lesions[source_lesion]['fractions']
                                if "Volume" in which_params:
                                    st.session_state.lesions[target_lesion]['volume'] = st.session_state.lesions[source_lesion]['volume']
                                if "Metrics" in which_params:
                                    st.session_state.lesions[target_lesion]['prescription_isodose'] = st.session_state.lesions[source_lesion]['prescription_isodose']
                                    st.session_state.lesions[target_lesion]['ptv_coverage'] = st.session_state.lesions[source_lesion]['ptv_coverage']
                                    st.session_state.lesions[target_lesion]['conformity_index'] = st.session_state.lesions[source_lesion]['conformity_index']
                                    st.session_state.lesions[target_lesion]['gradient_index'] = st.session_state.lesions[source_lesion]['gradient_index']
                                    st.session_state.lesions[target_lesion]['max_dose'] = st.session_state.lesions[source_lesion]['max_dose']
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
                            current_site = st.session_state.lesions[i]['site']
                            
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
                                    st.session_state.lesions[i]['site'] = custom_region
                            else:
                                st.session_state.lesions[i]['site'] = selected_region
                            
                            # Treatment type
                            treatment_options = list(self.treatment_types.values())
                            
                            # Ensure treatment_type is properly initialized
                            if 'treatment_type' not in st.session_state.lesions[i] or st.session_state.lesions[i]['treatment_type'] not in treatment_options:
                                st.session_state.lesions[i]['treatment_type'] = self.treatment_types["SRS"]
                            
                            current_treatment = st.session_state.lesions[i]['treatment_type']
                            
                            # Find index of current treatment
                            try:
                                treatment_index = treatment_options.index(current_treatment)
                            except (ValueError, TypeError):
                                # If treatment_type isn't set or is invalid, default to SRS
                                treatment_index = 0
                                st.session_state.lesions[i]['treatment_type'] = self.treatment_types["SRS"]
                                
                            st.session_state.lesions[i]['treatment_type'] = st.radio(
                                "Treatment Type",
                                treatment_options,
                                index=treatment_index,
                                key=f"lesion_treatment_type_{i}"
                            )
                            
                            # Show fractions input if SRT is selected
                            if st.session_state.lesions[i]['treatment_type'] == self.treatment_types["SRT"]:
                                # Ensure fractions is initialized to a valid value (at least 2 for SRT)
                                if not 'fractions' in st.session_state.lesions[i] or st.session_state.lesions[i]['fractions'] < 2:
                                    st.session_state.lesions[i]['fractions'] = 5  # Default to 5 fractions for SRT
                                
                                st.session_state.lesions[i]['fractions'] = st.number_input(
                                    "Number of Fractions", 
                                    min_value=2, 
                                    max_value=10, 
                                    value=st.session_state.lesions[i]['fractions'],
                                    key=f"lesion_fractions_{i}"
                                )
                            else:
                                st.session_state.lesions[i]['fractions'] = 1
                        
                        with col2:
                            # Target volume for this specific lesion
                            st.session_state.lesions[i]['volume'] = st.number_input(
                                "Target Volume (cc)", 
                                min_value=0.01, 
                                value=st.session_state.lesions[i]['volume'],
                                step=0.1, 
                                key=f"lesion_volume_{i}"
                            )
                            
                            # Dose prescription
                            if 'treatment_type' in st.session_state.lesions[i]:
                                if st.session_state.lesions[i]['treatment_type'] == self.treatment_types["SRS"]:
                                    default_dose = 18.0
                                else:
                                    default_dose = 25.0
                            else:
                                default_dose = 18.0  # Default to SRS dose if no treatment type set
                            
                            # Get current dose value or use default
                            current_dose = st.session_state.lesions[i].get('dose', default_dose)
                            if current_dose is None or current_dose <= 0:
                                current_dose = default_dose
                                
                            st.session_state.lesions[i]['dose'] = st.number_input(
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
                            st.session_state.lesions[i]['prescription_isodose'] = st.number_input(
                                "Prescription Isodose (%)", 
                                min_value=80.0, 
                                max_value=100.0, 
                                value=float(st.session_state.lesions[i].get('prescription_isodose', 80.0)),
                                step=0.1,
                                format="%.1f",
                                key=f"lesion_isodose_{i}"
                            )
                            
                            st.session_state.lesions[i]['ptv_coverage'] = st.number_input(
                                "PTV Coverage (%)", 
                                min_value=90.0, 
                                max_value=100.0, 
                                value=float(st.session_state.lesions[i].get('ptv_coverage', 98.0)),
                                step=0.1,
                                format="%.1f",
                                key=f"lesion_coverage_{i}"
                            )
                        
                        with metrics_cols[1]:
                            # Improved input handling for CI
                            try:
                                current_ci = float(st.session_state.lesions[i].get('conformity_index', 1.2))
                                if current_ci <= 0 or current_ci > 3.0:
                                    current_ci = 1.2
                            except (ValueError, TypeError):
                                current_ci = 1.2
                            
                            # Direct text input for CI to avoid lag issues
                            ci_str = st.text_input(
                                "Conformity Index (0.01-3.0)", 
                                value=str(current_ci),
                                key=f"lesion_ci_text_{i}"
                            )
                            
                            # Convert input to float with validation
                            try:
                                new_ci = float(ci_str)
                                # Constrain to valid range
                                if 0.01 <= new_ci <= 3.0:
                                    st.session_state.lesions[i]['conformity_index'] = new_ci
                                else:
                                    st.warning("Conformity Index must be between 0.01 and 3.0")
                            except ValueError:
                                st.warning("Please enter a valid number for Conformity Index")
                            
                            # Improved input handling for GI
                            try:
                                current_gi = float(st.session_state.lesions[i].get('gradient_index', 3.0))
                                if current_gi <= 0 or current_gi > 10.0:
                                    current_gi = 3.0
                            except (ValueError, TypeError):
                                current_gi = 3.0
                            
                            # Direct text input for GI to avoid lag issues
                            gi_str = st.text_input(
                                "Gradient Index (0.01-10.0)", 
                                value=str(current_gi),
                                key=f"lesion_gi_text_{i}"
                            )
                            
                            # Convert input to float with validation
                            try:
                                new_gi = float(gi_str)
                                # Constrain to valid range
                                if 0.01 <= new_gi <= 10.0:
                                    st.session_state.lesions[i]['gradient_index'] = new_gi
                                else:
                                    st.warning("Gradient Index must be between 0.01 and 10.0")
                            except ValueError:
                                st.warning("Please enter a valid number for Gradient Index")
                            
                            # Get current max dose - use slider as requested
                            try:
                                current_max = int(st.session_state.lesions[i].get('max_dose', 125))
                                if current_max < 110 or current_max > 150:
                                    current_max = 125
                            except (ValueError, TypeError):
                                current_max = 125
                                
                            st.session_state.lesions[i]['max_dose'] = st.slider(
                                "Maximum Dose (%)", 
                                min_value=110, 
                                max_value=150, 
                                value=current_max,
                                step=1,
                                key=f"lesion_maxdose_{i}"
                            )
                            
                    with lesion_tabs[2]:  # Redesigned Quick Presets tab
                        st.markdown("### Fractionation Presets")
                        
                        # Use a modern card-like design with CSS
                        st.markdown("""
                        <style>
                        .preset-container {
                            display: flex;
                            flex-wrap: wrap;
                            gap: 10px;
                            margin-bottom: 20px;
                        }
                        .preset-header {
                            font-weight: bold;
                            margin-bottom: 10px;
                        }
                        </style>
                        
                        <div class="preset-header">SRS (Single Fraction)</div>
                        """, unsafe_allow_html=True)
                        
                        # Use a cleaner 4-column layout for SRS presets
                        cols = st.columns(4)
                        
                        # SRS presets
                        srs_presets = [
                            {"dose": 16.0, "label": "16 Gy × 1"},
                            {"dose": 18.0, "label": "18 Gy × 1"},
                            {"dose": 20.0, "label": "20 Gy × 1"},
                            {"dose": 21.0, "label": "21 Gy × 1"}
                        ]
                        
                        for idx, preset in enumerate(srs_presets):
                            with cols[idx % 4]:
                                if st.button(preset["label"], key=f"q_srs_{preset['dose']}_{i}", use_container_width=True):
                                    st.session_state.lesions[i]['dose'] = preset["dose"]
                                    st.session_state.lesions[i]['fractions'] = 1
                                    st.session_state.lesions[i]['treatment_type'] = self.treatment_types["SRS"]
                                    st.rerun()
                        
                        st.markdown("""
                        <div class="preset-header">SRT (Multiple Fractions)</div>
                        """, unsafe_allow_html=True)
                        
                        # SRT presets with cleaner layout
                        cols = st.columns(4)
                        
                        # SRT presets - automatically switch to SRT mode
                        srt_presets = [
                            {"dose": 25.0, "fractions": 5, "label": "25 Gy × 5"},
                            {"dose": 27.0, "fractions": 3, "label": "27 Gy × 3"},
                            {"dose": 30.0, "fractions": 5, "label": "30 Gy × 5"},
                            {"dose": 35.0, "fractions": 5, "label": "35 Gy × 5"}
                        ]
                        
                        for idx, preset in enumerate(srt_presets):
                            with cols[idx % 4]:
                                if st.button(preset["label"], key=f"q_srt_{preset['dose']}_{preset['fractions']}_{i}", use_container_width=True):
                                    st.session_state.lesions[i]['dose'] = preset["dose"]
                                    st.session_state.lesions[i]['fractions'] = preset["fractions"]
                                    st.session_state.lesions[i]['treatment_type'] = self.treatment_types["SRT"]
                                    st.rerun()
        
        # Generate button
        generate_pressed = st.button("Generate Write-Up", type="primary", key="srs_generate")
        
        # Check if we have all required information and the button was pressed
        required_fields = [physician, physicist, patient_age]
        
        # No need to check fractions globally since they're set per lesion now
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
                
            for field in missing_fields:
                st.warning(f"Missing required field: {field}")
                
            return None
        
        # If all required fields are filled and button is pressed, generate the write-up
        if generate_pressed and all_fields_filled:
            # Create patient details with lesion summary
            if num_lesions == 1:
                lesion_details = f"a {st.session_state.lesions[0]['volume']} cc lesion located in the {st.session_state.lesions[0]['site']}"
            else:
                # Create a detailed list of each lesion
                lesion_details = f"{num_lesions} brain lesions: "
                lesion_list = []
                
                for i, lesion in enumerate(st.session_state.lesions):
                    lesion_list.append(f"a {lesion['volume']} cc lesion in the {lesion['site']}")
                
                # Join the lesion descriptions with commas and 'and' for the last one
                if len(lesion_list) > 1:
                    lesion_details += ", ".join(lesion_list[:-1]) + f", and {lesion_list[-1]}"
                else:
                    lesion_details += lesion_list[0]
            
            patient_details = f"a {patient_age}-year-old {patient_sex} with {lesion_details}"
            
            # Check if we have mixed treatment types
            treatment_types_set = set(lesion['treatment_type'] for lesion in st.session_state.lesions)
            
            if len(treatment_types_set) == 1:
                # Single treatment type for all lesions
                if self.treatment_types["SRS"] in treatment_types_set:
                    treatment_type_text = "stereotactic radiosurgery (SRS)"
                    fraction_text = "single fraction"
                else:  # SRT
                    treatment_type_text = "stereotactic radiotherapy (SRT)"
                    
                    # Get the fractions from the first lesion (all should be the same)
                    fractions = st.session_state.lesions[0]['fractions']
                    fraction_text = f"{fractions} fractions"
            else:
                # Mixed treatment types
                treatment_type_text = "mixed SRS/SRT treatment"
                fraction_text = "mixed fractionation schedules"
            
            # Generate the write-up
            write_up = self._generate_srs_write_up(
                physician=physician,
                physicist=physicist,
                patient_details=patient_details,
                treatment_type=treatment_type_text,
                fraction_text=fraction_text,
                lesions=st.session_state.lesions,
                constants=self.constants
            )
            
            return write_up
        
        return None
    
    def _generate_srs_write_up(self, physician, physicist, patient_details, 
                             treatment_type, fraction_text, 
                             lesions, constants):
        """Generate the SRS write-up for multiple lesions."""
        
        # First paragraph - consultation request
        write_up = f"Dr. {physician} requested a medical physics consultation for --- for an MRI image fusion and {treatment_type}. "
        write_up += f"The patient is {patient_details}. "
        write_up += f"Dr. {physician} has elected to treat with a {treatment_type} technique "
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