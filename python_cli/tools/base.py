class Tool:
    name=""; description=""; permission_level="SAFE"
    def schema(self): return {"type":"function","function":{"name":self.name,"description":self.description,"parameters":{"type":"object","properties":{},"required":[]}}}
    async def execute(self,args): raise NotImplementedError
