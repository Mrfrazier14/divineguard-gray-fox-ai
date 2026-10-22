import unittest
from types import SimpleNamespace as NS
from unittest.mock import Mock
from grayfox.service import generate, ConfigurationError, ProviderError

class ProviderTests(unittest.TestCase):
    def test_anthropic_text_blocks(self):
        client = Mock()
        client.messages.create.return_value = NS(content=[NS(type='thinking'), NS(type='text', text='Hello')])
        self.assertEqual(generate('hi', 'anthropic', client, {'ANTHROPIC_MODEL':'test'}), 'Hello')
        client.messages.create.assert_called_once_with(model='test', max_tokens=512, messages=[{'role':'user','content':'hi'}])

    def test_openai_no_storage(self):
        client = Mock()
        client.responses.create.return_value = NS(output_text='Hello')
        self.assertEqual(generate('hi', 'openai', client, {'OPENAI_MODEL':'test'}), 'Hello')
        client.responses.create.assert_called_once_with(model='test', input='hi', max_output_tokens=512, store=False)

    def test_openrouter_explicit_route(self):
        client = Mock()
        client.chat.completions.create.return_value = NS(choices=[NS(message=NS(content='Router response'))])
        self.assertEqual(generate('hi','openrouter',client,{'OPENROUTER_MODEL':'test-model'}),'Router response')
        self.assertEqual(client.chat.completions.create.call_args.kwargs['extra_body'],{'provider':{'allow_fallbacks':False}})
        client.responses.create.assert_not_called()

    def test_configuration(self):
        with self.assertRaises(ConfigurationError):
            generate('hi', 'unknown', environ={})
        with self.assertRaises(ConfigurationError):
            generate('hi', environ={})
        with self.assertRaises(ConfigurationError):
            generate('hi', 'openai', environ={'OPENAI_MODEL':'test'})

    def test_bounds_prevent_calls(self):
        client = Mock()
        for prompt, tokens in [('',512), ('x'*12001,512), ('hi',0), ('hi',2049), ('hi',True)]:
            with self.assertRaises(ValueError):
                generate(prompt, 'openai', client, {'OPENAI_MODEL':'test'},tokens)
        client.responses.create.assert_not_called()

    def test_sanitized_failure(self):
        client = Mock()
        client.responses.create.side_effect = RuntimeError('SECRET_KEY prompt')
        with self.assertRaises(ProviderError) as error:
            generate('hi', 'openai', client, {'OPENAI_MODEL':'test'})
        self.assertNotIn('SECRET_KEY', str(error.exception))
        self.assertTrue(error.exception.__suppress_context__)

    def test_empty_output(self):
        client = Mock()
        client.responses.create.return_value = NS(output_text='')
        with self.assertRaises(ProviderError):
            generate('hi', 'openai', client, {'OPENAI_MODEL':'test'})
