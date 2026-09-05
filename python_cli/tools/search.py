from .base import Tool
from ..project.ignore import ignored
class Grep(Tool):
    name="grep"; description="Search text recursively in workspace, excluding secret/vendor directories."; permission_level="SAFE"
    def __init__(self,pm):self.pm=pm
    def schema(self): return {"type":"function","function":{"name":self.name,"description":self.description,"parameters":{"type":"object","properties":{"query":{"type":"string"},"path":{"type":"string"}},"required":["query"]}}}
    async def execute(self,a):
        try: root=self.pm.resolve(a.get("path","."))
        except PermissionError as e: return {"success":False,"tool":self.name,"error":str(e),"code":"PATH_OUTSIDE_WORKSPACE"}
        hits=[]
        for p in root.rglob('*'):
            if ignored(p) or not p.is_file(): continue
            try:
                for i,line in enumerate(p.read_text(errors="replace").splitlines(),1):
                    if a["query"] in line: hits.append({"path":str(p.relative_to(self.pm.root)),"line":i,"text":line[:500]})
                    if len(hits)>=200:return {"success":True,"tool":self.name,"data":{"matches":hits,"truncated":True}}
            except OSError: pass
        return {"success":True,"tool":self.name,"data":{"matches":hits,"truncated":False}}
class Glob(Tool):
    name="glob"; description="Find files using a glob pattern inside workspace."; permission_level="SAFE"
    def __init__(self,pm):self.pm=pm
    def schema(self): return {"type":"function","function":{"name":self.name,"description":self.description,"parameters":{"type":"object","properties":{"pattern":{"type":"string"}},"required":["pattern"]}}}
    async def execute(self,a):
        out=[]
        for p in self.pm.root.glob(a["pattern"]):
            if not ignored(p): out.append(str(p.relative_to(self.pm.root)))
        return {"success":True,"tool":self.name,"data":{"files":out[:500],"count":len(out)}}
class Tree(Tool):
    name="tree"; description="List workspace project structure."; permission_level="SAFE"
    def __init__(self,pm):self.pm=pm
    async def execute(self,a):return {"success":True,"tool":self.name,"data":{"tree":self.pm.tree()}}
