# Notes

In-progress analysis, temporary notes, open questions, and working context for the `ai-test-strategy-generator` repository.

> **Update Policy:** Use for temporary notes, unresolved questions, and short-lived working context.
> **Scope:** Capability-specific. Promote durable points into `memory.md` or `insights.md`.

---

## Temporary Session Notes
- Repo initialized on 2026-04-08.
- Local memory layer and `plan.md` created before feature planning.
- `git status` produced a warning about `.git/index.lock` remaining behind in this environment.
- User asked that the memory layer remain part of the product/project itself.
- Implementation plan should cover full test lifecycle, automation strategy, reporting, AI impact, edge cases, and learning documentation.
- Additional explicit dimensions requested: shift-left strategy, layered approach, greenfield vs brownfield posture, existing automation state, automation end-goal, and CI/CD integration.
- User asked whether a Karpathy-style autoresearch refinement loop can be applied here and whether current binary validations are sufficient.

## Open Questions
- Should the first MVP output be markdown, JSON, or both?
- What amount of deterministic logic should be included in v1 versus later?
- Should the lightweight output model remain minimal until LLM integration, or grow earlier?

## Phase Status Snapshot
- Phase 1 complete
- Phase 2 complete
- Phase 3 complete
- Phase 4 hardening complete
- Phase 6 partially started through learning docs

## Validation Snapshot
- Deterministic validation harness defined in `docs/VALIDATION-HARNESS.md`
- Initial benchmark scenarios created in `benchmarks/`

## Backlog Snapshot
- Detailed Phase 4 backlog created in `docs/PHASE-4-IMPLEMENTATION-BACKLOG.md`
- Phase 4 slices are now complete, including the optional lightweight output model plus README and usage guide
- Immediate planning focus should move to the next post-Phase-5 milestone
- Public publishing prep now includes AGPL and the explicit decision to keep development workflow files public

## Testing Rule Snapshot
- Before further feature work, existing code must receive automated tests
- Use stdlib tooling if third-party test tools are unavailable
- Red phase found environment-specific test temp-file issues
- Green achieved after moving tests to repo-local temp files
- Refactor kept the fix simple and removed brittle cleanup logic
- Additional red/green cycle added negative and edge-case coverage before proceeding

## Current Working Snapshot
- Phase 5 hardening is now complete.
- Latest hardening additions cover:
  - invalid manifest posture
  - empty artifact list
  - directory path references
- Current full-suite baseline: 69 passed, 0 failed
- Focused hardening trace output is in `.tracecov-phase5-hardening/`
