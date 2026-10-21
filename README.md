# DivineGuard Gray Fox AI

A server-side Python integration starter with a common `generate()` interface for Anthropic Messages and OpenAI Responses. It includes a CLI, bounded input/output, explicit model selection, 30-second SDK timeouts, disabled automatic retries, sanitized failures and mock-based tests.

## Setup and use

Complete development setup below. `requirements.lock.txt` pins the tested SDK environment; install it with `python -m pip install -r requirements.lock.txt` for runtime-only use. `requirements.txt` records supported dependency ranges for future deliberate upgrades.

```sh
cp .env.example .env
# Edit .env locally: choose a provider, its API key and a model enabled in that account.
printf 'Explain the difference between an RFI and an RFP.' | python -m grayfox --provider anthropic
printf 'Draft a short opportunity-review checklist.' | python -m grayfox --provider openai
```

The CLI loads `.env` without overriding existing environment values. Library consumers must load their own environment. Model names are deliberately blank: the model from an earlier conversation was not verified for this account. Select a valid model from your provider dashboard. A ChatGPT or Claude subscription does not establish API credentials or API billing access.

```python
from grayfox.service import generate
text = generate('Summarize these non-sensitive requirements.', provider='openai', max_tokens=512)
```

## Behavior and privacy

`AI_PROVIDER` selects `anthropic` (default) or `openai`. The selected provider requires its `*_API_KEY` and `*_MODEL`; the other provider is optional. Prompts must contain 1-12000 characters; output limits must be integers from 1 to 2048. Anthropic text blocks are combined; non-text blocks are ignored. OpenAI requests use `store=False`. Provider-side retention policies still apply. There is no automatic provider fallback: it could disclose data to an unexpected service or incur another charge.

Exceptions do not expose raw provider response bodies. The code does not log prompts or keys. Never pass sensitive procurement or customer data without checking authorization and provider data terms. A model answer is draft assistance, not an official procurement source or verified qualification.

## Verification and limitations

Unit tests use injected clients and HTTP mock transports; no API keys or paid calls are needed. They verify request shape, text extraction, empty responses, validation and error sanitization. Live model access and provider billing are not verified. The CLI is not a public API server and has no authentication, tenant authorization, quotas, billing, durable history or streaming.

Before exposing it through SaaS: build an authenticated backend, derive tenant identity from verified tokens, enforce per-user spend limits, load keys server-side from a secret manager and test live calls using approved non-sensitive prompts. Add provider-specific metrics without logging secrets.

Official API references: [Anthropic Python SDK](https://platform.claude.com/docs/en/api/sdks/python), [OpenAI Python SDK](https://github.com/openai/openai-python).

## Repository family

| Repository | Responsibility |
| --- | --- |
| [GovCon Pulse](https://github.com/Mrfrazier14/divineguard-govcon-pulse) | Local opportunity tracking and evidence links |
| [Gray Fox AI](https://github.com/Mrfrazier14/divineguard-gray-fox-ai) | Server-side Anthropic and OpenAI adapters |
| [SaaS Platform](https://github.com/Mrfrazier14/divineguard-saas-platform) | Shared AWS identity, storage and runtime foundation |

## Development

Python 3.11+ is required. Each repository has its own environment; run commands from its root.

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
```

GitHub Actions runs tests on Python 3.11 and 3.13. `.env`, local databases, virtual environments and AWS configuration are ignored. `.env.example` contains placeholders only. Never commit keys, credentials, customer data or bid evidence containing private information.

Read [architecture](docs/ARCHITECTURE.md) for the future integration boundary. These are new starter implementations; they do not migrate the earlier desktop application or hosted pilot. No production readiness, live billing, bid submission or deployed AWS service is implied.
