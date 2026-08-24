import os
import re

class Prompt:
    def __init__(self, prompts_dir=None):
        if prompts_dir is None:
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            self.prompts_dir = os.path.join(project_root, "src", "prompts")
        else:
            self.prompts_dir = prompts_dir
        self._ensure_prompts_dir()
    
    def _ensure_prompts_dir(self):
        if not os.path.exists(self.prompts_dir):
            os.makedirs(self.prompts_dir)
    
    def load(self, filename, **kwargs):
        filepath = os.path.join(self.prompts_dir, f"{filename}.md")
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Prompt file not found: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            template = f.read()
        
        return self._render(template, kwargs)
    
    def _render(self, template, variables):
        def replace_var(match):
            var_name = match.group(1)
            if var_name in variables:
                value = variables[var_name]
                if isinstance(value, (list, dict)):
                    import json
                    return json.dumps(value, ensure_ascii=False, indent=2)
                return str(value)
            return match.group(0)
        
        return re.sub(r'\{(\w+)\}', replace_var, template)
    
    def list_prompts(self):
        if not os.path.exists(self.prompts_dir):
            return []
        return [f[:-3] for f in os.listdir(self.prompts_dir) if f.endswith('.md')]
