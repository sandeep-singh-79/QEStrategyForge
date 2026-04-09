# AI Test Strategy Generator - Phase 6 Implementation Plan

Last Updated: 2026-04-09

## Purpose

Phase 6 introduces bounded LLM synthesis on top of the deterministic core built in Phases 4 and 5.

The objective is not to replace the existing deterministic pipeline.
The objective is to use the LLM only where it adds value:
- synthesizing richer strategy narrative
- connecting tradeoffs across sections
- producing more human-readable strategy guidance

The deterministic layers must remain the system of control.

## Phase 6 Goal

Support an optional LLM-backed generation path that:
- accepts the same normalized input package already used by the deterministic engine
- reuses the same classification and rule outputs
- generates a richer strategy draft inside the existing output contract
- passes the same structural validation as the deterministic renderer
- remains measurable through deterministic benchmark checks

## Why This Phase Matters

This phase helps with:
- making the output more realistic and portfolio-ready
- teaching bounded prompt design and controlled synthesis
- preparing the repo for later AI-native QE positioning
- proving that LLM value can be added without giving up determinism

It should still remain:
- bounded
- testable
- explainable
- easy to compare against the deterministic baseline

## Phase 6 Design Principle

Do not let the LLM own the strategy logic.

Phase 6 should use:
- deterministic input validation
- deterministic classification
- deterministic rule decisions
- constrained prompt construction
- structural output validation

The LLM should not:
- invent unsupported facts
- bypass the rule layer
- produce a free-form document outside the output contract
- silently replace deterministic decisions

## Engineering Rules For Phase 6

Phase 6 implementation must follow these rules:

- deterministic logic stays primary
- TDD in the order: red -> green -> refactor
- KISS by default
- DRY when duplication becomes meaningful
- YAGNI for client, abstraction, and prompt-layer decisions
- SOLID where it improves maintainability and testability
- design patterns only when code complexity justifies them
- reuse existing input, classification, rule, rendering, and validation layers wherever possible

No Phase 6 slice is complete unless:
- deterministic tests exist
- normal, negative, and edge-case scenarios are covered where relevant
- pass/fail results are reported
- coverage details are reported for changed code

## Proposed Phase 6 Scope

Phase 6 should add:

1. an LLM prompt-building layer
- converts normalized input, context classification, and rule outputs into a bounded prompt package

2. an LLM client boundary
- one simple adapter interface
- one concrete implementation can be added later without spreading provider-specific code

3. a draft-generation flow
- obtain LLM output
- validate structure
- fail clearly if required headings or labels are missing

4. deterministic repair or fallback behavior
- if LLM output is structurally invalid, either:
  - run one constrained repair pass, or
  - fall back to the deterministic renderer

## Explicit Non-Goals For Phase 6

Do not add yet:
- multi-agent orchestration
- autonomous iterative self-modification
- provider switching frameworks
- prompt optimization loops
- live external connectors
- document OCR or broad unstructured parsing
- subjective quality scoring as the main acceptance gate

## Recommended LLM Responsibility Split

Use deterministic code for:
- input validation
- artifact normalization
- context classification
- rule derivation
- output contract enforcement
- benchmark assertions

Use the LLM for:
- cross-section synthesis
- readable strategy wording
- linking tradeoffs across lifecycle, automation, governance, and AI posture
- making assumptions explicit in fluent language

## Prompt Design Requirements

The prompt builder should include:
- normalized engagement input
- context classification summary
- deterministic rule outputs
- required output headings
- required labeled lines
- explicit instruction to avoid inventing missing facts
- explicit instruction to surface assumptions and gaps

The prompt should also state:
- current state vs target state must be preserved
- brownfield-only guidance must not leak into greenfield scenarios
- AI guidance must remain consistent with `ai_adoption_posture`

## Output Strategy For Phase 6

The LLM path should still produce the same top-level output shape as Phase 4 and 5:
- same required headings
- same required labels
- same structural validation path
- same benchmark assertion path

This allows direct comparison between:
- deterministic renderer output
- bounded LLM-assisted output

## Validation Model For Phase 6

Phase 6 should add deterministic validation for:
- missing model configuration
- unsupported LLM mode selection
- structurally invalid LLM output
- missing required headings or labels after LLM generation
- forbidden benchmark leakage still being absent
- fallback behavior working predictably

Phase 6 should also add deterministic tests for:
- prompt builder contents
- LLM client contract behavior
- successful LLM draft generation path
- structurally invalid LLM output path
- deterministic fallback path
- benchmark scenario compatibility

## Binary Success Condition

Phase 6 passes only if:
- one bounded LLM path can run from the existing normalized input
- the LLM output passes structural validation or falls back predictably
- benchmark assertions still pass for at least one scenario
- deterministic and LLM-assisted paths remain comparable in output shape

## Suggested Delivery Slices

1. `6.1 LLM mode contract`
- define how deterministic vs LLM-assisted mode is selected
- keep deterministic mode as the default safe path

2. `6.2 Prompt builder`
- construct bounded prompts from normalized input, classifications, and rules

3. `6.3 LLM client interface`
- define one simple client boundary
- keep provider-specific code isolated

4. `6.4 Mocked LLM flow`
- implement the first end-to-end path using a fake/mock client for deterministic tests

5. `6.5 Structural validation and fallback`
- validate LLM output
- repair once or fall back deterministically

6. `6.6 Benchmark compatibility`
- prove at least one scenario still passes through the bounded LLM path

7. `6.7 Hardening`
- add negative and edge-case tests
- refactor only where complexity justifies it

## Recommended First Phase 6 Test Strategy

Start with a fake client rather than a real provider because:
- it keeps TDD deterministic
- it proves the orchestration shape before provider wiring
- it avoids network and credential dependency during core design

After the fake client path is stable, add one thin real-client integration point.

## Recommended Phase 6 Output

At the end of Phase 6, the repo should support:
- deterministic strategy generation
- optional bounded LLM-assisted strategy generation
- the same validation and benchmark harness
- a clean comparison path between both modes

## Recommended Next Step After This Plan

Create a dedicated Phase 6 backlog, then implement in this order:

1. mode selection contract
2. prompt builder
3. mock LLM client
4. LLM orchestration flow
5. fallback behavior
6. benchmark-compatible validation
