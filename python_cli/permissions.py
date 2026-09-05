from __future__ import annotations
from dataclasses import dataclass
import re
SAFE={"read_file","grep","glob","tree"}; ASK={"write_file","edit_file","bash"}
DENY_PATTERNS=[r"(^|\s)rm\s+-rf\s+/(\s|$)",r"(^|\s)(shutdown|reboot|mkfs)(\s|$)",r"(^|\s)format\s+",r"(^|\s)dd\s+if=",r":\(\)\s*\{.*:\|:&.*\};:"]
@dataclass
class PermissionDecision:
    allowed: bool
    reason: str
    mode: str
class PermissionManager:
    def __init__(self): self.always_allowed=set()
    def classify(self, tool, args=None):
        if tool in SAFE: return PermissionDecision(True,"safe","SAFE")
        if tool in ASK:
            if tool=="bash":
                cmd=(args or {}).get("command","")
                if any(re.search(p,cmd,re.I) for p in DENY_PATTERNS): return PermissionDecision(False,"dangerous command","DENY")
            if tool in self.always_allowed: return PermissionDecision(True,"always allowed","ASK")
            return PermissionDecision(False,"user approval required","ASK")
        return PermissionDecision(False,"unknown tool","DENY")
    def grant_always(self, tool): self.always_allowed.add(tool)
