import json
import os
from typing import Dict, Any


class PromptManager:
    def __init__(self, prompts_dir: str = "prompts"):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        self.prompts_dir = os.path.join(project_root, prompts_dir)
        self.prompts = {}
        self._load_prompts()
    
    def _load_prompts(self):
        if not os.path.exists(self.prompts_dir):
            print("Warning: Prompts directory not found: " + self.prompts_dir)
            return
        
        for filename in os.listdir(self.prompts_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.prompts_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        file_prompts = json.load(f)
                        self.prompts.update(file_prompts)
                except Exception as e:
                    print("Error loading prompt file " + filepath + ": " + str(e))
    
    def get_prompt(self, prompt_key: str, **kwargs) -> str:
        if prompt_key not in self.prompts:
            raise KeyError("Prompt not found: " + prompt_key)
        
        prompt_config = self.prompts[prompt_key]
        template = prompt_config.get('template', '')
        
        formatted_prompt = template
        for key, value in kwargs.items():
            placeholder = "{" + key + "}"
            formatted_prompt = formatted_prompt.replace(placeholder, str(value))
        
        return formatted_prompt
    
    def list_prompts(self) -> Dict[str, str]:
        return {key: config.get('description', 'No description') 
                for key, config in self.prompts.items()}
    
    def reload_prompts(self):
        self.prompts.clear()
        self._load_prompts()