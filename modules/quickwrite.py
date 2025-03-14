import streamlit as st
from .templates import ConfigManager
from .dibh import DIBHModule
from .fusion import FusionModule
from .prior_dose import PriorDoseModule
from .pacemaker import PacemakerModule
from .sbrt import SBRTModule
from .srs import SRSModule
from .quickwrite_orchestrator import QuickWriteOrchestrator

class QuickWriteModule:
    def __init__(self):
        """Initialize the Quick Write module."""
        self.config_manager = ConfigManager()
        
        # Initialize all modules - refactored ones use the base class
        self.dibh_module = DIBHModule(self.config_manager)
        self.fusion_module = FusionModule(self.config_manager)
        self.prior_dose_module = PriorDoseModule(self.config_manager)
        
        # Legacy modules - will be refactored in future phases
        self.pacemaker_module = PacemakerModule() 
        self.sbrt_module = SBRTModule()
        self.srs_module = SRSModule()
        
        # Create module dictionary for the orchestrator with refactored modules
        self.modules = {
            "dibh": self.dibh_module,
            "fusion": self.fusion_module,
            "prior_dose": self.prior_dose_module,
            # Other modules will be added as they're refactored
        }
        
        # Initialize the orchestrator
        self.orchestrator = QuickWriteOrchestrator(self.modules)
    
    def render_unified_workflow(self):
        """Render the unified workflow for multiple write-ups."""
        return self.orchestrator.render_workflow()
    
    # Legacy methods for backward compatibility - these will be gradually removed
        
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