# Session Plan

> **Purpose:** Track the active planning and execution steps for the `ai-test-strategy-generator` repository.
> **Scope:** Session-specific or cycle-specific. Refresh as milestones move and promote durable outcomes into `claude-memory/`.
> **Last Updated:** 2026-04-21

---

## Session Details

| Field | Value |
|---|---|
| Capability | ai-test-strategy-generator |
| Objective | MVP SEALED |
| Current Phase | All phases complete (4–8, 10–12) |
| Current Focus | None — capability sealed at v1.0.0; moving to Release Risk Scoring Engine |

---

## Plan Tracks

| Track | Goal | Status | Notes |
|---|---|---|---|
| T1 - Repo Setup | Initialize repository and local operating files | Complete | Git repo and memory/plan structure created |
| T2 - Capability Definition | Define what the system does and does not do in MVP | Complete | Documented in `docs/IMPLEMENTATION-PLAN.md` |
| T3 - MVP Scope | Define first usable slice | In progress | First milestone direction documented |
| T4 - Build Plan | Turn MVP into milestone and weekly steps | In progress | Repo-level implementation plan created |
| T5 - Validation Model | Define pass/fail checks for future work | Complete | Binary validation rules established in repo instructions |
| T6 - Learning Layer | Add documentation that teaches strategy formation | Complete | Learning guide and scenario library created |
| T7 - Input Model | Define the MVP input shape and source model | Complete | `docs/V1-INPUT-TEMPLATE.md` created |
| T8 - Phase Plan | Define phase-wise implementation path | Complete | `docs/PHASED-IMPLEMENTATION.md` created |
| T9 - Output Model | Define the v1 output contract | Complete | `docs/V1-OUTPUT-TEMPLATE.md` created |
| T10 - Phase Review | Check current status against phased plan | Complete | Current phase status added to `docs/PHASED-IMPLEMENTATION.md` |
| T11 - Rule Layer | Make the strategy engagement-specific through explicit rules | Complete | `docs/DECISION-RULES.md` created |
| T12 - Validation Harness | Define deterministic benchmark and validation approach | Complete | `docs/VALIDATION-HARNESS.md` and `benchmarks/` created |
| T13 - Phase 4 Backlog | Create detailed phased implementation backlog | Complete | `docs/PHASE-4-IMPLEMENTATION-BACKLOG.md` created |
| T14 - Runtime Foundation | Implement Slices 4.1 to 4.3 | Complete | Python scaffold, input loader, and input validator working |
| T15 - Context Classification | Implement Slice 4.4 with tests | Complete | Context classifier added and tested |
| T16 - Rule Engine | Implement Slice 4.5 with tests | Complete | Deterministic rule engine added and tested |
| T17 - Deterministic Renderer | Implement Slice 4.7 with tests | Complete | Markdown renderer added and tested |
| T18 - Output Validator | Implement Slice 4.8 with tests | Complete | Structural output validator added and tested |
| T19 - Benchmark Runner | Implement Slice 4.9 with tests | Complete | Benchmark assertion runner added and tested |
| T20 - End-to-End Flow | Implement Slice 4.10 with tests | Complete | First benchmark end-to-end flow added and tested |
| T21 - Phase 4 Hardening | Run additional benchmarks and close deterministic gaps | Complete | 4 benchmark scenarios now pass end-to-end |
| T22 - Output Model | Add lightweight structured output model | Complete | `StrategyDocument` and `StrategySection` now structure renderer output |
| T23 - README | Add first-time usage documentation | Complete | Root README added |
| T24 - Usage Guide | Add detailed execution guide | Complete | `docs/USAGE-GUIDE.md` added |
| T25 - Phase 5 Plan | Define the artifact-folder MVP implementation plan | Complete | `docs/PHASE-5-IMPLEMENTATION-PLAN.md` added |
| T26 - Phase 5 Backlog | Create detailed execution backlog for artifact-folder MVP | Complete | `docs/PHASE-5-IMPLEMENTATION-BACKLOG.md` added |
| T27 - Artifact Contract And Loader | Implement Slice 5.1 to 5.3 with tests | Complete | Manifest contract, folder loader, and `.md/.yaml/.json` readers added |
| T28 - Artifact Mapping And Merge | Implement Slice 5.4 to 5.5 with tests | Complete | Artifact mapping and normalized merge logic added |
| T29 - Artifact End-To-End Flow | Implement Slice 5.6 to 5.7 with tests | Complete | Artifact-folder path now reuses the main strategy pipeline and committed benchmark assets exist |
| T30 - Phase 5 Hardening | Close deterministic artifact-folder edge cases | Complete | Empty manifests, invalid posture, directory paths, path traversal, and incomplete artifact sets now fail predictably |
| T31 - Phase 6 Plan | Define bounded LLM integration on top of deterministic core | Complete | `docs/PHASE-6-IMPLEMENTATION-PLAN.md` added |
| T32 - Phase 6 Backlog | Create detailed execution backlog for bounded LLM integration | Complete | `docs/PHASE-6-IMPLEMENTATION-BACKLOG.md` added |
| T33 - Phase 6 Build | Deliver all 7 Phase 6 slices (mode contract through hardening) | Complete | 128 tests green; new modules: prompt_builder, llm_client, llm_flow |
| T34 - Phase 7 Build | Deliver all 9 Phase 7 slices (real providers, CLI composition root, live tests, coverage hardening) | Complete | 240 tests green + 2 live; new modules: config_loader, ollama_client, openai_client, gemini_client, client_factory; cli.py rewritten as composition root; RuntimeError fallback fixed; glm-5:cloud live validated |
| T35 - Phase 8 Build | Deliver all 6 Phase 8 slices (prompt engineering, scenario templates, content assertions, --compare) | Complete | 268 tests green + 6 live; prompts/v1/ templates; scenario selection; REQUIRED_LABELS expanded to 18; context-aware repair; comparison.py + --compare CLI flag |
| T37 - Phase 10 Build | Deliver all Phase 10 slices (Karpathy optimization loop, binary scoring, 5 mutation strategies, scoreboard) | Complete | 342 tests; optimizer_score.py, prompt_mutations.py, prompt_optimizer.py |
| T38 - Phase 11 Build | Deliver content-depth assertions, NFR vertical slice, QEStrategyForge self-benchmark | Complete | 373 tests; nfr_priorities field, 7th classifier, 10th rule key, 19th label, 2 new benchmarks |
| T39 - Phase 12 Plan | Define Phase 12 backlog from Codex review priority actions | Complete | `docs/PHASE-12-IMPLEMENTATION-PLAN.md` created with binary acceptance criteria and Claude handoff prompt |

---

## Immediate Next Actions

Codex review received 2026-04-17. Phase 12 planned. Merge current PR after Phase 12 or as a gating dependency.

**Phase 12 priority actions (from Codex review):**

1. **P12-A — Optimizer test portability** (independent, small): replace `tempfile.gettempdir()` in `prompt_optimizer.py` and `test_prompt_optimizer.py` with repo-local writable temp path (`tmp/`, gitignored). ~5 tests.

2. **P12-B — Expand input schema**: add first-class input fields for release cadence, team topology/QE capacity, environments, data/privacy constraints, reporting audience, target quality gates. Extend `input_validator.py`, `models.py`, and classifier/rule_engine to consume them. ~20–30 tests.

3. **P12-C — Deepen deterministic renderer**: use classifications and rule decisions to vary test phase sequencing, recommended test levels by risk, manual/automation boundary, CI/CD gate progression, governance/reporting audience, and immediate next actions. See `renderer.py:60,77,116,143`. ~15–20 tests.

4. **P12-D — NFR per-priority rendering**: when `nfr_depth=deep`, render concrete approach lines per named NFR priority (performance/security/accessibility/resilience) instead of one generic line. Conditional rendering for the NFR label (not universal). ~10 tests.

5. **P12-E — Section-aware validation**: upgrade `validate_output()` from substring presence to: (a) each required label appears exactly once, (b) each label appears in its expected section, (c) forbidden contradictions evaluated by section context. Extend assertion adequacy checks in `benchmark_runner.py`. ~15–20 tests.

6. **P12-F — New benchmark scenarios**: add 4 new scenarios reflecting enterprise QE planning realities: (a) strong-automation-weak-governance, (b) regulated-brownfield-manual-release, (c) incomplete-context-contradictory, (d) multi-integration-unstable-dependencies. ~10–15 tests.

**Order of execution**: P12-A → P12-B → P12-C → P12-D → P12-E → P12-F (B gates C/D; E gates F).

---

## Decisions & Notes

- This repo follows the same memory and `plan.md` discipline as the top-level upskilling workspace.
- Repo-level memory is capability-specific; top-level memory remains program-level.
- The repo must include learning documentation as part of the product, not as separate leftover notes.
- MVP recommendation: start with structured input file plus small artifact-folder support, not live external connectors.
- V1 input and output templates are now defined before coding begins.
- Current status review: Phase 1, Phase 2, and Phase 3 are complete; Phase 6 is partially underway; Phase 4 is the next active phase.
- The strategy is now explicitly engagement-specific through a rules layer rather than broad generic prose.
- Deterministic benchmark scenarios now exist to support future objective validation.
- Phase 4 detailed implementation backlog is now defined as the execution board for coding work.
- Slices 4.1, 4.2, and 4.3 are now complete with a working CLI validation path.
- Code implementation should follow KISS and reuse-first principles.
- Code should be tested before a slice is marked complete, with pass/fail and coverage details recorded.
- Phase 6 LLM mode selection: CLI flag `--mode deterministic|llm_assisted` (default: deterministic)
- Phase 6 fallback strategy: constrained repair pass → deterministic renderer → explicit failure
- Phase 6 LLM client: provider-agnostic Protocol; future providers (gpt-5.4, Gemini, Ollama/GLM4.7) plug in without changing orchestration
- Phase 7 provider config: `strategy.config.yaml` holds non-secret defaults; `STRATEGY_LLM_API_KEY` env var for secrets — security invariant, not preference
- Phase 7 CLI: composition root pattern; `_build_provider_config()` implements 4-layer merge (defaults → config file → env vars → CLI flags)
- Phase 7 fallback fix: RuntimeError from `generate()` is caught in `llm_flow.py`, sets `markdown=""`, triggers repair→deterministic fallback chain (exit code 3)
- Phase 7 test baseline: 240 non-live tests + 2 live tests (glm-5:cloud via Ollama, ~152 s)
- Phase 7 live model: `glm-5:cloud` via Ollama; override with `STRATEGY_LLM_MODEL` env var or `--model` CLI flag
- Phase 5 hardening baseline is now green: 69 tests passed, 0 failed.
- Phase 6 baseline: 128 tests passed, 0 failed.
- Phase 6 planning now exists in `docs/PHASE-6-IMPLEMENTATION-PLAN.md`.
- Phase 6 backlog now exists in `docs/PHASE-6-IMPLEMENTATION-BACKLOG.md`.
