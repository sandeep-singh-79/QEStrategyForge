# AI Test Strategy Generator - Phase 6 Implementation Backlog

Last Updated: 2026-04-09

## Purpose

Turn the Phase 6 bounded LLM plan into a working, testable generation path in small deterministic slices.

Engineering rules for all slices:
- keep implementation simple
- prefer reuse before adding abstractions
- follow TDD: red -> green -> refactor
- require deterministic tests for normal, negative, and edge-case paths
- report pass/fail and coverage before marking a slice complete
- refactor only when duplication or complexity becomes real

## Phase 6 Goal

Build a bounded LLM-assisted generation path that:
- reuses the existing normalized input package
- reuses deterministic classification and rule outputs
- generates richer strategy text inside the same output contract
- passes structural validation or falls back predictably
- remains benchmarkable through deterministic assertions

## Phase 6 Success Condition

Phase 6 is complete only if:
- the repo can run in deterministic mode and LLM-assisted mode
- the LLM path stays inside the existing output contract
- invalid LLM output fails or falls back predictably
- at least one benchmark scenario passes through the LLM path
- deterministic and LLM-assisted outputs remain comparable in structure

## Delivery Slices

## Slice 6.1 - LLM Mode Contract

Status:
- Not started

Goal:
Define the explicit runtime contract for deterministic mode versus LLM-assisted mode.

Deliverables:
- mode selection rules
- configuration model for LLM mode
- safe default behavior

Tasks:
- define runtime mode values
- decide how mode is passed into the orchestration path
- keep deterministic mode as the default
- fail clearly for unsupported mode values

Binary validation:
- passes if valid mode values are accepted and invalid mode values fail deterministically

## Slice 6.2 - Prompt Builder

Status:
- Not started

Goal:
Construct a bounded prompt package from existing deterministic state.

Deliverables:
- prompt builder module
- prompt context object or structured dictionary

Tasks:
- reuse normalized input package
- reuse context classification output
- reuse rule-engine output
- include required headings and required labels
- include explicit no-invention instruction
- include explicit assumptions and gaps instruction

Binary validation:
- passes if the prompt builder always includes required context blocks and output contract instructions

## Slice 6.3 - LLM Client Interface

Status:
- Not started

Goal:
Create a minimal client boundary for text generation without binding Phase 6 to one provider everywhere.

Deliverables:
- simple client interface
- request/response contract
- one fake client for deterministic testing

Tasks:
- define a minimal generation request model
- define a minimal generation response model
- add a fake client that returns deterministic content for tests
- keep provider-specific logic out of orchestration code

Binary validation:
- passes if orchestration can call the fake client through the interface without provider-specific assumptions

## Slice 6.4 - Mocked LLM Flow

Status:
- Not started

Goal:
Run the first end-to-end LLM-assisted flow using the fake client.

Deliverables:
- LLM orchestration path
- deterministic tests for the mocked flow

Tasks:
- add a new end-to-end function for LLM-assisted generation
- call prompt builder
- call fake client
- convert returned text into the existing output validation path
- preserve output writing behavior

Binary validation:
- passes if one benchmark scenario completes successfully through the fake-client path

## Slice 6.5 - Structural Validation And Fallback

Status:
- Not started

Goal:
Ensure structurally invalid LLM output never silently succeeds.

Deliverables:
- structural validation reuse in LLM path
- one constrained fallback behavior

Tasks:
- validate LLM output using the existing structural validator
- choose and implement one fallback:
  - deterministic renderer fallback, or
  - one constrained repair pass
- return explicit failure when both generation and fallback fail

Binary validation:
- passes if structurally invalid LLM output triggers predictable fallback or failure every time

## Slice 6.6 - Benchmark Compatibility

Status:
- Not started

Goal:
Prove that the bounded LLM path still satisfies benchmark expectations.

Deliverables:
- at least one benchmark-compatible LLM path
- comparison evidence between deterministic and LLM-assisted modes

Tasks:
- run at least one existing benchmark through LLM-assisted mode
- verify structural validation still passes
- verify benchmark assertions still pass
- compare output shape with deterministic mode

Binary validation:
- passes if one benchmark scenario succeeds through both deterministic and LLM-assisted paths

## Slice 6.7 - Hardening

Status:
- Not started

Goal:
Strengthen negative and edge-case behavior before any real provider integration is added.

Deliverables:
- additional negative tests
- edge-case tests
- small refactors only where complexity justifies them

Tasks:
- test missing model configuration
- test unsupported mode selection
- test fake client error propagation
- test fallback behavior when LLM output is malformed
- refactor only if orchestration complexity or duplication becomes real

Binary validation:
- passes if the known Phase 6 edge cases fail or recover predictably

## Immediate Implementation Order

1. Slice 6.1
2. Slice 6.2
3. Slice 6.3
4. Slice 6.4
5. Slice 6.5
6. Slice 6.6
7. Slice 6.7
