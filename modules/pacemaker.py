import streamlit as st
from .templates import TemplateManager, ConfigManager

class PacemakerModule:
    def __init__(self):
        """Initialize the Pacemaker module."""
        self.template_manager = TemplateManager()
        self.config_manager = ConfigManager()
        
        # Common treatment sites
        self.treatment_sites = [
            "brain", "head and neck", "thorax", "breast", "lung", 
            "liver", "pancreas", "abdomen", "pelvis", "prostate", 
            "endometrium", "cervix", "rectum", "spine", "extremity"
        ]
        
        # Common device vendors
        self.device_vendors = [
            "Medtronic", "Boston Scientific", "Abbott/St. Jude Medical", 
            "Biotronik", "MicroPort", "ZOLL"
        ]
        
    def render_pacemaker_form(self):
        """Render the form for pacemaker write-ups."""
        st.subheader("Pacemaker Write-Up Generator")
        
        # Two-column layout for efficient use of space
        col1, col2 = st.columns(2)
        
        with col1:
            # Staff information
            st.markdown("#### Staff Information")
            physician = st.selectbox("Physician Name", 
                                    self.config_manager.get_physicians(), 
                                    key="pacemaker_physician")
            physicist = st.selectbox("Physicist Name", 
                                    self.config_manager.get_physicists(), 
                                    key="pacemaker_physicist")
            
            # Patient information
            st.markdown("#### Patient Information")
            patient_age = st.number_input("Patient Age", min_value=0, max_value=120, key="pacemaker_age")
            patient_sex = st.selectbox("Patient Sex", ["male", "female", "other"], key="pacemaker_sex")
            patient_details = f"a {patient_age}-year-old {patient_sex}"
        
        with col2:
            # Treatment information
            st.markdown("#### Treatment Information")
            treatment_site = st.selectbox("Treatment Site", 
                                        self.treatment_sites, 
                                        key="pacemaker_site")
            
            dose = st.number_input("Prescription Dose (Gy)", min_value=0.0, value=45.0, step=0.1, key="pacemaker_dose")
            fractions = st.number_input("Number of Fractions", min_value=1, value=15, key="pacemaker_fractions")
        
        # Pacemaker details
        st.markdown("#### Pacemaker Information")
        col1, col2 = st.columns(2)
        
        with col1:
            device_vendor = st.selectbox("Device Vendor", 
                                        self.device_vendors + ["Other"],
                                        key="device_vendor")
            
            if device_vendor == "Other":
                custom_vendor = st.text_input("Custom Vendor", key="custom_vendor")
                device_vendor = custom_vendor if custom_vendor else "the vendor"
            
            device_model = st.text_input("Device Make/Model", key="device_model")
            device_serial = st.text_input("Device Serial Number", key="device_serial")
            
        with col2:
            pacing_dependent = st.radio("Pacing Dependent?", 
                                     ["Yes", "No", "Unknown"],
                                     key="pacing_dependent")
            
            # Risk level selection
            risk_level = st.selectbox("Risk Level", 
                                    ["Low", "Medium", "High"],
                                    key="risk_level")
            
            # TPS calculated doses
            tps_max_dose = st.number_input("TPS Maximum Dose to Device (Gy)", 
                                         min_value=0.0, 
                                         max_value=10.0,
                                         value=0.5,
                                         step=0.1,
                                         key="tps_max_dose")
            
            tps_mean_dose = st.number_input("TPS Mean Dose to Device (Gy)", 
                                          min_value=0.0, 
                                          max_value=10.0,
                                          value=0.2,
                                          step=0.1,
                                          key="tps_mean_dose")
            
        # OSLD measurement
        st.markdown("#### Dosimetry Measurements")
        osld_mean_dose = st.number_input("OSLD Measured Mean Dose (Gy)", 
                                       min_value=0.0, 
                                       max_value=10.0,
                                       value=0.0,
                                       step=0.01,
                                       key="osld_mean_dose")
        
        # Generate button
        generate_pressed = st.button("Generate Write-Up", type="primary", key="pacemaker_generate")
        
        # Check if we have all required information and the button was pressed
        required_fields = [
            physician, physicist, patient_age, treatment_site, dose, fractions,
            device_vendor, risk_level, tps_max_dose, tps_mean_dose
        ]
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
            if not device_vendor or (device_vendor == "Other" and not custom_vendor):
                missing_fields.append("Device Vendor")
            if not risk_level:
                missing_fields.append("Risk Level")
            if tps_max_dose == 0:
                missing_fields.append("TPS Maximum Dose")
            if tps_mean_dose == 0:
                missing_fields.append("TPS Mean Dose")
                
            for field in missing_fields:
                st.warning(f"Missing required field: {field}")
                
            return None
        
        # If all required fields are filled and button is pressed, generate the write-up
        if generate_pressed and all_fields_filled:
            # Generate write-up based on inputs
            write_up = self._generate_pacemaker_write_up(
                physician=physician,
                physicist=physicist,
                patient_details=patient_details,
                treatment_site=treatment_site,
                dose=dose,
                fractions=fractions,
                device_vendor=device_vendor,
                device_model=device_model,
                device_serial=device_serial,
                pacing_dependent=pacing_dependent,
                risk_level=risk_level,
                tps_max_dose=tps_max_dose,
                tps_mean_dose=tps_mean_dose,
                osld_mean_dose=osld_mean_dose
            )
            
            return write_up
        
        return None
    
    def _generate_pacemaker_write_up(self, physician, physicist, patient_details, 
                                   treatment_site, dose, fractions, device_vendor,
                                   device_model, device_serial, pacing_dependent,
                                   risk_level, tps_max_dose, tps_mean_dose, 
                                   osld_mean_dose):
        """Generate the pacemaker write-up based on the inputs."""
        
        # Format model and serial info
        model_text = f"model number {device_model}" if device_model else "implanted cardiac device"
        serial_text = f"serial number {device_serial}" if device_serial else ""
        if model_text and serial_text:
            device_info = f"{model_text}, {serial_text},"
        elif model_text:
            device_info = f"{model_text},"
        elif serial_text:
            device_info = f"{serial_text},"
        else:
            device_info = ""
        
        # Format pacing dependent info
        if pacing_dependent == "Yes":
            pacing_text = "It is noted that they are pacing dependent."
        elif pacing_dependent == "No":
            pacing_text = "It is noted that they are not pacing dependent."
        else:
            pacing_text = ""
        
        # Basic write-up structure
        write_up = f"Dr. {physician} requested a medical physics consultation for {patient_details} "
        write_up += f"undergoing radiation treatment to their {treatment_site} for the dose of {dose} Gy in {fractions} fractions. "
        write_up += f"The patient has a {device_info} from {device_vendor}. {pacing_text}\n\n"
        
        write_up += "Our treatment plan follows the guidelines of the manufacturer for radiation therapy. "
        write_up += "No primary radiation fields intercept the pacemaker. The device was contoured in the treatment planning system. "
        write_up += f"The maximum dose to the device was {tps_max_dose} Gy, with a mean dose of {tps_mean_dose} Gy, "
        write_up += "which is well below the AAPM recommended total dose of 2 Gy.\n\n"
        
        write_up += "One potential complication with any pacemaker is that radiation could induce an increased sensor rate. "
        
        # Risk-level specific content
        if risk_level == "Low":
            write_up += f"However, our dosimetry analysis puts this patient at a low risk for any radiation induced cardiac complications. "
            write_up += "A defibrillator is always available during treatment in case of emergency. "
            write_up += "A heart rate monitor is then used to monitor for events that would require the defibrillator. "
            write_up += "The patient had their device interrogated before the start of treatment."
        elif risk_level == "Medium":
            write_up += f"However, our dosimetry analysis puts this patient at a medium risk for any radiation induced cardiac complications. "
            write_up += "A defibrillator is always available during treatment in case of emergency. "
            write_up += "A heart rate monitor is then used to monitor for events that would require the defibrillator. "
            write_up += "The patient had their device interrogated before the start of treatment and will have it "
            write_up += "interrogated again in the middle of treatment and after the end of treatment."
        else:  # High risk
            write_up += f"Our dosimetry analysis puts this patient at a high risk for radiation induced cardiac complications. "
            write_up += "A defibrillator is always available during treatment in case of emergency. "
            write_up += "A heart rate monitor is used to monitor for events that would require the defibrillator. "
            write_up += "The patient had their device interrogated before the start of treatment and will have it "
            write_up += "interrogated after each treatment fraction. A cardiologist is on standby during each treatment."
        
        # OSLD measurements
        if osld_mean_dose > 0:
            write_up += "\n\nOptically stimulated luminescence dosimeters (OSLDs) were placed on the patient's skin to record "
            write_up += f"the radiation dose to the device. The average dose received by these OSLDs was {osld_mean_dose} Gy, "
            total_osld = osld_mean_dose * fractions
            write_up += f"resulting in a total dose of {total_osld:.2f} Gy from the {fractions}-fraction treatment."
        
        # Final approval
        write_up += f"\n\nThis was reviewed by the prescribing radiation oncologist, Dr. {physician}, and the medical physicist, Dr. {physicist}."
        
        return write_up
    
    def display_write_up(self, write_up):
        """Display the generated write-up with a copy button."""
        if write_up:
            st.markdown("### Generated Write-Up")
            
            # Create a container with custom styling for better visibility
            with st.container():
                # Display in text area for viewing/editing
                st.text_area("", write_up, height=300, key="pacemaker_result", label_visibility="collapsed")
                
                # Add a tooltip with copy instructions
                st.info("💡 To copy: Click inside the text box, use Ctrl+A (or Cmd+A on Mac) to select all, then Ctrl+C (or Cmd+C) to copy.")
                
                # Optional: Add download button
                st.download_button(
                    label="Download as Text File",
                    data=write_up,
                    file_name="pacemaker_write_up.txt",
                    mime="text/plain"
                )