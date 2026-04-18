from .context_manager import ContextManager
from .result import Result


class Agent:
    def __init__(self, name, llm_provider):
        self.name = name
        self.llm = llm_provider
        self.context_manager = ContextManager()
        self.contexts = []
        self.inputs = []

    def add_context(self, context_name):
        context_content = self.context_manager.get_context(context_name)
        if context_content:
            self.contexts.append(context_content)
        return self

    def add_input(self, input_text):
        self.inputs.append(input_text)
        return self

    def think(self):
        full_context = "\n\n".join(self.contexts)
        
        if self.inputs:
            input_text = "\n\n".join(self.inputs)
            full_context = f"{full_context}\n\nInput: {input_text}" if full_context else input_text

        raw_response = self.llm.generate(full_context)
        return Result(raw_response)
