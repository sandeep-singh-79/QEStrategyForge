# Memory

Current state, decisions, and active priorities for the `ai-test-strategy-generator` capability.

> **Update Policy:** Update this file when the current capability direction, decisions, next actions, or blockers change.
> **Scope:** Capability-specific and durable across sessions for this repository.

---

## Capability Context
- Repository purpose: build a business-facing AI-native QE system that generates a test strategy from inputs such as RFP scope, requirements, system landscape, and constraints.
- Product intent clarified on 2026-04-17: this is a decision-support tool for a Test Architect / QA Lead to produce client-specific test strategies from engagement inputs. It is not a general QA strategy generator for autonomous AI agents.
- Current stage: **MVP SEALED at v1.0.0**. All phases complete (4, 5, 6, 7, 8, 10, 11, 12). 489 tests passing, 97% coverage.
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
- Phase 10 direction: Karpathy-style prompt optimization loop. Decision made 2026-04-16.
- Optimization scoring: purely binary. Count of pass/fail checks across benchmarks. No weighted composites.
- Hybrid mutation strategy: cumulative within a run (mutate best-so-far), fresh baseline on new runs.
- Experiment tracking: optimization_runs/ directory (.gitignored). Config, scoreboard, per-iteration prompt snapshots, mutation descriptors. Only winning prompts (prompts/v2/) committed.
- Winning prompts saved as prompts/v2/ (never overwrite v1). User explicitly adopts by updating prompt_builder.py.
- Per-iteration wall-clock timeout: 300s default.
- After Phase 10: merge to master, park repo, transition to intelligent-regression-optimizer.

## Active Next Work
- MVP is sealed. Capability is parked.
- Next system: `release-risk-scoring-engine` (third capability).

## Blockers
- No setup blocker.
- Git in this environment may leave stray lock files in `.git` during some commands; if Git operations fail, inspect lock-file state first.

## Known Deferred Technical Debt

### Resolved in Phase 12 (2026-04-17)
- **P12-A COMPLETE**: Optimizer temp portability — repo-local `tmp/optimizer/` path; all 391 tests passing.
- **P12-B COMPLETE**: Input schema expansion — release_cadence, qe_capacity, reporting_audience, environment/privacy/quality-gate list fields.
- **P12-C COMPLETE**: Deterministic renderer depth — 5 helper functions vary lifecycle posture, layered strategy, CI/CD, AI usage, next steps by classification.
- **P12-D COMPLETE**: NFR per-priority rendering — deep mode emits `Non-Functional Priorities: <csv>` summary + `NFR Detail: <priority> — <guidance>` per priority.
- **P12-E COMPLETE**: Section-aware validation — `LABEL_SECTION_MAP` tracks 20 labels, each verified for placement; duplicates caught; repair inserts into correct sections.
- **P12-F COMPLETE**: 3 new benchmark scenarios: regulated-brownfield-manual-release, greenfield-aggressive-timeline, multi-integration-unstable-dependencies.

### Still Open
- **Benchmark assertions**: still substring-only; adequacy/sequencing checks not yet implemented.
- **Repair mechanism** still produces section-correct injection, but overall quality (coherence, sequencing) of repaired documents is not evaluated.


### Pre-existing Deferred Debt
- **NFR label is universal, not conditional**: `"Non-Functional Priorities:"` required on every engagement; generic fallback when `nfr_priorities` absent. Fix deferred to Phase 12 NFR rendering work.
- **Live integration tests for OpenAI and Gemini**: only Ollama has live tests; deferred.
- **Extended artifact types**: `.pdf`, `.docx`, `.xlsx`, `.csv` still not supported; deferred.
- **CODEX.md reference**: deferred from Phase 6, still not created; deferred.
- **Multi-agent orchestration**: no autonomous agent loop; deferred.

## Implementation Snapshot
- Phases 1–10 complete.
- Phase 10 delivered: optimizer_score.py (binary scoring), prompt_mutations.py (5 strategies), prompt_optimizer.py (Karpathy loop), models.py ValidationResult.total_checks, benchmark_runner run_assertions total_checks, cli.py --optimize flags + _run_optimization() + scoreboard.yaml writer, repair_stats wired to comparison report. 55 new tests + 3 total_checks tests. .gitignore: optimization_runs/. Docs updated.
- Test baseline: 342 non-live tests passing. 6 live Ollama tests passing.
- Key updated modules in Phase 9: prompt_builder.py (A1), openai_client.py (A2), gemini_client.py (A2, A3), models.py (B1, E1), end_to_end_flow.py (B1), artifact_end_to_end_flow.py (B1), llm_flow.py (B2, B3, E1), comparison.py (E2), pyproject.toml (C1).
- Key new test files: tests/conftest.py (C1), tests/test_contracts.py (D3).
- not_applicable decision values are filtered from the prompt decisions block.
- LLM temperature=0.0; some nondeterminism remains at this setting (GLM model specific).
- Slice 4.6 is complete. Slice 4.12 is complete.
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
- Phase 5 implementation planning now exists in `docs/PHASE-5-IMPLEMENTATION-PLAN.md`.
- Phase 5 slices 5.1 to 5.3 are complete:
  - artifact folder contract
  - artifact loader
  - supported file readers
- Phase 5 slices 5.4 to 5.5 are complete:
  - artifact mappers
  - merge and normalization
- Phase 5 slices 5.6 to 5.7 are complete:
  - end-to-end artifact flow
  - committed artifact benchmark
- Phase 5 slice 5.8 is complete:
  - invalid manifest posture now fails early
  - empty artifact lists now fail early
  - directory references now fail as invalid artifact paths
  - path traversal remains blocked
  - incomplete artifact sets fail through the reused validation path
- Phase 6 implementation planning now exists in `docs/PHASE-6-IMPLEMENTATION-PLAN.md`.
- Phase 6 backlog now exists in `docs/PHASE-6-IMPLEMENTATION-BACKLOG.md`.
- Phase 6 direction is:
  - deterministic core remains primary
  - LLM is bounded to synthesis, not control
  - structural validation and fallback remain mandatory
- Phase 6 is now complete. All 7 slices delivered:
  - Slice 6.1: GENERATION_MODES, validate_mode, LLMConfig in models.py; --mode CLI flag in cli.py
  - Slice 6.2: prompt_builder.py (builds bounded prompts from normalized input + classifications + rules)
  - Slice 6.3: llm_client.py (LLMClient Protocol, GenerationRequest/Response, FakeLLMClient)
  - Slice 6.4: llm_flow.py (run_llm_benchmark_flow, run_llm_input_package_flow)
  - Slice 6.5: _repair_output (constrained repair) + deterministic renderer fallback in llm_flow.py
  - Slice 6.6: benchmark compatibility confirmed — fake client passes structural validation + brownfield assertions
  - Slice 6.7: hardening tests covering missing files, client errors, fallback exhaustion, content specificity
- Phase 6 full test baseline: 128 tests passed, 0 failed (59 new Phase 6 tests)
- LLM client is provider-agnostic; future providers (gpt-5.4, Gemini, Ollama/GLM4.7) plug in via LLMClient Protocol
- Fallback chain: LLM output → constrained repair → deterministic renderer → explicit failure
- Planned Phase 5 MVP file-type support:
  - `.md`
  - `.yaml`
  - `.yml`
  - `.json`
- Explicitly deferred from Phase 5:
  - `.pdf`
  - `.docx`
  - `.xlsx`
  - `.csv`
  - images
  - live external connectors
- Phase 5 test baseline:
  - `tests.test_artifact_loader`: 12 passed, 0 failed
  - `tests.test_artifact_mapping`: 4 passed, 0 failed
  - `tests.test_artifact_end_to_end_flow`: 3 passed, 0 failed
  - full suite: 69 passed, 0 failed
- Phase 5 coverage evidence:
  - `.tracecov-phase5-hardening/ai_test_strategy_generator.artifact_end_to_end_flow.cover`
    - 33 lines, 93% coverage
  - `.tracecov-phase5-hardening/ai_test_strategy_generator.artifact_loader.cover`
    - 112 lines, 91% coverage
  - `.tracecov-phase5-hardening/ai_test_strategy_generator.artifact_mapping.cover`
    - 118 lines, 83% coverage
  - `.tracecov-phase5-hardening/ai_test_strategy_generator.end_to_end_flow.cover`
    - 55 lines, 87% coverage
