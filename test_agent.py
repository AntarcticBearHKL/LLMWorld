from SimEngine import Agent, DeepSeekProvider

if __name__ == "__main__":
    agent = Agent("测试Agent", DeepSeekProvider())
    agent.add_context("OutputFormat")
    agent.add_input("你好")
    
    print("=== Agent思考 ===")
    result = agent.think()
    print(result)
    print(f"thinking: {result['thinking']}")
    print(f"action: {result['action']}")
