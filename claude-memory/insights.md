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
