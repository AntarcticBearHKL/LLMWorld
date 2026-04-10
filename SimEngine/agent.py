from .llm_provider import DeepSeekProvider
from .prompt_manager import PromptManager
from .context_manager import ContextManager


class Agent:
    def __init__(self, name, llm_provider, context_name=None, identity=None):
        self.name = name
        self.llm = llm_provider
        self.prompt_manager = PromptManager()
        self.context_manager = ContextManager()
        self.context_name = context_name  # 使用哪个 context 文件
        self.identity = identity          # 在该文件中的身份标识

    def think(self, context_name=None, identity=None, input_data=""):
        # 优先用调用时传入的，否则用初始化时绑定的
        ctx_name = context_name or self.context_name
        ctx_identity = identity or self.identity

        environment_context = ""
        if ctx_name and self.context_manager.has_context(ctx_name, ctx_identity):
            environment_context = self.context_manager.get_context(ctx_name, ctx_identity)

        full_context = input_data
        if environment_context:
            full_context = f"{environment_context}\n\nInput: {input_data}" if input_data else environment_context

        prompt = self.prompt_manager.get_prompt("think_prompt", context=full_context)
        return self.llm.generate(prompt)
