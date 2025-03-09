import streamlit as st
import random
import json
from datetime import datetime
import os
from pathlib import Path
import math

# Import our game components
from modules.game_components import (
    DataManager, Character, GameState, AchievementManager, SaveManager
)

# Import question bank directly
from modules.question_bank import QuestionBank

class GameModule:
    def __init__(self):
        """Initialize the Medical Physics Residency Game module."""
        # Initialize data managers
        self.data_manager = DataManager("data")
        self.save_manager = SaveManager("data/saves")
        
        # Initialize question bank
        self.question_bank = QuestionBank()
        
        # Ensure data directories exist
        os.makedirs("data", exist_ok=True)
        os.makedirs("data/saves", exist_ok=True)
        
        # Load data
        self._load_game_data()
        
        # Patch the GameState class with our improved question method
        self._patch_game_state()
    
    def _patch_game_state(self):
        """Patch the GameState class to use all questions from the question bank."""
        def get_question_for_difficulty(game_state_self, difficulty, data_manager, category=None):
            """Get a question of appropriate difficulty and category."""
            # Use all questions from the question bank
            question_bank = self.question_bank.questions
            
            # Filter questions by difficulty
            filtered_questions = [q for q in question_bank if q["difficulty"] == difficulty]
            
            # Further filter by category if specified
            if category and category != "general":
                category_questions = [q for q in filtered_questions if q["category"] == category]
                # Only use category filtering if we found matches
                if category_questions:
                    filtered_questions = category_questions
            
            # If no questions match, use any question of appropriate difficulty
            if not filtered_questions:
                filtered_questions = [q for q in question_bank if abs(q["difficulty"] - difficulty) <= 1]
            
            # If still no questions, use any question
            if not filtered_questions:
                filtered_questions = question_bank
                
            if not filtered_questions:
                # Fallback to a default question if nothing else is available
                return {
                    "id": "default",
                    "category": category or "general",
                    "difficulty": difficulty,
                    "question": "What is the primary goal of quality assurance in medical physics?",
                    "options": [
                        "To reduce equipment costs",
                        "To ensure patient safety and treatment accuracy",
                        "To minimize staff workload",
                        "To satisfy regulatory requirements only"
                    ],
                    "correct_answer": 1,
                    "explanation": "The primary goal of quality assurance in medical physics is to ensure patient safety and treatment accuracy through systematic testing and verification procedures."
                }
            
            # Return a random question from the filtered list
            return random.choice(filtered_questions)
        
        # Apply our patch to the GameState class
        GameState._get_question_for_difficulty = get_question_for_difficulty
    
    def _load_game_data(self):
        """Load the game data from JSON files."""
        # Get data from the data manager
        self.classes = self.data_manager.get_data("classes").get("classes", [])
        self.relics = self.data_manager.get_data("relics").get("relics", [])
        self.perks = self.data_manager.get_data("perks").get("perks", [])
        self.consumables = self.data_manager.get_data("consumables").get("consumables", [])
        self.encounters = self.data_manager.get_data("encounters").get("encounters", [])
        self.achievements = self.data_manager.get_data("achievements").get("achievements", [])
        self.challenge_modes = self.data_manager.get_data("challenge_modes").get("challenge_modes", [])
    
    # ===== MAIN ENTRY POINT =====
    
    def render_game_module(self):
        """Main entry point for rendering the game module."""
        st.title("Medical Physics Residency: The Game")
        
        # Add custom CSS for the game
        self._add_custom_css()
        
        # Initialize session state if not already done
        self._init_session_state()
        
        # Add character visualization - NEW FEATURE
        if st.session_state.game_view == "game" and st.session_state.current_character:
            self._render_character_visualization()
        
        # Render the appropriate view
        view_renderers = {
            "hub": self._render_hub_interface,
            "character_select": self._render_character_select,
            "game": self._render_game_interface,
            "question": self._render_question_interface,
            "result": self._render_question_result,
            "level_up": self._render_level_up_interface,
            "encounter": self._render_encounter_interface,
            "elite": self._render_elite_interface,
            "boss": self._render_boss_interface,
            "run_end": self._render_run_end_interface,
            "achievements": self._render_achievements_interface,
            "settings": self._render_settings_interface,
            "help": self._render_help_interface,
            "instructions": self._render_instructions_interface  # NEW VIEW
        }
        
        # Get the current view and render it
        current_view = st.session_state.game_view
        if current_view in view_renderers:
            view_renderers[current_view]()
        else:
            st.error(f"Unknown game view: {current_view}")
    
    # ===== NEW CHARACTER VISUALIZATION =====
    
    def _render_character_visualization(self):
        """Render a visual representation of the character."""
        character = st.session_state.current_character
        
        # Create a simple character representation based on icon
        character_icon = character.icon if hasattr(character, 'icon') else "(o o)"
        character_name = character.name if hasattr(character, 'name') else "Character"
        
        # Character container
        st.sidebar.markdown("## Your Character")
        
        # Character visualization with CSS animation
        st.sidebar.markdown(f"""
        <div class="character-visual">
            <div class="character-avatar">
                <div class="character-icon">{character_icon}</div>
                <div class="character-pulse"></div>
            </div>
            <div class="character-name">{character_name}</div>
            <div class="character-stats">
                <div>❤️ Lives: {character.lives}/{character.max_lives}</div>
                <div>✨ Insight: {character.insight}</div>
                <div>📊 Level: {character.level}</div>
            </div>
        </div>
        <style>
            .character-visual {{
                text-align: center;
                padding: 10px;
                background: #f8f9fa;
                border-radius: 10px;
                margin-bottom: 20px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }}
            .character-avatar {{
                position: relative;
                display: inline-block;
            }}
            .character-icon {{
                font-size: 28px;
                font-family: monospace;
                background: white;
                width: 80px;
                height: 80px;
                line-height: 80px;
                border-radius: 50%;
                margin: 0 auto;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                position: relative;
                z-index: 2;
            }}
            .character-pulse {{
                position: absolute;
                width: 80px;
                height: 80px;
                border-radius: 50%;
                background: rgba(52, 152, 219, 0.3);
                top: 0;
                left: 50%;
                transform: translateX(-50%);
                z-index: 1;
                animation: pulse 2s infinite;
            }}
            @keyframes pulse {{
                0% {{ transform: translateX(-50%) scale(1); opacity: 1; }}
                70% {{ transform: translateX(-50%) scale(1.1); opacity: 0.7; }}
                100% {{ transform: translateX(-50%) scale(1.2); opacity: 0; }}
            }}
            .character-name {{
                font-weight: bold;
                margin: 10px 0 5px;
            }}
            .character-stats {{
                font-size: 14px;
                text-align: left;
                padding: 5px 10px;
            }}
        </style>
        """, unsafe_allow_html=True)
        
        # Character movement animation when floor changes
        if hasattr(st.session_state, 'floor_changed') and st.session_state.floor_changed:
            st.sidebar.markdown("""
            <style>
                .character-icon {
                    animation: bounce 1s;
                }
                @keyframes bounce {
                    0%, 20%, 50%, 80%, 100% {transform: translateY(0);}
                    40% {transform: translateY(-20px);}
                    60% {transform: translateY(-10px);}
                }
            </style>
            """, unsafe_allow_html=True)
            # Reset the flag
            st.session_state.floor_changed = False
    
    # ===== STYLE AND INITIALIZATION =====
    
    def _add_custom_css(self):
        """Add custom CSS for the game UI."""
        st.markdown("""
        <style>
            /* Node styling */
            .node-card {
                border-radius: 10px;
                padding: 15px;
                text-align: center;
                margin: 10px 5px;
                cursor: pointer;
                transition: transform 0.2s, box-shadow 0.2s;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                min-height: 120px;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
            }
            .node-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            }
            .question-card {
                background-color: #3498db;
                color: white;
            }
            .reference-card {
                background-color: #2ecc71;
                color: white;
            }
            .rest-card {
                background-color: #9b59b6;
                color: white;
            }
            .treasure-card {
                background-color: #f1c40f;
                color: black;
            }
            .elite-card {
                background-color: #e74c3c;
                color: white;
            }
            .boss-card {
                background-color: #34495e;
                color: white;
            }
            .encounter-card {
                background-color: #1abc9c;
                color: white;
            }
            
            /* Character selection */
            .character-card {
                border-radius: 10px;
                padding: 20px;
                margin: 10px 0;
                background-color: white;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                transition: transform 0.2s;
                border: 2px solid transparent;
            }
            .character-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            }
            .character-card.selected {
                border-color: #3498db;
                background-color: #f0f8ff;
            }
            
            /* Hub cards */
            .hub-card {
                border-radius: 10px;
                padding: 20px;
                margin: 10px 0;
                background-color: white;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                transition: transform 0.2s;
            }
            .hub-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.15);
            }
            .locked {
                opacity: 0.6;
                filter: grayscale(70%);
            }
            
            /* Stats display */
            .stat-container {
                display: flex;
                justify-content: space-around;
                padding: 15px;
                background-color: #2c3e50;
                color: white;
                border-radius: 8px;
                margin-bottom: 20px;
                flex-wrap: wrap;
            }
            .stat-container > div {
                margin: 0 10px;
            }
            .progress-bar-container {
                margin-top: 5px;
                height: 8px;
                background-color: #ecf0f1;
                border-radius: 4px;
                overflow: hidden;
            }
            .progress-bar-value {
                height: 100%;
                background-color: #3498db;
            }
            
            /* Items and relics */
            .item-card {
                border-radius: 8px;
                padding: 12px;
                margin: 8px 0;
                background-color: #f8f9fa;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                transition: transform 0.2s;
                border-left: 4px solid #3498db;
            }
            .item-card:hover {
                transform: translateY(-3px);
                box-shadow: 0 3px 6px rgba(0,0,0,0.15);
            }
            .relic-card {
                border-radius: 8px;
                padding: 12px;
                margin: 8px 0;
                background-color: #f8f9fa;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                transition: transform 0.2s;
                border-left: 4px solid #e74c3c;
            }
            .relic-card:hover {
                transform: translateY(-3px);
                box-shadow: 0 3px 6px rgba(0,0,0,0.15);
            }
            .rarity-common {
                border-color: #3498db;
            }
            .rarity-uncommon {
                border-color: #9b59b6;
            }
            .rarity-rare {
                border-color: #f1c40f;
            }
            .rarity-legendary {
                border-color: #e74c3c;
                background-color: #fff9e6;
            }
            
            /* Result messages */
            .correct {
                color: #2ecc71;
                font-weight: bold;
            }
            .incorrect {
                color: #e74c3c;
                font-weight: bold;
            }
            
            /* Floor progress */
            .floor-indicator {
                display: inline-block;
                width: 30px;
                height: 30px;
                line-height: 30px;
                text-align: center;
                border-radius: 50%;
                background-color: #95a5a6;
                color: white;
                margin: 0 2px;
            }
            .floor-current {
                background-color: #3498db;
                font-weight: bold;
            }
            .floor-completed {
                background-color: #2ecc71;
            }
            .floor-boss {
                background-color: #e74c3c;
            }
            
            /* Achievements */
            .achievement-card {
                border-radius: 8px;
                padding: 15px;
                margin: 10px 0;
                background-color: #f8f9fa;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                opacity: 0.7;
                filter: grayscale(70%);
            }
            .achievement-card.unlocked {
                opacity: 1;
                filter: none;
                border-left: 4px solid #f1c40f;
                background-color: #fffde7;
            }
            
            /* Difficulty indicators */
            .difficulty {
                color: #f1c40f;
                letter-spacing: 2px;
            }
            
            /* Question styling */
            .question-option {
                padding: 10px 15px;
                margin: 8px 0;
                border-radius: 8px;
                background-color: #f8f9fa;
                cursor: pointer;
                transition: background-color 0.2s;
                border: 1px solid #ddd;
            }
            .question-option:hover {
                background-color: #e9ecef;
            }
            .option-selected {
                background-color: #3498db;
                color: white;
            }
            .option-correct {
                background-color: #2ecc71;
                color: white;
            }
            .option-incorrect {
                background-color: #e74c3c;
                color: white;
            }
            
            /* Instructions styling */
            .instruction-card {
                border-radius: 8px;
                padding: 15px;
                margin: 15px 0;
                background-color: #f8f9fa;
                border-left: 4px solid #3498db;
            }
            .instruction-step {
                margin: 10px 0;
                padding-left: 20px;
                position: relative;
            }
            .instruction-step:before {
                content: "•";
                position: absolute;
                left: 0;
                color: #3498db;
                font-weight: bold;
            }
                    
            /* Node status indicators */
            .node-status {
                padding: 3px 8px;
                border-radius: 10px;
                font-size: 0.7em;
                font-weight: bold;
            }
            
            .node-visited .node-status {
                background-color: #2ecc71;
                color: white;
            }
            
            .node-unavailable {
                opacity: 0.7;
                filter: grayscale(50%);
            }
            
            .node-unavailable .node-status {
                background-color: #95a5a6;
                color: white;
            }
            
            /* Node hover effects */
            .node-card {
                position: relative;
                overflow: hidden;
            }
            
            .node-card::before {
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
                transition: left 0.5s;
            }
            
            .node-card:hover::before {
                left: 100%;
            }
            
            /* Path animations */
            @keyframes pulse {
                0% { transform: scale(1); }
                50% { transform: scale(1.05); }
                100% { transform: scale(1); }
            }
            
            .question-card:not(.node-unavailable):not(.node-visited) {
                animation: pulse 2s infinite;
            }
            
            .elite-card:not(.node-unavailable):not(.node-visited) {
                animation: pulse 1.5s infinite;
            }
            
            .boss-card:not(.node-unavailable):not(.node-visited) {
                animation: pulse 1s infinite;
            }
        </style>
        """, unsafe_allow_html=True)
    
    def _generate_node_content(self, node, game_state):
        """Generate content for a node based on its type."""
        node_type = node.get("type", "question")
        difficulty = node.get("difficulty", 1)
        category = node.get("category", "general")
        
        if node_type == "question":
            # Use the question bank to get a suitable question
            question = self.question_bank.get_random_question(category, difficulty)
            return question if question else {
                "question": "What is the primary goal of quality assurance in medical physics?",
                "options": ["To reduce costs", "To ensure patient safety", "To minimize workload", "To satisfy regulations"],
                "correct_answer": 1,
                "explanation": "The primary goal of QA is to ensure patient safety and treatment accuracy."
            }
        
        elif node_type == "reference":
            return {
                "title": "Reference Material",
                "text": "You study important concepts in medical physics.",
                "effect": {"type": "gain_insight", "value": 10 * difficulty}
            }
        
        elif node_type == "rest":
            return {
                "title": "Break Room",
                "text": "You take a moment to rest and recover.",
                "effect": {"type": "restore_life", "value": 1}
            }
        
        elif node_type == "treasure":
            return {
                "title": "Conference",
                "text": "You attend a conference and make valuable connections.",
                "effect": {"type": "find_item", "rarity": "common" if difficulty <= 1 else "uncommon"}
            }
        
        elif node_type == "elite":
            # Create multiple questions for elite
            questions = []
            for i in range(2):  # Elite nodes have 2 questions
                q = self.question_bank.get_random_question(category, difficulty)
                if q:
                    questions.append(q)
            
            if not questions:
                # Fallback if no questions found
                questions = [{
                    "question": "What principle forms the basis of ALARA in radiation protection?",
                    "options": ["Maximizing dose", "Minimizing dose", "Optimizing dose", "Standardizing dose"],
                    "correct_answer": 2,
                    "explanation": "ALARA (As Low As Reasonably Achievable) is based on optimizing dose."
                }]
            
            return {
                "title": "Complex Case",
                "text": "You face a challenging clinical scenario.",
                "questions": questions,
                "reward": {"type": "find_relic", "rarity": "uncommon"}
            }
        
        elif node_type == "boss":
            # Create multiple questions of increasing difficulty for boss
            questions = []
            for i in range(3):  # Boss has 3 questions
                q = self.question_bank.get_random_question(category, min(3, i+1))
                if q:
                    questions.append(q)
            
            if not questions:
                # Fallback
                questions = [{
                    "question": "What is the primary challenge in IMRT QA?",
                    "options": ["Setup time", "Dose verification", "Record keeping", "Staff training"],
                    "correct_answer": 1,
                    "explanation": "Verifying the complex dose distribution is the primary challenge in IMRT QA."
                }]
            
            return {
                "title": "Rotation Evaluation",
                "text": "Your knowledge is being tested as part of your rotation evaluation.",
                "questions": questions,
                "reward": {"type": "complete_rotation", "value": game_state.current_floor}
            }
        
        elif node_type == "encounter":
            return {
                "title": "Special Event",
                "text": "You encounter an interesting situation that tests your knowledge.",
                "effect": {"type": "gain_insight", "value": 15}
            }
        
        # Default content if type not recognized
        return {
            "title": "Unknown Node",
            "text": "You encounter an unknown situation.",
            "effect": {"type": "gain_insight", "value": 5}
        }

    def _init_session_state(self):
        """Initialize session state for game data if not already done."""
        # Use a unique key for this module to avoid conflicts
        if 'game_initialized' not in st.session_state:
            st.session_state.game_initialized = True
            
            # Game view state
            st.session_state.game_view = "hub"
            st.session_state.question_result = None
            st.session_state.current_question = None
            st.session_state.encountering_event = None
            
            # Player data
            st.session_state.player_data = {
                "class": None,
                "level": 1,
                "completed_runs": 0,
                "total_score": 0,
                "highest_score": 0,
                "highest_floor": 0
            }
            
            # Current run
            st.session_state.current_character = None
            st.session_state.game_state = None
            
            # Achievement tracking
            st.session_state.achievement_manager = AchievementManager(self.data_manager)
            
            # Session flags
            st.session_state.save_on_exit = True
            st.session_state.selected_character_class = None
            st.session_state.pending_perk_selection = None
            st.session_state.run_success = None
            st.session_state.final_score = 0
            
            # UI state
            st.session_state.show_question_timer = False
            st.session_state.difficulty_setting = "normal"
            st.session_state.hub_unlocked = ["resident_office", "clinical_area"]
            
            # Character animation state
            st.session_state.floor_changed = False
    
    # ===== GAME LOGIC METHODS =====
    
    def start_new_run(self):
        """Initialize a new run with the selected character class."""
        if not st.session_state.selected_character_class:
            st.error("Please select a character class first.")
            return
        
        # Get the selected class data
        class_data = next((c for c in self.classes if c["id"] == st.session_state.selected_character_class), None)
        if not class_data:
            st.error("Selected character class not found.")
            return
        
        # Create the character
        character = Character(class_data)
        
        # Add starting relic if defined
        if hasattr(character, 'starting_relic_id') and character.starting_relic_id:
            starting_relic = next((r for r in self.relics if r["id"] == character.starting_relic_id), None)
            if starting_relic:
                character.add_relic(starting_relic)
        
        # Create the game state
        game_state = GameState(character)
        
        # Generate a branching path
        game_state.generate_branching_path(self.data_manager)
        
        # Store in session state
        st.session_state.current_character = character
        st.session_state.game_state = game_state
        
        # Switch to game view
        st.session_state.game_view = "game"
    
    def visit_node(self, node_id):
        """Process a player visiting a node."""
        game_state = st.session_state.game_state
        if not game_state:
            st.error("No active game found.")
            return
        
        # Visit the node
        node = game_state.visit_node(node_id)
        if not node:
            st.error("Node not found or already visited.")
            return
        
        # Generate content if needed
        if node["content"] is None:
            node["content"] = self._generate_node_content(node, game_state)
        
        # Process node effects
        result = game_state.process_node_effects(node, self.data_manager)
        
        # Handle different node types
        node_type = result.get("node_type")
        
        if node_type == "question":
            # Show question UI
            st.session_state.current_question = result.get("question")
            st.session_state.game_view = "question"
        
        elif node_type == "reference":
            # Show reference result
            st.session_state.question_result = "reference"
            st.session_state.game_view = "result"
        
        elif node_type == "rest":
            # Show rest result
            st.session_state.question_result = "rest"
            st.session_state.game_view = "result"
        
        elif node_type == "treasure":
            # Show treasure result
            st.session_state.question_result = "treasure"
            st.session_state.found_item = result.get("item")
            st.session_state.game_view = "result"
        
        elif node_type == "elite":
            # Show elite challenge
            st.session_state.elite_questions = result.get("questions")
            st.session_state.elite_reward = result.get("reward")
            st.session_state.elite_title = result.get("title")
            st.session_state.elite_text = result.get("text")
            st.session_state.current_elite_question = 0
            st.session_state.game_view = "elite"
        
        elif node_type == "boss":
            # Show boss challenge
            st.session_state.boss_questions = result.get("questions")
            st.session_state.boss_reward = result.get("reward")
            st.session_state.boss_title = result.get("title")
            st.session_state.boss_text = result.get("text")
            st.session_state.current_boss_question = 0
            st.session_state.game_view = "boss"
        
        elif node_type == "encounter":
            # Show encounter
            st.session_state.encountering_event = result.get("encounter")
            st.session_state.game_view = "encounter"
    
    def answer_question(self, answer_index):
        """Process a player answering a question."""
        game_state = st.session_state.game_state
        question = st.session_state.current_question
        
        if not game_state or not question:
            st.error("No active question found.")
            return
        
        # Process the answer
        result = game_state.answer_question(question, answer_index, self.data_manager)
        
        # Store result for display
        st.session_state.answer_result = result
        
        # Check for level up
        if result.get("level_up"):
            st.session_state.pending_perk_selection = result.get("perk_choices")
            st.session_state.game_view = "level_up"
        elif result.get("run_over"):
            # End the run
            self.end_run(False)
        else:
            # Show result
            st.session_state.question_result = "correct" if result.get("correct") else "incorrect"
            st.session_state.game_view = "result"
    
    def select_perk(self, perk_id):
        """Select a perk after leveling up."""
        game_state = st.session_state.game_state
        if not game_state:
            st.error("No active game found.")
            return
        
        # Select the perk
        result = game_state.select_perk(perk_id, self.data_manager)
        
        # Clear the pending selection
        st.session_state.pending_perk_selection = None
        
        # Return to the previous state (usually the result screen)
        st.session_state.question_result = "correct"  # Assuming we're coming from a correct answer
        st.session_state.game_view = "result"
    
    def continue_after_node(self):
        """Continue to next stage after completing a node."""
        game_state = st.session_state.game_state
        if not game_state:
            st.error("No active game found.")
            return
        
        # Check if a node on this floor has been visited
        if game_state.check_floor_completion():
            # Complete the floor
            result = game_state.complete_floor()
            
            # Check if this was the last floor
            if game_state.current_floor >= game_state.max_floor:
                self.end_run(True)
                return
            
            # Generate the next floor
            game_state.generate_new_floor(self.data_manager)
            
            # Set floor changed flag for animation
            st.session_state.floor_changed = True
        
        # Back to game view
        st.session_state.game_view = "game"
    
    def end_run(self, success):
        """End the current run."""
        game_state = st.session_state.game_state
        if not game_state:
            st.error("No active game found.")
            return
        
        # End the run
        result = game_state.end_run(success)
        
        # Update player data
        st.session_state.player_data["completed_runs"] += 1
        st.session_state.player_data["total_score"] += result.get("final_score", 0)
        st.session_state.player_data["highest_score"] = max(
            st.session_state.player_data["highest_score"],
            result.get("final_score", 0)
        )
        st.session_state.player_data["highest_floor"] = max(
            st.session_state.player_data["highest_floor"],
            game_state.current_floor
        )
        
        # Check for achievements
        unlocked_achievements = st.session_state.achievement_manager.check_run_achievements(game_state)
        
        # Store run results
        st.session_state.run_success = success
        st.session_state.final_score = result.get("final_score", 0)
        st.session_state.unlocked_achievements = unlocked_achievements
        
        # Check for hub area unlocks based on progress
        self._check_for_hub_unlocks()
        
        # Auto-save
        if st.session_state.save_on_exit:
            self.save_manager.save_game(
                game_state,
                st.session_state.player_data,
                st.session_state.achievement_manager
            )
        
        # Show run end screen
        st.session_state.game_view = "run_end"
    
    def _check_for_hub_unlocks(self):
        """Check for new hub area unlocks based on game progress."""
        # Define hub areas
        hub_areas = self._get_hub_areas()
        
        # Check each area for unlocks
        for area in hub_areas:
            if area["id"] in st.session_state.hub_unlocked:
                continue
            
            if area["unlock_condition"].startswith("completed_runs:"):
                required = int(area["unlock_condition"].split(":")[1])
                if st.session_state.player_data["completed_runs"] >= required:
                    st.session_state.hub_unlocked.append(area["id"])
                    st.session_state.new_area_unlocked = area["id"]
            
            elif area["unlock_condition"].startswith("max_floor:"):
                required = int(area["unlock_condition"].split(":")[1])
                if st.session_state.player_data["highest_floor"] >= required:
                    st.session_state.hub_unlocked.append(area["id"])
                    st.session_state.new_area_unlocked = area["id"]
    
    def return_to_hub(self):
        """Return to the hub interface."""
        st.session_state.game_view = "hub"
        st.session_state.current_character = None
        st.session_state.game_state = None
    
    # ===== INTERFACE RENDERING METHODS =====
    
    def _render_hub_interface(self):
        """Render the hub (department) interface."""
        st.subheader("Memorial Hospital Physics Department")
        
        # Add a prominent instructions button
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("📚 Game Instructions", key="show_instructions", use_container_width=True):
                st.session_state.game_view = "instructions"
                return
        
        # Show player stats
        if st.session_state.player_data["completed_runs"] > 0:
            stats_col1, stats_col2, stats_col3 = st.columns(3)
            with stats_col1:
                st.metric("Completed Runs", st.session_state.player_data["completed_runs"])
            with stats_col2:
                st.metric("Highest Score", st.session_state.player_data["highest_score"])
            with stats_col3:
                st.metric("Highest Floor", st.session_state.player_data["highest_floor"])
        
        st.markdown("Your medical physics journey begins here. Choose an area to explore.")
        
        # Check for newly unlocked areas
        if hasattr(st.session_state, 'new_area_unlocked'):
            area_name = next((a["name"] for a in self._get_hub_areas() if a["id"] == st.session_state.new_area_unlocked), "New Area")
            st.success(f"🎉 Congratulations! You've unlocked a new area: {area_name}")
            # Clear the notification after showing
            delattr(st.session_state, 'new_area_unlocked')
        
        # Arrange hub areas in a grid
        hub_areas = self._get_hub_areas()
        cols = st.columns(3)  # 3 columns
        
        for i, area in enumerate(hub_areas):
            with cols[i % 3]:
                # Check if area is unlocked
                is_unlocked = area["id"] in st.session_state.hub_unlocked
                
                # Create the hub area card
                with st.container():
                    st.markdown(f"""
                    <div class="hub-card {'' if is_unlocked else 'locked'}">
                        <h3>{area["icon"]} {area["name"]} {' 🔒' if not is_unlocked else ''}</h3>
                        <p>{area["description"]}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Only make the button work if area is unlocked
                    if is_unlocked:
                        if st.button(f"Enter {area['name']}", key=f"area_{area['id']}"):
                            if area["id"] == "clinical_area":
                                # Go to character selection
                                st.session_state.game_view = "character_select"
                            elif area["id"] == "achievements":
                                # View achievements
                                st.session_state.game_view = "achievements"
                            else:
                                # Other areas would have their own functions
                                st.info(f"Entering {area['name']} - Feature coming soon!")
    
    def _get_hub_areas(self):
        """Get the hub areas configuration."""
        return [
            {"id": "resident_office", "name": "Resident Office", "description": "Your personal workspace", "unlock_condition": "start", "icon": "🏠"},
            {"id": "clinical_area", "name": "Clinical Area", "description": "Start a new rotation", "unlock_condition": "start", "icon": "🏥"},
            {"id": "planning_room", "name": "Planning Room", "description": "Improve treatment planning skills", "unlock_condition": "completed_runs:3", "icon": "📋"},
            {"id": "machine_shop", "name": "Machine Shop", "description": "Learn about equipment", "unlock_condition": "completed_runs:5", "icon": "🔧"},
            {"id": "research_lab", "name": "Research Lab", "description": "Conduct experiments", "unlock_condition": "max_floor:5", "icon": "🔬"},
            {"id": "conference_room", "name": "Conference Room", "description": "Special challenges", "unlock_condition": "completed_runs:8", "icon": "🎓"},
            {"id": "achievements", "name": "Achievement Hall", "description": "View your achievements", "unlock_condition": "completed_runs:1", "icon": "🏆"}
        ]
    
    def _render_instructions_interface(self):
        """Render the game instructions interface."""
        st.subheader("How to Play")
        
        if st.button("← Back to Department", key="back_to_hub_from_instructions"):
            st.session_state.game_view = "hub"
            return
        
        # Basic game overview
        st.markdown("""
        ## Medical Physics Residency: The Game
        
        Welcome to your virtual medical physics residency! In this educational game, 
        you'll navigate through different clinical rotations, answering questions and 
        solving challenges to advance your career.
        """)
        
        # Instructions cards
        st.markdown("""
        <div class="instruction-card">
            <h3>📋 Getting Started</h3>
            <div class="instruction-step">Choose a character class from the Clinical Area, each with unique abilities</div>
            <div class="instruction-step">Progress through floors by visiting nodes and completing challenges</div>
            <div class="instruction-step">Collect items, relics, and perks to boost your capabilities</div>
            <div class="instruction-step">Try to reach the highest floor with the best score!</div>
        </div>
        
        <div class="instruction-card">
            <h3>🎮 Gameplay Mechanics</h3>
            <div class="instruction-step">Each floor contains multiple nodes to visit</div>
            <div class="instruction-step">Answering questions correctly earns experience and score</div>
            <div class="instruction-step">Wrong answers cost lives - if you run out, your rotation ends</div>
            <div class="instruction-step">Complete all nodes on a floor to advance to the next one</div>
            <div class="instruction-step">Special boss challenges appear every 5 floors</div>
        </div>
        
        <div class="instruction-card">
            <h3>🧩 Node Types</h3>
            <div class="instruction-step">📝 <strong>Question</strong>: Test your knowledge</div>
            <div class="instruction-step">📚 <strong>Reference</strong>: Study without risk</div>
            <div class="instruction-step">☕ <strong>Break Room</strong>: Recover a life</div>
            <div class="instruction-step">🎁 <strong>Conference</strong>: Find useful items</div>
            <div class="instruction-step">⚠️ <strong>Complex Case</strong>: Multiple challenging questions</div>
            <div class="instruction-step">⭐ <strong>Rotation Evaluation</strong>: Major milestone challenges</div>
            <div class="instruction-step">🔍 <strong>Special Event</strong>: Unique encounters</div>
        </div>
        
        <div class="instruction-card">
            <h3>🏆 Progress & Rewards</h3>
            <div class="instruction-step">Level up to unlock new perks</div>
            <div class="instruction-step">Earn achievements for special milestones</div>
            <div class="instruction-step">Unlock new areas in the hospital as you complete more rotations</div>
            <div class="instruction-step">Improve your knowledge and see your high scores increase</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Controls explanation
        st.subheader("Controls")
        st.markdown("""
        - Click on nodes to visit them
        - Select answers by clicking option buttons
        - Use items from your inventory when needed
        - Navigate between different hospital areas from the hub
        """)
        
        # Back button
        st.button("Start Playing!", key="start_playing_from_instructions", on_click=lambda: setattr(st.session_state, 'game_view', 'hub'))
    
    def _render_character_select(self):
        """Render the character selection interface."""
        st.subheader("Select Your Character")
        st.markdown("Choose your character class to begin a new rotation.")
        
        # Navigation
        if st.button("← Back to Department", key="back_to_hub_from_char_select"):
            st.session_state.game_view = "hub"
            return
        
        # Character selection
        classes = self.classes
        if not classes:
            st.error("No character classes found. Please check the game data.")
            return
        
        # Use a 2-column layout for character cards
        self._render_character_selection_cards(classes)
        
        # Start button (only enabled if a character is selected)
        st.markdown("---")
        if st.session_state.selected_character_class:
            if st.button("Start Rotation", key="start_rotation", type="primary"):
                self.start_new_run()
        else:
            st.warning("Please select a character class to begin.")
    
    def _render_character_selection_cards(self, classes):
        """Render the character selection cards in a grid."""
        col1, col2 = st.columns(2)
        
        for i, char_class in enumerate(classes):
            with col1 if i % 2 == 0 else col2:
                # Check if this class is selected
                is_selected = st.session_state.selected_character_class == char_class["id"]
                
                # Character card
                st.markdown(f"""
                <div class="character-card{'  selected' if is_selected else ''}">
                    <h3>{char_class["name"]}</h3>
                    <div style="font-family: monospace; font-size: 1.2em; text-align: center; margin: 10px 0;">
                        {char_class["icon"]}
                    </div>
                    <p>{char_class["description"]}</p>
                    <p><strong>Starting Relic:</strong> {self._get_relic_name(char_class["starting_relic"])}</p>
                    <p><strong>Special Ability:</strong> {char_class["special_ability"]["name"]} - {char_class["special_ability"]["description"]}</p>
                    <p><strong>Weakness:</strong> {char_class["weakness"]["description"]}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Selection button
                if st.button("Select" if not is_selected else "Selected ✓", key=f"select_{char_class['id']}"):
                    st.session_state.selected_character_class = char_class["id"]
                    st.rerun()
    
    def _get_relic_name(self, relic_id):
        """Get the name of a relic by ID."""
        relic = next((r for r in self.relics if r["id"] == relic_id), None)
        return relic["name"] if relic else "Unknown Relic"
    
    def _render_game_interface(self):
        """Render the main game (run) interface."""
        game_state = st.session_state.game_state
        character = st.session_state.current_character
        
        if not game_state or not character:
            self._render_error_state()
            return
        
        # Player stats
        self._render_player_stats(character, game_state)
        
        # Visual path map - NEW!
        self._render_visual_path_map(game_state)
        
        # Game board - current floor
        self._render_current_floor_nodes(game_state)
        
        # Inventory and relics
        self._render_inventory_and_relics(character)
    
    def _render_error_state(self):
        """Render error state when no active game is found."""
        st.error("No active game found.")
        if st.button("Return to Department"):
            self.return_to_hub()
    
    def _render_player_stats(self, character, game_state):
        """Render the player stats bar."""
        # Stats container
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"**Character:** {character.name}")
        
        with col2:
            st.markdown(f"**Lives:** ❤️ {character.lives}/{character.max_lives}")
        
        with col3:
            st.markdown(f"**Insight:** ✨ {character.insight}")
        
        with col4:
            st.markdown(f"**Level:** Lv. {character.level}")
        
        # Experience bar
        exp_percentage = min(100, int(character.experience / character.experience_to_next_level * 100))
        st.markdown(f"""
        <div class="progress-bar-container">
            <div class="progress-bar-value" style="width: {exp_percentage}%;"></div>
        </div>
        <div style="text-align: center; font-size: 0.8em; color: #7f8c8d;">
            Experience: {character.experience} / {character.experience_to_next_level}
        </div>
        """, unsafe_allow_html=True)
        
        # Current score
        st.markdown(f"**Score:** {game_state.score}")

    def _render_path_map(self, game_state):
        """Render a simple map of the path structure."""
        if not game_state.path:
            return
            
        st.markdown("### Progress Map")
        
        # For a simple initial implementation, just show floor progress
        total_floors = game_state.max_floor
        current_floor = game_state.current_floor
        
        # Create a progress bar
        progress_percentage = (current_floor - 1) / total_floors * 100
        
        st.markdown(f"""
        <div style="margin: 10px 0;">
            <div style="background-color: #f0f0f0; height: 20px; border-radius: 10px; overflow: hidden;">
                <div style="background-color: #3498db; width: {progress_percentage}%; height: 100%;"></div>
            </div>
            <div style="text-align: center; margin-top: 5px; font-size: 0.8em;">
                Floor {current_floor} of {total_floors}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Show a basic text representation of floors
        cols = st.columns(total_floors)
        for i in range(total_floors):
            floor_num = i + 1
            with cols[i]:
                if floor_num < current_floor:
                    st.markdown(f"<div style='text-align: center; color: #2ecc71;'>✓</div>", unsafe_allow_html=True)
                elif floor_num == current_floor:
                    st.markdown(f"<div style='text-align: center; color: #3498db; font-weight: bold;'>{floor_num}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div style='text-align: center; color: #95a5a6;'>{floor_num}</div>", unsafe_allow_html=True)

    def _render_visual_path_map(self, game_state):
        """Render a visual map of the game path using SVG with node type icons."""
        
        if not game_state.path:
            return
        
        st.markdown("### Path Map")
        
        # Configure SVG dimensions
        svg_width = 700
        svg_height = 250
        node_radius = 15
        floor_spacing = svg_width / (game_state.max_floor + 1)
        
        # Start building SVG
        svg = f'<svg width="{svg_width}" height="{svg_height}" xmlns="http://www.w3.org/2000/svg">'
        
        # Draw connecting lines between floors
        for floor_idx in range(game_state.max_floor - 1):
            current_floor_nodes = game_state.path[floor_idx] if floor_idx < len(game_state.path) else []
            next_floor_nodes = game_state.path[floor_idx + 1] if floor_idx + 1 < len(game_state.path) else []
            
            # Skip if either floor is empty
            if not current_floor_nodes or not next_floor_nodes:
                continue
            
            # Draw connections from each node on current floor to each node on next floor
            x1 = floor_spacing * (floor_idx + 1)
            x2 = floor_spacing * (floor_idx + 2)
            
            for i, node1 in enumerate(current_floor_nodes):
                # Calculate y position for current node
                y1 = svg_height * (i + 1) / (len(current_floor_nodes) + 1)
                
                # Check if this node is visited
                node1_visited = node1.get("visited", False)
                
                for j, node2 in enumerate(next_floor_nodes):
                    # Calculate y position for next node
                    y2 = svg_height * (j + 1) / (len(next_floor_nodes) + 1)
                    
                    # For branching paths, check if there's a connection
                    if hasattr(game_state, 'path_connections'):
                        connection_exists = node2["id"] in game_state.path_connections.get(node1["id"], [])
                        if not connection_exists:
                            continue
                    
                    # Determine connection style based on visited state
                    if node1_visited and node2.get("visited", False):
                        # Path fully traveled
                        line_style = 'stroke="#2ecc71" stroke-width="3"'
                    elif node1_visited:
                        # Available path
                        line_style = 'stroke="#3498db" stroke-width="2"'
                    else:
                        # Unavailable path
                        line_style = 'stroke="#bdc3c7" stroke-width="1" stroke-dasharray="5,5"'
                    
                    svg += f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" {line_style} />'
        
        # Draw nodes for each floor
        for floor_idx, floor_nodes in enumerate(game_state.path):
            x = floor_spacing * (floor_idx + 1)
            
            # Draw floor label
            floor_label = f"Floor {floor_idx + 1}"
            if floor_idx + 1 == game_state.current_floor:
                label_style = 'font-weight: bold; fill: #3498db;'
            else:
                label_style = 'fill: #7f8c8d;'
            
            svg += f'<text x="{x}" y="20" text-anchor="middle" style="{label_style}">{floor_label}</text>'
            
            # Draw each node on this floor
            for i, node in enumerate(floor_nodes):
                y = svg_height * (i + 1) / (len(floor_nodes) + 1)
                
                # Determine node availability
                is_available = True
                if floor_idx + 1 > game_state.current_floor:
                    # Future floor - not available yet
                    is_available = False
                elif floor_idx + 1 == game_state.current_floor:
                    # Current floor - check branching availability
                    if hasattr(game_state, 'get_available_nodes'):
                        available_nodes = game_state.get_available_nodes()
                        is_available = node in available_nodes
                
                # Node style based on state
                if node.get("visited", False):
                    # Visited node
                    circle_style = 'fill="#2ecc71" stroke="#27ae60" stroke-width="2"'
                    text_style = 'fill="white" font-weight="bold"'
                    opacity = '1'
                elif floor_idx + 1 == game_state.current_floor and is_available:
                    # Current floor node (available)
                    circle_style = 'fill="#3498db" stroke="#2980b9" stroke-width="2"'
                    text_style = 'fill="white"'
                    opacity = '1'
                else:
                    # Future or unavailable node - SHOW TYPE BUT GREYED OUT
                    # Use different colors based on node type for better visualization
                    node_colors = {
                        "question": "#3498db",
                        "reference": "#2ecc71",
                        "rest": "#9b59b6",
                        "treasure": "#f1c40f",
                        "elite": "#e74c3c",
                        "boss": "#34495e",
                        "encounter": "#1abc9c"
                    }
                    base_color = node_colors.get(node.get("type", "question"), "#95a5a6")
                    circle_style = f'fill="{base_color}" stroke="#7f8c8d" stroke-width="1"'
                    text_style = 'fill="white"'
                    opacity = '0.5'  # Partially transparent for future nodes
                
                # Get node icon based on type
                node_icons = {
                    "question": "📝",
                    "reference": "📚",
                    "rest": "☕",
                    "treasure": "🎁",
                    "elite": "⚠️",
                    "boss": "⭐",
                    "encounter": "🔍"
                }
                node_icon = node_icons.get(node.get("type", "unknown"), "❓")
                
                # Draw node circle with opacity
                svg += f'<circle cx="{x}" cy="{y}" r="{node_radius}" {circle_style} opacity="{opacity}" />'
                
                # Draw node text (emoji)
                svg += f'<text x="{x}" y="{y+5}" text-anchor="middle" style="{text_style}" font-size="12px" opacity="{opacity}">{node_icon}</text>'
                
                # Add difficulty indicator for available nodes
                if node.get("difficulty", 1) > 1:
                    difficulty_pips = "★" * node.get("difficulty", 1)
                    svg += f'<text x="{x}" y="{y+25}" text-anchor="middle" fill="#f1c40f" font-size="8px" opacity="{opacity}">{difficulty_pips}</text>'
                
                # Add tooltip with more details
                tooltip_text = f"{node.get('name', 'Node')} ({node.get('category', 'unknown').capitalize()}) - Difficulty: {node.get('difficulty', 1)}"
                svg += f'<title>{tooltip_text}</title>'
        
        svg += '</svg>'
        
        # Render the SVG in Streamlit
        st.markdown(svg, unsafe_allow_html=True)

    def _render_floor_progress(self, game_state):
        """Render a visual indicator of floor progress."""
        max_floor = game_state.max_floor
        current_floor = game_state.current_floor
        
        # Create a progress bar with floor indicators
        indicators = []
        for i in range(1, max_floor + 1):
            if i == current_floor:
                css_class = "floor-current"
            elif i < current_floor:
                css_class = "floor-completed"
            else:
                css_class = ""
            
            # Mark boss floors
            if i % 5 == 0:
                css_class += " floor-boss"
            
            indicators.append(f'<span class="floor-indicator {css_class}">{i}</span>')
        
        st.markdown(f"""
        <div style="text-align: center; margin: 10px 0;">
            {"".join(indicators)}
        </div>
        """, unsafe_allow_html=True)
    
    def _render_current_floor_nodes(self, game_state):
        """Render the nodes for the current floor with better "clickable" styling."""
        st.subheader(f"Floor {game_state.current_floor}")
        
        # Add instructions to clarify the choice mechanic
        st.markdown("### Choose Your Path")
        st.markdown("Select one node to proceed to the next floor.")
        
        # Get nodes for the current floor
        current_floor_index = game_state.current_floor - 1
        if current_floor_index < 0 or current_floor_index >= len(game_state.path):
            st.error("Floor data not found.")
            return
        
        current_floor_nodes = game_state.path[current_floor_index]
        
        # If using branching paths, get only the available nodes
        if hasattr(game_state, 'get_available_nodes'):
            available_nodes = game_state.get_available_nodes()
        else:
            available_nodes = current_floor_nodes
        
        # Check if any node on this floor has been visited
        floor_completed = any(node["visited"] for node in current_floor_nodes)
        
        # Create columns for nodes
        cols = st.columns(len(current_floor_nodes))
        
        # Custom CSS for better button styling
        st.markdown("""
        <style>
            /* Make buttons look more like cards */
            .node-button {
                width: 100%;
                height: auto;
                padding: 15px !important;
                white-space: normal !important;
                text-align: center;
                display: flex !important;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                color: white !important;
                border: none !important;
                border-radius: 10px !important;
                transition: transform 0.2s, box-shadow 0.2s;
            }
            
            .node-button:hover:not(:disabled) {
                transform: translateY(-5px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.2) !important;
            }
            
            /* Node type colors */
            .question-button { background-color: #3498db !important; }
            .reference-button { background-color: #2ecc71 !important; }
            .rest-button { background-color: #9b59b6 !important; }
            .treasure-button { background-color: #f1c40f !important; color: black !important; }
            .elite-button { background-color: #e74c3c !important; }
            .boss-button { background-color: #34495e !important; }
            .encounter-button { background-color: #1abc9c !important; }
            
            /* Node visited/unavailable styles */
            .node-visited { background-color: #2ecc71 !important; }
            .node-unavailable { 
                opacity: 0.7;
                filter: grayscale(40%);
            }
            
            /* Button content styling */
            .node-icon {
                font-size: 24px;
                margin-bottom: 8px;
            }
            
            .node-title {
                font-weight: bold;
                margin-bottom: 5px;
            }
            
            .node-difficulty {
                color: #f1c40f;
                letter-spacing: 2px;
                margin-bottom: 5px;
            }
            
            .node-category {
                font-size: 12px;
                margin-bottom: 8px;
            }
            
            .node-status-badge {
                font-size: 10px;
                padding: 3px 8px;
                border-radius: 10px;
                background-color: rgba(255,255,255,0.2);
                margin-top: 5px;
            }
        </style>
        """, unsafe_allow_html=True)
        
        for i, node in enumerate(current_floor_nodes):
            with cols[i]:
                # Determine if this node is available in the path
                is_available = node in available_nodes
                
                # Get node type and state information
                node_type = node["type"]
                node_visited = node["visited"]
                
                # Create CSS classes for the button
                button_classes = f"node-button {node_type}-button"
                if node_visited:
                    button_classes += " node-visited"
                elif not is_available or floor_completed:
                    button_classes += " node-unavailable"
                
                # Difficulty stars
                difficulty_stars = "★" * node["difficulty"] if node["difficulty"] > 0 else "—"
                
                # Determine status badge text
                if node_visited:
                    status_text = "Completed"
                elif not is_available or floor_completed:
                    status_text = "Unavailable"
                else:
                    status_text = "Available"
                
                # Create the button HTML
                button_html = f"""
                <div class="node-icon">{node['icon']}</div>
                <div class="node-title">{node['name']}</div>
                <div class="node-difficulty">{difficulty_stars}</div>
                <div class="node-category">{node.get('category', '').capitalize()}</div>
                <div class="node-status-badge">{status_text}</div>
                """
                
                # Determine button functionality
                disabled = node_visited or not is_available or floor_completed
                
                # Create the actual button - Streamlit allows HTML within a button
                if st.button(button_html, key=f"node_button_{node['id']}", 
                            disabled=disabled, use_container_width=True,
                            help=f"{node['name']} ({node.get('category', '').capitalize()}) - Difficulty: {node['difficulty']}"):
                    self.visit_node(node["id"])
        
        # Add a "Continue" button if floor is completed
        if floor_completed:
            st.markdown("---")
            if st.button("Continue to Next Floor", type="primary", use_container_width=True):
                self.continue_after_node()

    def _render_enhanced_node_card(self, node, is_available):
        """Render a more detailed and interactive node card."""
        # Get node type info
        node_type = node["type"]
        node_visited = node["visited"]
        
        # Style based on node type
        card_class = f"node-card {node_type}-card"
        if not is_available:
            card_class += " node-unavailable"
        if node_visited:
            card_class += " node-visited"
        
        # Difficulty pips
        difficulty_display = "★" * node["difficulty"] if node["difficulty"] > 0 else "—"
        
        # Render card with more details
        with st.container():
            st.markdown(f"""
            <div class="{card_class}">
                <div style="font-size: 2em;">{node['icon']}</div>
                <div style="font-weight: bold;">{node['name']}</div>
                <div class="difficulty">{difficulty_display}</div>
                <div style="font-size: 0.8em; margin-top: 5px;">{node.get('category', '').capitalize()}</div>
                <div style="margin-top: 8px;">
                    <span class="node-status">{
                        "Completed" if node_visited else 
                        "Available" if is_available else 
                        "Unavailable"
                    }</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Node interaction button
            if not node_visited and is_available:
                node_button_text = self._get_node_button_text(node)
                if st.button(node_button_text, key=f"visit_{node['id']}"):
                    self.visit_node(node["id"])
            elif node_visited:
                st.button("Completed", key=f"visited_{node['id']}", disabled=True)
            else:
                st.button("Unavailable", key=f"unavailable_{node['id']}", disabled=True)

    def _get_node_button_text(self, node):
        """Get appropriate button text based on node type."""
        node_type = node.get("type", "question")
        
        button_texts = {
            "question": "Answer Question",
            "reference": "Study Material",
            "rest": "Take a Break",
            "treasure": "Find Treasure",
            "elite": "Face Challenge",
            "boss": "Face Evaluation",
            "encounter": "Explore Event"
        }
        
        return button_texts.get(node_type, "Choose")
    
    def _render_node_card(self, node):
        """Render a single node card."""
        # Get node type info
        node_type = node["type"]
        
        # Style based on node type
        card_class = f"node-card {node_type}-card"
        
        # Difficulty pips
        difficulty_display = "★" * node["difficulty"] if node["difficulty"] > 0 else "—"
        
        # Render card
        with st.container():
            st.markdown(f"""
            <div class="{card_class}">
                <div style="font-size: 2em;">{node['icon']}</div>
                <div>{node['name']}</div>
                <div class="difficulty">{difficulty_display}</div>
                <div style="font-size: 0.8em; margin-top: 5px;">{node.get('category', '').capitalize()}</div>
            </div>
            """, unsafe_allow_html=True)
    
    def _render_inventory_and_relics(self, character):
        """Render the inventory and relics sections."""
        st.markdown("---")
        inv_col, relic_col = st.columns(2)
        
        with inv_col:
            self._render_inventory(character)
        
        with relic_col:
            self._render_relics(character)
    
    def _render_inventory(self, character):
        """Render the player's inventory."""
        st.subheader("Inventory")
        
        if not character.inventory:
            st.info("Your inventory is empty. Find items during your rotations!")
            return
        
        # Display each item
        for i, item in enumerate(character.inventory):
            rarity_class = f"rarity-{item.get('rarity', 'common')}"
            
            st.markdown(f"""
            <div class="item-card {rarity_class}">
                <h4>{item.get('icon', '🔮')} {item['name']}</h4>
                <p>{item['description']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Use", key=f"use_item_{i}"):
                # Apply item effect
                character.use_item(i)
                st.rerun()
    
    def _render_relics(self, character):
        """Render the player's relics."""
        st.subheader("Relics")
        
        if not character.relics:
            st.info("You don't have any relics yet.")
            return
        
        # Display each relic
        for relic in character.relics:
            rarity_class = f"rarity-{relic.get('rarity', 'common')}"
            
            st.markdown(f"""
            <div class="relic-card {rarity_class}">
                <h4>{relic.get('icon', '🔮')} {relic['name']}</h4>
                <p>{relic['description']}</p>
                <p><em>{relic['effect']['description']}</em></p>
            </div>
            """, unsafe_allow_html=True)
    
    def _render_question_interface(self):
        """Render the question interface."""
        question = st.session_state.current_question
        
        if not question:
            st.error("No question found!")
            if st.button("Return to Game"):
                st.session_state.game_view = "game"
            return
        
        # Get category info
        category_name = question.get("category", "Unknown").capitalize()
        
        # Question card
        st.subheader(f"{category_name} Question")
        st.markdown(f"### {question['question']}")
        
        # Option buttons
        for i, option in enumerate(question['options']):
            if st.button(f"{chr(65+i)}. {option}", key=f"answer_{i}", use_container_width=True):
                self.answer_question(i)
    
    def _render_question_result(self):
        """Render the result of answering a question."""
        # Determine which type of result to show
        result_type = st.session_state.question_result
        
        if result_type == "correct":
            self._render_correct_answer_result()
        elif result_type == "incorrect":
            self._render_incorrect_answer_result()
        elif result_type == "reference":
            self._render_reference_result()
        elif result_type == "rest":
            self._render_rest_result()
        elif result_type == "treasure":
            self._render_treasure_result()
        else:
            st.error("Unknown result type")
        
        # Continue button
        if st.button("Continue", key="result_continue"):
            self.continue_after_node()
    
    def _render_correct_answer_result(self):
        """Render the result for a correct answer."""
        answer_result = st.session_state.get('answer_result', {})
        question = st.session_state.current_question
        
        st.success("CORRECT!")
        if question:
            st.markdown(f"### Explanation:")
            st.markdown(question.get("explanation", "No explanation available."))
        
        # Show rewards
        st.markdown("### Rewards:")
        exp_gained = answer_result.get("experience_gained", 0)
        score_gained = answer_result.get("score_gained", 0)
        streak = answer_result.get("streak", 0)
        
        st.markdown(f"* +{exp_gained} XP")
        st.markdown(f"* +{score_gained} points")
        
        if streak > 1:
            st.markdown(f"* Streak bonus: {streak}x")
    
    def _render_incorrect_answer_result(self):
        """Render the result for an incorrect answer."""
        question = st.session_state.current_question
        
        st.error("INCORRECT!")
        if question:
            st.markdown(f"### Explanation:")
            st.markdown(question.get("explanation", "No explanation available."))
        
        # Show penalty
        st.markdown("### Penalty:")
        st.markdown("* -1 life")
        st.markdown("* Streak reset")
    
    def _render_reference_result(self):
        """Render the result for a reference node."""
        st.info("You studied the material carefully.")
        st.markdown("### Gained:")
        st.markdown("* +10 insight")
    
    def _render_rest_result(self):
        """Render the result for a rest node."""
        st.success("You took a well-deserved break.")
        st.markdown("### Effect:")
        st.markdown("* +1 life restored")
    
    def _render_treasure_result(self):
        """Render the result for a treasure node."""
        st.success("You found a useful item!")
        if hasattr(st.session_state, 'found_item'):
            item = st.session_state.found_item
            if item:
                st.markdown(f"### {item.get('icon', '🎁')} {item['name']}")
                st.markdown(item["description"])
    
    def _render_level_up_interface(self):
        """Render the level-up interface with perk selection."""
        character = st.session_state.current_character
        
        if not character:
            st.error("No active character found.")
            return
        
        st.markdown(f"""
        <h2 style="text-align: center;">Level Up! 🎉</h2>
        <p style="text-align: center;">Your character has reached level {character.level}!</p>
        """, unsafe_allow_html=True)
        
        # Show available perks to choose from
        st.subheader("Choose a Perk")
        
        perk_choices = st.session_state.pending_perk_selection
        if not perk_choices:
            st.warning("No perks available to select.")
            if st.button("Continue without a perk"):
                st.session_state.game_view = "result"
            return
        
        # Display perk options
        self._render_perk_choices(perk_choices)
    
    def _render_perk_choices(self, perk_choices):
        """Render perk choices for level up."""
        cols = st.columns(len(perk_choices))
        
        for i, perk in enumerate(perk_choices):
            with cols[i]:
                rarity_class = f"rarity-{perk.get('rarity', 'common')}"
                
                st.markdown(f"""
                <div class="item-card {rarity_class}">
                    <h4>{perk['name']}</h4>
                    <p>{perk['description']}</p>
                    <p><em>{perk['effect']['description']}</em></p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("Select", key=f"select_perk_{perk['id']}"):
                    self.select_perk(perk['id'])
    
    def _render_encounter_interface(self):
        """Render the special encounter interface."""
        encounter = st.session_state.encountering_event
        if not encounter:
            st.error("No active encounter found.")
            return
        
        st.subheader(encounter["name"])
        st.markdown(encounter["description"])
        
        # Handle different encounter types
        encounter_type = encounter.get("type", "unknown")
        
        # Dictionary of encounter renderers
        encounter_renderers = {
            "choice": self._render_choice_encounter,
            "shop": self._render_shop_encounter,
            "challenge": self._render_challenge_encounter,
            "training": self._render_training_encounter,
            "rest": self._render_rest_encounter,
            "multi_event": self._render_multi_event_encounter
        }
        
        # Get the appropriate renderer for this encounter type
        renderer = encounter_renderers.get(encounter_type)
        if renderer:
            renderer(encounter)
        else:
            st.warning(f"Unknown encounter type: {encounter_type}")
            if st.button("Continue"):
                st.session_state.encountering_event = None
                self.continue_after_node()
    
    def _render_choice_encounter(self, encounter):
        """Render a choice-based encounter."""
        choices = encounter.get("choices", [])
        
        for i, choice in enumerate(choices):
            st.markdown(f"### Option {i+1}: {choice['text']}")
            
            if st.button(f"Choose Option {i+1}", key=f"choice_{i}"):
                # Handle the choice
                # For now, just continue
                st.session_state.encountering_event = None
                self.continue_after_node()
    
    def _render_shop_encounter(self, encounter):
        """Render a shop encounter."""
        items = encounter.get("items", [])
        character = st.session_state.current_character
        
        st.markdown(f"### Available Items")
        st.markdown(f"You have {character.insight} insight points to spend.")
        
        for i, item in enumerate(items):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**{item['name']}**: {item['description']}")
                st.markdown(f"*Cost: {item['cost']} insight*")
            
            with col2:
                if character.insight >= item['cost']:
                    if st.button(f"Purchase", key=f"buy_{i}"):
                        # Purchase the item
                        character.insight -= item['cost']
                        
                        # Add the item based on its type
                        if item['effect']['type'] == 'relic':
                            relic = next((r for r in self.relics if r['id'] == item['effect']['id']), None)
                            if relic:
                                character.add_relic(relic)
                        elif item['effect']['type'] == 'consumable':
                            consumable = next((c for c in self.consumables if c['id'] == item['effect']['id']), None)
                            if consumable:
                                for _ in range(item['effect'].get('quantity', 1)):
                                    character.add_to_inventory(consumable)
                        
                        st.rerun()
                else:
                    st.button(f"Cannot Afford", key=f"cant_buy_{i}", disabled=True)
        
        if st.button("Leave Shop"):
            st.session_state.encountering_event = None
            self.continue_after_node()
    
    def _render_challenge_encounter(self, encounter):
        """Render a challenge encounter."""
        # Similar to a question, but with different rewards/penalties
        st.markdown("### Challenge")
        st.markdown(encounter.get("description", ""))
        
        # For now, just a continue button
        if st.button("Accept Challenge"):
            # In a full implementation, this would show a question or task
            st.session_state.encountering_event = None
            self.continue_after_node()
    
    def _render_training_encounter(self, encounter):
        """Render a training/mentorship encounter."""
        skill_options = encounter.get("skill_options", [])
        
        st.markdown("### Available Skills")
        
        for i, skill in enumerate(skill_options):
            st.markdown(f"**{skill['name']}**: {skill['description']}")
            
            if st.button(f"Learn {skill['name']}", key=f"learn_{i}"):
                # Learn the skill (add the perk)
                perk = next((p for p in self.perks if p['id'] == skill['perk']), None)
                if perk:
                    st.session_state.current_character.add_perk(perk)
                
                st.session_state.encountering_event = None
                self.continue_after_node()
        
        if st.button("Decline Training"):
            st.session_state.encountering_event = None
            self.continue_after_node()
    
    def _render_rest_encounter(self, encounter):
        """Render a rest encounter."""
        effects = encounter.get("effects", [])
        
        st.markdown("### Effects")
        for effect in effects:
            if effect["type"] == "heal":
                st.markdown(f"* Restore {effect['value']} lives")
            elif effect["type"] == "skip_reward":
                st.markdown("* Skip rewards for this floor")
        
        if st.button("Rest"):
            # Apply effects
            for effect in effects:
                if effect["type"] == "heal":
                    st.session_state.current_character.restore_life(effect["value"])
            
            st.session_state.encountering_event = None
            self.continue_after_node()
    
    def _render_multi_event_encounter(self, encounter):
        """Render a multi-event encounter."""
        events = encounter.get("events", [])
        
        st.markdown("### Available Activities")
        
        for i, event in enumerate(events):
            st.markdown(f"**{event['name']}**: {event['description']}")
            
            if st.button(f"Choose {event['name']}", key=f"event_{i}"):
                # For simplicity, just apply rewards directly
                if "reward" in event:
                    reward = event["reward"]
                    if reward["type"] == "insight":
                        st.session_state.current_character.insight += reward["value"]
                    elif reward["type"] == "experience":
                        st.session_state.current_character.gain_experience(reward["value"])
                    elif reward["type"] == "consumable":
                        consumable = next((c for c in self.consumables if c['rarity'] == reward['rarity']), None)
                        if consumable:
                            st.session_state.current_character.add_to_inventory(consumable)
                
                st.session_state.encountering_event = None
                self.continue_after_node()
    
    def _render_elite_interface(self):
        """Render the elite challenge interface."""
        if not hasattr(st.session_state, 'elite_questions') or not st.session_state.elite_questions:
            st.error("No elite challenge questions found.")
            return
        
        questions = st.session_state.elite_questions
        current_question_index = st.session_state.get('current_elite_question', 0)
        
        if current_question_index >= len(questions):
            # All questions answered, show reward
            self._render_elite_completion(st.session_state.elite_reward)
        else:
            # Show the current question
            self._render_elite_question(questions[current_question_index], current_question_index, len(questions))
    
    def _render_elite_completion(self, reward):
        """Render the elite challenge completion screen."""
        st.success("Challenge completed successfully!")
        
        if reward:
            st.markdown("### Reward")
            if reward["type"] == "find_relic":
                rarity = reward.get("rarity", "common")
                # Find a relic of the specified rarity
                available_relics = [r for r in self.relics if r.get("rarity") == rarity]
                if available_relics:
                    relic = random.choice(available_relics)
                    st.session_state.current_character.add_relic(relic)
                    
                    st.markdown(f"You received the **{relic['name']}** relic!")
                    st.markdown(relic["description"])
        
        if st.button("Continue"):
            st.session_state.elite_questions = None
            st.session_state.elite_reward = None
            self.continue_after_node()
    
    def _render_elite_question(self, question, current_index, total_questions):
        """Render an elite challenge question."""
        st.subheader(f"Challenge Question {current_index + 1}/{total_questions}")
        st.markdown(question["question"])
        
        # Options
        for i, option in enumerate(question['options']):
            if st.button(f"{chr(65+i)}. {option}", key=f"elite_answer_{i}", use_container_width=True):
                # Check the answer
                if i == question["correct_answer"]:
                    # Correct
                    st.session_state.current_elite_question += 1
                    st.rerun()
                else:
                    # Incorrect - lose the challenge
                    st.session_state.elite_questions = None
                    st.session_state.elite_reward = None
                    st.session_state.current_character.take_damage(1)
                    st.session_state.question_result = "incorrect"
                    st.session_state.current_question = question  # To show the explanation
                    st.session_state.game_view = "result"
    
    def _render_boss_interface(self):
        """Render the boss challenge interface."""
        if not hasattr(st.session_state, 'boss_questions') or not st.session_state.boss_questions:
            st.error("No boss challenge questions found.")
            return
        
        questions = st.session_state.boss_questions
        current_question_index = st.session_state.get('current_boss_question', 0)
        
        if current_question_index >= len(questions):
            # All questions answered, show reward
            self._render_boss_completion(st.session_state.boss_reward)
        else:
            # Show current question
            self._render_boss_question(questions[current_question_index], current_question_index, len(questions))
    
    def _render_boss_completion(self, reward):
        """Render the boss challenge completion screen."""
        st.success("Boss challenge completed successfully!")
        
        if reward:
            st.markdown("### Reward")
            if reward["type"] == "complete_rotation":
                floor_value = reward.get("value", 0)
                st.markdown(f"You've completed the rotation evaluation for floor {floor_value}!")
        
        if st.button("Continue"):
            st.session_state.boss_questions = None
            st.session_state.boss_reward = None
            self.continue_after_node()
    
    def _render_boss_question(self, question, current_index, total_questions):
        """Render a boss challenge question."""
        st.subheader(f"Boss Question {current_index + 1}/{total_questions}")
        st.markdown(question["question"])
        
        # Options
        for i, option in enumerate(question['options']):
            if st.button(f"{chr(65+i)}. {option}", key=f"boss_answer_{i}", use_container_width=True):
                # Check the answer
                if i == question["correct_answer"]:
                    # Correct
                    st.session_state.current_boss_question += 1
                    st.rerun()
                else:
                    # Incorrect - lose a life but continue
                    st.session_state.current_character.take_damage(1)
                    
                    if st.session_state.current_character.lives <= 0:
                        # Game over
                        self.end_run(False)
                        return
                    
                    st.session_state.current_boss_question += 1
                    st.rerun()
    
    def _render_run_end_interface(self):
        """Render the end-of-run summary."""
        success = st.session_state.run_success
        final_score = st.session_state.final_score
        game_state = st.session_state.game_state
        
        # Success or failure header
        if success:
            st.success("# Rotation Complete!")
            st.markdown("Your clinical rotation has been completed successfully. Your knowledge and skills have grown!")
        else:
            st.error("# Rotation Incomplete")
            st.markdown("You weren't able to complete this rotation. Take what you've learned and try again!")
        
        # Stats
        self._render_run_end_stats(game_state, final_score)
        
        # Add path statistics section
        if hasattr(game_state, 'path_history'):
            st.subheader("Path Statistics")
            
            path_summary = game_state.path_history.get_path_summary()
            player_strategy = game_state.path_history.get_player_strategy()
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Nodes Visited", path_summary["nodes_visited"])
            
            with col2:
                st.metric("Elites Defeated", path_summary["elites_defeated"])
            
            with col3:
                st.metric("Highest Floor", path_summary["highest_floor"])
            
            with col4:
                st.metric("Path Strategy", player_strategy)
            
            # Show node distribution
            st.subheader("Node Type Distribution")
            
            # Convert to percentages for better visualization
            total_nodes = path_summary["nodes_visited"]
            if total_nodes > 0:
                percentages = {k: (v / total_nodes) * 100 for k, v in path_summary["node_distribution"].items()}
                
                # Create a horizontal bar chart
                # For Streamlit, we need to format the data correctly
                import pandas as pd
                chart_data = []
                for node_type, percentage in percentages.items():
                    if percentage > 0:
                        chart_data.append({
                            "Node Type": node_type.capitalize(),
                            "Percentage": percentage
                        })
                
                # Use Streamlit's native bar chart if we have data
                if chart_data:
                    chart_df = pd.DataFrame(chart_data).set_index("Node Type")
                    st.bar_chart(chart_df)
        
        # Unlocked achievements
        self._render_unlocked_achievements()
        
        # Return to hub button
        if st.button("Return to Department", key="return_to_hub"):
            self.return_to_hub()
    
    def _render_run_end_stats(self, game_state, final_score):
        """Render the end of run statistics."""
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Floors Completed", game_state.current_floor if game_state else 0)
        
        with col2:
            st.metric("Questions Correct", game_state.streak if game_state else 0)
        
        with col3:
            st.metric("Final Score", final_score)
        
        with col4:
            st.metric("Total Rotations", st.session_state.player_data["completed_runs"])
    
    def _render_unlocked_achievements(self):
        """Render any unlocked achievements in this run."""
        if hasattr(st.session_state, 'unlocked_achievements') and st.session_state.unlocked_achievements:
            st.subheader("Achievements Unlocked")
            
            for achievement_result in st.session_state.unlocked_achievements:
                if achievement_result["success"]:
                    achievement = achievement_result["achievement"]
                    st.markdown(f"""
                    <div class="achievement-card unlocked">
                        <h4>{achievement['icon']} {achievement['name']}</h4>
                        <p>{achievement['description']}</p>
                    </div>
                    """, unsafe_allow_html=True)
    
    def _render_achievements_interface(self):
        """Render the achievements interface."""
        st.subheader("Achievement Hall")
        
        if st.button("← Back to Department", key="back_to_hub_from_achievements"):
            st.session_state.game_view = "hub"
            return
        
        # Get achievements and organize by difficulty
        self._render_achievements_by_difficulty()
    
    def _render_achievements_by_difficulty(self):
        """Render achievements grouped by difficulty level."""
        # Get achievements
        achievements = self.data_manager.get_data("achievements").get("achievements", [])
        unlocked_achievements = st.session_state.achievement_manager.unlocked_achievements
        
        # Group achievements by difficulty
        difficulties = ["easy", "medium", "hard", "very_hard"]
        achievements_by_difficulty = {d: [] for d in difficulties}
        
        for achievement in achievements:
            difficulty = achievement.get("difficulty", "medium")
            achievements_by_difficulty[difficulty].append(achievement)
        
        # Display achievements by difficulty
        for difficulty in difficulties:
            difficulty_name = {
                "easy": "Basic Achievements",
                "medium": "Intermediate Achievements",
                "hard": "Advanced Achievements",
                "very_hard": "Expert Achievements"
            }.get(difficulty, difficulty.capitalize())
            
            st.markdown(f"### {difficulty_name}")
            
            if not achievements_by_difficulty[difficulty]:
                st.info(f"No {difficulty_name.lower()} achievements available.")
                continue
            
            # Create a 2-column layout for achievements
            cols = st.columns(2)
            
            for i, achievement in enumerate(achievements_by_difficulty[difficulty]):
                is_unlocked = achievement["id"] in unlocked_achievements
                
                with cols[i % 2]:
                    st.markdown(f"""
                    <div class="achievement-card{'  unlocked' if is_unlocked else ''}">
                        <h4>{achievement['icon']} {achievement['name']}</h4>
                        <p>{achievement['description']}</p>
                        <p>{'' if is_unlocked else '???'}</p>
                    </div>
                    """, unsafe_allow_html=True)
    
    def _render_settings_interface(self):
        """Render the settings interface."""
        st.subheader("Game Settings")
        
        if st.button("← Back to Department", key="back_to_hub_from_settings"):
            st.session_state.game_view = "hub"
            return
        
        # Settings sections
        self._render_game_settings()
        self._render_save_management()
    
    def _render_game_settings(self):
        """Render game settings options."""
        # Autosave setting
        st.checkbox("Auto-save on run completion", 
                   value=st.session_state.save_on_exit,
                   key="save_on_exit_setting",
                   on_change=lambda: setattr(st.session_state, 'save_on_exit', st.session_state.save_on_exit_setting))
        
        # Question timer
        st.checkbox("Show question timer", 
                   value=st.session_state.show_question_timer,
                   key="show_timer_setting",
                   on_change=lambda: setattr(st.session_state, 'show_question_timer', st.session_state.show_timer_setting))
        
        # Difficulty setting
        st.selectbox("Difficulty",
                    ["easy", "normal", "hard", "expert"],
                    index=["easy", "normal", "hard", "expert"].index(st.session_state.difficulty_setting),
                    key="difficulty_setting_select",
                    on_change=lambda: setattr(st.session_state, 'difficulty_setting', st.session_state.difficulty_setting_select))
    
    def _render_save_management(self):
        """Render save management section."""
        st.subheader("Save Management")
        
        # List available saves
        save_result = self.save_manager.list_saves()
        if save_result["success"] and save_result["saves"]:
            self._render_save_table(save_result["saves"])
        else:
            st.info("No saves found.")
        
        # Save current game
        st.subheader("Save Current Game")
        
        save_name = st.text_input("Save Name", value=f"save_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        
        if st.button("Save Game", key="save_game_button"):
            if not st.session_state.game_state:
                st.warning("No active game to save.")
            else:
                save_result = self.save_manager.save_game(
                    st.session_state.game_state,
                    st.session_state.player_data,
                    st.session_state.achievement_manager,
                    save_name
                )
                if save_result["success"]:
                    st.success(f"Game saved as '{save_name}'!")
                else:
                    st.error(f"Error saving game: {save_result['message']}")
    
    def _render_save_table(self, saves):
        """Render a table of available save files."""
        # Show saves in a table
        save_data = []
        for save in saves:
            save_data.append([
                save["name"],
                save["date"],
                save["player_class"],
                save["player_level"],
                save["completed_runs"]
            ])
        
        st.table({"Save Name": [s[0] for s in save_data],
                 "Date": [s[1] for s in save_data],
                 "Class": [s[2] for s in save_data],
                 "Level": [s[3] for s in save_data],
                 "Runs": [s[4] for s in save_data]})
        
        # Load/delete options
        col1, col2 = st.columns(2)
        
        with col1:
            selected_save = st.selectbox("Select Save", [s["name"] for s in saves])
            
            if st.button("Load Save", key="load_save_button"):
                # Load the selected save
                load_result = self.save_manager.load_game(selected_save, self.data_manager)
                if load_result["success"]:
                    st.session_state.player_data = load_result["player_data"]
                    st.session_state.game_state = load_result["game_state"]
                    st.session_state.achievement_manager = load_result["achievement_manager"]
                    
                    if st.session_state.game_state:
                        st.session_state.current_character = st.session_state.game_state.character
                        st.session_state.game_view = "game"
                    else:
                        st.session_state.game_view = "hub"
                    
                    st.success(f"Save '{selected_save}' loaded successfully!")
                    st.rerun()
                else:
                    st.error(f"Error loading save: {load_result['message']}")
        
        with col2:
            if st.button("Delete Save", key="delete_save_button"):
                # Delete the selected save
                delete_result = self.save_manager.delete_save(selected_save)
                if delete_result["success"]:
                    st.success(f"Save '{selected_save}' deleted successfully!")
                    st.rerun()
                else:
                    st.error(f"Error deleting save: {delete_result['message']}")
    
    def _render_help_interface(self):
        """Render the help and documentation interface."""
        st.subheader("Game Help & Documentation")
        
        if st.button("← Back to Department", key="back_to_hub_from_help"):
            st.session_state.game_view = "hub"
            return
        
        # Basic game explanation
        st.markdown("""
        ## How to Play
        
        **Medical Physics Residency: The Game** is a roguelike knowledge game where you progress through floors by answering 
        questions and making strategic choices. Here's how it works:
        
        1. **Select a Character Class**: Each class has unique abilities and starting relics.
        2. **Progress Through Floors**: Each floor has multiple nodes to visit.
        3. **Answer Questions**: Test your medical physics knowledge.
        4. **Collect Items & Relics**: Build your inventory with helpful tools.
        5. **Level Up**: Gain perks to strengthen your character.
        
        Try to reach the highest floor with the best score!
        """)
        
        # Additional help sections
        self._render_help_node_types()
        self._render_help_items_relics()
        self._render_help_classes()
        self._render_help_tips()
        self._render_help_scoring()
        self._render_help_acknowledgments()
    
    def _render_help_node_types(self):
        """Render help section for node types."""
        st.markdown("""
        ## Node Types
        
        * **📝 Question**: Answer medical physics questions to gain experience and advance.
        * **📚 Reference**: Study important concepts to gain insight without risk.
        * **☕ Break Room**: Recover a life point.
        * **🎁 Conference**: Find useful items to help on your journey.
        * **⚠️ Complex Case**: Challenging questions with better rewards.
        * **⭐ Rotation Evaluation**: Major tests at milestone floors (every 5th floor).
        * **🔍 Special Event**: Unique opportunities with various outcomes.
        """)
    
    def _render_help_items_relics(self):
        """Render help section for items and relics."""
        st.markdown("""
        ## Items & Relics
        
        **Items** are consumable one-time use tools that help you in specific situations.
        
        **Relics** are permanent artifacts that provide ongoing benefits throughout your run.
        
        Items and relics come in different rarities:
        * **Common**: Basic benefits
        * **Uncommon**: Stronger effects
        * **Rare**: Powerful advantages
        * **Legendary**: Game-changing abilities
        """)
    
    def _render_help_classes(self):
        """Render help section for character classes."""
        st.markdown("""
        ## Character Classes
        
        * **Therapy Newbie**: Fresh out of graduate school with enthusiasm. Gets bonus on treatment planning questions.
        * **QA Specialist**: Detail-oriented and meticulous. Excels at machine QA questions.
        * **Dosimetry Wizard**: Natural talent for calculations. Gets help with dosimetry questions.
        * **Regulatory Expert**: Knows all the rules. Gets bonus insights from reference nodes.
        * **Medical Physics Resident**: Balanced character with well-rounded education. Gets a free mistake on each floor.
        """)
    
    def _render_help_tips(self):
        """Render help section with gameplay tips."""
        st.markdown("""
        ## Tips for Success
        
        * Balance risk and reward when choosing which nodes to visit.
        * Consider your character's strengths and weaknesses when answering questions.
        * Use consumable items strategically rather than hoarding them.
        * Try to maintain a question streak for bonus points.
        * Complete achievements to unlock permanent benefits.
        * Unlock new areas in the department hub by completing runs and reaching higher floors.
        """)
    
    def _render_help_scoring(self):
        """Render help section for scoring system."""
        st.markdown("""
        ## Scoring System
        
        Your score is calculated based on:
        * Correct answers (base points)
        * Answer streak (bonus multiplier)
        * Floor completion (50 points per floor)
        * Remaining lives (20 points per life)
        * Successful run completion (500 bonus points)
        
        The difficulty setting also affects your scoring potential.
        """)
    
    def _render_help_acknowledgments(self):
        """Render acknowledgments section."""
        st.markdown("""
        ## Acknowledgments
        
        This game was designed as an educational tool for medical physics residents and students.
        The questions and content are inspired by medical physics concepts, but this is not intended
        as a formal study tool or replacement for proper education and training.
        
        Have fun and happy learning!
        """)