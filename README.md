# DivineGuard Gray Fox AI

Gray Fox AI is a DivineGuard IT Services LLC product initiative, founded and created by Aaron Frazier Jr.

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

## Unified Gray Fox AI desktop workspace

The macOS wrapper in `desktop/` presents one local conversation workspace with a provider selector for the OpenAI API (ChatGPT models) or Anthropic API (Claude models), original work modes for coding, code review, GovCon, business planning and creator work, local chat history, prompt drafts and backup export. Its gray canvas, charcoal sidebar and orange controls match the GovCon Pulse palette. Each request uses the selected provider's API key and an enabled model ID; the key is cleared from the form and is not written into the local workspace. ChatGPT and Claude subscriptions do not include API usage. The app sends up to 12 recent user/assistant messages for a turn, with a 2,048-token output ceiling.

This is a provider-connected assistant, not a copy of ChatGPT or Claude. It does not import their private tools, hidden instructions, account memory, subscriptions, browsing, or code-execution environments. The browser preview does not make provider requests. The current macOS shell has not been updated into a Windows build, and live API access still requires the owner's own provider credentials and billing.

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


## Combined local test workspace
Install this repository and `divineguard-govcon-pulse` into the same Python environment, plus the pinned provider SDK requirements. Run `python -m grayfox.workspace` and open http://127.0.0.1:8787. The browser uses the same Gray Fox interface with an opportunity panel backed by Pulse SQLite storage. Provider credentials are supplied for each request and are never written to storage or logs. Conversation history remains browser-local; opportunity records use the local Pulse database. The combined prompt is limited to 12,000 characters.

This loopback-only development workspace is not a production service. It has no customer accounts, tenant isolation, subscription billing, enforced per-customer spend limits or managed hosting. Do not expose it through a tunnel or public interface. The installed Mac app is not rebuilt by these source changes.

The local connection panel verifies a provider with one short API request and retains the verified key only in server memory for 30 minutes. Disconnect clears those connections. The proposal studio constructs a prompt from authorized company facts and solicitation text, flags unknown facts through its instructions, and exports the latest assistant response as an explicitly unreviewed Markdown draft. AI output still requires human validation; this is not an automatic compliance certification or bid submission tool.


## Provider connection link
Open http://127.0.0.1:8787/#connections in the running local workspace. OpenAI and Anthropic connect directly; OpenRouter is an optional third-party gateway for additional model IDs. Each connection requires that service's API key and an enabled model. No live provider is verified until the test succeeds. OpenRouter routes to an underlying model provider; its privacy and billing terms apply. The app does not fall back to another service; OpenRouter provider fallbacks are disabled. The OpenRouter option is supported in this local browser implementation, not the existing installed Mac binary.
