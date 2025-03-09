import json
import os
import random
from datetime import datetime

class DataManager:
    """Handles loading and saving game data from JSON files."""
    
    def __init__(self, data_dir="data"):
        """Initialize the data manager with the directory containing data files."""
        self.data_dir = data_dir
        self.data_files = {
            "classes": "game_classes.json",
            "relics": "game_relics.json",
            "perks": "game_perks.json",
            "consumables": "game_consumables.json",
            "encounters": "game_encounters.json",
            "achievements": "game_achievements.json",
            "challenge_modes": "game_challenge_modes.json"
        }
        self.data = {}
        self._load_all_data()
    
    def _load_all_data(self):
        """Load all data files."""
        for data_type, filename in self.data_files.items():
            self._load_data(data_type, filename)
    
    def _load_data(self, data_type, filename):
        """Load a specific data file."""
        filepath = os.path.join(self.data_dir, filename)
        
        # Create default data if file doesn't exist
        if not os.path.exists(filepath):
            self._create_default_data(data_type, filepath)
        
        try:
            with open(filepath, 'r') as file:
                self.data[data_type] = json.load(file)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading {filename}: {e}")
            # Use empty data structure as fallback
            self.data[data_type] = self._get_empty_data_structure(data_type)
    
    def _create_default_data(self, data_type, filepath):
        """Create a default data file if it doesn't exist."""
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Create empty data structure
        default_data = self._get_empty_data_structure(data_type)
        
        # Write to file
        with open(filepath, 'w') as file:
            json.dump(default_data, file, indent=2)
    
    def _get_empty_data_structure(self, data_type):
        """Get an empty data structure for the specified data type."""
        structures = {
            "classes": {"classes": []},
            "relics": {"relics": []},
            "perks": {"perks": []},
            "consumables": {"consumables": []},
            "encounters": {"encounters": []},
            "achievements": {"achievements": []},
            "challenge_modes": {"challenge_modes": []}
        }
        return structures.get(data_type, {})
    
    def save_data(self, data_type):
        """Save data of the specified type to its file."""
        if data_type not in self.data_files:
            print(f"Unknown data type: {data_type}")
            return False
        
        filepath = os.path.join(self.data_dir, self.data_files[data_type])
        
        try:
            with open(filepath, 'w') as file:
                json.dump(self.data[data_type], file, indent=2)
            return True
        except IOError as e:
            print(f"Error saving {data_type} data: {e}")
            return False
    
    def get_data(self, data_type):
        """Get data of the specified type."""
        return self.data.get(data_type, {})
    
    def get_item_by_id(self, data_type, item_id):
        """Get a specific item by ID from the specified data type."""
        if data_type not in self.data:
            return None
        
        items_list = self.data[data_type].get(data_type, [])
        for item in items_list:
            if item.get("id") == item_id:
                return item
        
        return None


class Character:
    """Represents a player character in the game."""
    
    def __init__(self, class_data):
        """Initialize a character from class data."""
        self.id = class_data.get("id")
        self.name = class_data.get("name")
        self.description = class_data.get("description")
        self.icon = class_data.get("icon")
        self.starting_stats = class_data.get("starting_stats", {})
        self.special_ability = class_data.get("special_ability", {})
        self.weakness = class_data.get("weakness", {})
        self.starting_relic_id = class_data.get("starting_relic")
        
        # Dynamic stats
        self.lives = self.starting_stats.get("max_lives", 3)
        self.max_lives = self.starting_stats.get("max_lives", 3)
        self.insight = self.starting_stats.get("insight", 0)
        self.level = 1
        self.experience = 0
        self.experience_to_next_level = self.starting_stats.get("experience_to_next_level", 100)
        
        # Collections
        self.active_perks = []
        self.inventory = []
        self.relics = []
    
    def gain_experience(self, amount, bonus_multiplier=1.0):
        """Award experience to the character with bonuses applied."""
        adjusted_amount = int(amount * bonus_multiplier)
        self.experience += adjusted_amount
        
        # Check for level up
        level_ups = 0
        while self.experience >= self.experience_to_next_level:
            self.experience -= self.experience_to_next_level
            self.level += 1
            level_ups += 1
            # Increase experience needed for next level
            self.experience_to_next_level = int(self.experience_to_next_level * 1.2)
        
        return level_ups
    
    def add_relic(self, relic):
        """Add a relic to the character."""
        self.relics.append(relic)
        
        # Apply immediate effects
        if "effect" in relic:
            effect = relic["effect"]
            if effect["type"] == "max_lives_bonus":
                self.max_lives += effect["value"]
                self.lives += effect["value"]
        
        # Apply side effects
        if "side_effect" in relic:
            side_effect = relic["side_effect"]
            if side_effect["type"] == "max_lives_penalty":
                self.max_lives = max(1, self.max_lives - side_effect["value"])
                self.lives = min(self.lives, self.max_lives)
    
    def add_perk(self, perk):
        """Add a perk to the character."""
        self.active_perks.append(perk)
    
    def add_to_inventory(self, item):
        """Add an item to the character's inventory."""
        self.inventory.append(item)
    
    def use_item(self, item_index):
        """Use an item from the inventory."""
        if 0 <= item_index < len(self.inventory):
            item = self.inventory.pop(item_index)
            return item
        return None
    
    def take_damage(self, amount):
        """Take damage (lose lives)."""
        # Apply damage reduction from perks/relics
        for perk in self.active_perks:
            if "effect" in perk and perk["effect"]["type"] == "damage_reduction":
                # Check if there's a condition
                if "condition" not in perk["effect"] or perk["effect"]["condition"] == "always":
                    amount = max(0, amount - perk["effect"]["value"])
        
        self.lives = max(0, self.lives - amount)
        return self.lives <= 0  # Return True if character is defeated
    
    def restore_life(self, amount):
        """Restore lives."""
        self.lives = min(self.max_lives, self.lives + amount)
    
    def to_dict(self):
        """Convert character to dictionary for saving."""
        return {
            "id": self.id,
            "name": self.name,
            "icon": self.icon,
            "lives": self.lives,
            "max_lives": self.max_lives,
            "insight": self.insight,
            "level": self.level,
            "experience": self.experience,
            "experience_to_next_level": self.experience_to_next_level,
            "active_perks": self.active_perks,
            "inventory": self.inventory,
            "relics": self.relics
        }
    
    @classmethod
    def from_dict(cls, data, class_data):
        """Create a character from a saved dictionary and class data."""
        character = cls(class_data)
        character.lives = data.get("lives", character.lives)
        character.max_lives = data.get("max_lives", character.max_lives)
        character.insight = data.get("insight", character.insight)
        character.level = data.get("level", character.level)
        character.experience = data.get("experience", character.experience)
        character.experience_to_next_level = data.get("experience_to_next_level", character.experience_to_next_level)
        character.active_perks = data.get("active_perks", character.active_perks)
        character.inventory = data.get("inventory", character.inventory)
        character.relics = data.get("relics", character.relics)
        return character


class GameState:
    """Manages the state of a game run."""
    
    def __init__(self, character, max_floor=10, nodes_per_floor=3):
        """Initialize a new game state with the specified character."""
        self.character = character
        self.current_floor = 0
        self.max_floor = max_floor
        self.nodes_per_floor = nodes_per_floor
        self.path = []  # List of floors, each floor is a list of nodes
        self.visited_nodes = set()
        self.current_node = None
        self.score = 0
        self.streak = 0
        self.start_time = datetime.now()
        self.end_time = None
        self.is_completed = False
        self.is_successful = False
        self.special_effects = {}  # For temporary effects
        self.path_history = PathHistory()  # Add this line 
        self.path_connections = {}  # Add this line for branching paths
    
    def generate_new_floor(self, data_manager):
        """Generate a new floor with nodes."""
        self.current_floor += 1
        
        # Create nodes for this floor
        floor_nodes = []
        
        # Determine node types based on floor number
        if self.current_floor % 5 == 0:
            # Boss floor every 5 floors
            floor_nodes.append(self._create_boss_node(data_manager))
        else:
            # Regular floor
            for i in range(self.nodes_per_floor):
                node_type = self._get_node_type_for_floor(self.current_floor, i)
                floor_nodes.append(self._create_node(node_type, data_manager))
        
        self.path.append(floor_nodes)
        return floor_nodes
    
    def _get_node_type_for_floor(self, floor, position):
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
        if floor > 6:
            possible_types.append("encounter")
        
        return random.choice(possible_types)
    
    def _create_node(self, node_type, data_manager):
        """Create a single node with appropriate properties."""
        # Get node type data
        node_types = [
            {"id": "question", "name": "Question", "description": "Test your knowledge", "difficulty": [1, 2, 3], "icon": "📝"},
            {"id": "reference", "name": "Reference", "description": "Learn without being tested", "difficulty": [0], "icon": "📚"},
            {"id": "rest", "name": "Break Room", "description": "Recover 1 life", "difficulty": [0], "icon": "☕"},
            {"id": "treasure", "name": "Conference", "description": "Find a helpful item", "difficulty": [0], "icon": "🎁"},
            {"id": "elite", "name": "Complex Case", "description": "Difficult but rewarding", "difficulty": [2, 3], "icon": "⚠️"},
            {"id": "boss", "name": "Rotation Evaluation", "description": "Major test of knowledge", "difficulty": [3], "icon": "⭐"},
            {"id": "encounter", "name": "Special Event", "description": "A unique opportunity", "difficulty": [1, 2], "icon": "🔍"}
        ]
        
        node_type_data = next((n for n in node_types if n["id"] == node_type), None)
        if not node_type_data:
            # Default to question if node type not found
            node_type_data = next((n for n in node_types if n["id"] == "question"), None)
        
        # Determine difficulty based on floor and node type
        difficulty = 1
        if node_type_data["difficulty"]:
            # Get possible difficulties for this node type
            possible_difficulties = node_type_data["difficulty"]
            
            # Higher floors increase chance of higher difficulty
            difficulty_index = 0
            
            if self.current_floor > 7:
                difficulty_index = len(possible_difficulties) - 1  # Highest difficulty
            elif self.current_floor > 3:
                difficulty_index = min(1, len(possible_difficulties) - 1)  # Medium difficulty
            
            difficulty = possible_difficulties[difficulty_index]
        
        # Get a random category
        categories = data_manager.get_data("classes").get("categories", [
            {"id": "dosimetry", "name": "Dosimetry", "color": "#3498db"},
            {"id": "qa", "name": "Quality Assurance", "color": "#2ecc71"},
            {"id": "radiation", "name": "Radiation Safety", "color": "#e74c3c"},
            {"id": "planning", "name": "Treatment Planning", "color": "#9b59b6"},
            {"id": "calculation", "name": "Calculations", "color": "#f1c40f"},
            {"id": "imaging", "name": "Imaging Physics", "color": "#1abc9c"},
            {"id": "regulations", "name": "Regulations", "color": "#e67e22"}
        ])
        
        category = random.choice(categories)["id"] if categories else "general"
        
        # Create the node
        return {
            "id": f"node_{self.current_floor}_{random.randint(1000, 9999)}",
            "type": node_type,
            "name": node_type_data["name"],
            "icon": node_type_data["icon"],
            "difficulty": difficulty,
            "category": category,
            "visited": False,
            "content": self._generate_node_content(node_type, difficulty, category, data_manager)
        }
    
    def _create_boss_node(self, data_manager):
        """Create a boss node for milestone floors."""
        return {
            "id": f"boss_{self.current_floor}_{random.randint(1000, 9999)}",
            "type": "boss",
            "name": "Rotation Evaluation",
            "icon": "⭐",
            "difficulty": 3,
            "category": "multi",
            "visited": False,
            "content": {
                "title": "Rotation Evaluation",
                "text": "Your knowledge is being tested as part of your rotation evaluation.",
                "questions": [
                    self._get_question_for_difficulty(1, data_manager),
                    self._get_question_for_difficulty(2, data_manager),
                    self._get_question_for_difficulty(3, data_manager)
                ],
                "reward": {"type": "complete_rotation", "value": self.current_floor}
            }
        }
    
    def _generate_node_content(self, node_type, difficulty, category, data_manager):
        """Generate content for a node based on type and difficulty."""
        if node_type == "question":
            return self._get_question_for_difficulty(difficulty, data_manager, category)
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
                    self._get_question_for_difficulty(difficulty, data_manager),
                    self._get_question_for_difficulty(difficulty, data_manager)
                ],
                "reward": {"type": "find_relic", "rarity": "uncommon"}
            }
        elif node_type == "encounter":
            # Get a random encounter
            encounters = data_manager.get_data("encounters").get("encounters", [])
            if encounters:
                return random.choice(encounters)
            else:
                return {
                    "title": "Unexpected Meeting",
                    "text": "You run into a colleague who shares some insights.",
                    "effect": {"type": "gain_insight", "value": 15}
                }
        
        return {"title": "Unknown", "text": "Something mysterious happens."}
    
    def _get_question_for_difficulty(self, difficulty, data_manager, category=None):
        """Get a question of appropriate difficulty and category."""
        # Use a sample question bank if none exists in data manager
        question_bank = [
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
        
        # Filter questions by difficulty and category if specified
        filtered_questions = [q for q in question_bank if q["difficulty"] == difficulty]
        if category:
            filtered_questions = [q for q in filtered_questions if q["category"] == category]
        
        # If no questions match, use any question of appropriate difficulty
        if not filtered_questions:
            filtered_questions = [q for q in question_bank if q["difficulty"] == difficulty]
        
        # If still no questions, use any question
        if not filtered_questions:
            filtered_questions = question_bank
        
        # Return a random question
        return random.choice(filtered_questions)
    
    def visit_node(self, node_id):
        """Process a player visiting a node."""
        # Find the node
        node = self.find_node_by_id(node_id)
        
        if not node or node["visited"]:
            return None
        
        # Mark as visited
        node["visited"] = True
        self.visited_nodes.add(node_id)
        self.current_node = node
        
        # Record in path history
        self.path_history.record_visit(node)
        
        return node
    
    def find_node_by_id(self, node_id):
        """Find a node by its ID."""
        for floor in self.path:
            for node in floor:
                if node["id"] == node_id:
                    return node
        return None
    
    def process_node_effects(self, node, data_manager):
        """Process the effects of visiting a node."""
        if not node:
            return {"success": False, "message": "Node not found"}
        
        result = {"success": True, "node_type": node["type"]}
        
        if node["type"] == "question":
            # Question nodes are handled separately in the answer_question method
            result["question"] = node["content"]
        
        elif node["type"] == "reference":
            # Apply reference effects
            if "effect" in node["content"]:
                self._apply_effect(node["content"]["effect"])
                result["effect"] = node["content"]["effect"]
            result["title"] = node["content"]["title"]
            result["text"] = node["content"]["text"]
        
        elif node["type"] == "rest":
            # Apply rest effects
            if "effect" in node["content"]:
                self._apply_effect(node["content"]["effect"])
                result["effect"] = node["content"]["effect"]
            result["title"] = node["content"]["title"]
            result["text"] = node["content"]["text"]
        
        elif node["type"] == "treasure":
            # Give an item
            rarity = node["content"]["effect"]["rarity"] if "effect" in node["content"] and "rarity" in node["content"]["effect"] else "common"
            item = self._get_random_item(rarity, data_manager)
            if item:
                self.character.add_to_inventory(item)
                result["item"] = item
            result["title"] = node["content"]["title"]
            result["text"] = node["content"]["text"]
        
        elif node["type"] == "elite":
            # Elite nodes have multiple questions
            result["questions"] = node["content"]["questions"]
            result["reward"] = node["content"]["reward"]
            result["title"] = node["content"]["title"]
            result["text"] = node["content"]["text"]
        
        elif node["type"] == "boss":
            # Boss nodes have special challenges
            result["questions"] = node["content"]["questions"]
            result["reward"] = node["content"]["reward"]
            result["title"] = node["content"]["title"]
            result["text"] = node["content"]["text"]
        
        elif node["type"] == "encounter":
            # Handle special encounters
            result["encounter"] = node["content"]
        
        return result
    
    def _apply_effect(self, effect):
        """Apply an effect to the character."""
        if not effect:
            return
        
        if effect["type"] == "restore_life":
            self.character.restore_life(effect["value"])
        elif effect["type"] == "gain_insight":
            self.character.insight += effect["value"]
        elif effect["type"] == "gain_experience":
            self.character.gain_experience(effect["value"])
    
    def _get_random_item(self, rarity, data_manager):
        """Get a random consumable item of the specified rarity."""
        consumables = data_manager.get_data("consumables").get("consumables", [])
        if not consumables:
            return None
        
        # Filter by rarity
        filtered_items = [item for item in consumables if item.get("rarity") == rarity]
        
        # If no items of specified rarity, use any item
        if not filtered_items:
            filtered_items = consumables
        
        return random.choice(filtered_items) if filtered_items else None
    
    def answer_question(self, question, answer_index, data_manager=None):
        """Process player answering a question."""
        if not question:
            return {"success": False, "message": "No question provided"}
        
        correct = (answer_index == question["correct_answer"])
        result = {
            "success": True,
            "correct": correct,
            "explanation": question.get("explanation", "")
        }
        
        if correct:
            # Correct answer
            self.streak += 1
            streak_bonus = 1 + min(self.streak * 0.1, 0.5)  # Cap at 50% bonus
            score_gained = int(10 * streak_bonus)
            self.score += score_gained
            result["streak"] = self.streak
            result["score_gained"] = score_gained
            
            # Award experience based on difficulty
            exp_gained = 20 * question.get("difficulty", 1)
            level_ups = self.character.gain_experience(exp_gained)
            result["experience_gained"] = exp_gained
            
            if level_ups > 0:
                result["level_up"] = True
                result["new_level"] = self.character.level
                
                # Offer perk selection if data_manager is provided
                if data_manager:
                    available_perks = self._get_available_perks(data_manager)
                    if available_perks:
                        result["perk_choices"] = random.sample(available_perks, min(3, len(available_perks)))
        else:
            # Incorrect answer
            self.streak = 0
            self.character.take_damage(1)
            result["lives_remaining"] = self.character.lives
            
            # Check if run is over
            if self.character.lives <= 0:
                self.end_run(False)
                result["run_over"] = True
        
        return result
    
    def generate_branching_path(self, data_manager):
        """Generate a branching path instead of individual floors."""
        path_generator = BranchingPathGenerator(max_floors=self.max_floor)
        floors, connections = path_generator.generate(data_manager)
        
        # Save path data
        self.path = floors
        self.path_connections = connections
        
        # Start at floor 1
        self.current_floor = 1
        
        return self.path
    
    def get_available_nodes(self):
        """Get nodes that are available to visit based on path connections."""
        # If we're on the first floor, all nodes are available
        if self.current_floor == 1:
            return self.path[0]
        
        # Otherwise, only nodes connected to visited nodes on previous floor
        available_nodes = []
        
        if not hasattr(self, 'path_connections'):
            # Fallback if no connection data
            return self.path[self.current_floor - 1]
        
        # Get all visited nodes from previous floor
        prev_floor_nodes = self.path[self.current_floor - 2]
        visited_prev_nodes = [node for node in prev_floor_nodes if node["visited"]]
        
        # Get all nodes connected to any visited node
        for source_node in visited_prev_nodes:
            for target_id in self.path_connections.get(source_node["id"], []):
                # Find the target node
                for node in self.path[self.current_floor - 1]:
                    if node["id"] == target_id:
                        available_nodes.append(node)
                        break
        
        return available_nodes

    def _get_available_perks(self, data_manager):
        """Get perks that are available to select."""
        all_perks = data_manager.get_data("perks").get("perks", [])
        
        # Filter out perks the character already has
        character_perk_ids = [p["id"] for p in self.character.active_perks]
        available_perks = [p for p in all_perks if p["id"] not in character_perk_ids]
        
        return available_perks
    
    def select_perk(self, perk_id, data_manager):
        """Select a perk after leveling up."""
        perk = data_manager.get_item_by_id("perks", perk_id)
        if perk:
            self.character.add_perk(perk)
            return {"success": True, "perk": perk}
        return {"success": False, "message": "Perk not found"}
    
    def check_floor_completion(self):
        """Check if a node on the current floor has been visited."""
        if not self.path or self.current_floor - 1 >= len(self.path):
            return False
        
        # Get the nodes for the current floor
        current_floor_nodes = self.path[self.current_floor - 1]
        
        # Check if ANY node has been visited (not ALL nodes)
        return any(node["visited"] for node in current_floor_nodes)
    
    def complete_floor(self):
        """Process completing a floor."""
        # Apply any between-floor effects
        for perk in self.character.active_perks:
            if "effect" in perk and perk["effect"]["type"] == "floor_life_recovery":
                self.character.restore_life(perk["effect"]["value"])
        
        # Record in path history
        self.path_history.record_floor_completion(self.current_floor)
        
        return {"success": True, "floor_completed": self.current_floor}
    
    def end_run(self, success):
        """End the current run."""
        self.is_completed = True
        self.is_successful = success
        self.end_time = datetime.now()
        
        # Calculate final score
        final_score = self.score + \
                     (500 if success else 0) + \
                     (self.current_floor * 50) + \
                     (self.character.lives * 20)
        
        duration = (self.end_time - self.start_time).total_seconds()
        
        return {
            "success": True,
            "run_completed": True,
            "run_successful": success,
            "final_score": final_score,
            "floors_completed": self.current_floor,
            "duration_seconds": duration,
            "character_level": self.character.level
        }
    
    def to_dict(self):
        """Convert game state to dictionary for saving."""
        return {
            "character": self.character.to_dict(),
            "current_floor": self.current_floor,
            "max_floor": self.max_floor,
            "nodes_per_floor": self.nodes_per_floor,
            "path": self.path,
            "visited_nodes": list(self.visited_nodes),
            "current_node": self.current_node,
            "score": self.score,
            "streak": self.streak,
            "start_time": self.start_time.timestamp(),
            "end_time": self.end_time.timestamp() if self.end_time else None,
            "is_completed": self.is_completed,
            "is_successful": self.is_successful
        }
    
    @classmethod
    def from_dict(cls, data, character):
        """Create a game state from a saved dictionary."""
        game_state = cls(character, data.get("max_floor", 10), data.get("nodes_per_floor", 3))
        game_state.current_floor = data.get("current_floor", 0)
        game_state.path = data.get("path", [])
        game_state.visited_nodes = set(data.get("visited_nodes", []))
        game_state.current_node = data.get("current_node")
        game_state.score = data.get("score", 0)
        game_state.streak = data.get("streak", 0)
        
        # Convert timestamps back to datetime objects
        start_time = data.get("start_time")
        if start_time:
            game_state.start_time = datetime.fromtimestamp(start_time)
        
        end_time = data.get("end_time")
        if end_time:
            game_state.end_time = datetime.fromtimestamp(end_time)
        
        game_state.is_completed = data.get("is_completed", False)
        game_state.is_successful = data.get("is_successful", False)
        
        return game_state


class AchievementManager:
    """Manages achievements and their tracking."""
    
    def __init__(self, data_manager):
        """Initialize with a data manager."""
        self.data_manager = data_manager
        self.achievements = data_manager.get_data("achievements").get("achievements", [])
        self.unlocked_achievements = set()
    
    def check_achievement(self, achievement_id):
        """Check if an achievement is unlocked."""
        return achievement_id in self.unlocked_achievements
    
    def unlock_achievement(self, achievement_id):
        """Unlock an achievement."""
        if achievement_id in self.unlocked_achievements:
            return {"success": False, "message": "Achievement already unlocked"}
        
        # Find the achievement
        achievement = next((a for a in self.achievements if a["id"] == achievement_id), None)
        if not achievement:
            return {"success": False, "message": "Achievement not found"}
        
        # Unlock it
        self.unlocked_achievements.add(achievement_id)
        
        return {
            "success": True,
            "achievement": achievement,
            "message": f"Achievement unlocked: {achievement['name']}"
        }
    
    def check_run_achievements(self, game_state):
        """Check if any achievements were unlocked during this run."""
        unlocked = []
        
        # First run achievement
        if "first_run" not in self.unlocked_achievements:
            unlocked.append(self.unlock_achievement("first_run"))
        
        # Perfect floor achievement
        if game_state.current_floor > 0 and game_state.character.lives == game_state.character.max_lives:
            if "perfect_floor" not in self.unlocked_achievements:
                unlocked.append(self.unlock_achievement("perfect_floor"))
        
        # Master physicist achievement
        if game_state.character.level >= 10:
            if "master_physicist" not in self.unlocked_achievements:
                unlocked.append(self.unlock_achievement("master_physicist"))
        
        # Ironman achievement
        if game_state.is_completed and game_state.is_successful and game_state.character.lives == game_state.character.max_lives:
            if "ironman" not in self.unlocked_achievements:
                unlocked.append(self.unlock_achievement("ironman"))
        
        return [u for u in unlocked if u["success"]]
    
    def to_dict(self):
        """Convert achievement manager to dictionary for saving."""
        return {
            "unlocked_achievements": list(self.unlocked_achievements)
        }
    
    @classmethod
    def from_dict(cls, data, data_manager):
        """Create an achievement manager from a saved dictionary."""
        manager = cls(data_manager)
        manager.unlocked_achievements = set(data.get("unlocked_achievements", []))
        return manager


class SaveManager:
    """Manages saving and loading game data."""
    
    def __init__(self, save_dir="data/saves"):
        """Initialize with a save directory."""
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)
    
    def save_game(self, game_state, player_data, achievement_manager, save_name=None):
        """Save the current game state."""
        if not save_name:
            save_name = f"save_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        save_data = {
            "game_state": game_state.to_dict() if game_state else None,
            "player_data": player_data,
            "achievements": achievement_manager.to_dict() if achievement_manager else None,
            "timestamp": datetime.now().timestamp(),
            "version": "1.0.0"
        }
        
        filepath = os.path.join(self.save_dir, f"{save_name}.json")
        
        try:
            with open(filepath, 'w') as file:
                json.dump(save_data, file, indent=2)
            return {"success": True, "save_name": save_name}
        except IOError as e:
            return {"success": False, "message": f"Error saving game: {e}"}
    
    def load_game(self, save_name, data_manager):
        """Load a saved game."""
        filepath = os.path.join(self.save_dir, f"{save_name}.json")
        
        if not os.path.exists(filepath):
            return {"success": False, "message": "Save file not found"}
        
        try:
            with open(filepath, 'r') as file:
                save_data = json.load(file)
            
            # Load player data
            player_data = save_data.get("player_data", {})
            
            # Load achievements
            achievement_data = save_data.get("achievements", {})
            achievement_manager = AchievementManager.from_dict(achievement_data, data_manager)
            
            # Load game state if it exists
            game_state = None
            game_state_data = save_data.get("game_state")
            if game_state_data:
                # Get character class data
                class_id = game_state_data["character"]["id"]
                class_data = data_manager.get_item_by_id("classes", class_id)
                if class_data:
                    # Create character
                    character = Character.from_dict(game_state_data["character"], class_data)
                    # Create game state
                    game_state = GameState.from_dict(game_state_data, character)
            
            return {
                "success": True,
                "player_data": player_data,
                "game_state": game_state,
                "achievement_manager": achievement_manager
            }
        except (json.JSONDecodeError, IOError) as e:
            return {"success": False, "message": f"Error loading save: {e}"}
    
    def list_saves(self):
        """List all available save files."""
        try:
            saves = []
            for filename in os.listdir(self.save_dir):
                if filename.endswith(".json"):
                    filepath = os.path.join(self.save_dir, filename)
                    try:
                        with open(filepath, 'r') as file:
                            save_data = json.load(file)
                        
                        # Extract metadata
                        timestamp = save_data.get("timestamp")
                        if timestamp:
                            date = datetime.fromtimestamp(timestamp)
                            formatted_date = date.strftime("%Y-%m-%d %H:%M:%S")
                        else:
                            formatted_date = "Unknown"
                        
                        player_data = save_data.get("player_data", {})
                        
                        saves.append({
                            "name": filename[:-5],  # Remove .json extension
                            "date": formatted_date,
                            "player_level": player_data.get("level", 1),
                            "player_class": player_data.get("class", "Unknown"),
                            "completed_runs": player_data.get("completed_runs", 0)
                        })
                    except:
                        # Skip files that can't be parsed
                        continue
            
            return {"success": True, "saves": saves}
        except Exception as e:
            return {"success": False, "message": f"Error listing saves: {e}"}
    
    def delete_save(self, save_name):
        """Delete a save file."""
        filepath = os.path.join(self.save_dir, f"{save_name}.json")
        
        if not os.path.exists(filepath):
            return {"success": False, "message": "Save file not found"}
        
        try:
            os.remove(filepath)
            return {"success": True, "message": f"Deleted save: {save_name}"}
        except IOError as e:
            return {"success": False, "message": f"Error deleting save: {e}"}

class PathHistory:
    """Tracks the player's path history and statistics."""
    
    def __init__(self):
        self.visited_nodes = []  # List of node IDs in visit order
        self.node_types = {      # Count of each node type visited
            "question": 0,
            "reference": 0,
            "rest": 0,
            "treasure": 0,
            "elite": 0,
            "boss": 0,
            "encounter": 0
        }
        self.floors_completed = 0
        self.elites_defeated = 0
        self.highest_floor = 0
    
    def record_visit(self, node):
        """Record a node visit."""
        self.visited_nodes.append(node["id"])
        
        # Update type counts
        node_type = node.get("type", "question")
        if node_type in self.node_types:
            self.node_types[node_type] += 1
            
        # Special counters
        if node_type == "elite":
            self.elites_defeated += 1
    
    def record_floor_completion(self, floor_num):
        """Record completing a floor."""
        self.floors_completed += 1
        self.highest_floor = max(self.highest_floor, floor_num)
    
    def get_path_summary(self):
        """Get a summary of the path."""
        return {
            "nodes_visited": len(self.visited_nodes),
            "floors_completed": self.floors_completed,
            "highest_floor": self.highest_floor,
            "elites_defeated": self.elites_defeated,
            "node_distribution": self.node_types.copy()
        }
    
    def get_player_strategy(self):
        """Analyze the player's path strategy."""
        if not self.visited_nodes:
            return "Undetermined"
        
        total = len(self.visited_nodes)
        
        # Calculate percentages
        percentages = {k: (v / total) * 100 for k, v in self.node_types.items()}
        
        # Determine strategy
        if percentages.get("elite", 0) >= 25:
            return "Challenge Seeker"
        elif percentages.get("rest", 0) >= 25:
            return "Cautious Explorer"
        elif percentages.get("treasure", 0) >= 25:
            return "Treasure Hunter"
        elif percentages.get("reference", 0) >= 25:
            return "Knowledge Seeker"
        elif percentages.get("question", 0) >= 50:
            return "Balanced Learner"
        else:
            return "Versatile Physicist"
        
class BranchingPathGenerator:
    """Generates true branching paths for the game, similar to Slay the Spire."""
    
    def __init__(self, max_floors=10, min_width=2, max_width=4):
        """Initialize the path generator with configuration options."""
        self.max_floors = max_floors
        self.min_width = min_width
        self.max_width = max_width
        
        # Path data
        self.nodes = []  # All nodes in the path
        self.floors = []  # Nodes organized by floor
        self.connections = {}  # Dictionary mapping node_id -> list of connected node_ids
        
    def generate(self, data_manager):
        """Generate a complete path structure and return it in GameState format."""
        import random
        
        # Initialize path structure
        self.floors = [[] for _ in range(self.max_floors)]
        self.connections = {}
        self.nodes = []
        
        # Create nodes for each floor
        for floor in range(self.max_floors):
            # Determine how many nodes on this floor
            if floor == 0:
                # First floor always has one starting node
                num_nodes = 1
            elif floor == self.max_floors - 1:
                # Last floor always has one boss node
                num_nodes = 1
            else:
                # Middle floors vary in width
                # More nodes in the middle of the path
                floor_factor = min(floor, self.max_floors - floor - 1) + 1
                num_nodes = min(self.max_width, max(self.min_width, floor_factor))
            
            # Create nodes for this floor
            floor_nodes = []
            for i in range(num_nodes):
                # Create a node
                node = self._create_node(floor, i, data_manager)
                floor_nodes.append(node)
                self.connections[node["id"]] = []
            
            # Add to floors
            self.floors[floor] = floor_nodes
            self.nodes.extend(floor_nodes)
        
        # Create connections between floors
        self._create_connections()
        
        # Convert to GameState format and return
        return self.floors, self.connections
    
    def _create_node(self, floor, position, data_manager):
        """Create a node for the path."""
        import random
        
        # Determine node type based on floor and position
        if floor == 0:
            # First floor is always a question
            node_type = "question"
        elif floor == self.max_floors - 1:
            # Last floor is always a boss
            node_type = "boss"
        else:
            # Determine node type based on floor and position
            node_type = self._get_node_type(floor, position)
        
        # Generate a category
        categories = ["dosimetry", "qa", "radiation", "planning", "calculation", "imaging", "regulations"]
        category = random.choice(categories)
        
        # Generate difficulty (higher floors = higher difficulty)
        base_difficulty = min(3, max(1, floor // 3 + 1))
        if node_type == "elite":
            difficulty = min(3, base_difficulty + 1)
        elif node_type == "boss":
            difficulty = 3
        else:
            difficulty = base_difficulty
        
        # Map node types to icons and names
        node_types = {
            "question": {"name": "Question", "icon": "📝"},
            "reference": {"name": "Reference", "icon": "📚"},
            "rest": {"name": "Break Room", "icon": "☕"},
            "treasure": {"name": "Conference", "icon": "🎁"},
            "elite": {"name": "Complex Case", "icon": "⚠️"},
            "boss": {"name": "Rotation Evaluation", "icon": "⭐"},
            "encounter": {"name": "Special Event", "icon": "🔍"}
        }
        
        # Create node data
        node_id = f"node_{floor}_{position}_{random.randint(1000, 9999)}"
        node = {
            "id": node_id,
            "type": node_type,
            "name": node_types[node_type]["name"],
            "icon": node_types[node_type]["icon"],
            "difficulty": difficulty,
            "category": category,
            "visited": False,
            "floor": floor,
            "position": position,
            # Content would be generated when the node is visited
            "content": None
        }
        
        return node
    
    def _get_node_type(self, floor, position):
        """Determine what type of node to place based on floor and position."""
        import random
        
        # Node type probabilities (default)
        probabilities = {
            "question": 50,
            "reference": 15,
            "rest": 15,
            "treasure": 10,
            "elite": 5,
            "encounter": 5
        }
        
        # Adjust probabilities based on floor
        if floor > 3:
            # More elites in later floors
            probabilities["elite"] += floor * 2
            probabilities["question"] -= floor * 2
        
        # Special adjustments for certain positions
        if position == 0:
            # First node in a row has higher chance of rest
            probabilities["rest"] += 10
            probabilities["question"] -= 10
        
        if position == self.max_width - 1:
            # Last node has higher chance of elite/treasure
            probabilities["elite"] += 15
            probabilities["treasure"] += 5
            probabilities["question"] -= 20
        
        # Normalize probabilities
        total = sum(probabilities.values())
        normalized = {k: v / total for k, v in probabilities.items()}
        
        # Choose node type based on probabilities
        r = random.random()
        cumulative = 0
        for node_type, probability in normalized.items():
            cumulative += probability
            if r <= cumulative:
                return node_type
        
        # Default to question if something goes wrong
        return "question"
    
    def _create_connections(self):
        """Create connections between nodes on adjacent floors."""
        import random
        
        # For each floor except the last
        for floor in range(self.max_floors - 1):
            current_floor_nodes = self.floors[floor]
            next_floor_nodes = self.floors[floor + 1]
            
            # Special case: if there's only one node on either floor, connect to all
            if len(current_floor_nodes) == 1 or len(next_floor_nodes) == 1:
                for source in current_floor_nodes:
                    for target in next_floor_nodes:
                        self.connections[source["id"]].append(target["id"])
                continue
            
            # General case: create branching connections
            for i, source in enumerate(current_floor_nodes):
                # Determine how many connections to make
                min_connections = 1
                max_connections = min(3, len(next_floor_nodes))
                num_connections = random.randint(min_connections, max_connections)
                
                # Choose target nodes based on position (prefer nearby nodes)
                target_indices = []
                available_targets = list(range(len(next_floor_nodes)))
                
                # Try to add a connection to a node in a similar position first
                similar_pos = int(i * len(next_floor_nodes) / len(current_floor_nodes))
                if similar_pos in available_targets:
                    target_indices.append(similar_pos)
                    available_targets.remove(similar_pos)
                
                # Add remaining random connections
                while len(target_indices) < num_connections and available_targets:
                    idx = random.choice(available_targets)
                    target_indices.append(idx)
                    available_targets.remove(idx)
                
                # Create the connections
                for idx in target_indices:
                    target = next_floor_nodes[idx]
                    self.connections[source["id"]].append(target["id"])
        
        # Ensure all nodes are reachable
        self._ensure_connectivity()
    
    def _ensure_connectivity(self):
        """Make sure all nodes have at least one incoming and outgoing connection."""
        import random
        
        # Every node except on the first floor should have at least one incoming connection
        for floor in range(1, self.max_floors):
            for target in self.floors[floor]:
                # Check if this node has any incoming connections
                has_incoming = any(target["id"] in self.connections[source["id"]] 
                                  for source in self.floors[floor-1])
                
                if not has_incoming:
                    # Connect it to a random node on the previous floor
                    source = random.choice(self.floors[floor-1])
                    self.connections[source["id"]].append(target["id"])
        
        # Every node except on the last floor should have at least one outgoing connection
        for floor in range(self.max_floors - 1):
            for source in self.floors[floor]:
                if not self.connections[source["id"]] and floor < self.max_floors - 1:
                    # Connect it to a random node on the next floor
                    target = random.choice(self.floors[floor+1])
                    self.connections[source["id"]].append(target["id"])