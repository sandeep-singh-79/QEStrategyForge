# AI Test Strategy Generator - Learning Guide

Last Updated: 2026-04-09

## Purpose

This document exists so the repo teaches strategy formation, not just outputs artifacts.

Use it to learn how to think about strategy in different situations.

## The Basic Idea Of Test Strategy

A test strategy is not a list of tests.

It is the answer to questions like:
- what quality risks matter most here?
- what levels of testing do we need?
- what should be automated and what should not?
- what environments and test data do we need?
- how will we know whether release risk is acceptable?
- how early can we prevent defects?
- which testing layers should carry the most confidence?

## A Simple Strategy Formation Model

Start with five questions:

1. What are we trying to protect?
- business flow
- customer trust
- compliance
- revenue
- operational stability

2. What kind of system is this?
- UI-heavy product
- API-heavy platform
- data-heavy system
- legacy enterprise application
- highly integrated domain platform

3. What can go wrong?
- integration failures
- wrong business logic
- performance degradation
- security or privacy issues
- data corruption
- release instability

4. What constraints do we have?
- small team
- short timeline
- weak environments
- weak automation maturity
- incomplete requirements
- regulatory controls

5. What is the most practical mix of testing?
- manual vs automation
- test levels
- test layers
- reporting
- governance
- AI augmentation

## How Strategy Changes By Situation

### Situation 1 - Tight Timeline

Strategy pattern:
- prioritize smoke, critical-path, and release-risk coverage
- defer nice-to-have automation
- increase clarity on tradeoffs

Learning:
- strategy is often about what not to do yet

### Situation 2 - Legacy System

Strategy pattern:
- protect current business-critical behavior first
- favor API and service-layer coverage where possible
- reduce dependence on brittle E2E suites

Learning:
- modernization strategy is part of test strategy

### Situation 2A - Greenfield Product

Strategy pattern:
- build quality controls early
- shift confidence left into unit, component, API, and contract layers
- embed quality gates directly into CI/CD

Learning:
- greenfield strategy is about building the right quality foundations early

### Situation 2B - Brownfield Product

Strategy pattern:
- protect existing business-critical behavior first
- assess what existing automation should be reused, stabilized, retired, or replaced
- modernize in phases without losing regression confidence

Learning:
- brownfield strategy is about controlled transition, not clean-slate theory

### Situation 3 - High-Regulation Domain

Strategy pattern:
- strengthen traceability, audit, data control, and approvals
- be careful about AI-generated recommendations without review

Learning:
- governance is part of quality, not overhead

### Situation 4 - Strong Automation, Weak Reporting

Strategy pattern:
- improve quality telemetry, release readiness, and risk reporting
- optimize what exists before adding more scripts

Learning:
- more automation is not always the next answer

### Situation 5 - Incomplete Information

Strategy pattern:
- produce a conditional strategy
- label assumptions clearly
- separate knowns from unknowns

Learning:
- honesty and structure beat fake completeness

## How To Think About Automation Strategy

Automation strategy should answer:
- what is worth automating?
- at what layer?
- when?
- why?
- with what maintenance cost?
- what automation already exists?
- what is the target end-state?
- how will CI/CD use the automation?

A simple rule:
- automate what is stable, repeated, high-value, and important for fast feedback
- do not automate everything just because it is possible

Another simple rule:
- automation is not complete when scripts exist
- it becomes strategically useful when it is reliable, maintainable, visible in reporting, and integrated into CI/CD and quality gates

## Shift-Left And Layered Thinking

Shift-left means:
- detect and prevent problems earlier
- move quality activity closer to requirements, design, and development

Examples:
- improve requirement clarity
- define acceptance criteria early
- use unit and API checks before pushing too much into UI regression
- introduce contract checks early for integrated systems

Layered strategy means:
- not all confidence should come from one layer
- earlier layers should carry more routine confidence when possible
- UI / E2E should focus on business-critical flows and cross-layer validation

## How Strategy Changes If Automation Already Exists

If automation does not exist:
- build foundations and sequence adoption realistically

If automation exists but is weak:
- stabilize and simplify before scaling

If automation is mature:
- focus more on optimization, governance, reporting, and release decision quality

## How To Think About AI In Strategy

Use AI for:
- accelerating drafting
- surfacing coverage gaps
- identifying likely risk areas
- summarizing reports

Do not trust AI blindly for:
- compliance interpretation
- final risk acceptance
- complete coverage claims
- release approval

## How the Bounded LLM Synthesis Layer Works

This repo uses a bounded synthesis model, not open-ended generation.

The LLM receives a structured context bundle — the same normalized document the deterministic renderer uses — and is asked to produce a markdown strategy document in a defined format. It does not have free access to the prompt shape or output schema.

There are two safety layers:

1. **Structural validation**: the LLM output is validated against the same required-section rules as the deterministic renderer. If it fails, a constrained repair pass runs to fill gaps.
2. **Deterministic fallback**: if the LLM call fails entirely (network error, timeout, provider error) or if repair still fails, the system falls back to the deterministic renderer automatically. The caller receives a `3` exit code indicating fallback was used.

This means the system always produces a valid strategy document — either LLM-assisted or deterministic. The LLM adds synthesis quality; it is never a point of failure.

The provider is selected at runtime:
- `--provider ollama` — local inference via Ollama REST API
- `--provider openai` — OpenAI-compatible APIs (gpt-4o, Azure OpenAI, etc.)
- `--provider gemini` — Google Gemini REST API

All three implement the same `LLMClient` Protocol. Switching providers does not change the orchestration logic.

A key design rule: provider configuration is resolved in four layers (defaults → config file → env vars → CLI flags). API keys and secrets always come from environment variables — never from config files.

## Learning Exercises For This Repo

1. Compare strategy for:
- an API-first insurance platform
- a legacy UI-heavy internal app

2. Compare strategy for:
- high test automation maturity
- low test automation maturity

3. Compare strategy for:
- complete input context
- incomplete input context

4. Compare AI posture for:
- AI-friendly organization
- low-trust, compliance-heavy organization

5. Compare LLM-assisted vs deterministic output for:
- the brownfield-partial-automation benchmark
- the greenfield-low-automation benchmark
- observe what the LLM adds vs what the deterministic renderer always produces

6. Inspect what happens when the LLM is unreachable:
- set `--provider ollama --model does-not-exist`
- observe exit code `3` and that a valid strategy document is still written
- understand why the fallback chain matters for reliability

7. Try artifact-folder ingestion:
- use `benchmarks/artifact-brownfield/` as input
- compare the output to the equivalent YAML input path
- read the manifest and understand how document types map to input fields

## Expected Learning Outcome

By working through this repo, you should learn:
- how to form a strategy from context
- how strategy changes with risk and constraints
- how automation fits into the bigger lifecycle
- how AI can assist without replacing judgment
- how bounded LLM synthesis differs from open-ended generation
- how to design a system that degrades gracefully when LLM providers fail
- how artifact-folder ingestion maps unstructured documents to a structured strategy context
