# AGENTS.md (repository rules for agents)

This file defines how automated or interactive agents must operate in this repository.

## Operating principles

1) No databases.
   - All state is stored as Markdown/YAML/TSV files in the repository.
   - If you need an “index”, regenerate it deterministically from frontmatter.

2) GitHub issues are the work surface; commits are the record.
   - Use issues to discuss, review, and decide.
   - Use commits to apply accepted changes.
   - Prefer small, reviewable commits with clear messages.

3) Avoid merge conflicts by serialising automation.
   - GitHub Actions workflows in this repo use a shared concurrency group.
   - Automated commits are sequential.

4) Respect licensing and provenance.
   - OWNED material: fulltext transcription is allowed in-repo.
   - REFERENCE-ONLY material: do **not** commit fulltext transcriptions. Commit metadata, citations, and short quotes only.

## What goes where

Owned documents:
- `vault/owned/<doc_id>/doc.md`      (metadata + notes)
- `vault/owned/<doc_id>/transcript.md` (full transcription in Markdown, owned only)
- `vault/raw/<doc_id>/*`            (original PDFs, images, dumps)

Reference-only documents:
- `vault/references/<doc_id>/doc.md`    (metadata + your own notes)
- NO fulltext in-repo. If needed, store locally under `vault/private/` (gitignored) or as workflow artifacts.

Atomic ideas:
- `ideas/<idea_id>.md` (each idea is one file, designed to be referenced/reused)

Projects:
- `projects/<proj_id>/project.md`
- `projects/<proj_id>/notebook.md` (optional: work log)

Lab notes:
- `lab/notebooks/<nb_id>.md` (single-agent scratchpad)
- `lab/blackboards/<bb_id>.md` (multi-agent discussion)

Publishing:
- blog posts live in `docs/_posts/YYYY-MM-DD-<slug>.md`
- posts must cite idea IDs and document IDs.

Indexes (generated):
- `catalog/documents.*`
- `catalog/ideas.*`
- `catalog/projects.*`
- `catalog/xref.*`

## ID policy

IDs must be stable and filesystem-safe.

Accepted forms:
- Documents:  `doc_YYYYMMDD_<8hex>`
- Ideas:      `idea_YYYYMMDD_<8hex>`
- Projects:   `proj_YYYYMMDD_<8hex>`
- Notebooks:  `nb_YYYYMMDD_<8hex>`
- Blackboards:`bb_YYYYMMDD_<8hex>`

Use `python tools/townctl.py id <kind>` to generate IDs.

## Frontmatter rules

All first-class objects MUST start with YAML frontmatter containing:
- `id`
- `title`
- `created`
- `updated`
- `status` (for ideas/projects/notebooks/blackboards)

Documents MUST include:
- `license.status` in {`owned`, `reference-only`}
- `identifiers` block when known (doi/arxiv/urn/url)

Ideas MUST include:
- `sources`: list of `{doc, locator, quote?}`
- `status`: `seed` | `validated` | `used` | `published`

Projects MUST include:
- `idea_ids`: list of idea IDs
- `status`: `backlog` | `active` | `paused` | `done`

## Copyright / fair-use guardrails (non-owned sources)

If `license.status: reference-only`:
- Do not commit full text.
- Do not commit long excerpts.
- Use short quotes only when necessary and keep them minimal.
- Prefer paraphrase + citation (DOI/URL + locator).

## Automation entrypoints

Deterministic tooling:
- `python tools/townctl.py lint`          (validate frontmatter + links)
- `python tools/townctl.py index`         (regenerate catalog tables)
- `python tools/townctl.py export-site`   (update site pages from catalog)

Optional agentic workflows (gh-aw):
- `.github/workflows/town-*.md` are sources for GitHub Next Agentic Workflows, compiled to `*.lock.yml`.

## Commit rules for automation

Automated commits must:
- include `[skip-town]` in the commit message when the commit is purely mechanical re-indexing, to avoid loops.
- avoid rewriting history.
- keep changes scoped (don’t reformat unrelated files).

## Tooling assumptions

In GitHub Actions:
- Python 3.11+
- `pip install -r tools/requirements.txt`
- Optional: pandoc/poppler for PDF conversion (if installed)

Locally:
- You may use Copilot/Codex/Claude Code; skills are provided under `skills/` and mirrored for compatibility.
