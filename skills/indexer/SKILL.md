# Indexing + export skill

Goal
- Keep all cross-references and catalog tables up to date.

Inputs
- The repository filesystem.

Outputs
- `catalog/documents.*`, `catalog/ideas.*`, `catalog/projects.*`, `catalog/xref.yml`
- `catalog/kanban.md`, `catalog/unused-ideas.md`
- Exported pages: `docs/ideas.md`, `docs/documents.md`, `docs/projects.md`, `docs/kanban.md`

Procedure
- `python tools/townctl.py index`
- `python tools/townctl.py export-site`
- `python tools/townctl.py lint`

Guardrails
- Generated files should be treated as build artifacts; don’t hand-edit them.
