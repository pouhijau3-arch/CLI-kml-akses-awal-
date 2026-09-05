from pathlib import Path
DEFAULT_IGNORES={'.git','.venv','node_modules','__pycache__','build','dist','.env'}
def ignored(path: Path)->bool:
    n=path.name
    return n in DEFAULT_IGNORES or n.startswith('.env.') or n.endswith(('.pem','.key')) or n=='id_rsa'
