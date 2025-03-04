import streamlit as st
from datetime import datetime
from .templates import TemplateManager, ConfigManager

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
                                         step=0.1,
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
                                          step=0.1,
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
    
    def _generate_prior_dose_write_up(self, physician, physicist, patient_details, current_treatment, 
                                     prior_treatments, has_overlap, dose_calc_method):
        """Generate the prior dose write-up text based on the inputs."""
        
        # Start with the introduction
        write_up = f"Dr. {physician} requested a medical physics consultation for {patient_details}. "
        write_up += "The consultation is about a dosimetric analysis for planning guidance, given that the patient had "
        write_up += "previously received radiation (patient re-treatment), including dose reconstruction and composite planning.\n\n"
        
        # Add current treatment details
        write_up += f"In {current_treatment['month']} of {current_treatment['year']}, the patient received external beam "
        write_up += f"radiotherapy for {current_treatment['dose']} Gy in {current_treatment['fractions']} fractions to the "
        write_up += f"{current_treatment['site']}. "
        
        # Add prior treatments
        for treatment in prior_treatments:
            write_up += f"In {treatment['month']} of {treatment['year']}, the patient received external beam "
            write_up += f"radiotherapy for {treatment['dose']} Gy in {treatment['fractions']} fractions to the "
            write_up += f"{treatment['site']}. "
        
        # Add overlap information
        if has_overlap == "No":
            write_up += "There is no significant overlap between the treatments. "
        else:
            if dose_calc_method == "Raw Dose":
                write_up += "The dose volumes were then summed, showing a significant overlap between the treatments. (DOSE STATS) "
            else:  # EQD2
                write_up += "The doses were converted to equivalent dose in 2 Gy fractions (EQD2) with an alpha/beta ratio of "
                write_up += "2 for the spinal cord and 3 for all other structures. The EQD2 volumes were then summed, "
                write_up += "showing a significant overlap between the treatments. (DOSE STATS) "
        
        # Add conclusion
        write_up += f"The findings were reviewed and approved by Dr. {physician} and Dr. {physicist}."
        
        return write_up
    
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