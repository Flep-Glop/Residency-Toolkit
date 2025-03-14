import streamlit as st
import zipfile
import io
import datetime
import os

class WriteUpDownloader:
    """Utility class for downloading single or multiple write-ups."""
    
    @staticmethod
    def download_single(write_up, module_name, patient_name=None):
        """Create a download button for a single write-up.
        
        Args:
            write_up: The text content of the write-up
            module_name: The name of the module that generated the write-up
            patient_name: Optional patient name for the filename
        """
        # Generate a safe filename
        filename = WriteUpDownloader._generate_filename(module_name, patient_name)
        
        # Create download button
        st.download_button(
            label=f"Download {module_name} Write-Up",
            data=write_up,
            file_name=filename,
            mime="text/plain"
        )
    
    @staticmethod
    def download_multiple(write_ups, patient_name=None):
        """Create a download button for multiple write-ups in a zip file.
        
        Args:
            write_ups: Dict mapping module_name to write_up content
            patient_name: Optional patient name for the filename
        """
        if not write_ups:
            st.warning("No write-ups available to download.")
            return
        
        # Create a zip file in memory
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for module_name, content in write_ups.items():
                # Generate filename for this write-up
                filename = WriteUpDownloader._generate_filename(module_name, patient_name)
                # Add to zip
                zip_file.writestr(filename, content)
        
        # Reset buffer position
        zip_buffer.seek(0)
        
        # Generate zip filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        patient_part = f"_{patient_name}" if patient_name else ""
        zip_filename = f"write_ups{patient_part}_{timestamp}.zip"
        
        # Create download button for the zip
        st.download_button(
            label="Download All Write-Ups (ZIP)",
            data=zip_buffer,
            file_name=zip_filename,
            mime="application/zip"
        )
    
    @staticmethod
    def _generate_filename(module_name, patient_name=None):
        """Generate a safe filename for a write-up.
        
        Args:
            module_name: The name of the module that generated the write-up
            patient_name: Optional patient name for the filename
            
        Returns:
            str: A safe filename for the write-up
        """
        # Clean module name for filename
        clean_module_name = module_name.lower().replace(" ", "_")
        
        # Generate timestamp for uniqueness
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Add patient name if provided
        patient_part = f"_{patient_name}" if patient_name else ""
        
        # Generate filename
        filename = f"{clean_module_name}{patient_part}_{timestamp}.txt"
        
        return filename


class WriteUpDisplay:
    """Utility class for displaying write-ups with consistent styling."""
    
    @staticmethod
    def display_write_up(write_up, module_name, download_button=True, patient_name=None):
        """Display a single write-up with consistent styling.
        
        Args:
            write_up: The text content of the write-up
            module_name: The name of the module that generated the write-up
            download_button: Whether to include a download button
            patient_name: Optional patient name for the download filename
        """
        if not write_up:
            st.info(f"No {module_name} write-up has been generated yet.")
            return
        
        st.markdown(f"### {module_name} Write-Up")
        
        # Create a container with custom styling for better visibility
        with st.container():
            # Display in text area for viewing/editing
            st.text_area(
                "",
                write_up,
                height=300,
                key=f"{module_name.lower()}_result",
                label_visibility="collapsed"
            )
            
            # Help text
            st.info("💡 To copy: Click inside the text box, use Ctrl+A (or Cmd+A on Mac) to select all, then Ctrl+C (or Cmd+C) to copy.")
            
            # Optional download button
            if download_button:
                WriteUpDownloader.display_download_options(write_up, module_name, patient_name)
    
    @staticmethod
    def display_multiple_write_ups(write_ups, patient_name=None):
        """Display multiple write-ups in tabs with consistent styling.
        
        Args:
            write_ups: Dict mapping module_name to write_up content
            patient_name: Optional patient name for the download filename
        """
        if not write_ups:
            st.info("No write-ups have been generated yet.")
            return
        
        # Create tabs for each write-up
        tab_labels = list(write_ups.keys())
        tabs = st.tabs(tab_labels)
        
        # Fill each tab with its content
        for i, (module_name, write_up) in enumerate(write_ups.items()):
            with tabs[i]:
                # Show individual write-up without its own download button
                WriteUpDisplay.display_write_up(
                    write_up,
                    module_name,
                    download_button=False,
                    patient_name=patient_name
                )
        
        # Add a universal download section
        st.markdown("### Download Options")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Individual downloads
            st.markdown("**Individual Write-Ups:**")
            for module_name, write_up in write_ups.items():
                WriteUpDownloader.download_single(write_up, module_name, patient_name)
        
        with col2:
            # Combined download
            st.markdown("**All Write-Ups:**")
            WriteUpDownloader.download_multiple(write_ups, patient_name)