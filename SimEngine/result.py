import json


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
