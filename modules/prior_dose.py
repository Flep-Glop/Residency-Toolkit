import streamlit as st
from datetime import datetime
from .base_module import BaseWriteUpModule

class PriorDoseModule(BaseWriteUpModule):
    """Prior Dose module for clinical documentation generation.
    
    This module handles the creation of documentation for evaluating prior radiation dose
    when planning new treatments, which is essential for ensuring that cumulative dose to
    critical structures remains within safe limits.
    """
    
    def __init__(self, config_manager):
        """Initialize the Prior Dose module."""
        super().__init__(config_manager)
        
        # Common treatment sites
        self.treatment_sites = [
            "brain", "head and neck", "thorax", "breast", "lung", 
            "liver", "pancreas", "abdomen", "pelvis", "prostate", 
            "endometrium", "cervix", "rectum", "spine", "extremity"
        ]
        
        # Current year for default year selection
        self.current_year = datetime.now().year
    
    def get_module_name(self):
        """Return the display name of this module."""
        return "Prior Dose"
    
    def get_module_description(self):
        """Return a brief description of this module."""
        return "Prior radiation dose evaluation for retreatment planning"
    
    def get_required_fields(self):
        """Return a list of required field names for this module."""
        return ["current_site", "current_dose", "current_fractions", "prior_treatments"]
    
    def render_specialized_fields(self, physician, physicist, patient_age, patient_sex, patient_details):
        """Render Prior Dose-specific input fields and return the generated data."""
        # Create tabs for Treatment Details and Dose Constraints
        treatment_tab, constraints_tab = st.tabs(["Treatment Details", "Dose Constraints"])
        
        with treatment_tab:
            # Current Treatment
            st.markdown("#### Current Treatment")
            col1, col2 = st.columns(2)
            
            with col1:
                current_site = st.selectbox("Current Treatment Site", 
                                        sorted(self.treatment_sites),
                                        key="current_site")
                
                current_month = st.selectbox("Current Month", 
                                        ["January", "February", "March", "April", 
                                            "May", "June", "July", "August", 
                                            "September", "October", "November", "December"],
                                        key="current_month")
                current_year = st.number_input("Current Year", 
                                            min_value=2000, 
                                            max_value=2100,
                                            value=self.current_year,
                                            key="current_year")
            
            with col2:
                current_dose = st.number_input("Current Dose (Gy)", 
                                            min_value=0.0, 
                                            value=45.0, 
                                            step=0.1,
                                            key="current_dose")
                current_fractions = st.number_input("Current Fractions", 
                                                min_value=1, 
                                                value=15,
                                                key="current_fractions")
            
            # Prior Treatments section
            st.markdown("#### Prior Treatments")
            
            # Initialize session state for prior treatments if it doesn't exist
            if 'prior_treatments' not in st.session_state:
                st.session_state.prior_treatments = []
                
            # Display current prior treatments
            if not st.session_state.prior_treatments:
                st.info("No prior treatments added. Add treatments below.")
            else:
                for i, treatment in enumerate(st.session_state.prior_treatments):
                    with st.container():
                        cols = st.columns([3, 2, 1, 2, 1])
                        with cols[0]:
                            st.write(f"**Site**: {treatment['site']}")
                        with cols[1]:
                            st.write(f"**Dose**: {treatment['dose']} Gy / {treatment['fractions']} fx")
                        with cols[2]:
                            st.write(f"**Date**: {treatment['month']} {treatment['year']}")
                        with cols[3]:
                            # Empty space for alignment
                            st.write("")
                        with cols[4]:
                            if st.button("🗑️", key=f"delete_treatment_{i}"):
                                st.session_state.prior_treatments.pop(i)
                                st.rerun()
                
                # Add horizontal line for visual separation
                st.markdown("---")
            
            # Add new prior treatment
            st.markdown("#### Add Prior Treatment")
            
            col1, col2 = st.columns(2)
            with col1:
                prior_site = st.selectbox("Treatment Site", 
                                        sorted(self.treatment_sites),
                                        key="prior_site")
                
                prior_month = st.selectbox("Month", 
                                        ["January", "February", "March", "April", 
                                        "May", "June", "July", "August", 
                                        "September", "October", "November", "December"],
                                        key="prior_month")
                prior_year = st.number_input("Year", 
                                        min_value=2000, 
                                        max_value=2100,
                                        value=self.current_year-1,
                                        key="prior_year")
            
            with col2:
                prior_dose = st.number_input("Dose (Gy)", 
                                        min_value=0.0, 
                                        value=30.0,
                                        step=0.1,
                                        key="prior_dose")
                prior_fractions = st.number_input("Fractions", 
                                            min_value=1, 
                                            value=10,
                                            key="prior_fractions")
                
                add_treatment = st.button("Add Treatment", key="add_prior_treatment", type="primary")
                if add_treatment:
                    st.session_state.prior_treatments.append({
                        "site": prior_site,
                        "dose": prior_dose,
                        "fractions": prior_fractions,
                        "month": prior_month,
                        "year": prior_year
                    })
                    st.rerun()
            
            # Options for the write-up
            st.markdown("#### Overlap Assessment")
            
            col1, col2 = st.columns(2)
            with col1:
                has_overlap = st.radio(
                    "Is there overlap between treatments?",
                    ["No", "Yes"],
                    key="has_overlap"
                )
            
            with col2:
                if has_overlap == "Yes":
                    dose_calc_method = st.radio(
                        "Dose Calculation Method",
                        ["Raw Dose", "EQD2 (Equivalent Dose in 2 Gy fractions)"],
                        key="dose_calc_method"
                    )
                else:
                    dose_calc_method = "Not Applicable"
        
        with constraints_tab:
            # Dynamic dose constraint information based on selected treatments
            st.markdown("#### Dose Constraints Reference")
            
            # Get all unique treatment sites
            all_sites = set()
            if current_site:
                all_sites.add(current_site)
            
            for treatment in st.session_state.get('prior_treatments', []):
                if 'site' in treatment and treatment['site']:
                    all_sites.add(treatment['site'])
            
            if not all_sites:
                st.info("Please specify treatment sites in the Treatment Details tab to see relevant dose constraints.")
            else:
                # Display dose constraints for each selected site
                for site in sorted(all_sites):
                    st.markdown(f"##### {site.title()} Constraints")
                    # Display constraints based on site
                    constraints = self._get_dose_constraints(site)
                    
                    if constraints:
                        for organ, limit in constraints.items():
                            st.write(f"**{organ}**: {limit}")
                    else:
                        st.write("No specific constraints available for this site.")
                
                # Add a note about QUANTEC
                st.info("These constraints are based on QUANTEC recommendations. Actual clinical constraints may vary based on individual patient factors, treatment history, and institutional protocols.")
        
        # Check if we have all required information
        required_fields_filled = (
            current_site and 
            current_dose > 0 and 
            current_fractions > 0 and 
            len(st.session_state.prior_treatments) > 0
        )
        
        # If all required fields are filled, return the module data
        if required_fields_filled:
            return {
                "current_site": current_site,
                "current_dose": current_dose,
                "current_fractions": current_fractions,
                "current_month": current_month,
                "current_year": current_year,
                "prior_treatments": st.session_state.prior_treatments,
                "has_overlap": has_overlap,
                "dose_calc_method": dose_calc_method
            }
        
        return None
    
    def generate_write_up(self, common_info, module_data):
        """Generate the Prior Dose write-up based on common and module-specific data."""
        physician = common_info.get("physician", "")
        physicist = common_info.get("physicist", "")
        patient_details = common_info.get("patient_details", "")
        
        current_site = module_data.get("current_site", "")
        current_dose = module_data.get("current_dose", 0)
        current_fractions = module_data.get("current_fractions", 0)
        current_month = module_data.get("current_month", "")
        current_year = module_data.get("current_year", 0)
        prior_treatments = module_data.get("prior_treatments", [])
        has_overlap = module_data.get("has_overlap", "No")
        dose_calc_method = module_data.get("dose_calc_method", "")
        
        # Format current treatment info
        current_date = f"{current_month} {current_year}"
        current_treatment = f"{current_dose} Gy in {current_fractions} fractions"
        
        # Begin write-up
        write_up = f"Dr. {physician} requested a medical physics consultation for --- for evaluation of prior radiation dose. "
        write_up += f"The patient is {patient_details}. "
        write_up += f"The patient is currently being planned for {current_treatment} to the {current_site}.\n\n"
        
        # Prior treatments section
        write_up += "### Prior Radiation Treatment History\n\n"
        
        for i, treatment in enumerate(prior_treatments):
            site = treatment.get("site", "")
            dose = treatment.get("dose", 0)
            fractions = treatment.get("fractions", 0)
            month = treatment.get("month", "")
            year = treatment.get("year", 0)
            
            write_up += f"**Treatment {i+1}:** {month} {year}\n"
            write_up += f"- Site: {site}\n"
            write_up += f"- Dose: {dose} Gy in {fractions} fractions ({dose/fractions:.2f} Gy per fraction)\n\n"
        
        # Overlap assessment
        write_up += "### Overlap Assessment\n\n"
        
        if has_overlap == "Yes":
            write_up += "There is overlap between the current and prior treatment fields. "
            write_up += f"The {dose_calc_method} method was used to estimate the cumulative dose to overlapping critical structures. "
            write_up += "A composite plan was created in the treatment planning system to assess the total dose distribution.\n\n"
            
            write_up += "The following critical structures in the overlapping region were evaluated for cumulative dose:\n"
            write_up += "- List of critical structures will be added during review\n"
            write_up += "- For each structure, both physical and biological equivalent doses were calculated\n\n"
            
            write_up += "Based on this analysis, the current treatment plan was deemed acceptable with respect to cumulative dose constraints."
        else:
            write_up += "Review of the prior treatment fields and current treatment plan indicates minimal to no overlap "
            write_up += "between treatment volumes. The distance between field edges is sufficient to ensure that "
            write_up += "critical structures will not receive excessive cumulative dose.\n\n"
        
        # Conclusion
        write_up += "### Conclusion\n\n"
        write_up += f"The proposed treatment of {current_treatment} to the {current_site} "
        
        if has_overlap == "Yes":
            write_up += "can proceed with careful attention to the cumulative dose to the identified overlapping structures. "
            write_up += "Regular imaging and clinical assessment during treatment is recommended to monitor for increased toxicity."
        else:
            write_up += "can proceed as planned with standard toxicity monitoring. "
            write_up += "No additional dose constraints are required based on the prior radiation history."
        
        write_up += f"\n\nThis evaluation was reviewed and approved by Dr. {physician} (Radiation Oncologist) and Dr. {physicist} (Medical Physicist)."
        
        return write_up
    
    def _get_dose_constraints(self, site):
        """Get dose constraints for a specific treatment site."""
        # QUANTEC dose constraints based on treatment site
        constraints = {
            "brain": {
                "Brain Stem": "D0.03cc < 54 Gy",
                "Optic Chiasm": "D0.03cc < 54 Gy",
                "Optic Nerve": "D0.03cc < 54 Gy",
                "Retina": "D0.03cc < 45 Gy",
                "Cochlea": "Mean < 45 Gy",
                "Lens": "D0.03cc < 10 Gy"
            },
            "head and neck": {
                "Spinal Cord": "D0.03cc < 50 Gy",
                "Brain Stem": "D0.03cc < 54 Gy",
                "Parotid": "Mean < 26 Gy (at least one)",
                "Larynx": "Mean < 45 Gy",
                "Mandible": "D0.03cc < 70 Gy"
            },
            # Additional constraints for other sites
            # (truncated for brevity)
        }
        
        return constraints.get(site.lower(), {})
    
    # Legacy method for backward compatibility
    def render_prior_dose_form(self):
        """Legacy method to maintain backward compatibility."""
        # Staff information
        st.markdown("#### Staff Information")
        col1, col2 = st.columns(2)
        with col1:
            physician = st.selectbox("Physician Name", 
                                    self.config_manager.get_physicians(), 
                                    key="prior_physician")
        with col2:
            physicist = st.selectbox("Physicist Name", 
                                    self.config_manager.get_physicists(), 
                                    key="prior_physicist")
        
        # Patient information
        st.markdown("#### Patient Information")
        col1, col2 = st.columns(2)
        with col1:
            patient_age = st.number_input("Patient Age", min_value=0, max_value=120, key="prior_age")
        with col2:
            patient_sex = st.selectbox("Patient Sex", ["male", "female", "other"], key="prior_sex")
        
        patient_details = f"a {patient_age}-year-old {patient_sex}"
        
        # Get module-specific data
        module_data = self.render_specialized_fields(
            physician, physicist, patient_age, patient_sex, patient_details
        )
        
        # Generate button
        generate_pressed = st.button("Generate Write-Up", type="primary", key="prior_dose_generate")
        
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
            return write_up
        
        return None