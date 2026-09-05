from __future__ import annotations
import json, asyncio
from .conversation import ConversationManager
from .context import ContextManager
from .planner import Planner
class AgentEngine:
    def __init__(self,provider,tools,permissions,pm,event_cb=None,permission_hook=None,max_steps=30):
        self.provider=provider; self.tools={t.name:t for t in tools}; self.permissions=permissions; self.pm=pm; self.events=event_cb or (lambda e:None); self.permission_hook=permission_hook; self.max_steps=max_steps; self.stop_event=asyncio.Event()
    def stop(self):self.stop_event.set()
    async def run(self,user):
        self.stop_event.clear(); c=ConversationManager(); c.add({"role":"system","content":ContextManager(self.pm).system_prompt()}); c.add({"role":"user","content":user})
        self.events({"type":"agent_started","message":"Agent started"}); self.events({"type":"agent_thinking","message":Planner().initial_note(user)})
        for step in range(self.max_steps):
            if self.stop_event.is_set(): self.events({"type":"agent_finished","message":"Agent stopped","stopped":True}); return "Agent stopped."
            try: msg=await self.provider.chat(c.all(),[t.schema() for t in self.tools.values()])
            except Exception as e: self.events({"type":"agent_error","message":str(e)}); return "Provider error: "+str(e)
            c.add(msg)
            calls=msg.get("tool_calls") or []
            if not calls:
                answer=msg.get("content") or "No final response returned."
                self.events({"type":"agent_finished","message":"Task completed"}); return answer
            for call in calls:
                fn=call.get("function",{}); name=fn.get("name");
                try: args=json.loads(fn.get("arguments") or "{}")
                except Exception: args={}
                tool=self.tools.get(name)
                if not tool:
                    result={"success":False,"tool":name,"error":"Unknown tool","code":"UNKNOWN_TOOL"}
                else:
                    decision=self.permissions.classify(name,args)
                    if not decision.allowed:
                        self.events({"type":"permission_required","tool":name,"args":args,"mode":decision.mode})
                        if self.permission_hook:
                            choice=await self.permission_hook(name,args)
                            if choice in ("allow","always"):
                                if choice=="always": self.permissions.grant_always(name)
                                self.events({"type":"permission_granted","tool":name})
                                try: result=await tool.execute(args)
                                except Exception as e: result={"success":False,"tool":name,"error":str(e),"code":"TOOL_ERROR"}
                            else: result={"success":False,"tool":name,"error":"Permission denied","code":"PERMISSION_DENIED"}
                        else:
                            result={"success":False,"tool":name,"error":"Permission required","code":"PERMISSION_REQUIRED"}
                    else:
                        self.events({"type":"tool_started","tool":name,"args":args})
                        try: result=await tool.execute(args)
                        except Exception as e: result={"success":False,"tool":name,"error":str(e),"code":"TOOL_ERROR"}
                        self.events({"type":"tool_finished","tool":name,"result":result})
                c.add({"role":"tool","tool_call_id":call.get("id",""),"content":json.dumps(result)})
        self.events({"type":"agent_error","message":"Maximum agent steps reached"}); return "Agent stopped after reaching the maximum step limit."
