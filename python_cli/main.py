import sys
from pathlib import Path
import uvicorn
if __name__=='__main__':
    sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
    print('CLI-KML starting...')
    print('Server running at: http://127.0.0.1:8787')
    uvicorn.run('python_cli.server:app',host='127.0.0.1',port=8787)
