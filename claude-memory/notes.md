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
- Resolved: Phase 7 direction → real LLM providers. Completed.
- Resolved: prompt versioning → prompts/v1/ directory. Completed in Phase 8.
- Resolved: comparison report → --compare CLI flag. Completed in Phase 8.
- Resolved: Phase 10 direction → Karpathy optimization loop. Decision made 2026-04-16.
- Open: should prompt mutation also modify scenario templates, or only base.txt? → Decided: base.txt only for Phase 10. Scenario templates unchanged.
- Closed: Phase 10 complete 2026-04-16. 342 tests. Commit 77e492d.

## Phase Status Snapshot
- Phase 1 complete
- Phase 2 complete
- Phase 3 complete
- Phase 4 hardening complete
- Phase 5 complete
- Phase 6 complete (2026-04-09)
- Phase 7 complete (2026-04-09)
- Phase 8 complete (2026-04-10)
- Phase 9 complete (2026-04-10)
- Phase 10 complete (2026-04-16) — Karpathy optimization loop, 345 tests, commits 77e492d, 314c776, 225c707
- Phase 11 planned (2026-04-16) — Content Depth + NFR Support + Self-Benchmark. See docs/PHASE-11-IMPLEMENTATION-PLAN.md
- Next: implement Phase 11, then merge to master

## Deferred Items Log

### Resolved in Phase 8 (no longer deferred)
- ~~Prompt versioning not tracked~~ — prompts/v1/ directory with versioned .txt files
- ~~Per-scenario prompt specialization~~ — 4 scenario templates + _select_scenario() priority chain
- ~~Content-level benchmark assertions~~ — all 6 assertion files strengthened; 6/6 live tests pass at exit_code 0

### Resolved in Phase 7 (no longer deferred)
- ~~CLI mode not wired to llm_flow~~ — fixed; cli.py is now the composition root
- ~~OpenAI-compatible client~~ — implemented (openai_client.py)
- ~~Gemini client~~ — implemented (gemini_client.py)
- ~~Ollama/GLM client~~ — implemented (ollama_client.py, tested live with glm-5:cloud)
- ~~Provider configuration~~ — implemented (config_loader.py + ProviderConfig + strategy.config.yaml)
- ~~artifact_mapping.py coverage 83%~~ — hardened to 100%
- ~~artifact_loader.py coverage 91%~~ — hardened to 100%
- ~~Greenfield artifact benchmark missing~~ — benchmarks/artifact-greenfield/ committed

### Still Deferred — Beyond Phase 10

**Live Provider Tests (beyond Ollama)**
- OpenAI live integration test: mirrors test_live_ollama.py but for OpenAI API.
- Gemini live integration test: mirrors test_live_ollama.py but for Gemini API.

**Extended Artifact Support**
- `.pdf`, `.docx`, `.xlsx`, `.csv` readers not implemented.

**Documentation / Reference**
- CODEX.md: cross-phase reference glossary for terms, labels, and decision vocabulary. Still deferred.

**Architecture / Platform**
- Multi-agent orchestration: no autonomous agent loop.
- Live external connectors: no Jira, Confluence, or API-source ingestion.

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
- Phase 6 is now complete.
- All 7 slices delivered: mode contract, prompt builder, LLM client, mocked flow, repair/fallback, benchmark compatibility, hardening.
- Full test suite: 128 passed, 0 failed.
- New modules: prompt_builder.py, llm_client.py, llm_flow.py
- Updated modules: models.py (GENERATION_MODES, validate_mode, LLMConfig), cli.py (--mode flag)
- New test files: test_generation_mode.py, test_prompt_builder.py, test_llm_client.py, test_llm_flow.py
