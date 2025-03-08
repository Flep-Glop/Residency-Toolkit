import streamlit as st
import json
import os
import re
import pandas as pd
from datetime import datetime
from pathlib import Path

class PnPModule:
    def __init__(self):
        """Initialize the Policies & Procedures module."""
        self.pp_data_file = "data/pp_documents.json"
        self.checklist_file = "data/pp_checklists.json"
        self.pp_documents = self._load_pp_documents()
        self.checklists = self._load_checklists()
        
        # Categories for P&Ps
        self.categories = [
            "Treatment Planning", 
            "Quality Assurance",
            "Patient Safety",
            "Treatment Delivery",
            "Imaging",
            "Brachytherapy",
            "Special Procedures"
        ]
    
    def _load_pp_documents(self):
        """Load P&P documents from file."""
        if not os.path.exists(self.pp_data_file):
            # Create default empty structure if file doesn't exist
            default_pp = {"documents": []}
            os.makedirs(os.path.dirname(self.pp_data_file), exist_ok=True)
            with open(self.pp_data_file, 'w') as file:
                json.dump(default_pp, file, indent=2)
            return default_pp
        
        try:
            with open(self.pp_data_file, 'r') as file:
                return json.load(file)
        except (json.JSONDecodeError, IOError):
            # If file is corrupted or can't be read, return empty structure
            return {"documents": []}
    
    def _load_checklists(self):
        """Load checklists from file."""
        if not os.path.exists(self.checklist_file):
            # Create default empty structure if file doesn't exist
            default_checklists = {"checklists": []}
            os.makedirs(os.path.dirname(self.checklist_file), exist_ok=True)
            with open(self.checklist_file, 'w') as file:
                json.dump(default_checklists, file, indent=2)
            return default_checklists
        
        try:
            with open(self.checklist_file, 'r') as file:
                return json.load(file)
        except (json.JSONDecodeError, IOError):
            # If file is corrupted or can't be read, return empty structure
            return {"checklists": []}
    
    def save_pp_documents(self):
        """Save P&P documents to file."""
        with open(self.pp_data_file, 'w') as file:
            json.dump(self.pp_documents, file, indent=2)
    
    def save_checklists(self):
        """Save checklists to file."""
        with open(self.checklist_file, 'w') as file:
            json.dump(self.checklists, file, indent=2)
    
    def render_pp_module(self):
        """Render the Policies & Procedures module UI."""
        st.title("Policies & Procedures")
        
        # Create tabs for Browse, Add/Edit, and Print
        browse_tab, manage_tab, print_tab = st.tabs(["Browse P&Ps", "Manage Documents", "Print/Export"])
        
        with browse_tab:
            self._render_browse_interface()
        
        with manage_tab:
            self._render_manage_interface()
        
        with print_tab:
            self._render_print_interface()
    
    def _render_browse_interface(self):
        """Render the browse interface for P&Ps."""
        st.subheader("Browse Policies & Procedures")
        
        # Search and filter controls
        col1, col2 = st.columns([3, 1])
        
        with col1:
            search_query = st.text_input("Search P&Ps", placeholder="Enter keywords...")
        
        with col2:
            category_filter = st.selectbox(
                "Filter by Category",
                ["All Categories"] + self.categories
            )
        
        # Perform search
        filtered_docs = self._search_pp_documents(search_query, category_filter)
        
        # Display results
        if filtered_docs:
            st.success(f"Found {len(filtered_docs)} documents matching your criteria")
            
            # Group documents by category for better organization
            docs_by_category = {}
            for doc in filtered_docs:
                category = doc["category"]
                if category not in docs_by_category:
                    docs_by_category[category] = []
                docs_by_category[category].append(doc)
            
            # Display documents by category
            for category, docs in docs_by_category.items():
                with st.expander(f"{category} ({len(docs)})", expanded=(len(docs_by_category) == 1)):
                    for doc in docs:
                        self._render_pp_card(doc)
        else:
            st.info("No documents found matching your criteria. Try adjusting your search terms or filters.")
    
    def _search_pp_documents(self, query, category):
        """Search and filter P&P documents based on criteria."""
        filtered_docs = []
        
        for doc in self.pp_documents["documents"]:
            # Filter by category
            if category != "All Categories" and doc["category"] != category:
                continue
            
            # Search by query (if provided)
            if query:
                query = query.lower()
                searchable_content = (
                    doc["title"].lower() + " " +
                    doc["category"].lower() + " " +
                    doc["objective"].lower() + " " +
                    doc["frequency"].lower() + " " +
                    doc["content"].lower()
                )
                
                if query not in searchable_content:
                    continue
            
            filtered_docs.append(doc)
        
        return filtered_docs
    
    def _render_pp_card(self, doc):
        """Render a card for a P&P document."""
        with st.container():
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.markdown(f"### {doc['title']}")
                st.markdown(f"**Objective:** {doc['objective']}")
                st.markdown(f"**Frequency:** {doc['frequency']}")
                last_updated = doc.get('last_updated', 'Unknown')
                updated_by = doc.get('updated_by', 'Unknown')
                st.markdown(f"*Last updated: {last_updated} by {updated_by}*")
            
            with col2:
                st.markdown("&nbsp;")  # Spacer
                view_button = st.button("View Full P&P", key=f"view_{doc['id']}")
                
                if doc['has_checklist']:
                    checklist_button = st.button("View Checklist", key=f"checklist_{doc['id']}")
                else:
                    st.markdown("*No checklist available*")
            
            # Handle button clicks
            if view_button:
                st.session_state.viewing_pp = doc['id']
                st.rerun()
            
            if doc['has_checklist'] and 'checklist_button' in locals() and checklist_button:
                st.session_state.viewing_checklist = doc['id']
                st.rerun()
            
            st.markdown("---")
        
        # Display full P&P if selected
        if hasattr(st.session_state, 'viewing_pp') and st.session_state.viewing_pp == doc['id']:
            self._render_full_pp(doc)
        
        # Display checklist if selected
        if hasattr(st.session_state, 'viewing_checklist') and st.session_state.viewing_checklist == doc['id']:
            self._render_checklist(doc['id'])
    
    def _render_full_pp(self, doc):
        """Render the full content of a P&P document."""
        with st.expander("Full Document", expanded=True):
            st.markdown(f"# {doc['title']}")
            st.markdown(f"**Objective:** {doc['objective']}")
            st.markdown(f"**Frequency:** {doc['frequency']}")
            
            # Convert the content Markdown to HTML and display
            st.markdown(doc['content'])
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Close", key=f"close_{doc['id']}"):
                    del st.session_state.viewing_pp
                    st.rerun()
            
            with col2:
                if doc['has_checklist']:
                    if st.button("Show Checklist", key=f"show_checklist_{doc['id']}"):
                        st.session_state.viewing_checklist = doc['id']
                        st.rerun()
    
    def _render_checklist(self, doc_id):
        """Render the checklist for a P&P document."""
        # Find the checklist for this document
        checklist = next((c for c in self.checklists["checklists"] if c["id"] == doc_id), None)
        
        if not checklist:
            st.warning(f"No checklist found for document ID: {doc_id}")
            return
        
        with st.expander("Checklist", expanded=True):
            st.markdown(f"# {checklist['title']}")
            st.markdown(f"*Last updated: {checklist['last_updated']} by {checklist['updated_by']}*")
            
            # Interactive checklist
            if 'checklist_state' not in st.session_state:
                st.session_state.checklist_state = {}
            
            checklist_id = f"checklist_{doc_id}"
            if checklist_id not in st.session_state.checklist_state:
                st.session_state.checklist_state[checklist_id] = [False] * len(checklist['items'])
            
            # Display each checklist item with a checkbox
            for i, item in enumerate(checklist['items']):
                col1, col2 = st.columns([20, 1])
                with col1:
                    st.checkbox(
                        item['text'] + (" *" if item['required'] else ""),
                        key=f"item_{doc_id}_{i}",
                        value=st.session_state.checklist_state[checklist_id][i],
                        on_change=self._update_checklist_state,
                        args=(checklist_id, i)
                    )
                
            # Progress bar for checklist completion
            completed = sum(st.session_state.checklist_state[checklist_id])
            total = len(checklist['items'])
            required_items = sum(1 for item in checklist['items'] if item['required'])
            required_completed = sum(1 for i, item in enumerate(checklist['items']) 
                                   if item['required'] and st.session_state.checklist_state[checklist_id][i])
            
            st.progress(completed / total)
            st.markdown(f"**Progress:** {completed}/{total} items completed")
            st.markdown(f"**Required Items:** {required_completed}/{required_items} completed")
            
            # Button to reset checklist
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("Reset Checklist", key=f"reset_{doc_id}"):
                    st.session_state.checklist_state[checklist_id] = [False] * len(checklist['items'])
                    st.rerun()
            
            with col2:
                if st.button("Print Checklist", key=f"print_checklist_{doc_id}"):
                    st.session_state.printing_checklist = doc_id
                    st.rerun()
            
            with col3:
                if st.button("Close Checklist", key=f"close_checklist_{doc_id}"):
                    del st.session_state.viewing_checklist
                    st.rerun()
    
    def _update_checklist_state(self, checklist_id, item_index):
        """Update the state of a checklist item when checked/unchecked."""
        st.session_state.checklist_state[checklist_id][item_index] = not st.session_state.checklist_state[checklist_id][item_index]
    
    def _render_manage_interface(self):
        """Render the interface for managing P&P documents and checklists."""
        st.subheader("Manage P&P Documents")
        
        # Tabs for document management and checklist management
        docs_tab, checklist_tab = st.tabs(["P&P Documents", "Checklists"])
        
        with docs_tab:
            self._render_manage_documents()
        
        with checklist_tab:
            self._render_manage_checklists()
    
    def _render_manage_documents(self):
        """Render the interface for managing P&P documents."""
        # List existing documents
        st.markdown("### Existing P&P Documents")
        
        # Create a table view
        doc_data = []
        for doc in self.pp_documents["documents"]:
            doc_data.append({
                "ID": doc["id"],
                "Title": doc["title"],
                "Category": doc["category"],
                "Last Updated": doc.get("last_updated", "Unknown"),
                "Has Checklist": "Yes" if doc["has_checklist"] else "No"
            })
        
        if doc_data:
            df = pd.DataFrame(doc_data)
            st.dataframe(df, hide_index=True)
            
            # Select document to edit
            doc_ids = [doc["id"] for doc in self.pp_documents["documents"]]
            doc_titles = [doc["title"] for doc in self.pp_documents["documents"]]
            doc_options = [f"{title} ({doc_id})" for doc_id, title in zip(doc_ids, doc_titles)]
            
            selected_doc = st.selectbox(
                "Select Document to Edit",
                ["-- Select a document --"] + doc_options
            )
            
            if selected_doc != "-- Select a document --":
                doc_id = selected_doc.split("(")[-1].strip(")")
                st.session_state.editing_doc = doc_id
                st.rerun()
        else:
            st.info("No documents available. Add your first P&P document.")
        
        # Add new document button
        if st.button("Add New P&P Document", key="add_new_doc"):
            st.session_state.adding_new_doc = True
            st.rerun()
        
        # Display document editor if editing
        if hasattr(st.session_state, 'editing_doc'):
            self._render_document_editor(st.session_state.editing_doc)
        
        # Display document creator if adding new
        if hasattr(st.session_state, 'adding_new_doc') and st.session_state.adding_new_doc:
            self._render_document_creator()
    
    def _render_document_editor(self, doc_id):
        """Render editor for an existing P&P document."""
        # Find the document
        doc = next((d for d in self.pp_documents["documents"] if d["id"] == doc_id), None)
        
        if not doc:
            st.error(f"Document with ID {doc_id} not found.")
            return
        
        st.markdown(f"### Edit P&P: {doc['title']}")
        
        # Document form
        title = st.text_input("Title", value=doc["title"], key="edit_title")
        category = st.selectbox("Category", self.categories, index=self.categories.index(doc["category"]) if doc["category"] in self.categories else 0, key="edit_category")
        objective = st.text_area("Objective", value=doc["objective"], key="edit_objective")
        frequency = st.text_area("Frequency", value=doc["frequency"], key="edit_frequency")
        content = st.text_area("Content (Markdown format)", value=doc["content"], height=300, key="edit_content")
        has_checklist = st.checkbox("Has Checklist", value=doc["has_checklist"], key="edit_has_checklist")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Save Changes", key="save_doc_changes"):
                # Update document
                doc["title"] = title
                doc["category"] = category
                doc["objective"] = objective
                doc["frequency"] = frequency
                doc["content"] = content
                doc["has_checklist"] = has_checklist
                doc["last_updated"] = datetime.now().strftime("%Y-%m-%d")
                
                # Save changes
                self.save_pp_documents()
                
                st.success(f"Document '{title}' updated successfully!")
                del st.session_state.editing_doc
                st.rerun()
        
        with col2:
            if st.button("Cancel", key="cancel_doc_edit"):
                del st.session_state.editing_doc
                st.rerun()
        
        with col3:
            if st.button("Delete Document", key="delete_doc"):
                # Confirm deletion
                st.warning(f"Are you sure you want to delete '{doc['title']}'? This cannot be undone.")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Yes, Delete", key="confirm_delete_doc"):
                        # Remove the document
                        self.pp_documents["documents"] = [d for d in self.pp_documents["documents"] if d["id"] != doc_id]
                        self.save_pp_documents()
                        
                        # Also remove associated checklist
                        self.checklists["checklists"] = [c for c in self.checklists["checklists"] if c["id"] != doc_id]
                        self.save_checklists()
                        
                        st.success(f"Document '{doc['title']}' deleted successfully!")
                        del st.session_state.editing_doc
                        st.rerun()
                with col2:
                    if st.button("Cancel Deletion", key="cancel_delete_doc"):
                        st.rerun()
    
    def _render_document_creator(self):
        """Render creator for a new P&P document."""
        st.markdown("### Add New P&P Document")
        
        # Document form
        title = st.text_input("Title", key="new_title")
        
        # Generate ID from title
        if title:
            doc_id = title.lower().replace(" ", "-")
        else:
            doc_id = ""
        
        st.text_input("Document ID (auto-generated)", value=doc_id, disabled=True, key="new_id")
        category = st.selectbox("Category", self.categories, key="new_category")
        objective = st.text_area("Objective", key="new_objective")
        frequency = st.text_area("Frequency", key="new_frequency")
        content = st.text_area("Content (Markdown format)", height=300, key="new_content")
        has_checklist = st.checkbox("Create Checklist", value=True, key="new_has_checklist")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Create Document", key="create_doc"):
                # Validate inputs
                if not title or not doc_id or not objective or not frequency or not content:
                    st.error("Please fill in all required fields.")
                    return
                
                # Check for duplicate ID
                if any(d["id"] == doc_id for d in self.pp_documents["documents"]):
                    st.error(f"A document with ID '{doc_id}' already exists. Please use a different title.")
                    return
                
                # Create new document
                new_doc = {
                    "id": doc_id,
                    "title": title,
                    "category": category,
                    "objective": objective,
                    "frequency": frequency,
                    "content": content,
                    "has_checklist": has_checklist,
                    "last_updated": datetime.now().strftime("%Y-%m-%d"),
                    "updated_by": "User"  # Consider replacing with actual user name
                }
                
                # Add document
                self.pp_documents["documents"].append(new_doc)
                self.save_pp_documents()
                
                # Create associated checklist if requested
                if has_checklist:
                    # Create a starter checklist with basic items
                    new_checklist = {
                        "id": doc_id,
                        "title": f"{title} Checklist",
                        "items": [
                            {"text": "First step", "required": True},
                            {"text": "Second step", "required": True},
                            {"text": "Optional step", "required": False}
                        ],
                        "last_updated": datetime.now().strftime("%Y-%m-%d"),
                        "updated_by": "User"  # Consider replacing with actual user name
                    }
                    
                    self.checklists["checklists"].append(new_checklist)
                    self.save_checklists()
                
                st.success(f"Document '{title}' created successfully!")
                del st.session_state.adding_new_doc
                st.rerun()
        
        with col2:
            if st.button("Cancel", key="cancel_new_doc"):
                del st.session_state.adding_new_doc
                st.rerun()
    
    def _render_manage_checklists(self):
        """Render the interface for managing checklists."""
        st.markdown("### Existing Checklists")
        
        # Create a table view
        checklist_data = []
        for checklist in self.checklists["checklists"]:
            # Find associated document
            doc = next((d for d in self.pp_documents["documents"] if d["id"] == checklist["id"]), None)
            doc_title = doc["title"] if doc else "Unknown Document"
            
            checklist_data.append({
                "ID": checklist["id"],
                "Title": checklist["title"],
                "Document": doc_title,
                "Items": len(checklist["items"]),
                "Last Updated": checklist.get("last_updated", "Unknown")
            })
        
        if checklist_data:
            df = pd.DataFrame(checklist_data)
            st.dataframe(df, hide_index=True)
            
            # Select checklist to edit
            checklist_ids = [c["id"] for c in self.checklists["checklists"]]
            checklist_titles = [c["title"] for c in self.checklists["checklists"]]
            checklist_options = [f"{title} ({checklist_id})" for checklist_id, title in zip(checklist_ids, checklist_titles)]
            
            selected_checklist = st.selectbox(
                "Select Checklist to Edit",
                ["-- Select a checklist --"] + checklist_options
            )
            
            if selected_checklist != "-- Select a checklist --":
                checklist_id = selected_checklist.split("(")[-1].strip(")")
                st.session_state.editing_checklist = checklist_id
                st.rerun()
        else:
            st.info("No checklists available.")
        
        # Display checklist editor if editing
        if hasattr(st.session_state, 'editing_checklist'):
            self._render_checklist_editor(st.session_state.editing_checklist)
    
    def _render_checklist_editor(self, checklist_id):
        """Render editor for an existing checklist."""
        # Find the checklist
        checklist = next((c for c in self.checklists["checklists"] if c["id"] == checklist_id), None)
        
        if not checklist:
            st.error(f"Checklist with ID {checklist_id} not found.")
            return
        
        # Find associated document
        doc = next((d for d in self.pp_documents["documents"] if d["id"] == checklist_id), None)
        doc_title = doc["title"] if doc else "Unknown Document"
        
        st.markdown(f"### Edit Checklist: {checklist['title']}")
        st.markdown(f"*Associated with P&P: {doc_title}*")
        
        # Checklist form
        title = st.text_input("Checklist Title", value=checklist["title"], key="edit_checklist_title")
        
        # Display existing items
        st.markdown("### Checklist Items")
        
        # Store items in session state for editing
        if 'edit_checklist_items' not in st.session_state:
            st.session_state.edit_checklist_items = checklist["items"].copy()
        
        # Display each item with edit controls
        for i, item in enumerate(st.session_state.edit_checklist_items):
            cols = st.columns([3, 1, 1])
            with cols[0]:
                st.session_state.edit_checklist_items[i]["text"] = st.text_input(
                    f"Item {i+1}",
                    value=item["text"],
                    key=f"edit_item_text_{i}"
                )
            
            with cols[1]:
                st.session_state.edit_checklist_items[i]["required"] = st.checkbox(
                    "Required",
                    value=item["required"],
                    key=f"edit_item_required_{i}"
                )
            
            with cols[2]:
                if st.button("Remove", key=f"remove_item_{i}"):
                    st.session_state.edit_checklist_items.pop(i)
                    st.rerun()
        
        # Add new item
        st.markdown("### Add New Item")
        new_item_text = st.text_input("New Item Text", key="new_item_text")
        new_item_required = st.checkbox("Required", key="new_item_required")
        
        if st.button("Add Item", key="add_checklist_item"):
            if new_item_text:
                st.session_state.edit_checklist_items.append({
                    "text": new_item_text,
                    "required": new_item_required
                })
                st.rerun()
            else:
                st.warning("Please enter item text.")
        
        # Save changes
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Save Changes", key="save_checklist_changes"):
                # Update checklist
                checklist["title"] = title
                checklist["items"] = st.session_state.edit_checklist_items
                checklist["last_updated"] = datetime.now().strftime("%Y-%m-%d")
                
                # Save changes
                self.save_checklists()
                
                st.success(f"Checklist '{title}' updated successfully!")
                del st.session_state.editing_checklist
                del st.session_state.edit_checklist_items
                st.rerun()
        
        with col2:
            if st.button("Cancel", key="cancel_checklist_edit"):
                del st.session_state.editing_checklist
                if 'edit_checklist_items' in st.session_state:
                    del st.session_state.edit_checklist_items
                st.rerun()
    
    def _render_print_interface(self):
        """Render the interface for printing/exporting P&Ps and checklists."""
        st.subheader("Print & Export Documents")
        
        # Select document and format
        doc_options = []
        for doc in self.pp_documents["documents"]:
            doc_options.append({"id": doc["id"], "title": doc["title"], "type": "P&P"})
        
        for checklist in self.checklists["checklists"]:
            doc_options.append({"id": checklist["id"], "title": checklist["title"], "type": "Checklist"})
        
        # Sort options by title
        doc_options.sort(key=lambda x: x["title"])
        
        # Create display options
        display_options = [f"{opt['title']} ({opt['type']})" for opt in doc_options]
        selected_option = st.selectbox(
            "Select Document to Export",
            ["-- Select a document --"] + display_options
        )
        
        if selected_option != "-- Select a document --":
            selected_index = display_options.index(selected_option)
            selected_doc = doc_options[selected_index]
            
            export_format = st.selectbox(
                "Export Format",
                ["PDF", "Markdown", "Printable HTML"]
            )
            
            if st.button("Generate Export", key="generate_export"):
                if selected_doc["type"] == "P&P":
                    document = next((d for d in self.pp_documents["documents"] if d["id"] == selected_doc["id"]), None)
                    if document:
                        self._export_pp_document(document, export_format)
                else:  # Checklist
                    checklist = next((c for c in self.checklists["checklists"] if c["id"] == selected_doc["id"]), None)
                    if checklist:
                        self._export_checklist(checklist, export_format)
    
    def _export_pp_document(self, document, format):
        """Generate export for a P&P document."""
        if format == "Markdown":
            # Generate Markdown
            markdown_content = f"# {document['title']}\n\n"
            markdown_content += f"**Objective:** {document['objective']}\n\n"
            markdown_content += f"**Frequency:** {document['frequency']}\n\n"
            markdown_content += document['content']
            
            # Add footer
            markdown_content += f"\n\n---\n*Last updated: {document.get('last_updated', 'Unknown')} by {document.get('updated_by', 'Unknown')}*"
            
            # Provide download link
            st.download_button(
                label="Download Markdown",
                data=markdown_content,
                file_name=f"{document['id']}.md",
                mime="text/markdown"
            )
        
        elif format == "Printable HTML":
            # Generate HTML
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>{document['title']}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                    h1 {{ color: #2c3e50; }}
                    h2 {{ color: #3498db; margin-top: 20px; }}
                    .objective {{ font-weight: bold; margin-bottom: 10px; }}
                    .frequency {{ font-style: italic; margin-bottom: 20px; }}
                    .footer {{ margin-top: 30px; font-size: 0.8em; color: #7f8c8d; }}
                    @media print {{
                        body {{ margin: 0.5in; }}
                    }}
                </style>
            </head>
            <body>
                <h1>{document['title']}</h1>
                <div class="objective">Objective: {document['objective']}</div>
                <div class="frequency">Frequency: {document['frequency']}</div>
                <div class="content">
                    {document['content']}
                </div>
                <div class="footer">
                    Last updated: {document.get('last_updated', 'Unknown')} by {document.get('updated_by', 'Unknown')}
                </div>
            </body>
            </html>
            """
            
            # Provide download link
            st.download_button(
                label="Download HTML",
                data=html_content,
                file_name=f"{document['id']}.html",
                mime="text/html"
            )
        
        elif format == "PDF":
            # For PDF, we'd ideally use a library like WeasyPrint or PDFKit
            # Since that's not available in this environment, we'll simulate it
            st.info("PDF generation typically requires additional libraries. In a full implementation, this would generate a PDF document. For now, please use the HTML option and print to PDF from your browser.")
    
    def _export_checklist(self, checklist, format):
        """Generate export for a checklist."""
        # Find associated document
        doc = next((d for d in self.pp_documents["documents"] if d["id"] == checklist["id"]), None)
        doc_title = doc["title"] if doc else "Unknown Document"
        
        if format == "Markdown":
            # Generate Markdown
            markdown_content = f"# {checklist['title']}\n\n"
            markdown_content += f"**Associated with:** {doc_title}\n\n"
            
            # Add each checklist item
            for i, item in enumerate(checklist['items']):
                required_marker = "*" if item['required'] else ""
                markdown_content += f"- [ ] {item['text']}{required_marker}\n"
            
            # Add footer
            markdown_content += f"\n\n---\n*Last updated: {checklist.get('last_updated', 'Unknown')} by {checklist.get('updated_by', 'Unknown')}*"
            
            # Provide download link
            st.download_button(
                label="Download Markdown",
                data=markdown_content,
                file_name=f"{checklist['id']}_checklist.md",
                mime="text/markdown"
            )
        
        elif format == "Printable HTML":
            # Generate HTML
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>{checklist['title']}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                    h1 {{ color: #2c3e50; }}
                    .associated {{ font-style: italic; margin-bottom: 20px; }}
                    .checklist {{ margin-top: 20px; }}
                    .checklist-item {{ margin-bottom: 10px; }}
                    .required {{ color: #e74c3c; }}
                    .footer {{ margin-top: 30px; font-size: 0.8em; color: #7f8c8d; }}
                    @media print {{
                        body {{ margin: 0.5in; }}
                        .checklist-item {{ page-break-inside: avoid; }}
                    }}
                </style>
            </head>
            <body>
                <h1>{checklist['title']}</h1>
                <div class="associated">Associated with: {doc_title}</div>
                
                <div class="checklist">
            """
            
            # Add each checklist item
            for item in checklist['items']:
                required_class = "required" if item['required'] else ""
                required_marker = "*" if item['required'] else ""
                html_content += f"""
                    <div class="checklist-item">
                        <input type="checkbox"> <span class="{required_class}">{item['text']}{required_marker}</span>
                    </div>
                """
            
            # Close the HTML
            html_content += f"""
                </div>
                
                <div class="footer">
                    Last updated: {checklist.get('last_updated', 'Unknown')} by {checklist.get('updated_by', 'Unknown')}
                </div>
            </body>
            </html>
            """
            
            # Provide download link
            st.download_button(
                label="Download HTML",
                data=html_content,
                file_name=f"{checklist['id']}_checklist.html",
                mime="text/html"
            )
        
        elif format == "PDF":
            # For PDF, we'd ideally use a library like WeasyPrint or PDFKit
            st.info("PDF generation typically requires additional libraries. In a full implementation, this would generate a PDF document. For now, please use the HTML option and print to PDF from your browser.")