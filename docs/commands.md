# Slash commands (issue comments)

These commands trigger GitHub Actions workflows (and/or optional gh-aw workflows).

## Librarian / ingestion

- `/librarian`
  - Runs `town-librarian.yml`
  - Downloads and ingests a document based on the librarian issue form.

## Idea mining

- `/mine-ideas <doc_id>`
  - Runs `town-idea-miner.yml`
  - Uses an LLM backend to create `ideas/*.md` from an owned transcript.

## Project scaffolding

- `/new-project <title>`
  - Runs `town-project.yml`
  - Creates `projects/<proj_id>/project.md` and links it to the issue.

## Publication workflow

- `/collect`
  - Runs `town-collector.yml`
  - Suggests idea/doc IDs and an outline (comment only).

- `/draft-post [idea_ids...] [doc_ids...]`
  - Runs `town-writer.yml`
  - Drafts a blog post into `docs/_posts/`.

- `/evaluate docs/_posts/YYYY-MM-DD-slug.md`
  - Runs `town-evaluator.yml`
  - Performs deterministic checks and posts findings.

Notes:
