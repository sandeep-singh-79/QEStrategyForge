# Insights

Reusable patterns, lessons learned, and decision rules for the `ai-test-strategy-generator` capability.

> **Protection Policy:** This file is NOT session-specific. Append durable insights that should survive across sessions.
> **Update Policy:** Add only lessons that are likely to recur or influence later design/build decisions.

---

## Capability Insights

1. This capability is a strong first showcase because it is easy to explain in business language.
- People can quickly understand: give the system scope and context, get a usable QE strategy back.

2. This capability teaches high-value patterns early.
- It naturally exercises context design, reasoning structure, explainability, and output shaping without requiring heavy technical ingestion first.

3. Business-capability-first reduces early over-engineering risk.
- It is better to prove a useful strategy-generation flow first and extract shared platform pieces later.

4. Validation should be explicit and binary from the start.
- Capability work is easier to manage when each increment has a clear pass/fail condition instead of a vague quality judgment.

5. Learning documentation should be treated as product scope when the goal is upskilling through building.
- If the repo is meant to teach strategy formation, the learning layer must be maintained deliberately, not left as optional commentary.

6. Full-lifecycle strategy coverage creates a stronger showcase than isolated automation guidance.
- A senior-facing QE strategy product should include lifecycle, reporting, governance, AI posture, and edge-case handling, not only test levels or tooling suggestions.

7. Strategy quality depends heavily on delivery posture and maturity.
- Greenfield vs brownfield, existing automation maturity, and CI/CD maturity materially change the right strategy.
- These should be modeled explicitly, not treated as minor variations.

8. Connector-first MVPs are a trap for this product.
- For this capability, the early value is in strategy logic and output quality, not in integrating every enterprise source.
- Start with structured input and artifact folders, then add connectors later if the core engine proves useful.

9. Input and output contracts should be fixed before generator implementation.
- For strategy products, defining the schema first makes reasoning, validation, and incremental build work much cleaner.

10. Engagement-specific strategy needs a rule layer.
- The useful pattern from `Agents & Skills` is not the whole workflow; it is the discipline of classification plus explicit branching rules.
- That pattern translates well here.

11. A self-improving loop is only as good as its evaluator.
- The useful part of `autoresearch` is not autonomy by itself; it is the tight loop of propose, run, measure, keep-or-reject.
- For this product, that only works if strategy quality can be scored by deterministic checks plus a constrained evaluation harness.

12. Deterministic validation requires machine-checkable output markers.
- If the strategy output is free-form only, validation becomes subjective.
- Exact section headings and labeled lines are necessary to keep the harness objective.

13. Simplicity matters more than framework elegance in early slices.
- For this repo, KISS is the right default.
- Reuse existing modules and add new abstractions only when repetition or validation pressure clearly justifies them.

14. Slice completion requires evidence, not just working behavior in one ad-hoc run.
- For this repo, completion means tested code plus reported pass/fail and coverage details.
- TDD discipline is appropriate: red, green, refactor.

15. The most effective early architecture for this product is classification -> rules -> rendering.
- That sequence keeps the system explainable and testable.
- It also separates deterministic posture decisions from later language-generation concerns.

16. Deterministic strategy validation depends on output anchors.
- Exact headings and exact labeled lines made structural validation practical.
- Without those anchors, strategy evaluation would have drifted into subjective review.

17. Environment-aware testing is part of engineering quality.
- In this workspace, repo-local temporary files were more reliable than system temp usage for tests.
- Test harness simplicity was improved by removing brittle cleanup behavior once it proved unnecessary.

18. KISS held up under real implementation pressure.
- A single package with small focused modules was sufficient through validation, classification, rules, and rendering.
- Stage-per-folder structure was unnecessary at this point and would have added complexity without payoff.

19. Testing negative and edge cases early improved system trust.
- Missing files, invalid YAML, unsupported extensions, blank values, unknown states, and incomplete context all needed explicit coverage.
- This was necessary before moving deeper into generation flow.

20. A Protocol-based LLM client boundary maintains testability without provider lock-in.
- Using `typing.Protocol` (with `@runtime_checkable`) lets orchestration code call any client through the same interface.
- FakeLLMClient and real provider clients are interchangeable at the call site — no mocking framework needed for basic tests.

21. Structural validation anchors must be defined before LLM integration is attempted.
- The repair pass and fallback strategy only work because validate_output uses exact heading/label string matches.
- Without machine-checkable anchors, LLM output quality becomes subjective and untestable.

22. Bounded prompt design should include the output contract explicitly.
- Listing required headings and labels directly in the prompt reduces the chance LLM output needs repair.
- No-invention and assumption-surfacing instructions belong in every generation prompt.

23. The repair → deterministic fallback chain is the right resilience model for bounded LLM integration.
- Repair handles minor structural omissions without discarding LLM content.
- Deterministic fallback guarantees a valid output even when the LLM fails completely.
- Explicit failure (exit_code 3) only triggers when the deterministic path itself is broken — a test-infrastructure problem, not a normal runtime case.

24. A FakeLLMClient that returns scenario-specific content only satisfies scenario-specific assertions.
- The FakeLLMClient is for structural and infrastructure testing only.
- Real benchmark assertion compatibility (content accuracy) requires a real LLM producing scenario-aware output.
- This boundary should be documented explicitly so future tests don't confuse structural validation with content quality.

25. CLI flags that are accepted but not wired through are a deferred technical debt, not a feature.
- The `--mode` flag was added to the parser in the same slice that defined the mode contract.
- But `main()` still calls `run_validation()` without reading the mode flag — so the LLM path is
  unreachable from the command line.
- Lesson: when a flag is introduced, the routing logic must be added in the same slice or the gap
  must be explicitly logged as deferred debt with a named owner slice.

26. Deferred items should be logged immediately, not left to be remembered.
- During Phase 6, several items were explicitly descoped: real providers, prompt versioning, extended
  artifact types, multi-agent orchestration.
- Without a written deferred log, these risk being forgotten or rediscovered as surprises.
- The notes.md deferred items log is the right place to track these per phase, with named future phases
  as the pickup target.

27. The repair pass must be structural-only; it must not attempt to synthesize factually correct content.
- `_repair_output` adds placeholder text (`Not specified in engagement context.`) for missing headings
  and injects `not specified` for missing labels.
- This is correct: the repair pass restores structural validity, not content quality.
- A repair pass that tries to produce realistic content would cross the boundary into generation and
  would need its own validation and testing discipline.

20. A renderer can still be deterministic and useful before any LLM is introduced.
- Producing the full output contract with rule-driven content first is a strong intermediate milestone.
- It proves the product shape before adding synthesis complexity.

21. Hardening benchmarks are useful for catching context leakage, not just crashes.
- The greenfield benchmark exposed that brownfield-only guidance was leaking into all outputs.
- Benchmark assertions should continue checking for forbidden context carryover, not only required content.

22. Benchmark wording must be designed for deterministic matching.
- If assertions look for terms like `quality gate`, `release`, or `reporting`, the renderer needs explicit stable phrases for those concepts.
- This is a good reason to keep benchmark-facing language deliberate instead of overly stylistic.

23. A lightweight output model is enough before LLM integration.
- `StrategyDocument` and `StrategySection` gave the renderer a cleaner structure without adding framework-heavy complexity.
- For this repo, that is the right level of refactor: enough structure to control growth, not enough to slow delivery.

24. First-time usage documentation is part of product readiness, not polish.
- Once the deterministic core was stable, README and usage guidance became necessary to make the repo independently usable.
- This is especially important for long-running upskilling repos where future sessions must recover quickly.

25. Deterministic ingestion work needs the same engineering discipline as generation work.
- Artifact-folder support should not weaken the pass/fail model established in Phase 4.
- New ingestion paths need normal, negative, and edge-case tests before they can be trusted.

26. Reuse is the default architecture for the next phase.
- Phase 5 should reuse the existing normalization and strategy pipeline rather than introduce a second path.
- DRY, YAGNI, and SOLID should guide refactoring, but only when real complexity appears.

27. Hardening should reject obviously invalid artifact manifests as early as possible.
- Invalid posture values, empty artifact lists, and directory references are loader problems, not later mapping or validation problems.
- Failing them early keeps errors clearer and reduces downstream ambiguity.

28. Not all useful coverage runs need to be full-suite runs.
- The full suite is the release gate, but focused trace runs on the changed slice are enough to prove hardening coverage for that slice.
- This keeps the feedback loop tighter while still preserving measurable evidence.

## Phase 7 Insights

29. The CLI is the correct composition root for dependency injection in a function-based architecture.
- `cli.py` builds ProviderConfig from merged layers (defaults → config file → env vars → CLI flags), calls the factory, and injects the resulting client into flow functions.
- Everything below the CLI receives its dependencies as arguments — no global state, no DI container.
- This makes all flows independently testable by passing any LLMClient directly without mocking.

30. Config resolution should follow a strict precedence chain: defaults → file → env vars → CLI flags.
- Later layers always win. This is the UNIX convention and the user's mental model for overrides.
- Secret values (api_key, tokens) must never appear in config files — warn and ignore if found.
- The `STRATEGY_LLM_` env var prefix prevents collisions with other tools in the same shell.

31. A Factory function (not a class) is the right pattern when construction logic is a simple if/elif.
- `create_llm_client(config: ProviderConfig) -> LLMClient` is 15 lines.
- A class-based AbstractFactory, registry, or plugin system would be over-engineering for three providers.
- The factory validates API key presence for providers that require it, keeping that concern in one place.

32. LLM provider errors must trigger the deterministic fallback, not propagate as exceptions.
- The original `run_llm_input_package_flow` let `RuntimeError` from `generate()` escape the function entirely.
- The correct behavior: catch `RuntimeError`, set markdown to empty string, let the repair → fallback chain run.
- This means TimeoutError, network errors, and malformed responses all result in a valid strategy output, not a crash.
- A test that asserts `RuntimeError` propagates is asserting the wrong contract.

33. Live integration tests for cloud-routed or slow models need generous socket timeouts.
- `llama3.2:1b` timed out at 120s generating 4096 tokens locally.
- `glm-5:cloud` (Ollama cloud routing) needed ~152s for two benchmark runs.
- 300s is a reasonable default for a local-first integration test; tests should be skipped not failed when the provider is unavailable.
- The `@unittest.skipUnless` pattern (evaluated at collection time with a real health check) is cleaner than manual environment variable guards.

34. Coverage hardening must test private functions directly to reach dead-code guards.
- `_load_artifact_document` has a guard for unsupported file types that can never be reached through `load_artifact_folder` (because `_build_artifact_reference` rejects them first).
- The only way to cover it is to call `_load_artifact_document` directly with a manufactured reference.
- This is acceptable: the guard is a safety net, and covering it documents the invariant explicitly.

35. Benchmark artifact files must satisfy the input validator's enum constraints, not just be semantically reasonable.
- `Environment Maturity: greenfield - all environments to be provisioned` is humanly clear but fails enum validation (`weak | moderate | strong | unknown`).
- Artifact content must use exactly the values the validator accepts, even if they feel less descriptive for the scenario.
- This is the price of machine-checkable validation — it forces canonical vocabulary.

36. Existing tests that assert incorrect behavior must be updated when the behavior is deliberately changed.
- `test_llm_client_exception_propagates` asserted that RuntimeError escaped the flow.
- After fixing the fallback, this test became a false negative — it would pass only if the bug was re-introduced.
- Updating the test to assert correct behavior (fallback, not propagation) is mandatory, not optional cleanup.

37. The `strategy.config.yaml` file provides a safe, version-controllable way to share non-secret defaults.
- Provider base URL, temperature, max_tokens, and model can all be committed to a team config file.
- API keys and tokens must always come from environment variables — this is a security invariant, not a preference.
- The loader should warn loudly and ignore silently if a secret key appears in the config file.
