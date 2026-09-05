import pytest
from python_cli.project.manager import ProjectManager
@pytest.mark.asyncio
async def test_traversal(tmp_path):
 pm=ProjectManager(str(tmp_path))
 try: pm.resolve('../outside'); assert False
 except PermissionError: assert True
