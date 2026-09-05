from .base import Tool
class ReadFile(Tool):
    name="read_file"; description="Read a text file inside the workspace."; permission_level="SAFE"
    def __init__(self,pm): self.pm=pm
    def schema(self): return {"type":"function","function":{"name":self.name,"description":self.description,"parameters":{"type":"object","properties":{"path":{"type":"string"},"start_line":{"type":"integer"},"end_line":{"type":"integer"}},"required":["path"]}}}
    async def execute(self,a):
        try: p=self.pm.resolve(a["path"])
        except PermissionError as e: return {"success":False,"tool":self.name,"error":str(e),"code":"PATH_OUTSIDE_WORKSPACE"}
        if not p.is_file(): return {"success":False,"tool":self.name,"error":"FILE_NOT_FOUND","code":"FILE_NOT_FOUND"}
        text=p.read_text(errors="replace"); lines=text.splitlines()
        s=max(1,int(a.get("start_line",1))); e=min(len(lines),int(a.get("end_line",len(lines))))
        return {"success":True,"tool":self.name,"data":{"path":str(p.relative_to(self.pm.root)),"content":"\n".join(lines[s-1:e]),"lines":len(lines),"start_line":s,"end_line":e}}
class WriteFile(Tool):
    name="write_file"; description="Create or replace a text file inside the workspace."; permission_level="ASK"
    def __init__(self,pm): self.pm=pm
    def schema(self): return {"type":"function","function":{"name":self.name,"description":self.description,"parameters":{"type":"object","properties":{"path":{"type":"string"},"content":{"type":"string"}},"required":["path","content"]}}}
    async def execute(self,a):
        try: p=self.pm.resolve(a["path"])
        except PermissionError as e: return {"success":False,"tool":self.name,"error":str(e),"code":"PATH_OUTSIDE_WORKSPACE"}
        p.parent.mkdir(parents=True,exist_ok=True); p.write_text(a["content"])
        return {"success":True,"tool":self.name,"data":{"path":str(p.relative_to(self.pm.root)),"bytes":p.stat().st_size}}
class EditFile(Tool):
    name="edit_file"; description="Replace an exact text occurrence in a workspace file."; permission_level="ASK"
    def __init__(self,pm): self.pm=pm
    def schema(self): return {"type":"function","function":{"name":self.name,"description":self.description,"parameters":{"type":"object","properties":{"path":{"type":"string"},"old_text":{"type":"string"},"new_text":{"type":"string"}},"required":["path","old_text","new_text"]}}}
    async def execute(self,a):
        try: p=self.pm.resolve(a["path"])
        except PermissionError as e: return {"success":False,"tool":self.name,"error":str(e),"code":"PATH_OUTSIDE_WORKSPACE"}
        text=p.read_text(errors="replace"); old=a["old_text"]
        if old not in text:return {"success":False,"tool":self.name,"error":"old_text not found","code":"TEXT_NOT_FOUND"}
        new=text.replace(old,a["new_text"],1); p.write_text(new)
        return {"success":True,"tool":self.name,"data":{"path":str(p.relative_to(self.pm.root)),"changed":True}}
