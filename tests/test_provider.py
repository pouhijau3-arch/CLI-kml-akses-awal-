import pytest
from python_cli.providers.openai_compatible import OpenAICompatibleProvider
class Resp:
 status_code=200
 def json(self): return {'choices':[{'message':{'role':'assistant','content':'OK'}}]}
class Client:
 def __init__(self): self.args=None
 async def post(self,url,headers,json_data,timeout=120): self.args=(url,headers,json_data); return Resp()
@pytest.mark.asyncio
async def test_provider_request():
 c=Client(); p=OpenAICompatibleProvider('https://x.example/v1','secret','m',c); m=await p.chat([{'role':'user','content':'hi'}],[])
 assert c.args[0]=='https://x.example/v1/chat/completions'; assert c.args[1]['Authorization']=='Bearer secret'; assert c.args[2]['model']=='m'; assert m['content']=='OK'
