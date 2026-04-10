import json
import time
from datetime import datetime
from .agent import Agent

class World:
    def __init__(self):
        self.agents = {}
        self.events = []
        self.step = 0
        self.running = False
        
    def add_agent(self, name, llm_provider=None):
        agent = Agent(name, llm_provider)
        self.agents[name] = agent
        self.broadcast_event("system", name + " joined the world")
        
    def remove_agent(self, name):
        if name in self.agents:
            del self.agents[name]
            self.broadcast_event("system", name + " left the world")
    
    def broadcast_event(self, source, content, target="all"):
        event = {
            "timestamp": datetime.now().isoformat(),
            "source": source,
            "target": target,
            "content": content,
            "step": self.step
        }
        self.events.append(event)
    
    def agent_action(self, agent_name, action_type, target=None, content=""):
        if agent_name not in self.agents:
            return None
            
        if action_type == "chat" and target in self.agents:
            response = self.agents[target].think(input_data=content)
            self.broadcast_event(agent_name, "says to " + target + ": " + content, target)
            self.broadcast_event(target, "responds to " + agent_name + ": " + response, agent_name)
            return response
        else:
            self.broadcast_event(agent_name, action_type + ": " + content)
            return content
    
    def step_simulation(self):
        self.step += 1
        
        for agent in self.agents.values():
            thought = agent.think()
            if "quietly" not in thought:
                self.broadcast_event("internal", thought)
    
    def get_world_state(self):
        return {
            "step": self.step,
            "agents": list(self.agents.keys()),
            "recent_events": self.events[-10:] if len(self.events) >= 10 else self.events
        }
    
    def run_simulation(self, steps=1):
        self.running = True
        for _ in range(steps):
            if not self.running:
                break
            self.step_simulation()
            time.sleep(0.1)
    
    def stop_simulation(self):
        self.running = False