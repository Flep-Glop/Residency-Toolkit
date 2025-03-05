import streamlit as st
from datetime import datetime
from .templates import ConfigManager

class PriorDoseModule:
    def __init__(self):
        """Initialize the Prior Dose module."""
        self.template_manager = TemplateManager()
        self.config_manager = ConfigManager()
        
        # Common treatment sites
        self.treatment_sites = [
            "brain", "head and neck", "thorax", "breast", "lung", 
            "liver", "pancreas", "abdomen", "pelvis", "prostate", 
            "endometrium", "cervix", "rectum", "spine", "extremity"
        ]
        
        # Current year for default year selection
        self.current_year = datetime.now().year
        
    def render_prior_dose_form(self):
        """Render the form for prior dose write-ups."""
        st.subheader("Prior Dose Write-Up Generator")
        
        # Create tabs for Basic Info, Treatment Details, and Dose Constraints
        basic_tab, treatment_tab, constraints_tab = st.tabs(["Basic Information", "Treatment Details", "Dose Constraints"])
        
        with basic_tab:
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
        
        with treatment_tab:
            # Current Treatment
            st.markdown("#### Current Treatment")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                current_site = st.selectbox("Current Treatment Site", 
                                          sorted(self.treatment_sites),
                                          key="current_site")
            with col2:
                current_dose = st.number_input("Current Dose (Gy)", 
                                             min_value=0.0, 
                                             value=45.0, 
                                             step=0.1,  # Changed to 0.1
                                             key="current_dose")
            with col3:
                current_fractions = st.number_input("Current Fractions", 
                                                 min_value=1, 
                                                 value=15,
                                                 key="current_fractions")
            with col4:
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
                        cols = st.columns([3, 2, 1, 1, 2, 1])
                        with cols[0]:
                            st.write(f"**Site**: {treatment['site']}")
                        with cols[1]:
                            st.write(f"**Dose**: {treatment['dose']} Gy")
                        with cols[2]:
                            st.write(f"**Fx**: {treatment['fractions']}")
                        with cols[3]:
                            st.write(f"**Date**: {treatment['month']} {treatment['year']}")
                        with cols[4]:
                            # Empty space for alignment
                            st.write("")
                        with cols[5]:
                            if st.button("🗑️", key=f"delete_treatment_{i}"):
                                st.session_state.prior_treatments.pop(i)
                                st.rerun()
            
            # Add new prior treatment
            st.markdown("#### Add Prior Treatment")
            with st.container():
                cols = st.columns(5)
                with cols[0]:
                    prior_site = st.selectbox("Treatment Site", 
                                             sorted(self.treatment_sites),
                                             key="prior_site")
                with cols[1]:
                    prior_dose = st.number_input("Dose (Gy)", 
                                              min_value=0.0, 
                                              value=30.0,
                                              step=0.1,  # Changed to 0.1
                                              key="prior_dose")
                with cols[2]:
                    prior_fractions = st.number_input("Fractions", 
                                                  min_value=1, 
                                                  value=10,
                                                  key="prior_fractions")
                with cols[3]:
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
                with cols[4]:
                    if st.button("Add Treatment", key="add_prior_treatment"):
                        st.session_state.prior_treatments.append({
                            "site": prior_site,
                            "dose": prior_dose,
                            "fractions": prior_fractions,
                            "month": prior_month,
                            "year": prior_year
                        })
                        st.rerun()
            
            # Options for the write-up
            st.markdown("#### Write-Up Options")
            
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
            if 'current_site' in locals() and current_site:
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
        
        # Generate button
        generate_pressed = st.button("Generate Write-Up", type="primary", key="prior_dose_generate")
        
        # Check if we have all required information and the button was pressed
        required_fields = [physician, physicist, patient_age, current_site, current_dose, current_fractions]
        all_fields_filled = all(str(field) != "" and str(field) != "0" for field in required_fields)
        
        # Check if we have at least one prior treatment
        has_prior_treatments = len(st.session_state.prior_treatments) > 0
        
        # Show missing fields if any
        if generate_pressed and not all_fields_filled:
            st.error("Please fill in all required fields before generating the write-up.")
            for i, field in enumerate([physician, physicist, patient_age, current_site, current_dose, current_fractions]):
                if str(field) == "" or str(field) == "0":
                    field_names = ["Physician Name", "Physicist Name", "Patient Age", 
                                   "Current Site", "Current Dose", "Current Fractions"]
                    st.warning(f"Missing required field: {field_names[i]}")
            return None
        
        if generate_pressed and not has_prior_treatments:
            st.warning("Please add at least one prior treatment.")
            return None
        
        # If all required fields are filled and button is pressed, generate the write-up
        if generate_pressed and all_fields_filled and has_prior_treatments:
            # Generate the write-up based on the template and input data
            write_up = self._generate_prior_dose_write_up(
                physician=physician,
                physicist=physicist,
                patient_details=patient_details,
                current_treatment={
                    "site": current_site,
                    "dose": current_dose,
                    "fractions": current_fractions,
                    "month": current_month,
                    "year": current_year
                },
                prior_treatments=st.session_state.prior_treatments,
                has_overlap=has_overlap,
                dose_calc_method=dose_calc_method
            )
            
            return write_up
        
        return None
    
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
            "thorax": {
                "Lung": "V20 < 30%",
                "Heart": "V25 < 10%",
                "Esophagus": "Mean < 34 Gy"
            },
            "breast": {
                "Lung": "V20 < 30%",
                "Heart": "V25 < 10%"
            },
            "lung": {
                "Lung": "V20 < 30%",
                "Heart": "V25 < 10%",
                "Esophagus": "Mean < 34 Gy",
                "Spinal Cord": "D0.03cc < 50 Gy"
            },
            "liver": {
                "Liver": "Mean < 30 Gy",
                "Kidneys": "Mean < 18 Gy",
                "Spinal Cord": "D0.03cc < 45 Gy"
            },
            "pancreas": {
                "Kidneys": "Mean < 18 Gy",
                "Liver": "Mean < 30 Gy",
                "Duodenum": "D0.03cc < 55 Gy",
                "Spinal Cord": "D0.03cc < 45 Gy"
            },
            "abdomen": {
                "Kidneys": "Mean < 18 Gy",
                "Liver": "Mean < 30 Gy",
                "Spinal Cord": "D0.03cc < 45 Gy"
            },
            "pelvis": {
                "Rectum": "V75 < 15%, V70 < 20%, V65 < 25%, V60 < 35%, V50 < 50%",
                "Bladder": "V80 < 15%, V75 < 25%, V70 < 35%, V65 < 50%",
                "Femoral Heads": "V50 < 5%",
                "Small Bowel": "V45 < 195cc"
            },
            "prostate": {
                "Rectum": "V75 < 15%, V70 < 20%, V65 < 25%, V60 < 35%, V50 < 50%",
                "Bladder": "V80 < 15%, V75 < 25%, V70 < 35%, V65 < 50%",
                "Femoral Heads": "V50 < 5%"
            },
            "endometrium": {
                "Rectum": "V60 < 35%, V50 < 50%",
                "Bladder": "V65 < 50%",
                "Small Bowel": "V45 < 195cc",
                "Femoral Heads": "V50 < 5%"
            },
            "cervix": {
                "Rectum": "V60 < 35%, V50 < 50%",
                "Bladder": "V65 < 50%",
                "Small Bowel": "V45 < 195cc",
                "Femoral Heads": "V50 < 5%"
            },
            "rectum": {
                "Bladder": "V65 < 50%",
                "Small Bowel": "V45 < 195cc",
                "Femoral Heads": "V50 < 5%"
            },
            "spine": {
                "Spinal Cord": "D0.03cc < 50 Gy"
            },
            "extremity": {
                "Tissue": "Max < 105% of prescription"
            }
        }
        
        return constraints.get(site.lower(), {})
    
    def display_write_up(self, write_up):
        """Display the generated write-up with a copy button."""
        if write_up:
            st.markdown("### Generated Write-Up")
            
            # Create a container with custom styling for better visibility
            with st.container():
                # Display in text area for viewing/editing
                st.text_area("", write_up, height=300, key="prior_dose_result", label_visibility="collapsed")
                
                # Add a tooltip with copy instructions
                st.info("💡 To copy: Click inside the text box, use Ctrl+A (or Cmd+A on Mac) to select all, then Ctrl+C (or Cmd+C) to copy.")
                
                # Optional: Add download button
                st.download_button(
                    label="Download as Text File",
                    data=write_up,
                    file_name="prior_dose_write_up.txt",
                    mime="text/plain"
                )