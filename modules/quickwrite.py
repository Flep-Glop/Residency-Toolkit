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
    """Main module for generating various medical physics write-ups.
    
    This module serves as a central entry point for all write-up generators,
    handling both the legacy independent write-up interfaces and the new unified workflow.
    """
    
    def __init__(self):
        """Initialize the Quick Write module with all supported write-up types."""
        self.config_manager = ConfigManager()
        
        # Initialize all modules using the refactored architecture
        self.dibh_module = DIBHModule(self.config_manager)
        self.fusion_module = FusionModule(self.config_manager)
        self.prior_dose_module = PriorDoseModule(self.config_manager)
        self.pacemaker_module = PacemakerModule(self.config_manager)
        self.sbrt_module = SBRTModule(self.config_manager)
        self.srs_module = SRSModule(self.config_manager)
        
        # Create module dictionary for the orchestrator with all modules
        self.modules = {
            "dibh": self.dibh_module,
            "fusion": self.fusion_module,
            "prior_dose": self.prior_dose_module,
            "pacemaker": self.pacemaker_module,
            "sbrt": self.sbrt_module,
            "srs": self.srs_module
        }
        
        # Initialize the orchestrator for the unified workflow
        self.orchestrator = QuickWriteOrchestrator(self.modules)
    
    def render_unified_workflow(self):
        """Render the unified workflow for multiple write-ups."""
        try:
            return self.orchestrator.render_workflow()
        except Exception as e:
            self._handle_error("Error in unified workflow", e)
            return None
    
    # Legacy methods for backward compatibility - these will be gradually removed
    
    def render_dibh_form(self):
        """Delegate to the DIBHModule for DIBH write-ups."""
        try:
            return self.dibh_module.render_dibh_form()
        except Exception as e:
            self._handle_error("Error in DIBH module", e)
            return None

    def render_fusion_form(self):
        """Delegate to the FusionModule for enhanced fusion write-ups."""
        try:
            return self.fusion_module.render_fusion_form()
        except Exception as e:
            self._handle_error("Error in Fusion module", e)
            return None
    
    def render_prior_dose_form(self):
        """Delegate to the PriorDoseModule for prior dose write-ups."""
        try:
            return self.prior_dose_module.render_prior_dose_form()
        except Exception as e:
            self._handle_error("Error in Prior Dose module", e)
            return None
    
    def render_pacemaker_form(self):
        """Delegate to the PacemakerModule for pacemaker write-ups."""
        try:
            return self.pacemaker_module.render_pacemaker_form()
        except Exception as e:
            self._handle_error("Error in Pacemaker module", e)
            return None
    
    def render_sbrt_form(self):
        """Delegate to the SBRTModule for SBRT write-ups."""
        try:
            return self.sbrt_module.render_sbrt_form()
        except Exception as e:
            self._handle_error("Error in SBRT module", e)
            return None
    
    def render_srs_form(self):
        """Delegate to the SRSModule for SRS write-ups."""
        try:
            return self.srs_module.render_srs_form()
        except Exception as e:
            self._handle_error("Error in SRS module", e)
            return None
    
    def _handle_error(self, context, exception):
        """Handle exceptions with user-friendly error messages.
        
        Args:
            context: String describing where the error occurred
            exception: The exception that was raised
        """
        import traceback
        
        # Log the full error for debugging
        error_details = traceback.format_exc()
        print(f"ERROR in {context}: {str(exception)}\n{error_details}")
        
        # Show a user-friendly error message
        st.error(f"**{context}**: {str(exception)}")
        
        # In development mode, show full traceback
        if st.session_state.get("developer_mode", False):
            with st.expander("Error Details (Developer View)", expanded=False):
                st.code(error_details)
                
        # Offer recovery options
        st.info("You can try refreshing the page or contact support if the issue persists.")
        
        # Add a button to reset session state (as a last resort)
        if st.button("Reset Application"):
            for key in list(st.session_state.keys()):
                if key != "developer_mode":  # Preserve developer mode setting
                    del st.session_state[key]
            st.rerun()