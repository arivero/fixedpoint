from __future__ import annotations

import argparse
from pathlib import Path

from .ids import new_id
from .ingest import ingest
from .indexer import run as run_indexer
from .export_site import run as run_export
from .linting import lint as run_lint
from .scaffold import new_idea, new_project, new_notebook, new_blackboard
from .idea_mining import mine_ideas
from .blog_draft import draft_post
from .archive import archive_markdown_as_document
from .queue import process_librarian_queue
from .issue import parse_issue_template

def repo_root_from_here() -> Path:
    # tools/town/cli.py -> repo root is three levels up
    return Path(__file__).resolve().parents[2]

def cmd_id(args: argparse.Namespace) -> int:
    print(new_id(args.kind))
    return 0

def cmd_ingest(args: argparse.Namespace) -> int:
    root = repo_root_from_here()
    info = ingest(
        root,
        Path(args.source),
        license_status=args.license_status,
        title=args.title,
        url=args.url,
        doi=args.doi,
        urn=args.urn,
        doc_id=args.doc_id,
        ingested_by=args.ingested_by,
    )
    for k, v in info.items():
        print(f"{k}: {v}")
    return 0

def cmd_lint(args: argparse.Namespace) -> int:
    root = repo_root_from_here()
    errs = run_lint(root)
    if errs:
        print("Lint errors:\n")
        for e in errs:
            print("- " + e)
        return 2
    print("OK")
    return 0

def cmd_index(args: argparse.Namespace) -> int:
    root = repo_root_from_here()
    run_indexer(root)
    print("catalog updated")
    return 0

def cmd_export_site(args: argparse.Namespace) -> int:
    root = repo_root_from_here()
    run_export(root)
    print("site pages updated")
    return 0

def cmd_new_idea(args: argparse.Namespace) -> int:
    root = repo_root_from_here()
    p = new_idea(root, title=args.title, doc_id=args.doc_id, locator=args.locator)
    print(str(p.relative_to(root)))
    return 0

def cmd_new_project(args: argparse.Namespace) -> int:
    root = repo_root_from_here()
    p = new_project(root, title=args.title)
    print(str(p.relative_to(root)))
    return 0

def cmd_new_notebook(args: argparse.Namespace) -> int:
    root = repo_root_from_here()
    p = new_notebook(root, title=args.title, project_id=args.project_id)
    print(str(p.relative_to(root)))
    return 0

def cmd_new_blackboard(args: argparse.Namespace) -> int:
    root = repo_root_from_here()
    p = new_blackboard(root, title=args.title, topic=args.topic)
    print(str(p.relative_to(root)))
    return 0

def cmd_mine_ideas(args: argparse.Namespace) -> int:
    root = repo_root_from_here()
    paths = mine_ideas(root, doc_id=args.doc_id, max_ideas=args.max_ideas)
    for p in paths:
        print(str(p.relative_to(root)))
    return 0

def cmd_draft_post(args: argparse.Namespace) -> int:
    root = repo_root_from_here()
    body = Path(args.issue_body_file).read_text(encoding="utf-8")
    out = draft_post(
        root,
        issue_title=args.issue_title,
        issue_body=body,
        issue_number=args.issue_number,
        idea_ids=args.idea_ids,
        doc_ids=args.doc_ids,
    )
    print(str(out.relative_to(root)))
    return 0

def cmd_parse_issue(args: argparse.Namespace) -> int:
    body = Path(args.issue_body_file).read_text(encoding="utf-8")
    fields = parse_issue_template(body)
    for k, v in fields.items():
        print(f"{k}: {v}")
    return 0

def cmd_archive_md(args: argparse.Namespace) -> int:
    root = repo_root_from_here()
    info = archive_markdown_as_document(
        root,
        source_md=Path(args.source_md),
        title=args.title,
        license_status=args.license_status,
        url=args.url,
        doi=args.doi,
        urn=args.urn,
        doc_id=args.doc_id,
        ingested_by=args.ingested_by,
    )
    for k, v in info.items():
        print(f"{k}: {v}")
    return 0

def cmd_process_queue(args: argparse.Namespace) -> int:
    root = repo_root_from_here()
    if args.queue_kind == 'librarian':
        results = process_librarian_queue(root)
        for r in results:
            print(r)
        return 0
    raise SystemExit(f"Unknown queue kind: {args.queue_kind}")

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="townctl", description="Agentic Fixedpoint maintenance CLI")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("id", help="Generate a new ID")
    sp.add_argument("kind", choices=["doc", "idea", "proj", "nb", "bb"])
    sp.set_defaults(func=cmd_id)

    sp = sub.add_parser("ingest", help="Ingest a document into vault/")
    sp.add_argument("--source", required=True, help="Path to a local file (pdf/html/txt)")
    sp.add_argument("--license-status", required=True, choices=["owned", "reference-only"])
    sp.add_argument("--title", default=None)
    sp.add_argument("--url", default=None)
    sp.add_argument("--doi", default=None)
    sp.add_argument("--urn", default=None)
    sp.add_argument("--doc-id", default=None, help="Optional explicit document id")
    sp.add_argument("--ingested-by", default="manual")
    sp.set_defaults(func=cmd_ingest)

    sp = sub.add_parser("lint", help="Validate frontmatter and crossrefs")
    sp.set_defaults(func=cmd_lint)

    sp = sub.add_parser("index", help="Regenerate catalog indexes")
    sp.set_defaults(func=cmd_index)

    sp = sub.add_parser("export-site", help="Export catalog pages into site/")
    sp.set_defaults(func=cmd_export_site)

    sp = sub.add_parser("new-idea", help="Create a new idea card template")
    sp.add_argument("--title", required=True)
    sp.add_argument("--doc-id", required=True)
    sp.add_argument("--locator", default="transcript.md")
    sp.set_defaults(func=cmd_new_idea)

    sp = sub.add_parser("new-project", help="Create a new project template")
    sp.add_argument("--title", required=True)
    sp.set_defaults(func=cmd_new_project)

    sp = sub.add_parser("new-notebook", help="Create a new notebook template")
    sp.add_argument("--title", required=True)
    sp.add_argument("--project-id", required=True)
    sp.set_defaults(func=cmd_new_notebook)

    sp = sub.add_parser("new-blackboard", help="Create a new blackboard template")
    sp.add_argument("--title", required=True)
    sp.add_argument("--topic", required=True)
    sp.set_defaults(func=cmd_new_blackboard)

    sp = sub.add_parser("mine-ideas", help="Extract idea cards from an owned transcript using an LLM backend")
    sp.add_argument("--doc-id", required=True)
    sp.add_argument("--max-ideas", type=int, default=12)
    sp.set_defaults(func=cmd_mine_ideas)

    sp = sub.add_parser("draft-post", help="Draft a blog post from an issue + selected idea/doc IDs using an LLM backend")
    sp.add_argument("--issue-title", required=True)
    sp.add_argument("--issue-number", type=int, default=None)
    sp.add_argument("--issue-body-file", required=True)
    sp.add_argument("--idea-ids", nargs="*", default=None)
    sp.add_argument("--doc-ids", nargs="*", default=None)
    sp.set_defaults(func=cmd_draft_post)

    sp = sub.add_parser("parse-issue", help="Parse a GitHub issue form markdown into key/value pairs")
    sp.add_argument("--issue-body-file", required=True)
    sp.set_defaults(func=cmd_parse_issue)


    sp = sub.add_parser("archive-md", help="Archive an internal markdown artifact (notebook/blackboard) as a vault document")
    sp.add_argument("--source-md", required=True, help="Path to a markdown file inside the repo (e.g. lab/notebooks/...)")
    sp.add_argument("--license-status", default="owned", choices=["owned", "reference-only"])
    sp.add_argument("--title", default=None)
    sp.add_argument("--url", default=None)
    sp.add_argument("--doi", default=None)
    sp.add_argument("--urn", default=None)
    sp.add_argument("--doc-id", default=None)
    sp.add_argument("--ingested-by", default="archive")
    sp.set_defaults(func=cmd_archive_md)


    sp = sub.add_parser("process-queue", help="Process file-based queues under queue/")
    sp.add_argument("queue_kind", choices=["librarian"])
    sp.set_defaults(func=cmd_process_queue)

    return p

def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))
