import json
import unittest
import httpx
from anthropic import Anthropic
from openai import OpenAI
from grayfox.service import generate, ProviderError

class SDKContractTests(unittest.TestCase):
    def test_anthropic_sdk_http_contract(self):
        requests = []
        def respond(request):
            requests.append(request)
            return httpx.Response(200, json={'id':'msg_test','type':'message','role':'assistant','model':'test-model','content':[{'type':'text','text':'Anthropic answer'}],'stop_reason':'end_turn','stop_sequence':None,'usage':{'input_tokens':2,'output_tokens':3}})
        with Anthropic(api_key='mock-test-key',max_retries=0,http_client=httpx.Client(transport=httpx.MockTransport(respond))) as client:
            self.assertEqual(generate('hello','anthropic',client,{'ANTHROPIC_MODEL':'test-model'}),'Anthropic answer')
        self.assertEqual(requests[0].url.path, '/v1/messages')
        self.assertEqual(json.loads(requests[0].content)['messages'], [{'role':'user','content':'hello'}])

    def test_openai_sdk_http_contract(self):
        requests = []
        def respond(request):
            requests.append(request)
            return httpx.Response(200,json={'id':'resp_test','object':'response','created_at':0,'model':'test-model','status':'completed','output':[{'id':'msg_test','type':'message','role':'assistant','status':'completed','content':[{'type':'output_text','text':'OpenAI answer','annotations':[]}]}]})
        with OpenAI(api_key='mock-test-key',max_retries=0,http_client=httpx.Client(transport=httpx.MockTransport(respond))) as client:
            self.assertEqual(generate('hello','openai',client,{'OPENAI_MODEL':'test-model'}),'OpenAI answer')
        self.assertEqual(requests[0].url.path, '/v1/responses')
        self.assertIs(json.loads(requests[0].content)['store'],False)

    def test_provider_auth_failure_is_sanitized(self):
        def respond(request):
            return httpx.Response(401,json={'error':{'message':'sensitive-value','type':'authentication_error'}})
        with OpenAI(api_key='mock-test-key',max_retries=0,http_client=httpx.Client(transport=httpx.MockTransport(respond))) as client:
            with self.assertRaises(ProviderError) as error:
                generate('hello','openai',client,{'OPENAI_MODEL':'test-model'})
        self.assertNotIn('sensitive-value', str(error.exception))
