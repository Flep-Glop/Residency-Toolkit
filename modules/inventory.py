import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go

class InventoryModule:
    def __init__(self):
        """Initialize the Inventory module."""
        self.equipment_file = "data/inventory_equipment.json"
        self.user_data_file = "data/inventory_user_data.json"
        self.equipment = self._load_equipment()
        self.user_data = self._load_user_data()
        
        # Equipment categories
        self.categories = sorted(list(set([item["category"] for item in self.equipment["items"]])))
        
        # Manufacturers
        self.manufacturers = sorted(list(set([item["manufacturer"] for item in self.equipment["items"]])))
    
    def _load_equipment(self):
        """Load equipment data from file."""
        if not os.path.exists(self.equipment_file):
            # Create default empty structure if file doesn't exist
            default_equipment = {"items": []}
            os.makedirs(os.path.dirname(self.equipment_file), exist_ok=True)
            with open(self.equipment_file, 'w') as file:
                json.dump(default_equipment, file, indent=2)
            return default_equipment
        
        try:
            with open(self.equipment_file, 'r') as file:
                return json.load(file)
        except (json.JSONDecodeError, IOError):
            # If file is corrupted or can't be read, return empty structure
            return {"items": []}
    
    def _load_user_data(self):
        """Load user data (training, usage logs, notes) from file."""
        if not os.path.exists(self.user_data_file):
            # Create default empty structure if file doesn't exist
            default_user_data = {
                "training": {},  # equipment_id -> {"trained": bool, "comfort_level": 1-5, "training_date": date}
                "usage_logs": {},  # equipment_id -> [{"date": date, "purpose": str, "notes": str}, ...]
                "notes": {}  # equipment_id -> str (personal notes)
            }
            os.makedirs(os.path.dirname(self.user_data_file), exist_ok=True)
            with open(self.user_data_file, 'w') as file:
                json.dump(default_user_data, file, indent=2)
            return default_user_data
        
        try:
            with open(self.user_data_file, 'r') as file:
                return json.load(file)
        except (json.JSONDecodeError, IOError):
            # If file is corrupted or can't be read, return empty structure
            return {
                "training": {},
                "usage_logs": {},
                "notes": {}
            }
    
    def save_equipment(self):
        """Save equipment data to file."""
        with open(self.equipment_file, 'w') as file:
            json.dump(self.equipment, file, indent=2)
    
    def save_user_data(self):
        """Save user data to file."""
        with open(self.user_data_file, 'w') as file:
            json.dump(self.user_data, file, indent=2)
    
    def render_inventory_module(self):
        """Render the Inventory module UI."""
        st.title("Inventory Explorer")
        
        # Check if we're viewing details of a specific equipment
        if hasattr(st.session_state, 'viewing_equipment'):
            self._render_equipment_details()
        else:
            # Create tabs for Explore, Dashboard, and Manage
            explore_tab, dashboard_tab, manage_tab = st.tabs(["Explore Equipment", "Dashboard", "Manage Inventory"])
            
            with explore_tab:
                self._render_explore_interface()
            
            with dashboard_tab:
                self._render_dashboard_interface()
            
            with manage_tab:
                self._render_manage_interface()
    
    def _render_equipment_details(self):
        """Render detailed view of a specific equipment."""
        equipment_id = st.session_state.viewing_equipment
        item = next((i for i in self.equipment["items"] if i["id"] == equipment_id), None)
        
        if not item:
            st.error(f"Equipment with ID {equipment_id} not found.")
            if st.button("Back to Inventory"):
                del st.session_state.viewing_equipment
                st.rerun()
            return
        
        # Navigation header
        col1, col2 = st.columns([6, 1])
        with col1:
            st.subheader(f"Equipment Details: {item['name']}")
        with col2:
            if st.button("← Back", key="back_from_details"):
                del st.session_state.viewing_equipment
                st.rerun()
        
        st.markdown("---")
        
        # Main content area - split into two columns
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Equipment details
            st.markdown(f"# {item['name']}")
            st.markdown(f"**Manufacturer:** {item['manufacturer']}")
            st.markdown(f"**Category:** {item['category']}")
            
            # Availability indicator
            if item.get('available', False):
                st.success("**Status:** Available at MCC")
            else:
                st.warning("**Status:** Not available at MCC")
            
            # Description and specifications (if available)
            if 'description' in item and item['description']:
                st.markdown("### Description")
                st.markdown(item['description'])
            
            if 'specifications' in item and item['specifications']:
                st.markdown("### Specifications")
                for spec, value in item['specifications'].items():
                    st.markdown(f"**{spec}:** {value}")
            
            # Notes
            if 'notes' in item and item['notes']:
                st.info(f"**Notes:** {item['notes']}")
            
            # Vendor website
            if 'vendor_website' in item and item['vendor_website']:
                st.markdown(f"**Vendor Website:** [{item['vendor_website']}]({item['vendor_website']})")
            
            # Image (if available)
            if 'image_url' in item and item['image_url']:
                st.image(item['image_url'], caption=f"{item['manufacturer']} {item['name']}")
            
            # Usage instructions (if available)
            if 'usage_instructions' in item and item['usage_instructions']:
                with st.expander("Usage Instructions", expanded=False):
                    st.markdown(item['usage_instructions'])
            
            # Related documents/resources (if available)
            if 'related_resources' in item and item['related_resources']:
                with st.expander("Related Resources", expanded=False):
                    for resource in item['related_resources']:
                        st.markdown(f"- [{resource['title']}]({resource['url']})")
        
        with col2:
            # Training and usage tracking section
            st.markdown("### Your Experience")
            
            # Check if user has training record for this equipment
            training_data = self.user_data["training"].get(equipment_id, {})
            is_trained = training_data.get("trained", False)
            comfort_level = training_data.get("comfort_level", 0)
            training_date = training_data.get("training_date", "")
            
            # Training status
            trained = st.checkbox("I've been trained on this equipment", value=is_trained)
            
            # Only show these if trained
            if trained:
                comfort_level = st.slider(
                    "Comfort Level", 
                    min_value=1, 
                    max_value=5, 
                    value=comfort_level if comfort_level > 0 else 3,
                    help="1 = Novice, 5 = Expert"
                )
                training_date = st.date_input(
                    "Training Date",
                    value=datetime.strptime(training_date, "%Y-%m-%d").date() if training_date else datetime.now().date()
                )
            
            # Save training data if changed
            if (trained != is_trained or 
                comfort_level != training_data.get("comfort_level", 0) or
                (trained and str(training_date) != training_data.get("training_date", ""))):
                
                if trained:
                    self.user_data["training"][equipment_id] = {
                        "trained": trained,
                        "comfort_level": comfort_level,
                        "training_date": str(training_date)
                    }
                else:
                    # If untrained, remove the entry completely
                    if equipment_id in self.user_data["training"]:
                        del self.user_data["training"][equipment_id]
                
                self.save_user_data()
                st.success("Training information updated!")
            
            # Personal notes
            st.markdown("### Personal Notes")
            current_notes = self.user_data["notes"].get(equipment_id, "")
            new_notes = st.text_area("Your notes about this equipment", value=current_notes, height=150)
            
            if new_notes != current_notes:
                if new_notes.strip():
                    self.user_data["notes"][equipment_id] = new_notes
                else:
                    # Remove empty notes
                    if equipment_id in self.user_data["notes"]:
                        del self.user_data["notes"][equipment_id]
                
                self.save_user_data()
                st.success("Notes updated!")
            
            # Usage log
            st.markdown("### Usage Log")
            
            usage_logs = self.user_data["usage_logs"].get(equipment_id, [])
            
            if usage_logs:
                with st.expander("View Usage History", expanded=False):
                    for i, log in enumerate(usage_logs):
                        st.markdown(f"**{log['date']}** - {log['purpose']}")
                        if log['notes']:
                            st.markdown(f"*Notes: {log['notes']}*")
                        
                        if st.button("Delete Entry", key=f"delete_log_{i}"):
                            usage_logs.pop(i)
                            self.user_data["usage_logs"][equipment_id] = usage_logs
                            self.save_user_data()
                            st.success("Usage log entry deleted!")
                            st.rerun()
                        
                        st.markdown("---")
            
            # Add new usage log
            with st.expander("Log New Usage", expanded=False):
                usage_date = st.date_input("Date Used", value=datetime.now().date())
                purpose = st.text_input("Purpose/Procedure")
                log_notes = st.text_area("Notes", height=100)
                
                if st.button("Add to Log"):
                    if not purpose:
                        st.error("Please enter a purpose for this usage.")
                    else:
                        new_log = {
                            "date": str(usage_date),
                            "purpose": purpose,
                            "notes": log_notes
                        }
                        
                        if equipment_id not in self.user_data["usage_logs"]:
                            self.user_data["usage_logs"][equipment_id] = []
                        
                        self.user_data["usage_logs"][equipment_id].append(new_log)
                        self.save_user_data()
                        st.success("Usage log added!")
                        st.rerun()
    
    def _render_explore_interface(self):
        """Render the equipment exploration interface."""
        st.subheader("Explore Equipment")
        
        # Search and filter controls
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            search_query = st.text_input("Search Equipment", placeholder="Enter keywords...")
        
        with col2:
            category_filter = st.selectbox(
                "Filter by Category",
                ["All Categories"] + self.categories
            )
        
        with col3:
            availability_filter = st.selectbox(
                "Availability",
                ["All", "Available at MCC", "Not Available"]
            )
        
        # Additional filters in an expander
        with st.expander("Additional Filters", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                manufacturer_filter = st.multiselect(
                    "Manufacturers",
                    self.manufacturers
                )
            
            with col2:
                trained_filter = st.radio(
                    "Training Status",
                    ["All", "Trained", "Not Trained"]
                )
        
        # Apply filters
        filtered_items = self._filter_equipment(
            search_query, 
            category_filter, 
            availability_filter,
            manufacturer_filter,
            trained_filter
        )
        
        # Display view options
        view_option = st.radio(
            "View As",
            ["Cards", "Table", "Grid"],
            horizontal=True
        )
        
        # Display results
        if filtered_items:
            st.success(f"Found {len(filtered_items)} items matching your criteria")
            
            if view_option == "Cards":
                # Card view - group by category
                items_by_category = {}
                for item in filtered_items:
                    category = item["category"]
                    if category not in items_by_category:
                        items_by_category[category] = []
                    items_by_category[category].append(item)
                
                # Display items by category
                for category, items in items_by_category.items():
                    with st.expander(f"{category} ({len(items)})", expanded=(len(items_by_category) == 1)):
                        for item in items:
                            self._render_equipment_card(item)
            
            elif view_option == "Table":
                # Table view
                table_data = []
                for item in filtered_items:
                    # Check if user has training record for this equipment
                    is_trained = item["id"] in self.user_data["training"] and self.user_data["training"][item["id"]]["trained"]
                    
                    table_data.append({
                        "Name": item["name"],
                        "Manufacturer": item["manufacturer"],
                        "Category": item["category"],
                        "Available": "Yes" if item.get("available", False) else "No",
                        "Trained": "Yes" if is_trained else "No"
                    })
                
                df = pd.DataFrame(table_data)
                st.dataframe(df, use_container_width=True)
                
                # Add button to view details of selected equipment
                selected_item = st.selectbox(
                    "Select equipment to view details",
                    ["-- Select an item --"] + [item["name"] for item in filtered_items]
                )
                
                if selected_item != "-- Select an item --":
                    selected_item_data = next((i for i in filtered_items if i["name"] == selected_item), None)
                    if selected_item_data:
                        if st.button("View Details", key="view_selected_details"):
                            st.session_state.viewing_equipment = selected_item_data["id"]
                            st.rerun()
            
            else:  # Grid view
                # Grid view with cards
                cols = st.columns(3)
                for i, item in enumerate(filtered_items):
                    with cols[i % 3]:
                        # Create a simplified card for grid view
                        with st.container():
                            st.markdown(f"#### {item['name']}")
                            st.markdown(f"*{item['manufacturer']}*")
                            
                            # Show image if available
                            if 'image_url' in item and item['image_url']:
                                st.image(item['image_url'], width=150)
                            
                            # Availability badge
                            if item.get('available', False):
                                st.success("Available")
                            else:
                                st.warning("Not Available")
                            
                            # Check if user has been trained
                            is_trained = item["id"] in self.user_data["training"] and self.user_data["training"][item["id"]]["trained"]
                            if is_trained:
                                st.info("Trained ✓")
                            
                            if st.button("Details", key=f"grid_details_{item['id']}"):
                                st.session_state.viewing_equipment = item["id"]
                                st.rerun()
        
        else:
            st.info("No equipment found matching your criteria. Try adjusting your search or filters.")
    
    def _filter_equipment(self, query, category, availability, manufacturers, training_status):
        """Filter equipment based on search criteria."""
        filtered_items = []
        
        for item in self.equipment["items"]:
            # Filter by category
            if category != "All Categories" and item["category"] != category:
                continue
            
            # Filter by availability
            if availability == "Available at MCC" and not item.get("available", False):
                continue
            elif availability == "Not Available" and item.get("available", False):
                continue
            
            # Filter by manufacturer
            if manufacturers and item["manufacturer"] not in manufacturers:
                continue
            
            # Filter by training status
            is_trained = item["id"] in self.user_data["training"] and self.user_data["training"][item["id"]]["trained"]
            if training_status == "Trained" and not is_trained:
                continue
            elif training_status == "Not Trained" and is_trained:
                continue
            
            # Search by query
            if query:
                query = query.lower()
                searchable_content = (
                    item["name"].lower() + " " +
                    item["manufacturer"].lower() + " " +
                    item["category"].lower() + " " +
                    (item.get("description", "")).lower() + " " +
                    (item.get("notes", "")).lower()
                )
                
                if query not in searchable_content:
                    continue
            
            filtered_items.append(item)
        
        return filtered_items
    
    def _render_equipment_card(self, item):
        """Render a card for an equipment item."""
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"### {item['name']}")
                st.markdown(f"**Manufacturer:** {item['manufacturer']}")
                st.markdown(f"**Category:** {item['category']}")
                
                # Show notes if available
                if 'notes' in item and item['notes']:
                    st.info(item['notes'])
                
                # Show if user has been trained
                is_trained = item["id"] in self.user_data["training"] and self.user_data["training"][item["id"]]["trained"]
                if is_trained:
                    comfort_level = self.user_data["training"][item["id"]]["comfort_level"]
                    st.markdown(f"**Training Status:** Trained (Comfort Level: {comfort_level}/5)")
            
            with col2:
                # Availability badge
                if item.get('available', False):
                    st.success("Available at MCC")
                else:
                    st.warning("Not Available at MCC")
                
                # View details button
                view_button = st.button("View Details", key=f"view_{item['id']}")
                
                # Handle button click
                if view_button:
                    st.session_state.viewing_equipment = item['id']
                    st.rerun()
            
            st.markdown("---")
    
    def _render_dashboard_interface(self):
        """Render the dashboard interface with stats and visualizations."""
        st.subheader("Equipment Dashboard")
        
        # Basic statistics
        col1, col2, col3, col4 = st.columns(4)
        
        # Count total available equipment
        available_count = sum(1 for item in self.equipment["items"] if item.get("available", False))
        total_count = len(self.equipment["items"])
        
        # Count equipment user has been trained on
        trained_count = sum(
            1 for item_id in self.user_data["training"] 
            if self.user_data["training"][item_id].get("trained", False)
        )
        
        # Count equipment user has used
        used_count = len(self.user_data["usage_logs"])
        
        with col1:
            st.metric("Total Equipment", total_count)
        
        with col2:
            st.metric("Available at MCC", f"{available_count} ({int(available_count/total_count*100)}%)")
        
        with col3:
            st.metric("Trained On", f"{trained_count} ({int(trained_count/total_count*100)}%)")
        
        with col4:
            st.metric("Used", used_count)
        
        # Equipment distribution by category
        st.markdown("### Equipment by Category")
        
        # Prepare data for visualization
        category_counts = {}
        for item in self.equipment["items"]:
            category = item["category"]
            if category not in category_counts:
                category_counts[category] = {"total": 0, "available": 0}
            
            category_counts[category]["total"] += 1
            if item.get("available", False):
                category_counts[category]["available"] += 1
        
        # Convert to format suitable for plotting
        plot_data = []
        for category, counts in category_counts.items():
            plot_data.append({
                "category": category,
                "count": counts["total"],
                "type": "Total"
            })
            plot_data.append({
                "category": category,
                "count": counts["available"],
                "type": "Available at MCC"
            })
        
        df = pd.DataFrame(plot_data)
        
        # Create bar chart
        fig = px.bar(
            df, 
            x="category", 
            y="count", 
            color="type",
            barmode="group",
            title="Equipment Distribution by Category",
            labels={"category": "Category", "count": "Count", "type": "Status"}
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Training progress
        st.markdown("### Your Training Progress")
        
        # Prepare data for visualization
        training_data = []
        for category, counts in category_counts.items():
            # Count trained items in this category
            trained_in_category = sum(
                1 for item in self.equipment["items"]
                if item["category"] == category and 
                item["id"] in self.user_data["training"] and 
                self.user_data["training"][item["id"]].get("trained", False)
            )
            
            training_data.append({
                "category": category,
                "trained": trained_in_category,
                "total": counts["total"]
            })
        
        # Convert to DataFrame
        training_df = pd.DataFrame(training_data)
        training_df["percentage"] = (training_df["trained"] / training_df["total"] * 100).fillna(0).round(1)
        
        # Create bar chart
        fig = px.bar(
            training_df, 
            x="category", 
            y="percentage",
            title="Training Progress by Category (%)",
            labels={"category": "Category", "percentage": "% Trained"},
            color="percentage",
            color_continuous_scale="blues"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Recent activity
        st.markdown("### Recent Activity")
        
        # Collect all usage logs
        all_logs = []
        for item_id, logs in self.user_data["usage_logs"].items():
            item = next((i for i in self.equipment["items"] if i["id"] == item_id), None)
            if item:
                for log in logs:
                    all_logs.append({
                        "date": log["date"],
                        "equipment": item["name"],
                        "purpose": log["purpose"]
                    })
        
        # Sort by date (most recent first)
        all_logs.sort(key=lambda x: x["date"], reverse=True)
        
        # Display recent logs
        if all_logs:
            recent_logs = all_logs[:5]  # Show 5 most recent
            for log in recent_logs:
                st.markdown(f"**{log['date']}** - Used {log['equipment']} for {log['purpose']}")
        else:
            st.info("No usage activity recorded yet. Log your equipment usage to see it here.")
    
    def _render_manage_interface(self):
        """Render the interface for managing inventory."""
        st.subheader("Manage Inventory")
        
        # Tabs for equipment management and import/export
        manage_tab, import_tab = st.tabs(["Manage Equipment", "Import/Export"])
        
        with manage_tab:
            self._render_equipment_management()
        
        with import_tab:
            self._render_import_export()
    
    def _render_equipment_management(self):
        """Render the equipment management interface."""
        # List existing equipment
        st.markdown("### Equipment List")
        
        # Create a table view
        equipment_data = []
        for item in self.equipment["items"]:
            equipment_data.append({
                "ID": item["id"],
                "Name": item["name"],
                "Manufacturer": item["manufacturer"],
                "Category": item["category"],
                "Available": "Yes" if item.get("available", False) else "No"
            })
        
        if equipment_data:
            df = pd.DataFrame(equipment_data)
            st.dataframe(df, hide_index=True, use_container_width=True)
            
            # Select equipment to edit
            item_ids = [item["id"] for item in self.equipment["items"]]
            item_names = [item["name"] for item in self.equipment["items"]]
            item_options = [f"{name} ({item_id})" for item_id, name in zip(item_ids, item_names)]
            
            selected_item = st.selectbox(
                "Select Equipment to Edit",
                ["-- Select an item --"] + item_options
            )
            
            if selected_item != "-- Select an item --":
                item_id = selected_item.split("(")[-1].strip(")")
                st.session_state.editing_equipment = item_id
                st.rerun()
        else:
            st.info("No equipment available. Add your first equipment item.")
        
        # Add new equipment button
        if st.button("Add New Equipment", key="add_new_equipment"):
            st.session_state.adding_new_equipment = True
            st.rerun()
        
        # Bulk add from CSV
        with st.expander("Bulk Add from CSV", expanded=False):
            st.markdown("Upload a CSV file with equipment data to add multiple items at once.")
            st.markdown("The CSV should have these columns: name, manufacturer, category, available (yes/no), notes")
            
            uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
            if uploaded_file is not None:
                try:
                    df = pd.read_csv(uploaded_file)
                    
                    # Check required columns
                    required_columns = ["name", "manufacturer", "category"]
                    missing_columns = [col for col in required_columns if col not in df.columns]
                    
                    if missing_columns:
                        st.error(f"Missing required columns: {', '.join(missing_columns)}")
                    else:
                        # Preview data
                        st.write("Preview:")
                        st.dataframe(df.head())
                        
                        if st.button("Import Equipment"):
                            # Process each row
                            import_count = 0
                            for _, row in df.iterrows():
                                # Generate ID from name
                                item_id = row["name"].lower().replace(" ", "-")
                                
                                # Check if item already exists
                                if any(i["id"] == item_id for i in self.equipment["items"]):
                                    # Append a number to make ID unique
                                    base_id = item_id
                                    counter = 1
                                    while any(i["id"] == item_id for i in self.equipment["items"]):
                                        item_id = f"{base_id}-{counter}"
                                        counter += 1
                                
                                # Create new item
                                new_item = {
                                    "id": item_id,
                                    "name": row["name"],
                                    "manufacturer": row["manufacturer"],
                                    "category": row["category"],
                                    "available": row.get("available", "").lower() in ["yes", "true", "1", "y"],
                                    "notes": row.get("notes", "")
                                }
                                
                                # Add optional fields if present
                                if "description" in row:
                                    new_item["description"] = row["description"]
                                
                                if "vendor_website" in row:
                                    new_item["vendor_website"] = row["vendor_website"]
                                
                                # Add to equipment list
                                self.equipment["items"].append(new_item)
                                import_count += 1
                            
                            # Save changes
                            self.save_equipment()
                            
                            st.success(f"Successfully imported {import_count} equipment items!")
                            st.rerun()
                
                except Exception as e:
                    st.error(f"Error importing CSV: {str(e)}")
        
        # Display equipment editor if editing
        if hasattr(st.session_state, 'editing_equipment'):
            self._render_equipment_editor(st.session_state.editing_equipment)
        
        # Display equipment creator if adding new
        if hasattr(st.session_state, 'adding_new_equipment') and st.session_state.adding_new_equipment:
            self._render_equipment_creator()
    
    def _render_equipment_editor(self, item_id):
        """Render editor for an existing equipment item."""
        # Find the equipment
        item = next((i for i in self.equipment["items"] if i["id"] == item_id), None)
        
        if not item:
            st.error(f"Equipment with ID {item_id} not found.")
            return
        
        st.markdown(f"### Edit Equipment: {item['name']}")
        
        # Basic information
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Equipment Name", value=item["name"], key="edit_name")
            category = st.selectbox(
                "Category", 
                self.categories, 
                index=self.categories.index(item["category"]) if item["category"] in self.categories else 0, 
                key="edit_category"
            )
        
        with col2:
            manufacturer = st.selectbox(
                "Manufacturer",
                self.manufacturers,
                index=self.manufacturers.index(item["manufacturer"]) if item["manufacturer"] in self.manufacturers else 0,
                key="edit_manufacturer"
            )
            available = st.checkbox("Available at MCC", value=item.get("available", False), key="edit_available")
        
        # Additional information
        description = st.text_area("Description", value=item.get("description", ""), key="edit_description")
        notes = st.text_area("Notes", value=item.get("notes", ""), key="edit_notes")
        vendor_website = st.text_input("Vendor Website", value=item.get("vendor_website", ""), key="edit_vendor_website")
        image_url = st.text_input("Image URL", value=item.get("image_url", ""), key="edit_image_url")
        
        # Specifications (key-value pairs)
        st.markdown("### Specifications")
        specs = item.get("specifications", {})
        
        # Store specs in session state for editing
        if 'edit_specs' not in st.session_state:
            st.session_state.edit_specs = [{"key": k, "value": v} for k, v in specs.items()]
            if not st.session_state.edit_specs:
                st.session_state.edit_specs.append({"key": "", "value": ""})
        
        # Display each spec with edit controls
        for i, spec in enumerate(st.session_state.edit_specs):
            col1, col2, col3 = st.columns([2, 3, 1])
            
            with col1:
                st.session_state.edit_specs[i]["key"] = st.text_input(
                    "Specification", 
                    value=spec["key"], 
                    key=f"spec_key_{i}"
                )
            
            with col2:
                st.session_state.edit_specs[i]["value"] = st.text_input(
                    "Value", 
                    value=spec["value"], 
                    key=f"spec_value_{i}"
                )
            
            with col3:
                if st.button("Remove", key=f"remove_spec_{i}"):
                    st.session_state.edit_specs.pop(i)
                    st.rerun()
        
        # Add new spec button
        if st.button("Add Specification"):
            st.session_state.edit_specs.append({"key": "", "value": ""})
            st.rerun()
        
        # Related resources
        st.markdown("### Related Resources")
        resources = item.get("related_resources", [])
        
        # Store resources in session state for editing
        if 'edit_resources' not in st.session_state:
            st.session_state.edit_resources = [{"title": r["title"], "url": r["url"]} for r in resources]
            if not st.session_state.edit_resources:
                st.session_state.edit_resources.append({"title": "", "url": ""})
        
        # Display each resource with edit controls
        for i, resource in enumerate(st.session_state.edit_resources):
            col1, col2, col3 = st.columns([2, 3, 1])
            
            with col1:
                st.session_state.edit_resources[i]["title"] = st.text_input(
                    "Title", 
                    value=resource["title"], 
                    key=f"resource_title_{i}"
                )
            
            with col2:
                st.session_state.edit_resources[i]["url"] = st.text_input(
                    "URL", 
                    value=resource["url"], 
                    key=f"resource_url_{i}"
                )
            
            with col3:
                if st.button("Remove", key=f"remove_resource_{i}"):
                    st.session_state.edit_resources.pop(i)
                    st.rerun()
        
        # Add new resource button
        if st.button("Add Resource"):
            st.session_state.edit_resources.append({"title": "", "url": ""})
            st.rerun()
        
        # Usage instructions
        st.markdown("### Usage Instructions")
        usage_instructions = st.text_area(
            "Usage Instructions (Markdown format)", 
            value=item.get("usage_instructions", ""), 
            height=150,
            key="edit_usage_instructions"
        )
        
        # Save or cancel buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Save Changes", key="save_equipment_changes"):
                # Validate inputs
                if not name:
                    st.error("Equipment name is required.")
                    return
                
                # Update specifications
                updated_specs = {}
                for spec in st.session_state.edit_specs:
                    if spec["key"] and spec["value"]:
                        updated_specs[spec["key"]] = spec["value"]
                
                # Update resources
                updated_resources = []
                for resource in st.session_state.edit_resources:
                    if resource["title"] and resource["url"]:
                        updated_resources.append(resource)
                
                # Update item
                item["name"] = name
                item["category"] = category
                item["manufacturer"] = manufacturer
                item["available"] = available
                
                if description:
                    item["description"] = description
                elif "description" in item:
                    del item["description"]
                
                if notes:
                    item["notes"] = notes
                elif "notes" in item:
                    del item["notes"]
                
                if vendor_website:
                    item["vendor_website"] = vendor_website
                elif "vendor_website" in item:
                    del item["vendor_website"]
                
                if image_url:
                    item["image_url"] = image_url
                elif "image_url" in item:
                    del item["image_url"]
                
                if updated_specs:
                    item["specifications"] = updated_specs
                elif "specifications" in item:
                    del item["specifications"]
                
                if updated_resources:
                    item["related_resources"] = updated_resources
                elif "related_resources" in item:
                    del item["related_resources"]
                
                if usage_instructions:
                    item["usage_instructions"] = usage_instructions
                elif "usage_instructions" in item:
                    del item["usage_instructions"]
                
                # Save changes
                self.save_equipment()
                
                # Clear session state
                if 'edit_specs' in st.session_state:
                    del st.session_state.edit_specs
                
                if 'edit_resources' in st.session_state:
                    del st.session_state.edit_resources
                
                st.success(f"Equipment '{name}' updated successfully!")
                del st.session_state.editing_equipment
                st.rerun()
        
        with col2:
            if st.button("Cancel", key="cancel_equipment_edit"):
                # Clear session state
                if 'edit_specs' in st.session_state:
                    del st.session_state.edit_specs
                
                if 'edit_resources' in st.session_state:
                    del st.session_state.edit_resources
                
                del st.session_state.editing_equipment
                st.rerun()
        
        with col3:
            if st.button("Delete Equipment", key="delete_equipment"):
                # Confirm deletion
                st.warning(f"Are you sure you want to delete '{item['name']}'? This cannot be undone.")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Yes, Delete", key="confirm_delete_equipment"):
                        # Remove the equipment
                        self.equipment["items"] = [i for i in self.equipment["items"] if i["id"] != item_id]
                        self.save_equipment()
                        
                        # Also remove associated user data
                        if item_id in self.user_data["training"]:
                            del self.user_data["training"][item_id]
                        
                        if item_id in self.user_data["usage_logs"]:
                            del self.user_data["usage_logs"][item_id]
                        
                        if item_id in self.user_data["notes"]:
                            del self.user_data["notes"][item_id]
                        
                        self.save_user_data()
                        
                        st.success(f"Equipment '{item['name']}' deleted successfully!")
                        
                        # Clear session state
                        if 'edit_specs' in st.session_state:
                            del st.session_state.edit_specs
                        
                        if 'edit_resources' in st.session_state:
                            del st.session_state.edit_resources
                        
                        del st.session_state.editing_equipment
                        st.rerun()
                
                with col2:
                    if st.button("Cancel Deletion", key="cancel_equipment_delete"):
                        st.rerun()
    
    def _render_equipment_creator(self):
        """Render creator for a new equipment item."""
        st.markdown("### Add New Equipment")
        
        # Basic information
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Equipment Name", key="new_equipment_name")
            
            # Generate ID from name
            if name:
                item_id = name.lower().replace(" ", "-")
                
                # Check if ID already exists
                if any(i["id"] == item_id for i in self.equipment["items"]):
                    # Append a number to make ID unique
                    base_id = item_id
                    counter = 1
                    while any(i["id"] == item_id for i in self.equipment["items"]):
                        item_id = f"{base_id}-{counter}"
                        counter += 1
            else:
                item_id = ""
            
            st.text_input("Equipment ID (auto-generated)", value=item_id, disabled=True, key="new_equipment_id")
            
            # Allow adding new category
            new_category_option = "-- Add New Category --"
            category_options = self.categories + [new_category_option]
            selected_category = st.selectbox("Category", category_options, key="new_equipment_category")
            
            if selected_category == new_category_option:
                new_category = st.text_input("New Category Name", key="new_category_name")
                category = new_category
            else:
                category = selected_category
        
        with col2:
            # Allow adding new manufacturer
            new_manufacturer_option = "-- Add New Manufacturer --"
            manufacturer_options = self.manufacturers + [new_manufacturer_option]
            selected_manufacturer = st.selectbox("Manufacturer", manufacturer_options, key="new_equipment_manufacturer")
            
            if selected_manufacturer == new_manufacturer_option:
                new_manufacturer = st.text_input("New Manufacturer Name", key="new_manufacturer_name")
                manufacturer = new_manufacturer
            else:
                manufacturer = selected_manufacturer
            
            available = st.checkbox("Available at MCC", value=True, key="new_equipment_available")
        
        # Additional information
        description = st.text_area("Description", key="new_equipment_description")
        notes = st.text_area("Notes", key="new_equipment_notes")
        vendor_website = st.text_input("Vendor Website", key="new_equipment_vendor_website")
        image_url = st.text_input("Image URL", key="new_equipment_image_url")
        
        # Save or cancel buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Create Equipment", key="create_equipment"):
                # Validate inputs
                if not name or not category or not manufacturer:
                    st.error("Equipment name, category, and manufacturer are required.")
                    return
                
                # Create new equipment
                new_item = {
                    "id": item_id,
                    "name": name,
                    "category": category,
                    "manufacturer": manufacturer,
                    "available": available
                }
                
                # Add optional fields
                if description:
                    new_item["description"] = description
                
                if notes:
                    new_item["notes"] = notes
                
                if vendor_website:
                    new_item["vendor_website"] = vendor_website
                
                if image_url:
                    new_item["image_url"] = image_url
                
                # Add to equipment list
                self.equipment["items"].append(new_item)
                
                # Update category and manufacturer lists
                if category not in self.categories:
                    self.categories.append(category)
                    self.categories.sort()
                
                if manufacturer not in self.manufacturers:
                    self.manufacturers.append(manufacturer)
                    self.manufacturers.sort()
                
                # Save changes
                self.save_equipment()
                
                st.success(f"Equipment '{name}' created successfully!")
                del st.session_state.adding_new_equipment
                st.rerun()
        
        with col2:
            if st.button("Cancel", key="cancel_new_equipment"):
                del st.session_state.adding_new_equipment
                st.rerun()
    
    def _render_import_export(self):
        """Render the import/export interface."""
        st.markdown("### Export Equipment Data")
        
        export_format = st.selectbox(
            "Export Format",
            ["CSV", "JSON", "Excel"]
        )
        
        if st.button("Export Data"):
            if export_format == "CSV":
                # Prepare data for CSV export
                export_data = []
                for item in self.equipment["items"]:
                    export_data.append({
                        "name": item["name"],
                        "id": item["id"],
                        "manufacturer": item["manufacturer"],
                        "category": item["category"],
                        "available": "Yes" if item.get("available", False) else "No",
                        "notes": item.get("notes", ""),
                        "description": item.get("description", ""),
                        "vendor_website": item.get("vendor_website", ""),
                        "image_url": item.get("image_url", "")
                    })
                
                df = pd.DataFrame(export_data)
                
                # Convert to CSV
                csv = df.to_csv(index=False)
                
                # Provide download link
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name="inventory_equipment.csv",
                    mime="text/csv"
                )
            
            elif export_format == "JSON":
                # Export raw JSON data
                json_data = json.dumps(self.equipment, indent=2)
                
                st.download_button(
                    label="Download JSON",
                    data=json_data,
                    file_name="inventory_equipment.json",
                    mime="application/json"
                )
            
            else:  # Excel
                # Prepare data for Excel export
                export_data = []
                for item in self.equipment["items"]:
                    export_data.append({
                        "name": item["name"],
                        "id": item["id"],
                        "manufacturer": item["manufacturer"],
                        "category": item["category"],
                        "available": "Yes" if item.get("available", False) else "No",
                        "notes": item.get("notes", ""),
                        "description": item.get("description", ""),
                        "vendor_website": item.get("vendor_website", ""),
                        "image_url": item.get("image_url", "")
                    })
                
                df = pd.DataFrame(export_data)
                
                # Convert to Excel
                excel_buffer = BytesIO()
                df.to_excel(excel_buffer, index=False)
                excel_data = excel_buffer.getvalue()
                
                st.download_button(
                    label="Download Excel",
                    data=excel_data,
                    file_name="inventory_equipment.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        
        st.markdown("### Import Equipment Data")
        st.markdown("You can import equipment data from a JSON file exported from this system.")
        
        uploaded_file = st.file_uploader("Choose a JSON file", type="json")
        if uploaded_file is not None:
            try:
                import_data = json.load(uploaded_file)
                
                # Validate import data
                if "items" not in import_data:
                    st.error("Invalid JSON format. The file must contain an 'items' array.")
                else:
                    # Preview import data
                    st.write(f"Found {len(import_data['items'])} equipment items to import.")
                    
                    # Options for import
                    import_mode = st.radio(
                        "Import Mode",
                        ["Append (add to existing)", "Replace (delete existing)"]
                    )
                    
                    if st.button("Import Data"):
                        if import_mode == "Replace (delete existing)":
                            # Replace all equipment
                            self.equipment = import_data
                        else:
                            # Append new equipment
                            existing_ids = [item["id"] for item in self.equipment["items"]]
                            
                            for item in import_data["items"]:
                                if item["id"] in existing_ids:
                                    # Skip existing items
                                    continue
                                
                                # Add to equipment list
                                self.equipment["items"].append(item)
                                
                                # Update category and manufacturer lists
                                if item["category"] not in self.categories:
                                    self.categories.append(item["category"])
                                    self.categories.sort()
                                
                                if item["manufacturer"] not in self.manufacturers:
                                    self.manufacturers.append(item["manufacturer"])
                                    self.manufacturers.sort()
                        
                        # Save changes
                        self.save_equipment()
                        
                        st.success("Equipment data imported successfully!")
                        st.rerun()
            
            except Exception as e:
                st.error(f"Error importing JSON: {str(e)}")