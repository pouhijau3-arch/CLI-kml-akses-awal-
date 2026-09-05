from __future__ import annotations
from pathlib import Path
from .ignore import ignored
class ProjectManager:
    def __init__(self, workspace: str): self.set_workspace(workspace)
    def set_workspace(self, workspace): self.root=Path(workspace).expanduser().resolve(); self.root.mkdir(parents=True,exist_ok=True)
    def resolve(self, path: str)->Path:
        p=Path(path).expanduser(); candidate=(p if p.is_absolute() else self.root/p).resolve()
        try: candidate.relative_to(self.root)
        except ValueError: raise PermissionError("Path is outside workspace")
        return candidate
    def tree(self,max_depth=6):
        def walk(d,depth):
            if depth>max_depth:return []
            out=[]
            try: entries=sorted(d.iterdir(), key=lambda p:(not p.is_dir(),p.name.lower()))
            except OSError:return []
            for p in entries:
                if ignored(p): continue
                item={"name":p.name,"type":"directory" if p.is_dir() else "file","path":str(p.relative_to(self.root))}
                if p.is_dir(): item["children"]=walk(p,depth+1)
                out.append(item)
            return out
        return walk(self.root,0)
