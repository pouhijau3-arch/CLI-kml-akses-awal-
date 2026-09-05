from .base import Tool
import asyncio, os
class Bash(Tool):
    name="bash"; description="Run a shell command in the workspace."; permission_level="ASK"
    def __init__(self,pm):self.pm=pm
    def schema(self): return {"type":"function","function":{"name":self.name,"description":self.description,"parameters":{"type":"object","properties":{"command":{"type":"string"},"timeout":{"type":"integer"}},"required":["command"]}}}
    async def execute(self,a):
        timeout=min(max(int(a.get("timeout",120)),1),300)
        proc=await asyncio.create_subprocess_shell(a["command"],cwd=str(self.pm.root),stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.STDOUT,env=os.environ.copy())
        try: out,_=await asyncio.wait_for(proc.communicate(),timeout=timeout)
        except asyncio.TimeoutError:
            proc.kill(); await proc.communicate(); return {"success":False,"tool":self.name,"error":"Command timed out","code":"TIMEOUT"}
        text=out.decode(errors="replace")
        return {"success":proc.returncode==0,"tool":self.name,"data":{"exit_code":proc.returncode,"output":text[-12000:]},"error":None if proc.returncode==0 else text[-12000:],"code":"OK" if proc.returncode==0 else "COMMAND_FAILED"}
