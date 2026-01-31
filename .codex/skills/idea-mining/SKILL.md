# Idea mining skill

Goal
- Extract reusable, ATOMIC ideas from an owned transcript into `ideas/*.md`.

Inputs
- Document id `doc_YYYYMMDD_xxxxxxxx` with `vault/owned/<doc_id>/transcript.md`.
- Optional max idea count.

Outputs
- New `ideas/idea_YYYYMMDD_xxxxxxxx.md` files with:
  - `sources` pointing to the doc id and a locator
  - short statements and tags
- Updated `catalog/*` and exported site pages.

Procedure
1) Run the miner:
   - `python tools/townctl.py mine-ideas --doc-id <doc_id> --max-ideas 12`
   This uses the configured LLM backend (OpenAI/Anthropic) via environment variables:
   - `TOWN_LLM_BACKEND=openai|anthropic`
   - `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`
   - optional: `TOWN_LLM_MODEL`

2) Regenerate indexes:
   - `python tools/townctl.py index`
   - `python tools/townctl.py export-site`

3) Validate:
   - `python tools/townctl.py lint`

Guardrails
- Do not invent claims; every idea must be grounded in the transcript.
- Keep each idea atomic (one claim/definition/theorem).
- For reference-only sources, do not include long quotes.
