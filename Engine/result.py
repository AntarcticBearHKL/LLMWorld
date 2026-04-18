import json
import os
from datetime import datetime


class Result:
    def __init__(self, raw_response):
        self.raw = raw_response
        self.data = self._parse_json(raw_response)
    
    def _parse_json(self, response):
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {e}")
            return {}
    
    def get(self, key, default=None):
        return self.data.get(key, default)
    
    def __getitem__(self, key):
        return self.data[key]
    
    def __repr__(self):
        return f"Result({self.data})"
    
    def save(self, output_name):
        os.makedirs("output", exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{output_name}_{timestamp}.md"
        filepath = os.path.join("output", filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# {output_name}\n\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            
            if self.data:
                for key, value in self.data.items():
                    f.write(f"## {key}\n\n")
                    if isinstance(value, (list, dict)):
                        f.write(f"```json\n{json.dumps(value, ensure_ascii=False, indent=2)}\n```\n\n")
                    else:
                        f.write(f"{value}\n\n")
            else:
                f.write("## 原始输出\n\n")
                f.write(f"```\n{self.raw}\n```\n")
        
        print(f"结果已保存到: {filepath}")
        return filepath
