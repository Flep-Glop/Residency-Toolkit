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
        
        # Typical SRS fractionation for brain
        if site == "brain" and fractions == 1:
            if dose < 12 or dose > 24:
                return False, f"Single fraction SRS for brain typically uses 12-24 Gy (got {dose} Gy)"
        
        # Typical SBRT fractionation for lung
        elif site == "lung" and 3 <= fractions <= 5:
            if dose < 45 or dose > 60:
                return False, f"SBRT for lung typically uses 45-60 Gy in 3-5 fractions (got {dose} Gy)"
        
        # Typical breast fractionation
        elif site in ["breast", "left breast", "right breast"] and fractions > 10:
            if dose_per_fraction < 1.8 or dose_per_fraction > 2.7:
                return True, f"Breast dose/fraction ({dose_per_fraction:.2f} Gy) suggests {'hypofractionation' if dose_per_fraction > 2.0 else 'conventional fractionation'}"
    
    # Provide fractionation schema description
    if dose_per_fraction <= 2.0:
        return True, "Conventional fractionation"
    elif 2.0 < dose_per_fraction <= 5.0:
        return True, "Moderate hypofractionation"
    elif 5.0 < dose_per_fraction <= 10.0:
        return True, "Hypofractionation (SBRT range)"
    else:
        return True, "Extreme hypofractionation (SRS/SBRT range)"