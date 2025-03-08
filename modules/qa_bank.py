import streamlit as st
import json
import pandas as pd
from datetime import datetime
import os

class QABankModule:
    def __init__(self):
        """Initialize the QA Bank module."""
        self.qa_data_file = "data/qa_tests.json"
        self.preset_file = "data/qa_presets.json"
        self.qa_tests = self._load_qa_tests()
        self.presets = self._load_presets()
        
        # Categories for QA tests
        self.categories = [
            "Linac", "CT Simulator", "Treatment Planning System", 
            "Patient-Specific QA", "Imaging", "Brachytherapy",
            "Radiation Safety", "Dosimetry", "Mechanical"
        ]
        
        # Common frequencies
        self.frequencies = [
            "Daily", "Weekly", "Monthly", "Quarterly", 
            "Semi-Annual", "Annual", "As Needed"
        ]
    
    def _load_qa_tests(self):
        """Load QA test definitions from file."""
        if not os.path.exists(self.qa_data_file):
            # Create default test set if file doesn't exist
            default_tests = self._create_default_tests()
            os.makedirs(os.path.dirname(self.qa_data_file), exist_ok=True)
            with open(self.qa_data_file, 'w') as file:
                json.dump(default_tests, file, indent=2)
            return default_tests
        
        with open(self.qa_data_file, 'r') as file:
            return json.load(file)
    
    def _load_presets(self):
        """Load QA presets from file."""
        if not os.path.exists(self.preset_file):
            # Create default presets if file doesn't exist
            default_presets = self._create_default_presets()
            os.makedirs(os.path.dirname(self.preset_file), exist_ok=True)
            with open(self.preset_file, 'w') as file:
                json.dump(default_presets, file, indent=2)
            return default_presets
        
        with open(self.preset_file, 'r') as file:
            return json.load(file)
    
    def _create_default_tests(self):
        """Create a default set of QA tests."""
        return {
            "tests": [
                {
                    "id": "linac-output-constancy",
                    "name": "Linac Output Constancy",
                    "category": "Linac",
                    "description": "Verification of the constancy of the linac's radiation output.",
                    "tolerances": "±3% for photons, ±4% for electrons",
                    "method": "1. Set up the daily QA phantom\n2. Deliver 100 MU for each energy\n3. Record measured values\n4. Compare to baseline values",
                    "equipment": ["Daily QA phantom", "Electrometer"],
                    "references": ["TG-142", "TG-51"],
                    "frequency": "Daily",
                    "estimated_time": 15,
                    "dependencies": []
                },
                {
                    "id": "linac-flatness-symmetry",
                    "name": "Linac Flatness and Symmetry",
                    "category": "Linac",
                    "description": "Verification of the beam flatness and symmetry for all energies.",
                    "tolerances": "Flatness: ±3%, Symmetry: ±2%",
                    "method": "1. Set up the phantom with detector array\n2. Deliver 100 MU for each energy and field size\n3. Analyze the profiles\n4. Compare to baseline values",
                    "equipment": ["2D Detector Array", "Analysis Software"],
                    "references": ["TG-142"],
                    "frequency": "Monthly",
                    "estimated_time": 45,
                    "dependencies": ["linac-output-constancy"]
                },
                {
                    "id": "tps-dose-calculation",
                    "name": "TPS Dose Calculation Validation",
                    "category": "Treatment Planning System",
                    "description": "Verification of the accuracy of the dose calculation algorithm in the treatment planning system.",
                    "tolerances": "±2% for simple geometries, ±3% for heterogeneous regions",
                    "method": "1. Create test plans on standard phantoms\n2. Calculate dose using the TPS\n3. Measure dose in the phantom\n4. Compare calculated vs. measured",
                    "equipment": ["QA Phantom", "Dose Measurement Equipment", "Treatment Planning System"],
                    "references": ["TG-53", "TG-219"],
                    "frequency": "Quarterly",
                    "estimated_time": 180,
                    "dependencies": []
                },
                {
                    "id": "ct-sim-lasers",
                    "name": "CT Simulator Laser Alignment",
                    "category": "CT Simulator",
                    "description": "Verification of the alignment of positioning lasers in the CT simulator.",
                    "tolerances": "±1 mm",
                    "method": "1. Position the laser QA phantom\n2. Verify alignment of room lasers with phantom markings\n3. Measure and record any deviations",
                    "equipment": ["Laser Alignment Phantom", "Ruler/Calipers"],
                    "references": ["AAPM Report No. 39"],
                    "frequency": "Monthly",
                    "estimated_time": 20,
                    "dependencies": []
                },
                {
                    "id": "linac-mlc-test",
                    "name": "MLC Position Accuracy",
                    "category": "Linac",
                    "description": "Verification of the position accuracy of the multi-leaf collimator.",
                    "tolerances": "±1 mm leaf position accuracy",
                    "method": "1. Deliver picket fence test\n2. Analyze the image\n3. Check for MLC deviations",
                    "equipment": ["EPID", "QA-3 or similar software"],
                    "references": ["TG-142"],
                    "frequency": "Monthly",
                    "estimated_time": 30,
                    "dependencies": []
                }
            ]
        }
    
    def _create_default_presets(self):
        """Create default QA presets."""
        return {
            "presets": [
                {
                    "id": "daily-linac",
                    "name": "Daily Linac QA",
                    "description": "Standard daily quality assurance tests for linear accelerators",
                    "tests": ["linac-output-constancy"],
                    "notes": "Perform first thing in the morning before patient treatments",
                    "estimated_total_time": 15
                },
                {
                    "id": "monthly-linac",
                    "name": "Monthly Linac QA",
                    "description": "Comprehensive monthly quality assurance for linear accelerators",
                    "tests": [
                        "linac-output-constancy",
                        "linac-flatness-symmetry",
                        "linac-mlc-test"
                    ],
                    "notes": "Schedule this for a minimum 2-hour time slot with no patients",
                    "estimated_total_time": 90
                },
                {
                    "id": "monthly-ct-sim",
                    "name": "Monthly CT Simulator QA",
                    "description": "Monthly quality assurance for CT simulator",
                    "tests": ["ct-sim-lasers"],
                    "notes": "Best performed early morning before patient scans",
                    "estimated_total_time": 20
                }
            ]
        }
    
    def save_qa_tests(self):
        """Save QA tests to file."""
        with open(self.qa_data_file, 'w') as file:
            json.dump(self.qa_tests, file, indent=2)
    
    def save_presets(self):
        """Save QA presets to file."""
        with open(self.preset_file, 'w') as file:
            json.dump(self.presets, file, indent=2)
    
    def render_qa_bank(self):
        """Render the QA Bank module UI."""
        st.title("QA Bank")
        
        # Create tabs for Search, Presets, and Add/Edit
        search_tab, presets_tab, manage_tab = st.tabs(["Search Tests", "QA Presets", "Manage Tests"])
        
        with search_tab:
            self._render_search_interface()
        
        with presets_tab:
            self._render_presets_interface()
        
        with manage_tab:
            self._render_manage_interface()
    
    def _render_search_interface(self):
        """Render the search interface for QA tests."""
        st.subheader("Search QA Tests")
        
        # Search controls
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            search_query = st.text_input("Search Tests", placeholder="Enter test name, equipment, or keywords...")
        
        with col2:
            category_filter = st.selectbox(
                "Filter by Category",
                ["All Categories"] + self.categories
            )
        
        with col3:
            frequency_filter = st.selectbox(
                "Filter by Frequency",
                ["All Frequencies"] + self.frequencies
            )
        
        # Perform search
        filtered_tests = self._search_tests(search_query, category_filter, frequency_filter)
        
        # Display results
        if filtered_tests:
            st.success(f"Found {len(filtered_tests)} tests matching your criteria")
            
            for test in filtered_tests:
                with st.expander(f"{test['name']} ({test['frequency']})", expanded=False):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"**Category:** {test['category']}")
                        st.markdown(f"**Description:** {test['description']}")
                        st.markdown(f"**Estimated Time:** {test['estimated_time']} minutes")
                    
                    with col2:
                        st.markdown(f"**Frequency:** {test['frequency']}")
                        equipment_list = ", ".join(test['equipment'])
                        st.markdown(f"**Equipment:** {equipment_list}")
                    
                    st.markdown("### Tolerances")
                    st.markdown(test['tolerances'])
                    
                    st.markdown("### Method")
                    st.markdown(test['method'])
                    
                    st.markdown("### References")
                    for ref in test['references']:
                        st.markdown(f"- {ref}")
        else:
            st.info("No tests found matching your criteria. Try adjusting your search terms or filters.")
    
    def _search_tests(self, query, category, frequency):
        """Search and filter QA tests based on criteria."""
        filtered_tests = []
        
        for test in self.qa_tests["tests"]:
            # Filter by category
            if category != "All Categories" and test["category"] != category:
                continue
            
            # Filter by frequency
            if frequency != "All Frequencies" and test["frequency"] != frequency:
                continue
            
            # Search by query
            if query:
                query = query.lower()
                searchable_content = (
                    test["name"].lower() + " " +
                    test["description"].lower() + " " +
                    test["category"].lower() + " " +
                    test["tolerances"].lower() + " " +
                    test["method"].lower() + " " +
                    " ".join([e.lower() for e in test["equipment"]]) + " " +
                    " ".join([r.lower() for r in test["references"]])
                )
                
                if query not in searchable_content:
                    continue
            
            filtered_tests.append(test)
        
        return filtered_tests
    
    def _render_presets_interface(self):
        """Render the interface for working with QA presets."""
        st.subheader("QA Presets")
        
        # Two columns: preset selection and preset details
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Display available presets
            st.markdown("### Available Presets")
            preset_options = [preset["name"] for preset in self.presets["presets"]]
            
            if not preset_options:
                st.warning("No presets defined yet. Create one using the 'Create New Preset' section below.")
                selected_preset_name = None
            else:
                selected_preset_name = st.selectbox(
                    "Select a Preset",
                    preset_options
                )
            
            # Create new preset button
            if st.button("Create New Preset", key="create_preset_btn"):
                st.session_state.creating_new_preset = True
        
        # Display preset details or creation interface
        with col2:
            if hasattr(st.session_state, 'creating_new_preset') and st.session_state.creating_new_preset:
                self._render_preset_creation_interface()
            elif selected_preset_name:
                self._render_preset_details(selected_preset_name)
    
    def _render_preset_details(self, preset_name):
        """Render the details of a selected preset."""
        preset = next((p for p in self.presets["presets"] if p["name"] == preset_name), None)
        
        if not preset:
            st.error(f"Preset '{preset_name}' not found.")
            return
        
        st.markdown(f"## {preset['name']}")
        st.markdown(f"*{preset['description']}*")
        st.markdown(f"**Estimated Total Time:** {preset['estimated_total_time']} minutes")
        
        # Display notes
        st.markdown("### Notes")
        st.markdown(preset['notes'])
        
        # Display tests in this preset
        st.markdown("### Tests")
        
        # Get the full test details for each test in the preset
        preset_tests = []
        for test_id in preset['tests']:
            test = next((t for t in self.qa_tests["tests"] if t["id"] == test_id), None)
            if test:
                preset_tests.append(test)
        
        # Reordering interface
        if st.checkbox("Enable Test Reordering", key="enable_reordering"):
            st.markdown("Drag tests to reorder them for optimal workflow:")
            
            # This would require JavaScript interactivity which Streamlit doesn't natively support
            # Using a simpler approach with up/down buttons
            for i, test in enumerate(preset_tests):
                cols = st.columns([4, 1, 1])
                with cols[0]:
                    st.markdown(f"**{i+1}. {test['name']}** ({test['estimated_time']} min)")
                with cols[1]:
                    if i > 0 and st.button("↑", key=f"up_{test['id']}"):
                        # Move test up in the list
                        test_ids = preset['tests'].copy()
                        test_ids[i], test_ids[i-1] = test_ids[i-1], test_ids[i]
                        preset['tests'] = test_ids
                        self.save_presets()
                        st.rerun()
                with cols[2]:
                    if i < len(preset_tests)-1 and st.button("↓", key=f"down_{test['id']}"):
                        # Move test down in the list
                        test_ids = preset['tests'].copy()
                        test_ids[i], test_ids[i+1] = test_ids[i+1], test_ids[i]
                        preset['tests'] = test_ids
                        self.save_presets()
                        st.rerun()
        else:
            # Just display the tests in order
            for i, test in enumerate(preset_tests):
                with st.expander(f"{i+1}. {test['name']} ({test['estimated_time']} min)", expanded=False):
                    st.markdown(f"**Category:** {test['category']}")
                    st.markdown(f"**Description:** {test['description']}")
                    st.markdown(f"**Tolerances:** {test['tolerances']}")
                    st.markdown("**Method:**")
                    st.markdown(test['method'])
        
        # Function buttons for the preset
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Export Preset Checklist", key="export_checklist"):
                checklist_md = self._generate_checklist_markdown(preset, preset_tests)
                st.download_button(
                    label="Download Checklist",
                    data=checklist_md,
                    file_name=f"{preset['name'].replace(' ', '_')}_checklist.md",
                    mime="text/markdown"
                )
        
        with col2:
            if st.button("Edit Preset", key="edit_preset"):
                st.session_state.editing_preset = preset
                st.rerun()
        
        with col3:
            if st.button("Delete Preset", key="delete_preset"):
                # Confirm deletion
                st.warning(f"Are you sure you want to delete the preset '{preset['name']}'?")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Yes, Delete", key="confirm_delete"):
                        # Remove the preset and save
                        self.presets["presets"] = [p for p in self.presets["presets"] if p["id"] != preset["id"]]
                        self.save_presets()
                        st.success(f"Preset '{preset['name']}' deleted.")
                        st.rerun()
                with col2:
                    if st.button("Cancel", key="cancel_delete"):
                        st.rerun()
    
    def _render_preset_creation_interface(self):
        """Render the interface for creating a new QA preset."""
        st.markdown("## Create New Preset")
        
        # Basic preset information
        preset_name = st.text_input("Preset Name", placeholder="e.g., Monthly Linac QA")
        preset_description = st.text_area("Description", placeholder="Brief description of this preset's purpose")
        preset_notes = st.text_area("Notes", placeholder="Special instructions or tips for this preset")
        
        # Test selection
        st.markdown("### Select Tests")
        
        available_tests = self.qa_tests["tests"]
        
        # Group tests by category for easier selection
        tests_by_category = {}
        for test in available_tests:
            category = test["category"]
            if category not in tests_by_category:
                tests_by_category[category] = []
            tests_by_category[category].append(test)
        
        # Initialize selected tests in session state if needed
        if 'selected_tests' not in st.session_state:
            st.session_state.selected_tests = []
        
        # Allow selection of tests by category
        for category, tests in tests_by_category.items():
            with st.expander(f"{category} Tests"):
                for test in tests:
                    if st.checkbox(
                        f"{test['name']} ({test['frequency']}, {test['estimated_time']} min)",
                        key=f"test_{test['id']}",
                        value=test['id'] in st.session_state.selected_tests
                    ):
                        if test['id'] not in st.session_state.selected_tests:
                            st.session_state.selected_tests.append(test['id'])
                    else:
                        if test['id'] in st.session_state.selected_tests:
                            st.session_state.selected_tests.remove(test['id'])
        
        # Display selected tests
        if st.session_state.selected_tests:
            st.markdown("### Selected Tests")
            
            total_time = 0
            for test_id in st.session_state.selected_tests:
                test = next((t for t in available_tests if t["id"] == test_id), None)
                if test:
                    st.markdown(f"- {test['name']} ({test['estimated_time']} min)")
                    total_time += test['estimated_time']
            
            st.info(f"Total estimated time: {total_time} minutes")
        else:
            st.warning("No tests selected yet.")
        
        # Save or cancel
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Save Preset", key="save_new_preset"):
                if not preset_name:
                    st.error("Please enter a preset name.")
                elif not st.session_state.selected_tests:
                    st.error("Please select at least one test.")
                else:
                    # Calculate total time
                    total_time = sum(
                        next((t["estimated_time"] for t in available_tests if t["id"] == test_id), 0)
                        for test_id in st.session_state.selected_tests
                    )
                    
                    # Create new preset
                    new_preset = {
                        "id": preset_name.lower().replace(" ", "-"),
                        "name": preset_name,
                        "description": preset_description,
                        "tests": st.session_state.selected_tests,
                        "notes": preset_notes,
                        "estimated_total_time": total_time
                    }
                    
                    # Add to presets and save
                    self.presets["presets"].append(new_preset)
                    self.save_presets()
                    
                    # Clear session state
                    del st.session_state.creating_new_preset
                    del st.session_state.selected_tests
                    
                    st.success(f"Preset '{preset_name}' created successfully!")
                    st.rerun()
        
        with col2:
            if st.button("Cancel", key="cancel_new_preset"):
                # Clear session state
                del st.session_state.creating_new_preset
                if 'selected_tests' in st.session_state:
                    del st.session_state.selected_tests
                st.rerun()
    
    def _render_manage_interface(self):
        """Render the interface for managing QA tests."""
        st.subheader("Manage QA Tests")
        
        # Tabs for browsing and adding tests
        browse_tab, add_tab = st.tabs(["Browse Tests", "Add New Test"])
        
        with browse_tab:
            self._render_browse_tests()
        
        with add_tab:
            self._render_add_test()
    
    def _render_browse_tests(self):
        """Render the interface for browsing and editing tests."""
        # Filter by category
        category_filter = st.selectbox(
            "Filter by Category",
            ["All Categories"] + self.categories,
            key="browse_category_filter"
        )
        
        # Get filtered tests
        if category_filter == "All Categories":
            filtered_tests = self.qa_tests["tests"]
        else:
            filtered_tests = [t for t in self.qa_tests["tests"] if t["category"] == category_filter]
        
        if not filtered_tests:
            st.info(f"No tests found in category: {category_filter}")
            return
        
        # Display tests
        for test in filtered_tests:
            with st.expander(f"{test['name']} ({test['frequency']})", expanded=False):
                # Display test details
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**Category:** {test['category']}")
                    st.markdown(f"**Description:** {test['description']}")
                    st.markdown(f"**Tolerances:** {test['tolerances']}")
                
                with col2:
                    st.markdown(f"**Frequency:** {test['frequency']}")
                    st.markdown(f"**Time:** {test['estimated_time']} min")
                    
                    # Action buttons
                    if st.button("Edit", key=f"edit_{test['id']}"):
                        st.session_state.editing_test = test
                        st.rerun()
                    
                    if st.button("Delete", key=f"delete_{test['id']}"):
                        # Confirm deletion
                        st.warning(f"Are you sure you want to delete '{test['name']}'?")
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("Yes, Delete", key=f"confirm_delete_{test['id']}"):
                                # Remove the test and save
                                self.qa_tests["tests"] = [t for t in self.qa_tests["tests"] if t["id"] != test["id"]]
                                self.save_qa_tests()
                                
                                # Also remove from any presets
                                for preset in self.presets["presets"]:
                                    if test["id"] in preset["tests"]:
                                        preset["tests"].remove(test["id"])
                                self.save_presets()
                                
                                st.success(f"Test '{test['name']}' deleted.")
                                st.rerun()
                        with col2:
                            if st.button("Cancel", key=f"cancel_delete_{test['id']}"):
                                st.rerun()
    
    def _render_add_test(self):
        """Render the interface for adding a new QA test."""
        # Check if we're editing an existing test
        editing_existing = hasattr(st.session_state, 'editing_test')
        
        if editing_existing:
            test = st.session_state.editing_test
            st.markdown(f"## Edit Test: {test['name']}")
        else:
            test = {
                "id": "",
                "name": "",
                "category": self.categories[0],
                "description": "",
                "tolerances": "",
                "method": "",
                "equipment": [],
                "references": [],
                "frequency": self.frequencies[0],
                "estimated_time": 30,
                "dependencies": []
            }
            st.markdown("## Add New Test")
        
        # Basic information
        col1, col2 = st.columns(2)
        
        with col1:
            test_name = st.text_input("Test Name", value=test["name"], key="test_name")
            
            # Generate ID from name if not editing
            if not editing_existing:
                test_id = test_name.lower().replace(" ", "-")
            else:
                test_id = test["id"]
            
            test_category = st.selectbox(
                "Category",
                self.categories,
                index=self.categories.index(test["category"]) if test["category"] in self.categories else 0,
                key="test_category"
            )
        
        with col2:
            test_frequency = st.selectbox(
                "Frequency",
                self.frequencies,
                index=self.frequencies.index(test["frequency"]) if test["frequency"] in self.frequencies else 0,
                key="test_frequency"
            )
            
            test_time = st.number_input(
                "Estimated Time (minutes)",
                min_value=1,
                max_value=480,
                value=test["estimated_time"],
                key="test_time"
            )
        
        # Description and tolerances
        test_description = st.text_area(
            "Description",
            value=test["description"],
            height=100,
            key="test_description"
        )
        
        test_tolerances = st.text_area(
            "Tolerances",
            value=test["tolerances"],
            height=100,
            key="test_tolerances"
        )
        
        # Method
        test_method = st.text_area(
            "Method (step-by-step)",
            value=test["method"],
            height=200,
            key="test_method"
        )
        
        # Equipment and references
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Equipment")
            equipment_str = st.text_area(
                "Enter equipment (one per line)",
                value="\n".join(test["equipment"]),
                height=100,
                key="test_equipment"
            )
        
        with col2:
            st.markdown("### References")
            references_str = st.text_area(
                "Enter references (one per line)",
                value="\n".join(test["references"]),
                height=100,
                key="test_references"
            )
        
        # Dependencies - other tests that should be run before this one
        st.markdown("### Dependencies")
        st.markdown("Select tests that should be completed before this one:")
        
        other_tests = [t for t in self.qa_tests["tests"] if t["id"] != test_id]
        dependencies = []
        
        for other_test in other_tests:
            if st.checkbox(
                other_test["name"],
                value=other_test["id"] in test["dependencies"],
                key=f"dependency_{other_test['id']}"
            ):
                dependencies.append(other_test["id"])
        
        # Action buttons
        col1, col2 = st.columns(2)
        
        with col1:
            save_label = "Update Test" if editing_existing else "Add Test"
            if st.button(save_label, key="save_test"):
                # Validate inputs
                if not test_name:
                    st.error("Test name is required.")
                else:
                    # Parse equipment and references
                    equipment_list = [e.strip() for e in equipment_str.split("\n") if e.strip()]
                    references_list = [r.strip() for r in references_str.split("\n") if r.strip()]
                    
                    # Create or update test
                    updated_test = {
                        "id": test_id,
                        "name": test_name,
                        "category": test_category,
                        "description": test_description,
                        "tolerances": test_tolerances,
                        "method": test_method,
                        "equipment": equipment_list,
                        "references": references_list,
                        "frequency": test_frequency,
                        "estimated_time": test_time,
                        "dependencies": dependencies
                    }
                    
                    if editing_existing:
                        # Update existing test
                        self.qa_tests["tests"] = [updated_test if t["id"] == test_id else t for t in self.qa_tests["tests"]]
                        success_message = f"Test '{test_name}' updated successfully!"
                    else:
                        # Check for duplicate ID
                        if any(t["id"] == test_id for t in self.qa_tests["tests"]):
                            st.error(f"A test with ID '{test_id}' already exists. Please use a different name.")
                            return
                        
                        # Add new test
                        self.qa_tests["tests"].append(updated_test)
                        success_message = f"Test '{test_name}' added successfully!"
                    
                    # Save changes
                    self.save_qa_tests()
                    
                    # Clear editing state
                    if editing_existing:
                        del st.session_state.editing_test
                    
                    st.success(success_message)
                    st.rerun()
        
        with col2:
            if st.button("Cancel", key="cancel_test"):
                # Clear editing state
                if editing_existing:
                    del st.session_state.editing_test
                st.rerun()
    
    def _generate_checklist_markdown(self, preset, tests):
        """Generate a markdown checklist for a preset."""
        now = datetime.now().strftime("%Y-%m-%d")
        
        md = f"# {preset['name']} Checklist\n\n"
        md += f"**Date:** {now}\n\n"
        md += f"**Performed by:** ________________________\n\n"
        md += f"## Notes\n{preset['notes']}\n\n"
        md += f"## Tests\n\n"
        
        for i, test in enumerate(tests):
            md += f"### {i+1}. {test['name']}\n\n"
            md += f"* Category: {test['category']}\n"
            md += f"* Estimated time: {test['estimated_time']} minutes\n"
            md += f"* Equipment needed: {', '.join(test['equipment'])}\n\n"
            
            md += "**Method:**\n\n"
            method_steps = test['method'].split("\n")
            for step in method_steps:
                if step.strip():
                    md += f"* {step.strip()}\n"
            
            md += "\n**Tolerances:** " + test['tolerances'] + "\n\n"
            
            md += "**Results:**\n\n"
            md += "* [ ] Pass\n"
            md += "* [ ] Fail\n\n"
            
            md += "**Comments:**\n\n"
            md += "_________________________________________________________________\n\n"
            md += "_________________________________________________________________\n\n"
            
            md += "---\n\n"
        
        md += "## Sign-off\n\n"
        md += "**Physicist:** ________________________ **Date:** ____________\n\n"
        md += "**Supervisor:** _______________________ **Date:** ____________\n"
        
        return md