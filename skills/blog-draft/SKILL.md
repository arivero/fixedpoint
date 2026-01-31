# Blog drafting skill

Goal
- Draft a Jekyll blog post in `docs/_posts/` from a publication issue + selected ideas/documents.

Inputs
- Issue title and body (or a local note).
- Optional explicit `idea_ids` and `doc_ids`.

Outputs
- `docs/_posts/YYYY-MM-DD-<slug>.md` with frontmatter:
  - `layout: post`
  - `idea_ids: [...]`
  - `doc_ids: [...]`

Procedure
1) Prepare an issue body file (or use automation that writes it).
2) Draft:
   - `python tools/townctl.py draft-post --issue-title "<title>" --issue-number 123 --issue-body-file issue_body.txt --idea-ids idea_... --doc-ids doc_...`
   This uses the configured LLM backend:
   - `TOWN_LLM_BACKEND=openai|anthropic`
   - `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`

3) Regenerate indexes + validate:
   - `python tools/townctl.py index`
   - `python tools/townctl.py export-site`
   - `python tools/townctl.py lint`

Guardrails
- No long verbatim excerpts from reference-only sources.
- Always cite idea IDs and doc IDs inline.
