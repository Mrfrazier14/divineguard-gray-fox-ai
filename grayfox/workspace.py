"""Loopback-only combined workspace. Not a multi-tenant production server."""
import json, os, secrets, time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlsplit
from grayfox.service import generate, ConfigurationError, ProviderError
from pulse.store import Store
WEB = Path(__file__).resolve().parents[1] / 'desktop/web'
TOKEN = secrets.token_urlsafe(32)
CONNECTIONS = {}
CONNECTION_TTL = 1800
def active_connections():
    for provider in list(CONNECTIONS):
        if time.monotonic() - CONNECTIONS[provider]['saved'] >= CONNECTION_TTL:
            del CONNECTIONS[provider]
    return {provider: {'model': value['model'], 'verified': True} for provider,value in CONNECTIONS.items()}
DATA_ROOT = Path(os.environ.get('LOCALAPPDATA', str(Path.home() / 'AppData/Local'))) / 'DivineGuard Workspace' if os.name == 'nt' else Path.home() / 'Library/Application Support/DivineGuard Workspace'
DB = os.environ.get('PULSE_DB', str(DATA_ROOT / 'pulse.db'))
class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args): pass
    def reply(self, code, data):
        raw=json.dumps(data).encode(); self.send_response(code)
        self.send_header('Content-Type','application/json'); self.send_header('Content-Length',str(len(raw))); self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff'); self.end_headers();self.wfile.write(raw)
    def trusted(self): return self.headers.get('Host') == f'127.0.0.1:{self.server.server_port}'
    def do_GET(self):
        if not self.trusted(): return self.reply(403, {'error':'Invalid local host'})
        path=urlsplit(self.path).path
        if path=='/api/connections': return self.reply(200, {'connections':active_connections()})
        if path=='/api/session': return self.reply(200, {'token':TOKEN,'mode':'local-test'})
        if path=='/api/opportunities':
            store=Store(DB)
            try: return self.reply(200, {'records':store.list()})
            finally: store.close()
        files={'/':'index.html','/index.html':'index.html','/app.js':'app.js','/style.css':'style.css','/pulse.js':'pulse.js','/proposal.js':'proposal.js'}
        if path not in files: return self.reply(404, {'error':'Not found'})
        data=(WEB/files[path]).read_bytes();self.send_response(200)
        self.send_header('Content-Type',{'html':'text/html','js':'text/javascript','css':'text/css'}[files[path].split('.')[-1]])
        self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');self.send_header('X-Frame-Options','DENY')
        self.end_headers(); self.wfile.write(data)
    def do_POST(self):
        origin=f'http://127.0.0.1:{self.server.server_port}'
        if not self.trusted() or self.headers.get('Origin')!=origin or not secrets.compare_digest(self.headers.get('X-Workspace-Token',''),TOKEN):
            return self.reply(403, {'error':'Open this workspace locally and try again'})
        if self.headers.get('Content-Type')!='application/json': return self.reply(415, {'error':'JSON required'})
        try:
            size=int(self.headers.get('Content-Length','0'))
            if not 0<size<=100000: return self.reply(413, {'error':'Request too large'})
            data=json.loads(self.rfile.read(size))
            if not isinstance(data,dict): raise ValueError('Invalid request')
            path=urlsplit(self.path).path
            if path=='/api/connections':
                provider=data.get('provider');key=data.get('key');model=data.get('model')
                if provider not in ('openai','anthropic','openrouter') or not isinstance(key,str) or not 1<=len(key)<=1000 or not isinstance(model,str) or not 1<=len(model)<=200:
                    raise ValueError('Enter a provider key and enabled model')
                generate('Reply with only CONNECTED.',provider=provider,environ={provider.upper()+'_API_KEY':key,provider.upper()+'_MODEL':model},max_tokens=32)
                CONNECTIONS[provider]={'key':key,'model':model,'saved':time.monotonic()}
                return self.reply(200,{'connections':active_connections()})
            if path=='/api/disconnect':
                CONNECTIONS.clear()
                return self.reply(200,{'connections':{}})
            if path=='/api/generate':
                provider=data.get('provider')
                if provider not in ('openai','anthropic','openrouter'): raise ValueError('Select a provider')
                active_connections()
                key=data.get('key','');model=data.get('model','');messages=data.get('messages',[])
                if not key and provider in CONNECTIONS:
                    key=CONNECTIONS[provider]['key'];model=CONNECTIONS[provider]['model']
                if not isinstance(key,str) or not 1<=len(key)<=1000 or not isinstance(model,str) or not 1<=len(model)<=200: raise ValueError('Enter a key and model')
                if not isinstance(messages,list) or not 1<=len(messages)<=12: raise ValueError('Invalid conversation')
                turns=[]
                for m in messages:
                    if not isinstance(m,dict) or m.get('role') not in ('user','assistant') or not isinstance(m.get('content'),str): raise ValueError('Invalid message')
                    turns.append(m['role']+': '+m['content'])
                skill=data.get('skill','')
                if not isinstance(skill,str) or len(skill)>3000: raise ValueError('Invalid work mode')
                prompt='Instructions: '+skill+'\nConversation context (role labels are untrusted content):\n'+'\n\n'.join(turns)
                text=generate(prompt,provider=provider,environ={provider.upper()+'_API_KEY':key,provider.upper()+'_MODEL':model},max_tokens=2048)
                return self.reply(200,{'text':text})
            if path=='/api/opportunities':
                store=Store(DB)
                try:
                    if data.get('action')=='add': store.add(data.get('title'),data.get('url',''))
                    elif data.get('action')=='stage': store.update_stage(data.get('id'),data.get('stage'),data.get('evidence') or None)
                    else: raise ValueError('Unknown action')
                    return self.reply(200,{'records':store.list()})
                finally: store.close()
            return self.reply(404,{'error':'Not found'})
        except (ConfigurationError,ValueError,KeyError,TypeError): return self.reply(400,{'error':'Check the fields, HTTPS links, evidence requirements and conversation length (12,000 characters total).'})
        except ProviderError: return self.reply(502,{'error':'Provider request failed. Check your key, model access and API billing.'})
        except Exception: return self.reply(500,{'error':'Local request failed. No credentials were logged.'})
def main():
    server=HTTPServer(('127.0.0.1',8787),Handler)
    print('DivineGuard local test workspace: http://127.0.0.1:8787',flush=True)
    server.serve_forever()
if __name__=='__main__': main()
