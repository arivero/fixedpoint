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
- Add the missing issue/comment-driven GitHub Actions workflows (librarian, idea-miner, collector, writer, evaluator).

Notes:
- TODO: These workflows are not implemented yet; only scheduled maintenance is currently active.

Deliverables:
- Workflows in `.github/workflows/` that:
  - trigger on issue events and/or issue comments (slash-commands)
  - run the corresponding `python tools/townctl.py ...` commands
  - post results back to the issue (and commit changes sequentially)

Plan:
- Start with a single `issue_comment` router workflow.
- Add per-command parsing + safety checks.
- Add concurrency to serialize commits.

References:
- See `docs/commands.md` and `docs/architecture.md`
