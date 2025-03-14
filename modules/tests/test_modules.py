import unittest
import sys
import os
from unittest.mock import MagicMock, patch

# Add the parent directory to the path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import modules to test
from modules.base_module import BaseWriteUpModule
from modules.templates import ConfigManager
from validation_utils import FormValidator, validate_dose_fractionation

# Mock classes for testing
class MockModule(BaseWriteUpModule):
    """Mock implementation of BaseWriteUpModule for testing."""
    
    def __init__(self, config_manager):
        super().__init__(config_manager)
    
    def get_module_name(self):
        return "Mock Module"
    
    def get_module_description(self):
        return "A mock module for testing"
    
    def get_required_fields(self):
        return ["field1", "field2"]
    
    def render_specialized_fields(self, physician, physicist, patient_age, patient_sex, patient_details):
        # Return mock data
        return {
            "field1": "value1",
            "field2": "value2"
        }
    
    def generate_write_up(self, common_info, module_data):
        # Generate a mock write-up
        physician = common_info.get("physician", "")
        physicist = common_info.get("physicist", "")
        patient_details = common_info.get("patient_details", "")
        
        field1 = module_data.get("field1", "")
        field2 = module_data.get("field2", "")
        
        return f"Write-up for {patient_details} by Dr. {physician} and Dr. {physicist} with {field1} and {field2}"


class TestBaseModule(unittest.TestCase):
    """Test cases for the BaseWriteUpModule class and implementations."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config_manager = MagicMock()
        self.config_manager.get_physicians.return_value = ["Smith", "Jones"]
        self.config_manager.get_physicists.return_value = ["Brown", "Davis"]
        
        self.mock_module = MockModule(self.config_manager)
        
        # Common test data
        self.common_info = {
            "physician": "Smith",
            "physicist": "Brown",
            "patient_age": 45,
            "patient_sex": "female",
            "patient_details": "a 45-year-old female"
        }
        
        self.module_data = {
            "field1": "value1",
            "field2": "value2"
        }
    
    def test_module_initialization(self):
        """Test that modules initialize correctly with config manager."""
        self.assertEqual(self.mock_module.get_module_name(), "Mock Module")
        self.assertEqual(self.mock_module.get_description(), "A mock module for testing")
        self.assertEqual(self.mock_module.get_required_fields(), ["field1", "field2"])
    
    def test_generate_write_up(self):
        """Test that write-up generation works correctly."""
        write_up = self.mock_module.generate_write_up(self.common_info, self.module_data)
        expected = "Write-up for a 45-year-old female by Dr. Smith and Dr. Brown with value1 and value2"
        self.assertEqual(write_up, expected)
    
    @patch('streamlit.selectbox')
    @patch('streamlit.number_input')
    def test_specialized_fields(self, mock_number_input, mock_selectbox):
        """Test rendering of specialized fields."""
        # Configure mocks
        mock_selectbox.return_value = "Smith"
        mock_number_input.return_value = 45
        
        # Call the method
        result = self.mock_module.render_specialized_fields(
            "Smith", "Brown", 45, "female", "a 45-year-old female"
        )
        
        # Check the result
        self.assertEqual(result, {"field1": "value1", "field2": "value2"})


class TestValidationUtils(unittest.TestCase):
    """Test cases for the ValidationUtils class."""
    
    def test_validate_dose_fractionation(self):
        """Test dose and fractionation validation rules."""
        # Test invalid inputs
        is_valid, message = validate_dose_fractionation(0, 1)
        self.assertFalse(is_valid)
        
        # Test excessive dose per fraction
        is_valid, message = validate_dose_fractionation(30, 1)
        self.assertFalse(is_valid)
        
        # Test conventional fractionation
        is_valid, message = validate_dose_fractionation(60, 30)
        self.assertTrue(is_valid)
        self.assertIn("Conventional fractionation", message)
        
        # Test hypofractionation
        is_valid, message = validate_dose_fractionation(40, 15)
        self.assertTrue(is_valid)
        self.assertIn("Moderate hypofractionation", message)
        
        # Test SBRT range
        is_valid, message = validate_dose_fractionation(50, 5)
        self.assertTrue(is_valid)
        self.assertIn("SBRT range", message)
        
        # Test SRS range
        is_valid, message = validate_dose_fractionation(18, 1)
        self.assertTrue(is_valid)
        self.assertIn("Extreme hypofractionation", message)
        
        # Test with specific site - brain SRS
        is_valid, message = validate_dose_fractionation(18, 1, "brain")
        self.assertTrue(is_valid)
        
        # Test with specific site - brain SRS over max
        is_valid, message = validate_dose_fractionation(30, 1, "brain")
        self.assertFalse(is_valid)
        
        # Test with specific site - lung SBRT
        is_valid, message = validate_dose_fractionation(50, 5, "lung")
        self.assertTrue(is_valid)
    
    def test_form_validator(self):
        """Test FormValidator functionality."""
        validator = FormValidator()
        
        # Test required field validation
        self.assertFalse(validator.validate_required_field("", "Test Field"))
        self.assertTrue(validator.validate_required_field("value", "Test Field"))
        
        # Test numeric range validation
        self.assertFalse(validator.validate_required_field(5, "Number Field", min_value=10))
        self.assertTrue(validator.validate_required_field(15, "Number Field", min_value=10))
        self.assertFalse(validator.validate_required_field(15, "Number Field", max_value=10))
        
        # Test conditional validation
        self.assertTrue(validator.validate_conditional_field(False, "", "Conditional Field"))
        self.assertFalse(validator.validate_conditional_field(True, "", "Conditional Field"))
        
        # Test warning functionality
        validator.add_warning("This is a warning")
        self.assertEqual(len(validator.warnings), 1)
        self.assertEqual(validator.warnings[0], "This is a warning")
        
        # Test clinical validation
        self.assertTrue(validator.validate_clinical_values(5, "Clinical Field", (0, 10)))
        self.assertFalse(validator.validate_clinical_values(15, "Clinical Field", (0, 10)))
        
        # Test with warning range
        validator = FormValidator()
        self.assertTrue(validator.validate_clinical_values(5, "Clinical Field", (0, 10), (3, 7)))
        self.assertEqual(len(validator.warnings), 0)
        
        validator = FormValidator()
        self.assertTrue(validator.validate_clinical_values(8, "Clinical Field", (0, 10), (3, 7)))
        self.assertEqual(len(validator.warnings), 1)


if __name__ == "__main__":
    unittest.main()