# Publishing Checklist

Use this checklist before pushing the repository to a public GitHub repository.

## Repository Content

- confirm that benchmark scenarios are synthetic and contain no proprietary client content
- confirm that documentation contains no internal-only references, credentials, or local environment assumptions
- confirm that ignored generated artifacts are not tracked

## Repo Metadata

- confirm AGPL-3.0-or-later in `LICENSE` is the intended public license
- set a clear GitHub repository description
- add topics such as:
  - `quality-engineering`
  - `test-strategy`
  - `automation-strategy`
  - `agentic-qe`
  - `deterministic-validation`
  - `agpl`

## Files To Review Before Publishing

- `README.md`
- `docs/USAGE-GUIDE.md`
- `docs/VALIDATION-HARNESS.md`
- `benchmarks/`
- `claude-memory/`
- `plan.md`
- `AGENTS.md`

## Optional Public-Repo Choices

This repository intentionally keeps these files public as part of the development workflow:
- `claude-memory/`
- `plan.md`
- `AGENTS.md`

## Final Local Checks

Run:

```powershell
$env:PYTHONPATH='src'
python -m unittest discover -s tests -v
```

Confirm:
- tests pass
- `git status --short` is clean
- `.gitignore` is covering generated trace and `.cover` artifacts
