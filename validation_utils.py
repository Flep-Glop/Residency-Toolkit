import streamlit as st

class FormValidator:
    """Utility class for form validation with improved error handling."""
    
    def __init__(self):
        """Initialize the validator."""
        self.errors = []
        self.warnings = []
    
    def validate_required_field(self, value, field_name, min_value=None, max_value=None):
        """Validate a required field with optional range validation.
        
        Args:
            value: The field value to validate
            field_name: The display name of the field
            min_value: Optional minimum value for numeric fields
            max_value: Optional maximum value for numeric fields
            
        Returns:
            bool: True if validation passed, False otherwise
        """
        # Check if the value is empty or zero
        if value in (None, "", 0):
            self.errors.append(f"Missing required field: {field_name}")
            return False
        
        # Range validation for numeric fields
        if min_value is not None and isinstance(value, (int, float)):
            if value < min_value:
                self.errors.append(f"{field_name} must be at least {min_value}")
                return False
                
        if max_value is not None and isinstance(value, (int, float)):
            if value > max_value:
                self.errors.append(f"{field_name} must not exceed {max_value}")
                return False
        
        return True
    
    def validate_conditional_field(self, condition, value, field_name, error_message=None):
        """Validate a field that is required only under certain conditions.
        
        Args:
            condition: Boolean indicating if the field is required
            value: The field value to validate
            field_name: The display name of the field
            error_message: Optional custom error message
            
        Returns:
            bool: True if validation passed, False otherwise
        """
        if condition and value in (None, "", 0):
            msg = error_message or f"Missing required field: {field_name}"
            self.errors.append(msg)
            return False
        return True
    
    def add_warning(self, message):
        """Add a warning message that doesn't fail validation but should be displayed.
        
        Args:
            message: The warning message to display
        """
        self.warnings.append(message)
    
    def validate_clinical_values(self, value, field_name, expected_range, warning_range=None):
        """Validate clinical values with expected ranges and optional warning ranges.
        
        Args:
            value: The clinical value to validate
            field_name: The display name of the clinical value
            expected_range: Tuple of (min, max) for expected range
            warning_range: Optional tuple of (min, max) for warning range
            
        Returns:
            bool: True if validation passed, False otherwise
        """
        min_expected, max_expected = expected_range
        
        # Hard validation against expected range
        if value < min_expected or value > max_expected:
            self.errors.append(f"{field_name} ({value}) is outside expected range ({min_expected}-{max_expected})")
            return False
        
        # Soft validation with warnings
        if warning_range:
            min_warning, max_warning = warning_range
            if value < min_warning or value > max_warning:
                self.add_warning(f"{field_name} ({value}) is unusual - please verify")
        
        return True
    
    def display_validation_results(self, override_option=True):
        """Display validation errors and warnings in the Streamlit UI.
        
        Args:
            override_option: Whether to show an override checkbox for errors
            
        Returns:
            bool: True if validation passed or was overridden, False otherwise
        """
        if not self.errors and not self.warnings:
            return True
        
        if self.errors:
            with st.container():
                st.error("Please fix the following errors:")
                for error in self.errors:
                    st.markdown(f"- {error}")
                
                # Option to override validation in exceptional cases
                if override_option:
                    override = st.checkbox("Override validation (use with caution)")
                    if override:
                        st.warning("You're overriding validation checks. Ensure all information is clinically appropriate.")
                        return True
                return False
                
        if self.warnings:
            with st.container():
                st.warning("Please verify the following:")
                for warning in self.warnings:
                    st.markdown(f"- {warning}")
        
        # If there are only warnings (no errors), validation passes
        return True


def validate_dose_fractionation(dose, fractions, site=None):
    """Validate dose and fractionation combinations based on clinical guidelines.
    
    Args:
        dose: The total dose in Gy
        fractions: The number of fractions
        site: Optional treatment site for site-specific validation
        
    Returns:
        tuple: (is_valid, message) indicating if the combination is valid and why
    """
    if dose <= 0 or fractions <= 0:
        return False, "Dose and fractions must be greater than 0"
    
    dose_per_fraction = dose / fractions
    
    # General safety limits
    if dose_per_fraction > 20:
        return False, f"Dose per fraction ({dose_per_fraction:.2f} Gy) exceeds 20 Gy/fraction safety limit"
    
    # Site-specific validation
    if site:
        site = site.lower()
        
        # Brain/SRS specific validation
        if "brain" in site or any(region in site for region in ["frontal", "parietal", "temporal", "occipital", "cerebellum", "brainstem"]):
            if fractions == 1:  # Single fraction SRS
                if dose < 12:
                    return True, f"Dose ({dose} Gy) is below typical single-fraction SRS range (12-24 Gy)"
                if dose > 24:
                    return False, f"Single fraction SRS dose ({dose} Gy) exceeds typical maximum of 24 Gy"
                if dose > 15 and "brainstem" in site:
                    return False, f"Single fraction SRS dose ({dose} Gy) exceeds typical maximum of 15 Gy for brainstem"
            elif 2 <= fractions <= 5:  # Fractionated SRT
                if dose < 18:
                    return True, f"Dose ({dose} Gy) is below typical SRT range for {fractions} fractions"
                if dose > 35:
                    return False, f"SRT dose ({dose} Gy) exceeds typical maximum for {fractions} fractions"
        
        # Lung SBRT validation
        elif "lung" in site:
            if fractions <= 5:  # SBRT fractionation
                if dose < 30:
                    return True, f"Dose ({dose} Gy) is below typical lung SBRT range"
                if dose > 60:
                    return False, f"Lung SBRT dose ({dose} Gy) exceeds typical maximum of 60 Gy"
        
        # Breast validation
        elif "breast" in site:
            if fractions >= 15:  # Conventional or hypofractionated
                if dose_per_fraction > 2.75:
                    return False, f"Breast dose/fraction ({dose_per_fraction:.2f} Gy) exceeds typical maximum of 2.75 Gy/fraction"
            elif 5 <= fractions < 15:  # Hypofractionated
                if dose_per_fraction > 6.0:
                    return False, f"Hypofractionated breast dose/fraction ({dose_per_fraction:.2f} Gy) exceeds typical maximum of 6.0 Gy/fraction"
        
        # Prostate validation
        elif "prostate" in site:
            if fractions <= 5:  # SBRT
                if dose < 35:
                    return True, f"Prostate SBRT dose ({dose} Gy) is below typical range"
                if dose > 40:
                    return False, f"Prostate SBRT dose ({dose} Gy) exceeds typical maximum of 40 Gy for {fractions} fractions"
            elif fractions > 20:  # Conventional
                if dose < 70:
                    return True, f"Conventional prostate dose ({dose} Gy) is below typical range"
                if dose > 80:
                    return False, f"Conventional prostate dose ({dose} Gy) exceeds typical maximum of 80 Gy"
        
        # Liver SBRT validation  
        elif "liver" in site:
            if fractions <= 5:  # SBRT
                if dose < 30:
                    return True, f"Liver SBRT dose ({dose} Gy) is below typical range"
                if dose > 60:
                    return False, f"Liver SBRT dose ({dose} Gy) exceeds typical maximum of 60 Gy for {fractions} fractions"
    
    # Provide fractionation schema description based on dose per fraction
    if dose_per_fraction <= 2.0:
        return True, "Conventional fractionation"
    elif 2.0 < dose_per_fraction <= 5.0:
        return True, "Moderate hypofractionation"
    elif 5.0 < dose_per_fraction <= 10.0:
        return True, "Hypofractionation (SBRT range)"
    else:
        return True, "Extreme hypofractionation (SRS/SBRT range)"


def validate_treatment_site_consistency(treatment_site, dose, fractions):
    """Validate that the treatment site is consistent with the dose/fractionation.
    
    Args:
        treatment_site: The anatomical treatment site
        dose: The total dose in Gy
        fractions: The number of fractions
        
    Returns:
        tuple: (is_valid, message) indicating if the combination is valid and why
    """
    treatment_site = treatment_site.lower() if isinstance(treatment_site, str) else ""
    
    # Calculate dose per fraction
    dose_per_fraction = dose / fractions if fractions > 0 else 0
    
    # SRS/SRT (brain) validation
    if any(site in treatment_site for site in ["brain", "frontal", "parietal", "temporal", "occipital", "cerebellum"]):
        if fractions == 1 and dose < 12:
            return False, f"Single fraction brain treatment with {dose} Gy is below typical SRS range (12-24 Gy)"
            
        if fractions > 5 and dose_per_fraction > 3:
            return False, f"Brain treatments with >5 fractions typically use ≤3 Gy/fraction (got {dose_per_fraction:.2f} Gy)"
    
    # SBRT validation for non-brain sites
    elif fractions <= 5 and dose_per_fraction >= 6:
        if any(site in treatment_site for site in ["breast", "head and neck", "pelvis"]):
            return False, f"SBRT with {dose_per_fraction:.2f} Gy/fraction is not typically used for {treatment_site}"
    
    # Conventional validation
    elif fractions >= 25 and dose_per_fraction < 1.8:
        if any(site in treatment_site for site in ["lung nodule", "liver metastasis", "bone metastasis"]):
            return True, f"Consider hypofractionation for {treatment_site} instead of conventional fractionation"
    
    return True, ""


class ClinicalValidationRules:
    """Repository of clinical validation rules for different treatment scenarios."""
    
    @staticmethod
    def get_organ_dose_constraints(organ, treatment_type="conventional"):
        """Get dose constraints for specific organs at risk.
        
        Args:
            organ: The organ name
            treatment_type: The treatment type (conventional, sbrt, srs)
            
        Returns:
            dict: Constraints for the organ
        """
        # Standardize inputs
        organ = organ.lower()
        treatment_type = treatment_type.lower()
        
        # Base constraints dictionary
        constraints = {
            # Brain/head & neck constraints
            "brain": {
                "conventional": {"mean": 45, "max": 60, "unit": "Gy"},
                "srs": {"max": 12, "unit": "Gy"},
            },
            "brainstem": {
                "conventional": {"max": 54, "unit": "Gy"},
                "sbrt": {"max": 23, "unit": "Gy"},
                "srs": {"max": 15, "unit": "Gy"},
            },
            "optic chiasm": {
                "conventional": {"max": 54, "unit": "Gy"},
                "srs": {"max": 10, "unit": "Gy"},
            },
            "optic nerve": {
                "conventional": {"max": 54, "unit": "Gy"},
                "srs": {"max": 10, "unit": "Gy"},
            },
            "cochlea": {
                "conventional": {"mean": 45, "unit": "Gy"},
            },
            "parotid": {
                "conventional": {"mean": 26, "unit": "Gy"},
            },
            
            # Thoracic constraints
            "heart": {
                "conventional": {"mean": 26, "unit": "Gy"},
                "sbrt": {"max": 30, "unit": "Gy"},
            },
            "lung": {
                "conventional": {"v20": 30, "unit": "%"},
                "sbrt": {"v20": 10, "unit": "%"},
            },
            "esophagus": {
                "conventional": {"mean": 34, "unit": "Gy"},
                "sbrt": {"max": 27, "unit": "Gy"},
            },
            "spinal cord": {
                "conventional": {"max": 50, "unit": "Gy"},
                "sbrt": {"max": 18, "unit": "Gy"},
                "srs": {"max": 14, "unit": "Gy"},
            },
            
            # Abdominal constraints
            "liver": {
                "conventional": {"mean": 30, "unit": "Gy"},
                "sbrt": {"v15": 700, "unit": "cc"},
            },
            "kidney": {
                "conventional": {"mean": 18, "unit": "Gy"},
                "sbrt": {"v12": 25, "unit": "%"},
            },
            "bowel": {
                "conventional": {"max": 50, "unit": "Gy"},
                "sbrt": {"max": 27, "unit": "Gy"},
            },
            
            # Pelvic constraints
            "rectum": {
                "conventional": {"v70": 20, "unit": "%"},
                "sbrt": {"v36": 1, "unit": "cc"},
            },
            "bladder": {
                "conventional": {"v70": 35, "unit": "%"},
                "sbrt": {"v37": 10, "unit": "cc"},
            },
        }
        
        # Return the constraints if found
        if organ in constraints and treatment_type in constraints[organ]:
            return constraints[organ][treatment_type]
        
        return None