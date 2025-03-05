import os
import json

class ConfigManager:
    def __init__(self, config_file="data/config.json"):
        """Initialize the config manager."""
        self.config_file = config_file
        self.config = self._load_config()
    
    def _load_config(self):
        """Load configuration from file."""
        if not os.path.exists(self.config_file):
            # Create default config if it doesn't exist
            default_config = {
                "physicians": ["Dalwadi"],
                "physicists": ["Paschal"]
            }
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w') as file:
                json.dump(default_config, file, indent=2)
            return default_config
        
        with open(self.config_file, 'r') as file:
            return json.load(file)
    
    def get_physicians(self):
        """Get list of physicians."""
        return self.config.get("physicians", [])
    
    def get_physicists(self):
        """Get list of physicists."""
        return self.config.get("physicists", [])