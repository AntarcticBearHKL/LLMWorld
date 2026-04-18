import os
from typing import Optional


class ContextManager:
    def __init__(self, contexts_dir: str = "contexts"):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        self.contexts_dir = os.path.join(project_root, contexts_dir)
        
    def get_context(self, name: str) -> Optional[str]:
        filepath = os.path.join(self.contexts_dir, f"{name}.md")
        
        if not os.path.exists(filepath):
            print(f"Warning: Context file not found: {filepath}")
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading context file {filepath}: {str(e)}")
            return None
    
    def list_contexts(self) -> list:
        if not os.path.exists(self.contexts_dir):
            return []
        
        return [f[:-3] for f in os.listdir(self.contexts_dir) if f.endswith('.md')]
