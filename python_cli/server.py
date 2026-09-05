from __future__ import annotations
import asyncio, time, os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from .config import ConfigManager, normalize_base_url
from .project.manager import ProjectManager
from .permissions import PermissionManager
from .providers.openai_compatible import OpenAICompatibleProvider
from .tools import ReadFile,WriteFile,EditFile,Grep,Glob,Tree,Bash

BASE=Path(__file__).resolve().parent.parent; WEB=BASE/'web'; app=FastAPI(title='CLI-KML')
app.mount('/static',StaticFiles(directory=WEB),name='static'); cfg=ConfigManager(); events=[]; current_agent=None; permission_waiters={}
class ConfigIn(BaseModel): provider:str='openai-compatible'; api_key:str|None=None; base_url:str|None=None; model:str|None=None; workspace:str|None=None
class ProjectIn(BaseModel): workspace:str
class ChatIn(BaseModel): message:str
class PermissionIn(BaseModel): tool:str; decision:str; request_id:str|None=None

def config_data():return cfg.load()
def make_runtime():
    d=config_data(); ws=d.get('workspace') or str(Path.cwd()); pm=ProjectManager(ws); p=d.get('providers',{}).get(d.get('active_provider','openai-compatible'),{}); provider=OpenAICompatibleProvider(p.get('base_url','https://api.openai.com/v1'),p.get('api_key',''),d.get('active_model','gpt-4o-mini'))
    return pm,provider

def emit(e): events.append({"ts":time.time(),**e}); del events[:-300]
@app.get('/')
async def root():return FileResponse(WEB/'index.html')
@app.get('/api/status')
async def status():
    d=config_data(); return {"connected":bool(d.get('providers',{}).get(d.get('active_provider'),{}).get('api_key')),"model":d.get('active_model'),"workspace":d.get('workspace')}
@app.get('/api/config')
async def get_config():return cfg.public()
@app.post('/api/config')
async def save_config(x:ConfigIn):
    d=cfg.load(); name=x.provider; p=d.setdefault('providers',{}).setdefault(name,{"models":[]})
    if x.api_key is not None: p['api_key']=x.api_key
    if x.base_url is not None: p['base_url']=normalize_base_url(x.base_url)
    if x.model is not None:
        d['active_model']=x.model; models=p.setdefault('models',[])
        ids=[m.get('id') if isinstance(m,dict) else m for m in models]
        if x.model not in ids: models.append(x.model)
    d['active_provider']=name
    if x.workspace is not None: d['workspace']=str(Path(x.workspace).expanduser().resolve())
    cfg.save(d); return cfg.public()
@app.post('/api/test-connection')
async def test_connection():
    pm,p=make_runtime(); start=time.perf_counter()
    if not p.key: raise HTTPException(400,'API key is not configured')
    try: msg=await p.test(); return {"success":True,"model":p.model,"latency_ms":round((time.perf_counter()-start)*1000),"response":msg.get('content','')}
    except Exception as e: raise HTTPException(502,str(e))
@app.get('/api/project/tree')
async def project_tree():pm,_=make_runtime(); return {"workspace":str(pm.root),"tree":pm.tree()}
@app.get('/api/project/file')
async def project_file(path:str,start_line:int=1,end_line:int=1000):
    pm,_=make_runtime(); r=await ReadFile(pm).execute({"path":path,"start_line":start_line,"end_line":end_line})
    if not r['success']: raise HTTPException(404,r['error']); return r
    return r
@app.post('/api/project')
async def project(x:ProjectIn):
    d=cfg.load(); d['workspace']=str(Path(x.workspace).expanduser().resolve()); cfg.save(d); return {"workspace":d['workspace']}
@app.get('/api/activity')
async def activity():return events
@app.post('/api/stop')
async def stop():
    global current_agent
    if current_agent: current_agent.stop()
    return {"stopped":True}
@app.post('/api/tools/permission')
async def permission(x:PermissionIn):
    if x.decision=='always':
        # Tool-level persistence for this process; safe default is still deny for new sessions.
        for w in getattr(current_agent,'tools',{}).values():
            if w.name==x.tool: current_agent.permissions.grant_always(x.tool)
    key=x.request_id or x.tool; waiter=permission_waiters.pop(key,None)
    if waiter and not waiter.done(): waiter.set_result(x.decision)
    emit({"type":"permission_granted" if x.decision!='deny' else 'permission_denied',"tool":x.tool})
    return {"ok":True}
@app.post('/api/chat')
async def chat(x:ChatIn):
    global current_agent
    pm,p=make_runtime(); perms=PermissionManager()
    async def permission_hook(tool,args):
        key=f"{tool}:{time.time_ns()}"; fut=asyncio.get_running_loop().create_future(); permission_waiters[key]=fut
        emit({"type":"permission_required","tool":tool,"args":args,"request_id":key,"mode":"ASK"})
        try: return await asyncio.wait_for(fut, timeout=300)
        except asyncio.TimeoutError: permission_waiters.pop(key,None); return "deny"
    async def run():
        global current_agent
        tools=[ReadFile(pm),WriteFile(pm),EditFile(pm),Grep(pm),Glob(pm),Tree(pm),Bash(pm)]
        current_agent=__import__('python_cli.agent',fromlist=['AgentEngine']).AgentEngine(p,tools,perms,pm,emit,permission_hook)
        result=await current_agent.run(x.message); return result
    result=await run(); return {"answer":result}
