from pathlib import Path
from python_cli.config import ConfigManager,normalize_base_url

def test_normalize():
 assert normalize_base_url('https://example.com')=='https://example.com/v1'
 assert normalize_base_url('https://example.com/v1/')=='https://example.com/v1'
 assert normalize_base_url('https://example.com/v1/chat/completions')=='https://example.com/v1'

def test_save_load_secure(tmp_path):
 p=tmp_path/'c.json'; c=ConfigManager(p); c.save({'providers':{},'active_model':'x'})
 assert c.load()['active_model']=='x'; assert oct(p.stat().st_mode & 0o777)=='0o600'
