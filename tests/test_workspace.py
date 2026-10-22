import json, tempfile, threading, unittest
from http.client import HTTPConnection
from unittest.mock import patch
try:
 from grayfox import workspace as w
except ModuleNotFoundError as error:
 if error.name == 'pulse': raise unittest.SkipTest('Install GovCon Pulse to test combined workspace')
 raise
class WorkspaceTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.db=patch.object(w,'DB',self.tmp.name+'/pulse.db');self.db.start()
  self.server=w.HTTPServer(('127.0.0.1',0),w.Handler);self.thread=threading.Thread(target=self.server.serve_forever);self.thread.start();self.port=self.server.server_port
 def tearDown(self):
  self.server.shutdown();self.thread.join();self.server.server_close();self.db.stop();self.tmp.cleanup()
 def post(self,path,data,origin=None):
  c=HTTPConnection('127.0.0.1',self.port);c.request('POST',path,json.dumps(data),{'Content-Type':'application/json','Origin':origin or f'http://127.0.0.1:{self.port}','X-Workspace-Token':w.TOKEN});r=c.getresponse();status=r.status;body=json.loads(r.read());c.close();return status,body
 def test_rejects_foreign_origin(self):
  status,_=self.post('/api/opportunities',{'action':'add','title':'x','url':'https://sam.gov/'},'https://example.com');self.assertEqual(status,403)
 def test_persistence_and_evidence_gate(self):
  status,data=self.post('/api/opportunities',{'action':'add','title':'Test only','url':'https://sam.gov/'});self.assertEqual(status,200)
  key=data['records'][0]['id'];status,_=self.post('/api/opportunities',{'action':'stage','id':key,'stage':'Awarded'});self.assertEqual(status,400)
  status,data=self.post('/api/opportunities',{'action':'stage','id':key,'stage':'Watching'});self.assertEqual(data['records'][0]['stage'],'Watching')
 def test_provider_selection_and_no_key_storage(self):
  with patch.object(w,'generate',return_value='Mock response') as generate:
   status,data=self.post('/api/generate',{'provider':'openai','key':'test-key-only','model':'test-model','messages':[{'role':'user','content':'Test'}]});self.assertEqual(status,200);self.assertEqual(data['text'],'Mock response');self.assertEqual(generate.call_args.kwargs['provider'],'openai')
   self.assertFalse((__import__('pathlib').Path(self.tmp.name)/'pulse.db').exists())
if __name__=='__main__': unittest.main()
