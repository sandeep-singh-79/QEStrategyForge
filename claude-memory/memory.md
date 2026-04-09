# Memory

Current state, decisions, and active priorities for the `ai-test-strategy-generator` capability.

> **Update Policy:** Update this file when the current capability direction, decisions, next actions, or blockers change.
> **Scope:** Capability-specific and durable across sessions for this repository.

---

## Capability Context
- Repository purpose: build a business-facing AI-native QE system that generates a test strategy from inputs such as RFP scope, requirements, system landscape, and constraints.
- Current stage: deterministic MVP with Phase 4 complete.
- This is the first business-capability-first repository in the broader Agentic Upskilling program.

## Why This Capability First
- Strong alignment with current strengths in QE strategy, RFP work, and leadership communication.
- Easier to explain and demo than deeper platform-first capabilities.
- High learning value for context design, decision logic, explainability, and structured outputs.

## Expected Input / Output Direction
- Inputs likely to include:
  - RFP or requirement summary
  - scope and system landscape
  - constraints and assumptions
- Outputs likely to include:
  - test strategy
  - risk areas
  - automation approach
  - effort view
  - open questions / assumptions
  - reporting and governance guidance
  - AI incorporation guidance across the lifecycle

## Decisions Made
- This capability will live in its own separate repository and folder.
- This repo will have its own `claude-memory/` layer and `plan.md`.
- The top-level `Agentic Upskilling` workspace remains the program-level planning hub.
- Validation in this repo should use binary pass/fail rules for setup, capability definition, MVP scope, build increments, and context recovery.
- The product scope should cover the full test lifecycle, not only test case or automation recommendations.
- Learning documentation is part of the product and should be maintained alongside implementation artifacts.
- The strategy model must explicitly cover shift-left, layered testing, greenfield vs brownfield posture, existing automation maturity, and automation end-state including CI/CD integration.
- A Karpathy-style iterative improvement loop can be useful here, but only in a constrained form after stronger binary evaluation is in place for strategy outputs.
- Code should follow KISS and reuse-first principles; avoid unnecessary abstraction or new modules unless the current slice truly needs them.
- Refactor as complexity grows, and do not mark code complete until it is tested with reported pass/fail and coverage details.
- The repository will keep `claude-memory/`, `plan.md`, and `AGENTS.md` public as part of the visible development workflow.
- The repository will use AGPL-3.0-or-later.
- AGPL is the closest fit to the desired reciprocity behavior, but it does not require upstream pull requests back to this specific repository.

## Active Next Work
- Keep MVP ingestion constrained to structured input plus small artifact-folder support.
- Decide the next post-Phase-4 milestone.
- Decide whether artifact-folder ingestion should come before LLM integration.
- Decide how bounded LLM synthesis should fit on top of the deterministic core.

## Blockers
- No setup blocker.
- Git in this environment may leave stray lock files in `.git` during some commands; if Git operations fail, inspect lock-file state first.

## Implementation Snapshot
- Slices 4.1 to 4.3 are complete.
- Slice 4.4 is complete.
- Slice 4.5 is complete.
- Slice 4.7 is complete.
- Slice 4.8 is complete.
- Slice 4.9 is complete.
- Slice 4.10 is complete.
- Slice 4.11 is complete.
- Slice 4.6 is complete.
- Slice 4.12 is complete.
- Slice 4.13 is complete.
- Python project scaffold exists.
- Structured YAML input loading works.
- Deterministic input validation works for a benchmark scenario.
- Automated tests are now in place for current code.
- Test result baseline: 48 tests passed, 0 failed.
- Coverage evidence exists in `.tracecov-phase4-final/` for current production modules with 0 missing traced lines.
- Negative and edge-case tests are included for current code paths.
- Four benchmark scenarios now pass deterministically end-to-end.
- Root README and detailed usage guide now exist for first-time execution and recovery.
- Public-publishing prep is in place:
  - README links are GitHub-friendly
  - benchmark scenarios are labeled synthetic
  - `pyproject.toml` now declares `README.md`
  - publishing checklist exists in `docs/PUBLISHING-CHECKLIST.md`
  - AGPL license notice exists in `LICENSE`
