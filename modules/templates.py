import os
import string
import json

class TemplateManager:
    def __init__(self, templates_dir="data/templates"):
        """Initialize the template manager with the directory containing templates."""
        self.templates_dir = templates_dir
        self.templates = {}
        self._load_templates()
    
    def _load_templates(self):
        """Load all templates from the templates directory."""
        for filename in os.listdir(self.templates_dir):
            if filename.endswith(".txt"):
                template_name = os.path.splitext(filename)[0]
                file_path = os.path.join(self.templates_dir, filename)
                with open(file_path, 'r') as file:
                    self.templates[template_name] = file.read()
    
    def get_template(self, template_name):
        """Get a template by name."""
        return self.templates.get(template_name, "")
    
    def render_template(self, template_name, data):
        """Render a template with the provided data."""
        template = self.get_template(template_name)
        
        # Using string.Formatter for safe formatting
        formatter = string.Formatter()
        try:
            return template.format(**data)
        except KeyError as e:
            return f"Error: Missing field {e} in template"
        except Exception as e:
            return f"Error rendering template: {e}"

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