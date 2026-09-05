from __future__ import annotations
import json
from .base import Provider
from .http_client import HTTPClient
from ..config import normalize_base_url
class OpenAICompatibleProvider(Provider):
    def __init__(self,base_url,api_key,model,http_client=None): self.base=normalize_base_url(base_url); self.key=api_key; self.model=model; self.http=http_client or HTTPClient()
    @property
    def endpoint(self): return self.base+'/chat/completions'
    def _payload(self,messages,tools):
        p={"model":self.model,"messages":messages}
        if tools:p["tools"]=tools; p["tool_choice"]="auto"
        return p
    async def chat(self,messages,tools=None,stream=False):
        r=await self.http.post(self.endpoint,{"Authorization":"Bearer "+self.key,"Content-Type":"application/json"},self._payload(messages,tools))
        if r.status_code>=400: raise RuntimeError(f"Provider HTTP {r.status_code}: {r.text[:1000]}")
        if stream: return self._stream_response(r)
        data=r.json(); return data["choices"][0]["message"]
    async def _stream_response(self,r):
        return r.json()
    async def test(self):
        return await self.chat([{"role":"user","content":"Reply with OK"}],None,False)
