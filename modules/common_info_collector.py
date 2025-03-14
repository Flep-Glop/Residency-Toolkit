import streamlit as st

def collect_common_info(config_manager, existing_data=None):
    """Collect and validate common information.
    
    Args:
        config_manager: The configuration manager for physician/physicist lists
        existing_data: Optional dict with existing data to pre-fill fields
        
    Returns:
        dict: The collected common information, or None if not complete
    """
    # Create two columns for the form fields
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Staff Information")
        
        # Pre-fill values if they exist
        default_physician = existing_data.get("physician", "") if existing_data else ""
        physicians = config_manager.get_physicians()
        physician_index = physicians.index(default_physician) if default_physician in physicians else 0
        
        physician = st.selectbox(
            "Physician Name", 
            physicians,
            index=physician_index,
            key="common_physician"
        )
        
        default_physicist = existing_data.get("physicist", "") if existing_data else ""
        physicists = config_manager.get_physicists()
        physicist_index = physicists.index(default_physicist) if default_physicist in physicists else 0
        
        physicist = st.selectbox(
            "Physicist Name", 
            physicists,
            index=physicist_index,
            key="common_physicist"
        )
    
    with col2:
        st.markdown("#### Patient Information")
        
        default_age = existing_data.get("patient_age", 0) if existing_data else 0
        patient_age = st.number_input(
            "Patient Age", 
            min_value=0, 
            max_value=120, 
            value=default_age,
            key="common_age"
        )
        
        default_sex = existing_data.get("patient_sex", "male") if existing_data else "male"
        sex_options = ["male", "female", "other"]
        sex_index = sex_options.index(default_sex) if default_sex in sex_options else 0
        
        patient_sex = st.selectbox(
            "Patient Sex", 
            sex_options,
            index=sex_index,
            key="common_sex"
        )
    
    # Validate all fields are filled
    all_filled = all([physician, physicist, patient_age > 0])
    
    # Show validation messages if not all fields are filled
    if not all_filled:
        missing_fields = []
        if not physician:
            missing_fields.append("Physician Name")
        if not physicist:
            missing_fields.append("Physicist Name")
        if patient_age <= 0:
            missing_fields.append("Patient Age")
            
        if missing_fields:
            st.warning(f"Please fill in all required fields: {', '.join(missing_fields)}")
            return None
    
    # Return the collected data
    return {
        "physician": physician,
        "physicist": physicist,
        "patient_age": patient_age,
        "patient_sex": patient_sex,
        "patient_details": f"a {patient_age}-year-old {patient_sex}"
    }