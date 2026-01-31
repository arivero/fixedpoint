# Librarian ingest skill

Goal
- Add a new source document to the vault in a reproducible, file-based way.
- For owned material: keep raw + clean Markdown transcript in-repo.
- For reference-only material: store metadata + notes only; do NOT commit full text.

Inputs
- A local file path or a URL to a PDF/HTML/TXT.
- License status: `owned` or `reference-only`.
- Optional identifiers: DOI, arXiv, URN, canonical URL.

Outputs
- `vault/raw/<doc_id>/original.<ext>`
- `vault/owned/<doc_id>/doc.md` (+ `transcript.md`) OR `vault/references/<doc_id>/doc.md`
- Updated `catalog/*`.

Procedure
1) Generate a document id:
   - `python tools/townctl.py id doc`

2) Ingest:
   - `python tools/townctl.py ingest --source <file> --license-status owned --title "<title>" --url "<url>" --doi "<doi>" --urn "<urn>"`
   - For reference-only, use `--license-status reference-only`.

3) Regenerate catalog and site exports:
   - `python tools/townctl.py index`
   - `python tools/townctl.py export-site`

4) Validate:
   - `python tools/townctl.py lint`

Guardrails
- Never commit full text for `reference-only` documents.
- Put anything non-owned/sensitive into `vault/private/` (gitignored) and commit only metadata + your own notes.
