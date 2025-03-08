import streamlit as st
import random
import json
from datetime import datetime

class GameModule:
    def __init__(self):
        """Initialize the Medical Physics Residency Game module."""
        # Initialize game data
        self.categories = self._get_categories()
        self.node_types = self._get_node_types()
        self.hub_areas = self._get_hub_areas()
        self.perks = self._get_perks()
        self.consumables = self._get_consumables()
        self.question_bank = self._get_question_bank()
    
    def _render_game_module(self):
        """Main entry point for rendering the game module."""
        st.title("Medical Physics Residency: The Game")
        
        # Add custom CSS for the game
        self._add_custom_css()
        
        # Add introduction banner when first visiting game
        if 'game_intro_seen' not in st.session_state:
            st.session_state.game_intro_seen = True
            with st.container():
                st.info("""
                # Welcome to Medical Physics Residency: The Game!
                
                Your journey as a medical physics resident begins here. Navigate through 
                clinical rotations, answer knowledge-testing questions, and build your skills.
                
                Start your adventure by entering the Clinical Area in the department hub.
                """)
                if st.button("Got it!"):
                    st.rerun()
        
        # Initialize session state if not already done
        self._init_session_state()
        
        # Render the appropriate view
        if st.session_state.game_view == "hub":
            self._render_hub_interface()
        elif st.session_state.game_view == "game":
            self._render_game_interface()
        elif st.session_state.game_view == "question":
            self._render_question_interface()
        elif st.session_state.game_view == "result":
            self._render_question_result()
        elif st.session_state.game_view == "run_end":
            self._render_run_end_interface()
    
    def _add_custom_css(self):
        """Add custom CSS for the game UI."""
        st.markdown("""
        <style>
            .node-card {
                border-radius: 5px;
                padding: 10px;
                text-align: center;
                margin: 5px;
                cursor: pointer;
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
            .hub-card {
                border-radius: 10px;
                padding: 20px;
                margin: 10px 0;
                background-color: #f5f5f5;  /* Light gray instead of white */
                border: 1px solid #ddd;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                transition: transform 0.2s;
            }
            .hub-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.15);
            }
            .locked {
                opacity: 0.6;
                filter: blur(2px);  /* Blur locked content */
                pointer-events: none;  /* Prevent interaction */
            }
            .stat-container {
                display: flex;
                justify-content: space-around;
                padding: 10px;
                background-color: #2c3e50;
                color: white;
                border-radius: 5px;
                margin-bottom: 20px;
            }
            .progress-bar-container {
                margin-top: 5px;
                height: 5px;
                background-color: #ecf0f1;
                border-radius: 2px;
            }
            .progress-bar-value {
                height: 100%;
                background-color: #3498db;
            }
            .correct {
                color: #2ecc71;
                font-weight: bold;
            }
            .incorrect {
                color: #e74c3c;
                font-weight: bold;
            }
        </style>
        """, unsafe_allow_html=True)
    
    def _init_session_state(self):
        """Initialize session state for game data if not already done."""
        # Use a unique key for this module to avoid conflicts
        if 'game_initialized' not in st.session_state:
            st.session_state.game_initialized = True
            
            # Player stats
            st.session_state.player = {
                "name": "Resident",
                "year": 1,
                "rotation": 0,
                "lives": 3,
                "max_lives": 3,
                "insight": 0,
                "level": 1,
                "experience": 0,
                "experience_to_next_level": 100,
                "unlocked_perks": [],
                "active_perks": [],
                "inventory": []
            }
            
            # Game progression
            st.session_state.current_floor = 0
            st.session_state.max_floor = 10
            st.session_state.nodes_per_floor = 3
            st.session_state.current_node = None
            st.session_state.visited_nodes = set()
            st.session_state.hub_unlocked = ["resident_office", "clinical_area"]
            
            # Game state
            st.session_state.game_view = "hub"  # hub, game, question, result, run_end
            st.session_state.question_result = None  # correct, incorrect
            st.session_state.current_question = None
            
            # Meta progression
            st.session_state.completed_runs = 0
            st.session_state.achievements_unlocked = set()
            st.session_state.permanent_upgrades = set()
            
            # Current run
            st.session_state.current_run = {
                "path": [],
                "score": 0,
                "streak": 0,
                "relics": []
            }
    
    # ========== GAME DATA METHODS ==========
    
    def _get_categories(self):
        """Return the categories for questions."""
        return [
            {"id": "dosimetry", "name": "Dosimetry", "color": "#3498db"},
            {"id": "qa", "name": "Quality Assurance", "color": "#2ecc71"},
            {"id": "radiation", "name": "Radiation Safety", "color": "#e74c3c"},
            {"id": "planning", "name": "Treatment Planning", "color": "#9b59b6"},
            {"id": "calculation", "name": "Calculations", "color": "#f1c40f"},
            {"id": "imaging", "name": "Imaging Physics", "color": "#1abc9c"},
            {"id": "regulations", "name": "Regulations", "color": "#e67e22"}
        ]
    
    def _get_node_types(self):
        """Return the node types for the game."""
        return [
            {"id": "question", "name": "Question", "description": "Test your knowledge", "difficulty": [1, 2, 3], "icon": "📝"},
            {"id": "reference", "name": "Reference", "description": "Learn without being tested", "difficulty": [0], "icon": "📚"},
            {"id": "rest", "name": "Break Room", "description": "Recover 1 life", "difficulty": [0], "icon": "☕"},
            {"id": "treasure", "name": "Conference", "description": "Find a helpful item", "difficulty": [0], "icon": "🎁"},
            {"id": "elite", "name": "Complex Case", "description": "Difficult but rewarding", "difficulty": [2, 3], "icon": "⚠️"},
            {"id": "boss", "name": "Rotation Evaluation", "description": "Major test of knowledge", "difficulty": [3], "icon": "⭐"}
        ]
    
    def _get_hub_areas(self):
        """Return the hub areas for the game."""
        return [
            {"id": "resident_office", "name": "Resident Office", "description": "Your personal workspace", "unlock_condition": "start", "icon": "🏠"},
            {"id": "clinical_area", "name": "Clinical Area", "description": "Start a new rotation", "unlock_condition": "start", "icon": "🏥"},
            {"id": "planning_room", "name": "Planning Room", "description": "Improve treatment planning skills", "unlock_condition": "completed_runs:3", "icon": "📋"},
            {"id": "machine_shop", "name": "Machine Shop", "description": "Learn about equipment", "unlock_condition": "completed_runs:5", "icon": "🔧"},
            {"id": "research_lab", "name": "Research Lab", "description": "Conduct experiments", "unlock_condition": "max_floor:5", "icon": "🔬"},
            {"id": "conference_room", "name": "Conference Room", "description": "Special challenges", "unlock_condition": "completed_runs:8", "icon": "🎓"}
        ]
    
    def _get_perks(self):
        """Return the perks for the game."""
        return [
            {"id": "quick_learner", "name": "Quick Learner", "description": "Gain 15% more experience from questions", "effect": "experience_bonus", "value": 0.15},
            {"id": "resilient", "name": "Resilient", "description": "Start each rotation with +1 life", "effect": "max_lives_bonus", "value": 1},
            {"id": "dosimetry_expert", "name": "Dosimetry Expert", "description": "Dosimetry questions are 20% easier", "effect": "category_bonus", "category": "dosimetry", "value": 0.2},
            {"id": "qa_specialist", "name": "QA Specialist", "description": "QA questions are 20% easier", "effect": "category_bonus", "category": "qa", "value": 0.2},
            {"id": "clinical_mind", "name": "Clinical Mind", "description": "Treatment planning questions are 20% easier", "effect": "category_bonus", "category": "planning", "value": 0.2},
            {"id": "mathematical_genius", "name": "Mathematical Genius", "description": "Calculation questions show one wrong answer", "effect": "reveal_wrong_answer", "category": "calculation", "value": 1},
            {"id": "well_rested", "name": "Well Rested", "description": "Recover 1 life when completing a floor", "effect": "floor_life_recovery", "value": 1},
            {"id": "efficient_study", "name": "Efficient Study", "description": "50% chance to preserve consumables on use", "effect": "preserve_consumable", "value": 0.5}
        ]
    
    def _get_consumables(self):
        """Return the consumable items for the game."""
        return [
            {"id": "coffee", "name": "Coffee", "description": "Restore 1 life", "effect": "restore_life", "value": 1, "icon": "☕"},
            {"id": "study_guide", "name": "Study Guide", "description": "Next question has a hint", "effect": "show_hint", "duration": 1, "icon": "📖"},
            {"id": "energy_drink", "name": "Energy Drink", "description": "Next 3 questions give 25% more XP", "effect": "temp_exp_bonus", "value": 0.25, "duration": 3, "icon": "🥤"},
            {"id": "reference_sheet", "name": "Reference Sheet", "description": "Reveals one wrong answer on the next question", "effect": "reveal_wrong_answer", "duration": 1, "icon": "📝"},
            {"id": "lucky_charm", "name": "Lucky Charm", "description": "Next failure doesn't cost a life", "effect": "prevent_damage", "uses": 1, "icon": "🍀"}
        ]
    
    def _get_question_bank(self):
        """Return the question bank for the game."""
        return [
            {
                "id": "q1",
                "category": "dosimetry",
                "difficulty": 1,
                "question": "What is the correction factor for temperature and pressure called in TG-51?",
                "options": [
                    "PTP",
                    "kTP",
                    "CTP",
                    "PTC"
                ],
                "correct_answer": 1,
                "explanation": "kTP is the temperature-pressure correction factor in TG-51 that adjusts for the difference between calibration and measurement conditions."
            },
            {
                "id": "q2",
                "category": "qa",
                "difficulty": 1,
                "question": "Which of the following is typically measured in monthly linac QA?",
                "options": [
                    "Electron contamination",
                    "Output constancy",
                    "Leakage radiation",
                    "Housing integrity"
                ],
                "correct_answer": 1,
                "explanation": "Output constancy is a critical parameter checked during monthly QA to ensure the linac is delivering the expected dose."
            },
            {
                "id": "q3",
                "category": "radiation",
                "difficulty": 2,
                "question": "What is the annual effective dose limit for radiation workers?",
                "options": [
                    "5 mSv",
                    "20 mSv",
                    "50 mSv",
                    "100 mSv"
                ],
                "correct_answer": 1,
                "explanation": "The annual effective dose limit for radiation workers is 20 mSv averaged over 5 years, with no single year exceeding 50 mSv."
            },
            {
                "id": "q4",
                "category": "calculation",
                "difficulty": 2,
                "question": "A 6 MV photon beam has a PDD of 67.3% at 10 cm depth and 100 cm SSD. What is the approximate TMR at 10 cm depth and 100 cm SAD?",
                "options": [
                    "0.673",
                    "0.750",
                    "0.806",
                    "0.900"
                ],
                "correct_answer": 2,
                "explanation": "The TMR can be calculated from PDD using the relationship TMR = PDD × ((100+d)/100)². For 10 cm depth, TMR ≈ 0.673 × (110/100)² ≈ 0.806"
            },
            {
                "id": "q5",
                "category": "planning",
                "difficulty": 3,
                "question": "Which of the following optimization objectives would be LEAST appropriate for a prostate IMRT plan?",
                "options": [
                    "Maximize target coverage with 95% of prescription dose",
                    "Minimize rectal volume receiving >70 Gy",
                    "Minimize femoral head maximum dose to <45 Gy",
                    "Maximize dose conformity to femoral heads"
                ],
                "correct_answer": 3,
                "explanation": "Maximizing dose conformity to femoral heads would be inappropriate as the femoral heads are critical structures to avoid, not targets for dose delivery."
            }
        ]
    
    # ========== GAME FUNCTIONS ==========
    
    def start_new_run(self):
        """Initialize a new run."""
        # Reset run-specific state
        st.session_state.current_floor = 0
        st.session_state.current_node = None
        st.session_state.visited_nodes = set()
        st.session_state.player["lives"] = st.session_state.player["max_lives"]
        
        st.session_state.current_run = {
            "path": [],
            "score": 0,
            "streak": 0,
            "relics": []
        }
        
        # Generate the first floor
        self.generate_new_floor()
        
        # Switch to game view
        st.session_state.game_view = "game"
    
    def generate_new_floor(self):
        """Generate a new floor with nodes in a path structure."""
        st.session_state.current_floor += 1
        
        # Create nodes for this floor
        floor_nodes = []
        
        # Determine node types based on floor number
        if st.session_state.current_floor % 5 == 0:
            # Boss floor every 5 floors
            floor_nodes.append(self.create_node("boss", st.session_state.current_floor))
        else:
            # Regular floor - create multiple options
            num_options = min(3, st.session_state.current_floor + 1)  # More options on higher floors
            for i in range(num_options):
                node_type = self.get_node_type_for_floor(st.session_state.current_floor, i)
                floor_nodes.append(self.create_node(node_type, st.session_state.current_floor))
        
        st.session_state.current_run["path"].append(floor_nodes)
        return floor_nodes

    def complete_floor(self):
        """Process completing a floor - now just complete the visited node."""
        # Check if this was the last floor
        if st.session_state.current_floor >= st.session_state.max_floor:
            self.end_run(True)
            return
        
        # Generate the next floor
        self.generate_new_floor()
        
        # Apply any between-floor effects
        for perk in st.session_state.player["active_perks"]:
            if perk["effect"] == "floor_life_recovery":
                st.session_state.player["lives"] = min(
                    st.session_state.player["max_lives"],
                    st.session_state.player["lives"] + perk["value"]
                )
        
        # Back to game view
        st.session_state.game_view = "game"
    
    def get_node_type_for_floor(self, floor, position):
        """Determine what type of node to place based on floor and position."""
        # First floor is always easier
        if floor == 1:
            if position == 1:
                return "reference"  # Middle node on first floor is always a reference
            return "question"
        
        # Higher floors have more variety and difficulty
        possible_types = ["question", "question", "question"]
        
        # Add variety based on floor level
        if floor > 2:
            possible_types.extend(["reference", "rest"])
        if floor > 4:
            possible_types.extend(["treasure", "elite"])
        
        return random.choice(possible_types)
    
    def create_node(self, node_type, floor):
        """Create a single node with appropriate properties."""
        node_type_data = next((n for n in self.node_types if n["id"] == node_type), None)
        
        # Determine difficulty based on floor and node type
        difficulty = 1
        if node_type_data["difficulty"]:
            # Get possible difficulties for this node type
            possible_difficulties = node_type_data["difficulty"]
            
            # Higher floors increase chance of higher difficulty
            difficulty_index = 0
            
            if floor > 7:
                difficulty_index = len(possible_difficulties) - 1  # Highest difficulty
            elif floor > 3:
                difficulty_index = min(1, len(possible_difficulties) - 1)  # Medium difficulty
            
            difficulty = possible_difficulties[difficulty_index]
        
        # Create the node
        return {
            "id": f"node_{floor}_{random.randint(1000, 9999)}",
            "type": node_type,
            "name": node_type_data["name"],
            "icon": node_type_data["icon"],
            "difficulty": difficulty,
            "category": self.get_random_category(),
            "visited": False,
            "content": self.generate_node_content(node_type, difficulty)
        }
    
    def get_random_category(self):
        """Get a random category ID."""
        return self.categories[random.randint(0, len(self.categories) - 1)]["id"]
    
    def generate_node_content(self, node_type, difficulty):
        """Generate content for a node based on type and difficulty."""
        if node_type == "question":
            return self.get_question_for_difficulty(difficulty)
        elif node_type == "reference":
            return {
                "title": "Reference Material",
                "text": "You study important concepts in your textbook.",
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
            return {
                "title": "Complex Case",
                "text": "You face a particularly challenging clinical scenario.",
                "questions": [
                    self.get_question_for_difficulty(difficulty),
                    self.get_question_for_difficulty(difficulty)
                ],
                "reward": {"type": "find_relic", "rarity": "uncommon"}
            }
        elif node_type == "boss":
            return {
                "title": "Rotation Evaluation",
                "text": "Your knowledge is being tested as part of your rotation evaluation.",
                "questions": [
                    self.get_question_for_difficulty(max(1, difficulty - 1)),
                    self.get_question_for_difficulty(difficulty),
                    self.get_question_for_difficulty(difficulty)
                ],
                "reward": {"type": "complete_rotation", "value": st.session_state.current_floor}
            }
        return {"title": "Unknown", "text": "Something mysterious happens."}
    
    def get_question_for_difficulty(self, difficulty):
        """Get a question of appropriate difficulty."""
        # Filter questions by difficulty
        questions = [q for q in self.question_bank if q["difficulty"] == difficulty]
        
        # If no questions of this difficulty, adjust
        if not questions:
            return self.question_bank[random.randint(0, len(self.question_bank) - 1)]
        
        # Return a random question
        return questions[random.randint(0, len(questions) - 1)]
    
    def visit_node(self, node_id):
        """Process a player visiting a node."""
        # Find the node
        node = self.find_node_by_id(node_id)
        
        if not node or node["visited"]:
            return
        
        # Mark as visited
        node["visited"] = True
        st.session_state.visited_nodes.add(node_id)
        st.session_state.current_node = node
        
        # Process node effects
        self.process_node_effects(node)
    
    def find_node_by_id(self, node_id):
        """Find a node by its ID."""
        for floor in st.session_state.current_run["path"]:
            for node in floor:
                if node["id"] == node_id:
                    return node
        return None
    
    def process_node_effects(self, node):
        """Process the effects of visiting a node."""
        if not node:
            return
        
        if node["type"] == "question":
            # Show question UI
            st.session_state.game_view = "question"
            st.session_state.current_question = node["content"]
        elif node["type"] == "reference":
            # Apply reference effects
            self.apply_effect(node["content"]["effect"])
            st.session_state.game_view = "result"
            st.session_state.question_result = "reference"
        elif node["type"] == "rest":
            # Apply rest effects
            self.apply_effect(node["content"]["effect"])
            st.session_state.game_view = "result"
            st.session_state.question_result = "rest"
        elif node["type"] == "treasure":
            # Give an item
            item = self.get_random_item(node["content"]["effect"]["rarity"])
            st.session_state.player["inventory"].append(item)
            st.session_state.game_view = "result"
            st.session_state.question_result = "treasure"
        elif node["type"] == "elite":
            # Show elite challenge UI
            st.session_state.game_view = "elite"
        elif node["type"] == "boss":
            # Show boss challenge UI
            st.session_state.game_view = "boss"
    
    def apply_effect(self, effect):
        """Apply an effect to the player."""
        if not effect:
            return
        
        if effect["type"] == "restore_life":
            st.session_state.player["lives"] = min(
                st.session_state.player["max_lives"], 
                st.session_state.player["lives"] + effect["value"]
            )
        elif effect["type"] == "gain_insight":
            st.session_state.player["insight"] += effect["value"]
        elif effect["type"] == "gain_experience":
            self.gain_experience(effect["value"])
    
    def gain_experience(self, amount):
        """Award experience to the player with bonuses applied."""
        # Apply experience bonuses from perks
        bonus_multiplier = 1.0
        for perk in st.session_state.player["active_perks"]:
            if perk["effect"] == "experience_bonus":
                bonus_multiplier += perk["value"]
        
        adjusted_amount = int(amount * bonus_multiplier)
        st.session_state.player["experience"] += adjusted_amount
        
        # Check for level up
        while st.session_state.player["experience"] >= st.session_state.player["experience_to_next_level"]:
            self.level_up()
    
    def level_up(self):
        """Process player level up."""
        st.session_state.player["experience"] -= st.session_state.player["experience_to_next_level"]
        st.session_state.player["level"] += 1
        st.session_state.player["experience_to_next_level"] = int(st.session_state.player["experience_to_next_level"] * 1.2)
        
        # Offer perk selection
        # For simplicity, we'll just add a random perk for now
        available_perks = [p for p in self.perks if p["id"] not in [ap["id"] for ap in st.session_state.player["active_perks"]]]
        if available_perks:
            new_perk = random.choice(available_perks)
            st.session_state.player["active_perks"].append(new_perk)
    
    def get_random_item(self, rarity="common"):
        """Get a random consumable item."""
        return random.choice(self.consumables)
    
    def answer_question(self, answer_index):
        """Process player answering a question."""
        if "current_question" not in st.session_state or not st.session_state.current_question:
            return
        
        question = st.session_state.current_question
        correct = (answer_index == question["correct_answer"])
        
        if correct:
            # Correct answer
            st.session_state.current_run["streak"] += 1
            streak_bonus = 1 + st.session_state.current_run["streak"] * 0.1
            st.session_state.current_run["score"] += int(10 * streak_bonus)
            
            # Award experience based on difficulty
            self.gain_experience(20 * question["difficulty"])
            
            st.session_state.question_result = "correct"
        else:
            # Incorrect answer
            st.session_state.current_run["streak"] = 0
            st.session_state.player["lives"] -= 1
            
            st.session_state.question_result = "incorrect"
            
            # Check if run is over
            if st.session_state.player["lives"] <= 0:
                self.end_run(False)
                return
        
        # Show result
        st.session_state.game_view = "result"
    
    def continue_after_node(self):
        """Continue to next stage after completing a node."""
        # Check if all nodes on this floor are visited
        current_floor_index = st.session_state.current_floor - 1
        
        all_visited = True
        for node in st.session_state.current_run["path"][current_floor_index]:
            if not node["visited"]:
                all_visited = False
                break
        
        if all_visited:
            # Complete the floor
            self.complete_floor()
        else:
            # Back to game board
            st.session_state.game_view = "game"
    
    def complete_floor(self):
        """Process completing a floor."""
        # Check if this was the last floor
        if st.session_state.current_floor >= st.session_state.max_floor:
            self.end_run(True)
            return
        
        # Generate the next floor
        self.generate_new_floor()
        
        # Apply any between-floor effects
        for perk in st.session_state.player["active_perks"]:
            if perk["effect"] == "floor_life_recovery":
                st.session_state.player["lives"] = min(
                    st.session_state.player["max_lives"],
                    st.session_state.player["lives"] + perk["value"]
                )
        
        # Back to game view
        st.session_state.game_view = "game"
    
    def end_run(self, success):
        """End the current run."""
        # Calculate final score
        final_score = st.session_state.current_run["score"] + \
                      (500 if success else 0) + \
                      (st.session_state.current_floor * 50) + \
                      (st.session_state.player["lives"] * 20)
        
        # Record the run
        st.session_state.completed_runs += 1
        
        # Check for unlocks
        self.check_for_unlocks()
        
        # Show run end screen
        st.session_state.game_view = "run_end"
        st.session_state.run_success = success
        st.session_state.final_score = final_score
    
    def check_for_unlocks(self):
        """Check for new unlocks based on game progress."""
        # Check for hub area unlocks
        for area in self.hub_areas:
            if area["id"] in st.session_state.hub_unlocked:
                continue
            
            if area["unlock_condition"].startswith("completed_runs:"):
                required = int(area["unlock_condition"].split(":")[1])
                if st.session_state.completed_runs >= required:
                    st.session_state.hub_unlocked.append(area["id"])
            elif area["unlock_condition"].startswith("max_floor:"):
                required = int(area["unlock_condition"].split(":")[1])
                if st.session_state.current_floor >= required:
                    st.session_state.hub_unlocked.append(area["id"])
    
    def return_to_hub(self):
        """Return to the hub interface."""
        st.session_state.game_view = "hub"
    
    # ========== UI RENDERING METHODS ==========
    
    def _render_hub_interface(self):
        """Render the hub (department) interface."""
        st.subheader("Memorial Hospital Physics Department")
        st.markdown("Your medical physics journey begins here. Choose an area to explore.")
        
        # Arrange hub areas in a grid
        hub_areas = self.hub_areas
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
                                self.start_new_run()
                            else:
                                # Other areas would have their own functions
                                st.info(f"Entering {area['name']} - Feature coming soon!")
    
    def _render_game_interface(self):
        """Render the main game (run) interface."""
        # Player stats
        self._render_player_stats()
        
        # Game board - current floor
        col1, col2 = st.columns([5, 1])
        with col1:
            st.subheader(f"Floor {st.session_state.current_floor} / {st.session_state.max_floor}")
        with col2:
            if st.button("End Run", type="secondary", key="end_run_early"):
                # Confirm dialog
                if "confirm_end_run" not in st.session_state:
                    st.session_state.confirm_end_run = True
                    st.warning("Are you sure you want to end your run? Progress will be saved but the run will end.")
                    st.rerun()
                else:
                    del st.session_state.confirm_end_run
                    self.end_run(False)  # End the run without success
        
        # Game board - current floor
        st.subheader(f"Floor {st.session_state.current_floor} / {st.session_state.max_floor}")
        
        # Render the current floor nodes
        current_floor_nodes = st.session_state.current_run["path"][st.session_state.current_floor - 1]
        
        # Create columns for nodes
        cols = st.columns(len(current_floor_nodes))
        
        for i, node in enumerate(current_floor_nodes):
            with cols[i]:
                self._render_node_card(node)
        
        # Inventory
        st.markdown("---")
        self._render_inventory()
    
    def _render_node_card(self, node):
        """Render a single node card."""
        # Get node type info
        node_type = node["type"]
        
        # Style based on node type
        card_class = f"node-card {node_type}-card"
        
        # Difficulty pips
        difficulty_display = "★" * node["difficulty"]
        
        # Render card
        with st.container():
            st.markdown(f"""
            <div class="{card_class}">
                <div style="font-size: 2em;">{node['icon']}</div>
                <div>{node['name']}</div>
                <div>{difficulty_display}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Node interaction button
            if not node["visited"]:
                if st.button("Visit", key=f"visit_{node['id']}"):
                    self.visit_node(node["id"])
    
    def _render_player_stats(self):
        """Render the player stats bar."""
        # Stats container
        st.markdown("""
        <div class="stat-container">
            <div>👨‍⚕️ <span id="player-year">Year 1</span></div>
            <div>❤️ <span id="player-lives">3/3</span></div>
            <div>✨ <span id="player-insight">0</span></div>
            <div>📈 <span id="player-level">Lv. 1</span></div>
        </div>
        """.replace("Year 1", f"Year {st.session_state.player['year']}")
           .replace("3/3", f"{st.session_state.player['lives']}/{st.session_state.player['max_lives']}")
           .replace("0", f"{st.session_state.player['insight']}")
           .replace("Lv. 1", f"Lv. {st.session_state.player['level']}"), 
        unsafe_allow_html=True)
        
        # Experience bar
        exp_percentage = min(100, int(st.session_state.player["experience"] / st.session_state.player["experience_to_next_level"] * 100))
        st.markdown(f"""
        <div class="progress-bar-container">
            <div class="progress-bar-value" style="width: {exp_percentage}%;"></div>
        </div>
        <div style="text-align: center; font-size: 0.8em; color: #7f8c8d;">
            Experience: {st.session_state.player["experience"]} / {st.session_state.player["experience_to_next_level"]}
        </div>
        """, unsafe_allow_html=True)
    
    def _render_inventory(self):
        """Render the player's inventory."""
        st.subheader("Inventory")
        
        if not st.session_state.player["inventory"]:
            st.info("Your inventory is empty. Find items during your rotations!")
            return
        
        # Create columns for items
        cols = st.columns(5)  # 5 items per row max
        
        for i, item in enumerate(st.session_state.player["inventory"]):
            with cols[i % 5]:
                st.markdown(f"### {item['icon']} {item['name']}")
                st.write(item["description"])
                
                if st.button("Use", key=f"use_item_{i}"):
                    # Apply item effect
                    self.apply_effect(item["effect"])
                    # Remove from inventory
                    st.session_state.player["inventory"].pop(i)
                    st.rerun()
    
    def _render_question_interface(self):
        """Render the question interface."""
        # Get the current question
        question = st.session_state.current_question
        
        if not question:
            st.error("No question found!")
            return
        
        # Get category info
        category_data = next((c for c in self.categories if c["id"] == question["category"]), None)
        category_name = category_data["name"] if category_data else "Unknown"
        
        # Question card
        st.markdown(f"### {category_name} Question")
        st.markdown(f"#### {question['question']}")
        
        # Options
        for i, option in enumerate(question["options"]):
            if st.button(f"{chr(65+i)}. {option}", key=f"answer_{i}"):
                self.answer_question(i)
    
    def _render_question_result(self):
        """Render the result of answering a question."""
        # Get the current question
        question = st.session_state.current_question
        result = st.session_state.question_result
        
        if result == "correct":
            st.success("CORRECT!")
            st.markdown(f"### Explanation:")
            st.markdown(question["explanation"])
            
            # Show rewards
            st.markdown("### Rewards:")
            st.markdown(f"* +{20 * question['difficulty']} XP")
            st.markdown(f"* +{10} points")
            
            if st.session_state.current_run["streak"] > 1:
                st.markdown(f"* Streak bonus: {st.session_state.current_run['streak']}x")
        
        elif result == "incorrect":
            st.error("INCORRECT!")
            st.markdown(f"### Explanation:")
            st.markdown(question["explanation"])
            
            # Show penalty
            st.markdown("### Penalty:")
            st.markdown("* -1 life")
            st.markdown("* Streak reset")
        
        elif result == "reference":
            st.info("You studied the material carefully.")
            st.markdown("### Gained:")
            insight_gained = 10 * st.session_state.current_node["difficulty"]
            st.markdown(f"* +{insight_gained} insight")
        
        elif result == "rest":
            st.success("You took a well-deserved break.")
            st.markdown("### Effect:")
            st.markdown("* +1 life restored")
        
        elif result == "treasure":
            st.success("You found a useful item!")
            # Get the most recently added item
            if st.session_state.player["inventory"]:
                latest_item = st.session_state.player["inventory"][-1]
                st.markdown(f"### {latest_item['icon']} {latest_item['name']}")
                st.markdown(latest_item["description"])
        
        # Continue button
        if st.button("Continue", key="result_continue"):
            self.continue_after_node()
    
    def _render_run_end_interface(self):
        """Render the end-of-run summary."""
        success = st.session_state.run_success
        final_score = st.session_state.final_score
        
        if success:
            st.success("# Rotation Complete!")
            st.markdown("Your clinical rotation has been completed successfully. Your knowledge and skills have grown!")
        else:
            st.error("# Rotation Incomplete")
            st.markdown("You weren't able to complete this rotation. Take what you've learned and try again!")
        
        # Stats
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Floors Completed", st.session_state.current_floor)
            st.metric("Questions Correct", st.session_state.current_run["streak"])
        
        with col2:
            st.metric("Final Score", final_score)
            st.metric("Total Rotations", st.session_state.completed_runs)
        
        # Return to hub button
        if st.button("Return to Department", key="return_to_hub"):
            self.return_to_hub()