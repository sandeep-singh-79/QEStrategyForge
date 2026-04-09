# AGENTS.md - Workspace Instructions

The authoritative working context for this repository is maintained in:

- `claude-memory/memory.md`
- `claude-memory/insights.md`
- `claude-memory/notes.md`
- `plan.md`

Read these files before proceeding.

## Session Start Checklist

1. Read `AGENTS.md`
2. Read `claude-memory/memory.md`
3. Read `claude-memory/insights.md`
4. Read `claude-memory/notes.md`
5. Read `plan.md`
6. Confirm the active milestone, next action, and any blockers

## Working Rules

- This repo is the capability-specific workspace for `ai-test-strategy-generator`.
- Keep this repo's memory focused on this capability.
- Use the top-level `Agentic Upskilling` memory layer for cross-program strategy and portfolio decisions.
- Update memory continuously during the session, not only at the end.
- Follow KISS: keep code simple and direct.
- Follow DRY: remove duplication when it becomes real and recurring.
- Follow YAGNI: do not build speculative flexibility ahead of current validated need.
- Follow SOLID where it helps clarity, testability, and change safety; do not force abstraction for its own sake.
- Prefer reuse and extension of existing code before introducing new modules or abstractions.
- Write new code only when it is genuinely required by the current slice or validation need.
- Refactor when complexity starts increasing or duplication becomes visible.
- Introduce design patterns only when the code has become complex enough that a named pattern materially improves structure.
- All code must be tested before it is marked complete.
- Always report test pass/fail results and coverage details for code that was tested.
- Follow TDD in the standard order: red, green, refactor.
- For Phase 5 and later, every ingestion path must have deterministic validation and deterministic tests before it is considered complete.

## Memory Update Discipline

- Update `claude-memory/memory.md` when the repo's current state, decisions, next actions, or blockers change.
- Update `claude-memory/insights.md` when a lesson is reusable across future sessions or related repos.
- Update `claude-memory/notes.md` for temporary notes and unresolved questions.
- Update `plan.md` as the active session or execution-cycle tracker.

## Validation Rules

Use binary pass/fail validation for capability work.

- Repo setup passes only if:
  - Git is initialized
  - `AGENTS.md`, `plan.md`, and `claude-memory/` exist
  - repo memory includes purpose, next work, and blockers

- Capability definition passes only if:
  - the problem statement is written in one clear paragraph
  - inputs are named
  - outputs are named
  - non-goals are named

- MVP scope passes only if:
  - one first user-visible flow is identified
  - success can be checked in pass/fail terms
  - the milestone is small enough to complete without building the whole platform

- Build increment passes only if:
  - expected behavior is stated before implementation
  - at least one pass/fail check exists
  - result is recorded in `claude-memory/notes.md` or `claude-memory/memory.md`
  - automated tests exist for normal, negative, and edge-case behavior where applicable

- Context recovery passes only if:
  - `AGENTS.md`, `claude-memory/`, and `plan.md` were reloaded
  - active milestone, next step, and blockers were restated before work continues

## Context Recovery Rule

Reload context from files when:
- context compacts
- a new session starts or the session relaunches
- there is a long gap
- priorities or plans change materially
- another agent or the user may have changed files
- the thread feels inconsistent with the files
- a major code, architecture, or repo-structure decision is about to be made

## Ingestion Rules

- All file loading that accepts user-provided paths must use `Path.resolve()` then `is_relative_to(root)`. Neither alone is sufficient. No exceptions.
- Any new multi-file ingestion path must validate the manifest contract before opening any artifact file. Fail early on structural problems.
- For Phase 5 and later, every ingestion path must have deterministic validation and deterministic tests before it is considered complete.
- Coverage below 90% on any ingestion module (`artifact_loader`, `artifact_mapping`, or future loaders) is a hardening signal requiring a dedicated hardening slice before new features are added to that module.

## Output Contract Rules

- `REQUIRED_HEADINGS` and `REQUIRED_LABELS` in `output_validator.py` must be stable before any LLM integration work begins.
- Any change to either list is a breaking change. All dependent tests and benchmark assertion files must be updated in the same slice.
- Structural validation must use exact string matching only. Fuzzy or regex matching is not permitted.

## LLM Integration Rules

- Every prompt from `prompt_builder` must include: the full output contract (headings + labels), a no-invention instruction, an assumption-surfacing instruction, and a do-not-contradict instruction. Omitting any one is non-compliant.
- The repair pass (`_repair_output`) is structural-only: placeholder text for missing headings, `not specified` for missing labels. It must never synthesise content.
- `FakeLLMClient` is for structural and infrastructure testing only. Never use it to assert scenario-specific content accuracy. Content-level assertions require a real provider or a scenario-specific fake.
- Provider-specific code (API keys, base URLs, HTTP clients) belongs only in concrete client implementations, never in orchestration code. Credentials come from environment variables only.

## Test And Benchmark Rules

- Test temporary files must use `tests/.tmp/`. System temp directories have caused reliability issues in this repo and must not be reintroduced.
- Committed benchmark folders and input files are regression anchors. Do not delete or structurally modify them without a corresponding test update.
- When a new flow function is added, wire its CLI entry point in the same slice or log it immediately in `claude-memory/notes.md` under the Deferred Items Log with the target phase named explicitly.
- Deferred items must be logged in the same session the deferral is decided. Items not logged are not deferred — they are lost.
