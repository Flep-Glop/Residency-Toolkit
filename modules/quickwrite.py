import streamlit as st
from .templates import TemplateManager, ConfigManager
from .fusion import FusionModule
from .prior_dose import PriorDoseModule
from .pacemaker import PacemakerModule
from .sbrt import SBRTModule
from .srs import SRSModule
from .dibh import DIBHModule

class QuickWriteModule:
    def __init__(self):
        """Initialize the Quick Write module."""
        self.template_manager = TemplateManager()
        self.config_manager = ConfigManager()
        self.dibh_module = DIBHModule()
        self.fusion_module = FusionModule()
        self.prior_dose_module = PriorDoseModule()
        self.pacemaker_module = PacemakerModule()
        self.sbrt_module = SBRTModule()
        self.srs_module = SRSModule()
        
    def render_dibh_form(self):
        """Delegate to the DIBHModule for DIBH write-ups."""
        return self.dibh_module.render_dibh_form()

    def render_fusion_form(self):
        """Delegate to the FusionModule for enhanced fusion write-ups."""
        return self.fusion_module.render_fusion_form()
    
    def render_prior_dose_form(self):
        """Delegate to the PriorDoseModule for prior dose write-ups."""
        return self.prior_dose_module.render_prior_dose_form()
    
    def render_pacemaker_form(self):
        """Delegate to the PacemakerModule for pacemaker write-ups."""
        return self.pacemaker_module.render_pacemaker_form()
    
    def render_sbrt_form(self):
        """Delegate to the SBRTModule for SBRT write-ups."""
        return self.sbrt_module.render_sbrt_form()
    
    def render_srs_form(self):
        """Delegate to the SRSModule for SRS write-ups."""
        return self.srs_module.render_srs_form()
    
    def display_write_up(self, write_up):
        """Display the generated write-up with a copy button."""
        if write_up:
            st.markdown("### Generated Write-Up")
            
            # Create a container with custom styling for better visibility
            with st.container():
                # Display in text area for viewing/editing
                st.text_area("", write_up, height=300, key="result", label_visibility="collapsed")
                
                # Add a tooltip with copy instructions
                st.info("💡 To copy: Click inside the text box, use Ctrl+A (or Cmd+A on Mac) to select all, then Ctrl+C (or Cmd+C) to copy.")
                
                # Optional: Add download button
                st.download_button(
                    label="Download as Text File",
                    data=write_up,
                    file_name="write_up.txt",
                    mime="text/plain"
                )