import pytest
from python_cli.project.manager import ProjectManager
from python_cli.tools import ReadFile,WriteFile,EditFile,Grep,Glob,Tree
@pytest.mark.asyncio
async def test_tools(tmp_path):
 pm=ProjectManager(str(tmp_path)); w=WriteFile(pm); r=ReadFile(pm); e=EditFile(pm); g=Grep(pm); gl=Glob(pm); t=Tree(pm)
 assert (await w.execute({'path':'src/a.py','content':'print("Hello")'}))['success']
 assert (await r.execute({'path':'src/a.py'}))['data']['content']=='print("Hello")'
 assert (await e.execute({'path':'src/a.py','old_text':'Hello','new_text':'CLI-KML'}))['success']
 assert (await g.execute({'query':'CLI-KML'}))['data']['matches'][0]['path']=='src/a.py'
 assert 'src/a.py' in (await gl.execute({'pattern':'src/*.py'}))['data']['files']
 assert (await t.execute({}))['success']
 assert not (await r.execute({'path':'../../etc/passwd'}))['success']
