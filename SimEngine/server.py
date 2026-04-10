import json
import threading
from .world import World

class SimServer:
    def __init__(self):
        self.world = World()
        self.commands = {
            "add_agent": self.add_agent,
            "remove_agent": self.remove_agent,
            "agent_action": self.agent_action,
            "get_state": self.get_state,
            "run_steps": self.run_steps,
            "stop": self.stop,
            "chat": self.chat
        }
    
    def add_agent(self, name, llm_provider=None):
        self.world.add_agent(name, llm_provider)
        return "Agent " + name + " added"
    
    def remove_agent(self, name):
        self.world.remove_agent(name)
        return "Agent " + name + " removed"
    
    def agent_action(self, agent_name, action_type, target=None, content=""):
        action = self.world.agent_action(agent_name, action_type, target, content)
        return action
    
    def chat(self, from_agent, to_agent, message):
        return self.agent_action(from_agent, "chat", to_agent, message)
    
    def get_state(self):
        return self.world.get_world_state()
    
    def run_steps(self, steps=1):
        thread = threading.Thread(target=self.world.run_simulation, args=(steps,))
        thread.start()
        return "Running " + str(steps) + " steps"
    
    def stop(self):
        self.world.stop_simulation()
        return "Simulation stopped"
    
    def execute_command(self, command, **kwargs):
        if command in self.commands:
            return self.commands[command](**kwargs)
        return "Unknown command"
    
    def interactive_mode(self):
        print("TextWorld Simulation Server")
        
        while True:
            try:
                cmd_input = input("> ").strip().split()
                if not cmd_input:
                    continue
                    
                cmd = cmd_input[0]
                
                if cmd == "exit":
                    break
                elif cmd == "add_agent":
                    name = cmd_input[1]
                    print(self.add_agent(name))
                elif cmd == "remove_agent":
                    name = cmd_input[1]
                    print(self.remove_agent(name))
                elif cmd == "chat":
                    from_agent = cmd_input[1]
                    to_agent = cmd_input[2]
                    message = " ".join(cmd_input[3:])
                    print(self.chat(from_agent, to_agent, message))
                elif cmd == "run_steps":
                    steps = int(cmd_input[1]) if len(cmd_input) > 1 else 1
                    print(self.run_steps(steps))
                elif cmd == "get_state":
                    state = self.get_state()
                    print(json.dumps(state, indent=2))
                elif cmd == "stop":
                    print(self.stop())
                else:
                    print("Unknown command")
                    
            except (IndexError, ValueError):
                print("Invalid command format")
            except KeyboardInterrupt:
                break
        
        self.stop()