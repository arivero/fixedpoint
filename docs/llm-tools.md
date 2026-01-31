# LLM tool integration notes

This repo is designed so multiple LLM “entrypoints” can work on the same filesystem-based state.

## Copilot in the editor

- `AGENTS.md` is the canonical operating policy.
- `.github/copilot-instructions.md` provides a short pointer for Copilot.
- Skills live under `skills/` and are mirrored into `.github/skills`, `.claude/skills`, `.codex/skills`.

## Codex CLI / Claude Code

- `CLAUDE.md` points to `AGENTS.md` for persistent context.
- The skill mirrors allow agent runners that look for `.claude/skills` or `.codex/skills` to find the same procedures.

## GitHub Actions (agentic)

Some optional workflows (not all included by default) may call an LLM backend:
- idea-miner: `python tools/townctl.py mine-ideas`
- writer: `python tools/townctl.py draft-post`
- collector: `python -m town.collector`

Configure via repo variables + secrets:
- `vars.TOWN_LLM_BACKEND`: `openai` or `anthropic`
- `vars.TOWN_LLM_MODEL`: model id (backend-specific)
- `secrets.OPENAI_API_KEY` and/or `secrets.ANTHROPIC_API_KEY`

The LLM integration is intentionally thin so you can swap:
- GitHub-hosted models (Copilot/Models),
- OpenAI/Anthropic direct,
- or local tools, as long as they output the same plain-text artifacts.

## Adding new sources

- PDFs/scans: ingest as documents (`doc_*`) using the librarian pipeline.
- Emails or collaborator notes: ingest as `reference-only` documents (metadata + short quotes) or keep full content under `vault/private/`.
- LLM conversation dumps: store as documents with clear provenance in `doc.md` (and treat them as owned if you own the conversation transcript).
