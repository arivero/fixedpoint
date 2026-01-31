# Agentic Fixedpoint

This repository is a file-based research system that:
- stores your owned notes and PDFs as Markdown + raw originals,
- stores *references* to non-owned sources (and optionally keeps full transcriptions out-of-repo),
- extracts and tracks **atomic ideas** as first-class objects,
- groups ideas into **projects** and **publication issues**,
- publishes mature results as a GitHub Pages blog.

Coordination is GitHub-native: issues are the work surface; commits are the durable record; GitHub Pages is the publishing surface.

## Key design constraints

- No databases. Everything is plain text (Markdown/YAML/TSV), committed to Git.
- Every object (document, idea, project, notebook, blackboard, blog post) has a stable ID and lives in a predictable folder.
- “Owned” and “reference-only” materials are separated so you can keep non-owned fulltext out of the repository.
- Indexes are generated deterministically from frontmatter; nothing is “hidden state”.

## Automation

By default, this repo has no scheduled automation enabled.

- GitHub Pages can build the Jekyll site from `docs/` ("Pages from branch").
- Optional: add GitHub Actions workflows to run `townctl.py lint/index/export-site` on push or on a schedule.

Optional (modern agentic layer):
- `.github/workflows/*.md` are **GitHub Next Agentic Workflows** sources (gh-aw). They are designed to be compiled into `*.lock.yml` workflows and run as agents on issues and comments.

## Repository map (high level)

- `vault/`: documents (owned and references) + raw PDFs.
- `ideas/`: atomic idea cards.
- `projects/`: project proposals and work-in-progress.
- `lab/`: notebooks (private scratchpads) and blackboards (shared discussions).
- `catalog/`: generated indexes and cross-reference tables (plain text).
- `queue/`: file-based request queues (librarian + publication).
- `docs/`: GitHub Pages blog (Jekyll) + repository documentation.

See `AGENTS.md` for the rules agents must follow in this repo.

## Docs

- `docs/architecture.md` — object model and automation overview
- `docs/commands.md` — slash commands that trigger workflows
- `docs/labels.md` — recommended labels
- `docs/llm-tools.md` — Copilot / Codex CLI / Claude Code integration notes

## Quick start (local)

**Requirements:** Python 3.14+

1) Install tooling:
   - `python -m pip install -r tools/requirements.txt`

2) Ingest an owned PDF:
   - `python tools/townctl.py ingest --source path/to/file.pdf --license-status owned --title "My note" --url "https://..."`

3) Mine ideas (requires API key for OpenAI or Anthropic):
   - `export TOWN_LLM_BACKEND=openai`
   - `export OPENAI_API_KEY=...`
   - `python tools/townctl.py mine-ideas --doc-id doc_...`

4) Rebuild indexes and exported pages:
   - `python tools/townctl.py index`
   - `python tools/townctl.py export-site`
   - `python tools/townctl.py lint`
