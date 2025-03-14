from abc import ABC, abstractmethod
import streamlit as st

class BaseWriteUpModule(ABC):
    """Base class for all write-up modules."""
    
    def __init__(self, config_manager):
        """Initialize with the config manager."""
        self.config_manager = config_manager
    
    @abstractmethod
    def render_specialized_fields(self, physician, physicist, patient_age, patient_sex, patient_details):
        """Render module-specific input fields and return the generated data.
        
        Must be implemented by subclasses.
        
        Args:
            physician: The selected physician name
            physicist: The selected physicist name
            patient_age: The patient's age
            patient_sex: The patient's sex
            patient_details: Formatted patient details string
            
        Returns:
            dict: Collected module-specific data
        """
        pass
    
    @abstractmethod
    def generate_write_up(self, common_info, module_data):
        """Generate the write-up text from common info and module-specific data.
        
        Must be implemented by subclasses.
        
        Args:
            common_info: Dict with common patient and staff information
            module_data: Dict with module-specific data
            
        Returns:
            str: The generated write-up text
        """
        pass
    
    @abstractmethod
    def get_module_name(self):
        """Return the display name of this module."""
        pass
    
    @abstractmethod
    def get_module_description(self):
        """Return a brief description of this module."""
        pass
    
    @abstractmethod
    def get_required_fields(self):
        """Return a list of required field names for this module."""
        pass
    
    def display_write_up(self, write_up):
        """Display the generated write-up with a copy button."""
        if write_up:
            st.markdown("### Generated Write-Up")
            
            # Create a container with custom styling for better visibility
            with st.container():
                # Display in text area for viewing/editing
                st.text_area("", write_up, height=300, key=f"{self.get_module_name().lower()}_result", label_visibility="collapsed")
                
                # Add a tooltip with copy instructions
                st.info("💡 To copy: Click inside the text box, use Ctrl+A (or Cmd+A on Mac) to select all, then Ctrl+C (or Cmd+C) to copy.")
                
                # Optional: Add download button
                st.download_button(
                    label="Download as Text File",
                    data=write_up,
                    file_name=f"{self.get_module_name().lower()}_write_up.txt",
                    mime="text/plain"
                )