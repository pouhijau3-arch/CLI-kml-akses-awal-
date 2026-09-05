import pytest,json
from python_cli.agent.agent import AgentEngine
from python_cli.permissions import PermissionManager
from python_cli.project.manager import ProjectManager
from python_cli.tools import ReadFile
class Provider:
 def __init__(self): self.n=0
 async def chat(self,messages,tools=None,stream=False):
  self.n+=1
  if self.n==1:return {'role':'assistant','tool_calls':[{'id':'1','type':'function','function':{'name':'read_file','arguments':json.dumps({'path':'a.txt'})}}]}
  return {'role':'assistant','content':'verified'}
@pytest.mark.asyncio
async def test_agent_loop(tmp_path):
 (tmp_path/'a.txt').write_text('hello'); pm=ProjectManager(str(tmp_path)); a=AgentEngine(Provider(),[ReadFile(pm)],PermissionManager(),pm)
 assert await a.run('read it')=='verified'
