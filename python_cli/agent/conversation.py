class ConversationManager:
    def __init__(self):self.messages=[]
    def add(self,m):self.messages.append(m)
    def all(self):return list(self.messages)
