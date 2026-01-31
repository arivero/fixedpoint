---
id: proj_20260201_9c3a1f2b
title: "Implement issue-driven agent workflows"
created: 2026-02-01
updated: 2026-02-01
status: backlog  # backlog | active | paused | done
tags: [automation, github-actions]
idea_ids: []
issues: []
---

Goal:
- Add the missing issue/comment-driven GitHub Actions workflows (slash-command router + per-command runners).
- Make the workflow UX “GitHub-native” (issue templates, clear prompts, predictable outputs).

Notes:
- Current state: only scheduled maintenance is active (`town-maintenance`).

TODOs (missing workflows):
- Issue-driven (slash commands)
  - `town-router` (issue_comment): parse `/librarian`, `/mine-ideas`, `/collect`, `/draft-post`, `/evaluate`, `/new-project`, `/queue-run`, `/lint`, `/index`
  - `town-librarian` (workflow_call): run `python tools/townctl.py ingest ...` using the existing queue request templates
  - `town-idea-mining` (workflow_call): run `python tools/townctl.py mine-ideas ...` and attach results / summarize into the issue
  - `town-collector` (workflow_call): run `python tools/townctl.py collect ...` for new docs; enforce licensing guardrails
  - `town-writer` (workflow_call): run `python tools/townctl.py blog-draft ...` and open/attach draft post changes
  - `town-evaluator` (workflow_call): run `python tools/townctl.py evaluate ...` and post a structured report back to the issue
  - `town-project-compose` (workflow_call): scaffold project from idea IDs (or update existing) via `python tools/townctl.py scaffold ...`
- Queue-driven
  - `town-queue-processor` (schedule + workflow_dispatch): process items under `queue/` deterministically (no DB)
- Planned/optional (still missing)
  - GitHub Issue Forms: add `.github/ISSUE_TEMPLATE/*` for librarian/publication requests (mirror the `queue/*/request-template.md` fields)
  - “Skills mirroring” (if desired): copy `skills/*/SKILL.md` into `.github/skills/` for GitHub-native discovery
  - Artifact publishing: upload rendered reports/diffs as workflow artifacts (avoid committing large logs)
  - Permissions hardening: least-privilege `permissions:` per workflow + fork/PR restrictions

Deliverables:
- Workflows in `.github/workflows/` that:
  - trigger on issue events and/or issue comments (slash-commands)
  - run the corresponding `python tools/townctl.py ...` commands
  - post results back to the issue (and commit changes sequentially)
  - are safe-by-default (explicit allowlist of commands, no arbitrary shell)
  - respect repo policy (`AGENTS.md`), especially licensing constraints

Plan:
- Start with a single `issue_comment` router workflow.
- Add per-command parsing + safety checks.
- Add concurrency to serialize commits.
- Add minimal Issue Forms so the UX is “standard GitHub”.

References:
- See `docs/commands.md` and `docs/architecture.md`
