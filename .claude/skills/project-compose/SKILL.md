# Project composition skill

Goal
- Combine atomic ideas into a project proposal and track it on the kanban.

Inputs
- A short project title.
- A list of idea IDs to include.

Outputs
- `projects/<proj_id>/project.md` with `idea_ids` populated.
- Optional notebook: `lab/notebooks/<nb_id>.md`
- Updated `catalog/kanban.md` and other indexes.

Procedure
1) Create a project skeleton:
   - `python tools/townctl.py new-project --title "<title>"`

2) Edit `projects/<proj_id>/project.md`:
   - Fill `idea_ids: [idea_..., ...]`
   - Set `status: backlog|active|paused|done`
   - Add tags and plan.

3) (Optional) Create a notebook:
   - `python tools/townctl.py new-notebook --title "<title> notebook" --project-id <proj_id>`

4) Regenerate indexes + validate:
   - `python tools/townctl.py index`
   - `python tools/townctl.py export-site`
   - `python tools/townctl.py lint`

Guardrails
- Projects should reference ideas, not duplicate idea text.
- Use issues for discussion; keep `project.md` as the durable plan.
