import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from SimEngine import Agent, DeepSeekProvider

if __name__ == "__main__":
    # 两个 agent 各自绑定身份，自动只拿到属于自己的 context + shared
    landlord = Agent("李明", DeepSeekProvider(), context_name="rental", identity="房东")
    tenant   = Agent("小王", DeepSeekProvider(), context_name="rental", identity="租客")

    print("=== 房东的想法 ===")
    print(landlord.think())

    print("\n=== 租客的想法 ===")
    print(tenant.think())
