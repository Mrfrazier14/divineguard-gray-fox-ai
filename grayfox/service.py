import os

class ConfigurationError(ValueError):
    pass

class ProviderError(RuntimeError):
    pass

def generate(prompt, provider=None, client=None, environ=None, max_tokens=512):
    env = os.environ if environ is None else environ
    provider = provider or env.get('AI_PROVIDER', 'anthropic')
    if provider not in ('anthropic', 'openai', 'openrouter'):
        raise ConfigurationError('AI_PROVIDER must be anthropic, openai or openrouter')
    if not isinstance(prompt, str) or not prompt.strip() or len(prompt) > 12000:
        raise ValueError('Prompt must contain 1-12000 characters')
    if type(max_tokens) is not int or not 1 <= max_tokens <= 2048:
        raise ValueError('max_tokens must be an integer between 1 and 2048')
    prefix = provider.upper()
    model = env.get(f'{prefix}_MODEL', '').strip()
    if not model:
        raise ConfigurationError(f'Set {prefix}_MODEL to a model enabled in your account')
    key = env.get(f'{prefix}_API_KEY', '').strip()
    if client is None and not key:
        raise ConfigurationError(f'Set {prefix}_API_KEY locally')
    try:
        if provider == 'anthropic':
            if client is None:
                from anthropic import Anthropic
                with Anthropic(api_key=key, timeout=30.0, max_retries=0) as sdk:
                    return generate(prompt, provider, sdk, env, max_tokens)
            response = client.messages.create(model=model, max_tokens=max_tokens,
                messages=[{'role': 'user', 'content': prompt}])
            text = ''.join(block.text for block in response.content if block.type == 'text')
        elif provider == 'openrouter':
            if client is None:
                from openai import OpenAI
                with OpenAI(api_key=key, base_url='https://openrouter.ai/api/v1', timeout=30.0, max_retries=0) as sdk:
                    return generate(prompt, provider, sdk, env, max_tokens)
            response = client.chat.completions.create(model=model, messages=[{'role':'user','content':prompt}], max_tokens=max_tokens, extra_body={'provider':{'allow_fallbacks':False}})
            text = response.choices[0].message.content
        else:
            if client is None:
                from openai import OpenAI
                with OpenAI(api_key=key, timeout=30.0, max_retries=0) as sdk:
                    return generate(prompt, provider, sdk, env, max_tokens)
            response = client.responses.create(model=model, input=prompt,
                max_output_tokens=max_tokens, store=False)
            text = response.output_text
        if not text or not text.strip():
            raise ProviderError('Provider returned no text')
        return text
    except Exception:
        # SDK exception bodies may contain sensitive request details.
        raise ProviderError('AI request failed; check account access, quota and model configuration') from None
