import os
import re
from typing import Dict, Optional


class ContextManager:
    IDENTITY_PATTERN = re.compile(r'^@\[(.+?)\]', re.MULTILINE)

    def __init__(self, contexts_dir: str = "contexts"):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        self.contexts_dir = os.path.join(project_root, contexts_dir)
        # { context_file_name: { identity: content, ... } }
        self.contexts: Dict[str, Dict[str, str]] = {}
        self._load_contexts()

    def _parse_identities(self, raw: str) -> Dict[str, str]:
        """
        解析文件内容，按 @[身份] 标记拆分成 { identity: content } 字典。
        没有任何标记的文件，整体内容存在 'default' 键下。
        标记为 @[shared] 的块会在 get_context 时自动附加给所有身份。
        """
        parts = self.IDENTITY_PATTERN.split(raw)

        # parts[0] 是第一个标记之前的内容（可能为空）
        # 之后每两个元素是 (identity_name, content)
        if len(parts) == 1:
            # 没有任何 @[...] 标记
            return {"default": raw.strip()}

        result: Dict[str, str] = {}
        # parts[0] 是前导文本，忽略空白
        for i in range(1, len(parts), 2):
            identity = parts[i].strip()
            content = parts[i + 1].strip() if i + 1 < len(parts) else ""
            result[identity] = content

        return result

    def _load_contexts(self):
        if not os.path.exists(self.contexts_dir):
            print(f"Warning: Contexts directory not found: {self.contexts_dir}")
            return

        for filename in os.listdir(self.contexts_dir):
            if filename.endswith('.txt'):
                context_name = filename[:-4]
                filepath = os.path.join(self.contexts_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        raw = f.read()
                    self.contexts[context_name] = self._parse_identities(raw)
                    identities = list(self.contexts[context_name].keys())
                    print(f"Loaded context '{context_name}' with identities: {identities}")
                except Exception as e:
                    print(f"Error loading context file {filepath}: {str(e)}")

    def get_context(self, context_name: str, identity: Optional[str] = None) -> Optional[str]:
        """
        获取指定 context 中某个身份的内容。
        - identity=None 且文件无标记：返回 default 全文
        - identity=None 且文件有标记：返回所有块拼接
        - identity 指定：返回该身份的块 + shared 块（如果存在）
        """
        if context_name not in self.contexts:
            return None

        identity_map = self.contexts[context_name]

        if identity is None:
            return "\n\n".join(identity_map.values())

        shared = identity_map.get("shared", "")
        content = identity_map.get(identity)

        if content is None:
            print(f"Warning: identity '{identity}' not found in context '{context_name}'")
            return shared or None

        if shared:
            return f"{content}\n\n{shared}"
        return content

    def list_identities(self, context_name: str) -> list:
        if context_name not in self.contexts:
            return []
        return list(self.contexts[context_name].keys())

    def list_contexts(self) -> Dict[str, list]:
        return {name: list(identity_map.keys()) for name, identity_map in self.contexts.items()}

    def add_context(self, context_name: str, identity: str, content: str):
        if context_name not in self.contexts:
            self.contexts[context_name] = {}
        self.contexts[context_name][identity] = content

    def reload_contexts(self):
        self.contexts.clear()
        self._load_contexts()

    def has_context(self, context_name: str, identity: Optional[str] = None) -> bool:
        if context_name not in self.contexts:
            return False
        if identity is None:
            return True
        return identity in self.contexts[context_name]
