from __future__ import annotations
import json, os, tempfile
from pathlib import Path
from dataclasses import dataclass, asdict

CONFIG_PATH = Path.home() / ".cli_kml_config.json"
DEFAULT_BASE_URL = "https://api.openai.com/v1"

@dataclass
class ModelConfig:
    id: str
    display_name: str | None = None

@dataclass
class ProviderConfig:
    base_url: str = DEFAULT_BASE_URL
    api_key: str = ""
    models: list[ModelConfig] | list[str] | None = None

class ConfigManager:
    def __init__(self, path: Path = CONFIG_PATH): self.path = Path(path)
    def load(self) -> dict:
        if not self.path.exists():
            return {"providers":{"openai-compatible":asdict(ProviderConfig(models=["gpt-4o-mini"]))},"active_provider":"openai-compatible","active_model":"gpt-4o-mini","workspace":str(Path.cwd())}
        try: data=json.loads(self.path.read_text())
        except Exception: return {"providers":{"openai-compatible":asdict(ProviderConfig(models=["gpt-4o-mini"]))},"active_provider":"openai-compatible","active_model":"gpt-4o-mini","workspace":str(Path.cwd())}
        return data
    def save(self, data: dict):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd,tmp=tempfile.mkstemp(prefix=".cli_kml_", dir=str(self.path.parent)); os.close(fd)
        try:
            Path(tmp).write_text(json.dumps(data, indent=2))
            os.chmod(tmp,0o600); os.replace(tmp,self.path)
        finally:
            if os.path.exists(tmp): os.unlink(tmp)
    def public(self):
        d=self.load(); providers={}
        for name,p in d.get("providers",{}).items():
            providers[name]={"base_url":p.get("base_url",DEFAULT_BASE_URL),"models":p.get("models",[]),"has_api_key":bool(p.get("api_key"))}
        return {"providers":providers,"active_provider":d.get("active_provider"),"active_model":d.get("active_model"),"workspace":d.get("workspace")}

def normalize_base_url(base_url: str) -> str:
    u=base_url.strip().rstrip('/')
    if not u: raise ValueError("Base URL is required")
    if u.endswith('/chat/completions'): u=u[:-len('/chat/completions')]
    if not u.endswith('/v1'): u += '/v1'
    return u
