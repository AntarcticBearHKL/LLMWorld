class Member:
    def __init__(self, name, age, occupation, personality, habits):
        self.name = name
        self.age = age
        self.occupation = occupation
        self.personality = personality
        self.habits = habits
    
    def to_dict(self):
        return {
            "name": self.name,
            "age": self.age,
            "occupation": self.occupation,
            "personality": self.personality,
            "habits": self.habits
        }
