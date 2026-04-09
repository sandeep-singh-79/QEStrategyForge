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

This guide summarises the core patterns. Full case studies — including setup, risk profile, strategy decisions, tradeoffs, what good looks like, and common mistakes — are in the [Situations Catalogue](SITUATIONS-CATALOGUE.md).

### Core Situations

| Situation | Key Pattern | Full Case Study |
|---|---|---|
| Tight Timeline | Prioritise critical path; make tradeoffs explicit | [Situation 1](SITUATIONS-CATALOGUE.md#situation-1--tight-timeline) |
| Legacy System | Protect before you modernise; stabilise before you scale | [Situation 2](SITUATIONS-CATALOGUE.md#situation-2--legacy-system) |
| Greenfield Product | Build from the bottom up; embed CI/CD gates from day one | [Situation 3](SITUATIONS-CATALOGUE.md#situation-3--greenfield-product) |
| Brownfield Product | Audit before you build; retire before you scale | [Situation 4](SITUATIONS-CATALOGUE.md#situation-4--brownfield-product) |
| High-Regulation Domain | Compliance is a tested capability, not a sign-off | [Situation 5](SITUATIONS-CATALOGUE.md#situation-5--high-regulation-domain) |
| Microservices / Distributed | Contract testing is load-bearing; E2E sparingly | [Situation 6](SITUATIONS-CATALOGUE.md#situation-6--microservices--distributed-system) |
| High-Frequency Release | Pipeline speed and reliability over breadth | [Situation 7](SITUATIONS-CATALOGUE.md#situation-7--high-frequency-release-cadence-cicd-native) |
| Mobile-First / Cross-Platform | Deliberate device matrix; layer below the UI | [Situation 8](SITUATIONS-CATALOGUE.md#situation-8--mobile-first-or-cross-platform-product) |
| Data-Heavy / ML Pipeline | Assert on output data, not just execution | [Situation 9](SITUATIONS-CATALOGUE.md#situation-9--data-heavy-system-analytics--data-platform--ml-pipeline) |
| Third-Party Integration Heavy | Test your boundary; stub the vendor | [Situation 10](SITUATIONS-CATALOGUE.md#situation-10--third-party-integration-heavy) |
| Security-First Domain | Security is a pipeline layer, not a pen-test-once | [Situation 11](SITUATIONS-CATALOGUE.md#situation-11--security-first-domain-fintech-healthtech-deftech) |
| Performance-Critical System | Define SLAs before testing; all five types, not just load | [Situation 12](SITUATIONS-CATALOGUE.md#situation-12--performance-critical-system-trading-real-time-high-volume) |

### Edge Cases

Real engagements rarely match a single archetype. The [Situations Catalogue](SITUATIONS-CATALOGUE.md#edge-case-scenarios) covers the most common mismatches:

| Edge Case | Core Tension |
|---|---|
| Greenfield System, Brownfield Organisation | You cannot greenfield the org; design for the current maturity |
| Strong Automation, Wrong Layer | Rebalance the pyramid; don't just add more |
| Compliance-Heavy Domain, Startup Speed | Automate the traceability, not just the tests |
| Mature Automation, No Observability | A green pipeline is not a production quality guarantee |
| High Team Turnover / Knowledge Fragility | Maintainability is a quality attribute of the test suite |
| Multiple Parallel Streams | Define the target state before consolidating anything |
| UI Legacy + API Modernisation In Flight | Define layer ownership before both teams start building |
| Incomplete or Contradictory Requirements | Automate only what is stable and agreed |

## Testing Type Deep-Dives

These are separate documents covering specific testing types in full depth — what they are, when they are necessary, how to implement them, and common mistakes.

| Document | What It Covers |
|---|---|
| [Contract Testing](TESTING-TYPE-CONTRACT.md) | Consumer-driven vs. provider schema; where it fits vs. integration testing; what it catches; pipeline placement |
| [Performance Testing](TESTING-TYPE-PERFORMANCE.md) | Load, stress, spike, soak, and scalability — differentiated; SLA definition; pipeline integration |
| [Security Testing in the Pipeline](TESTING-TYPE-SECURITY.md) | SAST, SCA, DAST, pen testing — four layers; security functional tests; the security testing matrix |
| [Exploratory Testing](TESTING-TYPE-EXPLORATORY.md) | Session-based testing; charters; debriefs; when exploratory testing carries the most weight |
| [Accessibility Testing](TESTING-TYPE-ACCESSIBILITY.md) | WCAG; automated scanning, keyboard testing, screen reader testing; pipeline integration; legal risk |
| [Chaos and Resilience Testing](TESTING-TYPE-CHAOS.md) | Fault types; experiment structure; prerequisites; game days; chaos in CI/CD vs. production |

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

## Strategy Anti-Patterns

Recognising named mistakes is the first step to avoiding them. These are collected in a separate document with full description of each pattern, why teams fall into it, the actual harm, and what to do instead.

| Anti-Pattern | Signal |
|---|---|
| [Coverage Number Trap](STRATEGY-ANTI-PATTERNS.md#the-coverage-number-trap) | Stakeholders ask "how many tests?" |
| [Automation First Fallacy](STRATEGY-ANTI-PATTERNS.md#the-automation-first-fallacy) | High maintenance burden on new-feature automation |
| [UI Pyramid Inversion](STRATEGY-ANTI-PATTERNS.md#the-ui-pyramid-inversion) | Slow, flaky suite; low unit coverage |
| [Siloed QA Team](STRATEGY-ANTI-PATTERNS.md#the-siloed-qa-team) | Defects found late; engineers don't own tests |
| [Deferred Compliance](STRATEGY-ANTI-PATTERNS.md#the-deferred-compliance) | Bulk compliance effort pre-launch |
| [Tool-First Strategy](STRATEGY-ANTI-PATTERNS.md#the-tool-first-strategy) | Testing shaped by tool's strengths, not risk profile |
| [Fake Green](STRATEGY-ANTI-PATTERNS.md#the-fake-green) | Green pipeline; production incidents from untested scenarios |
| [Never-Retire Rule](STRATEGY-ANTI-PATTERNS.md#the-never-retire-rule) | Suite grows indefinitely; run time increases |

See [Strategy Anti-Patterns](STRATEGY-ANTI-PATTERNS.md) for full case studies.

## Strategy Thinking Frameworks

Portable mental models for making better strategy decisions — during formation, during reviews, and when pushing back on a quality approach.

| Framework | Core Question |
|---|---|
| [Risk-First Filter](STRATEGY-FRAMEWORKS.md#the-risk-first-filter) | What risk does this test protect against? |
| [Automation Viability Check](STRATEGY-FRAMEWORKS.md#the-automation-viability-check) | Is this scenario worth automating right now? |
| [Layer Before Climbing](STRATEGY-FRAMEWORKS.md#the-layer-before-climbing) | Could a lower layer give the same confidence more cheaply? |
| [Release Decision Check](STRATEGY-FRAMEWORKS.md#the-release-decision-check) | What questions does the test report actually answer? |
| [Shift-Left / Shift-Right Balance Check](STRATEGY-FRAMEWORKS.md#the-shift-left--shift-right-balance-check) | Is the strategy balanced across the delivery cycle? |
| [Assumption Visibility Rule](STRATEGY-FRAMEWORKS.md#the-assumption-visibility-rule) | What is this strategy assuming, and is it visible? |

See [Strategy Frameworks](STRATEGY-FRAMEWORKS.md) for full treatment including comparison tables.

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

1. Compare strategy for two system types — use the [Situations Catalogue](SITUATIONS-CATALOGUE.md):
- an API-first insurance platform
- a legacy UI-heavy internal app

2. Compare strategy for two automation maturity states — use the [Frameworks comparison table](STRATEGY-FRAMEWORKS.md#no-automation-vs-weak-automation-vs-mature-automation):
- high test automation maturity
- low test automation maturity

3. Compare strategy for two information states — use [Edge Case H](SITUATIONS-CATALOGUE.md#edge-case-h--incomplete-or-contradictory-requirements) and [Situation 3](SITUATIONS-CATALOGUE.md#situation-3--greenfield-product):
- complete input context
- incomplete input context

4. Compare AI posture for — use [Situation 5](SITUATIONS-CATALOGUE.md#situation-5--high-regulation-domain) and [Situation 7](SITUATIONS-CATALOGUE.md#situation-7--high-frequency-release-cadence-cicd-native):
- AI-friendly organization
- low-trust, compliance-heavy organization

5. Compare LLM-assisted vs deterministic output for:
- the brownfield-partial-automation benchmark
- the greenfield-low-automation benchmark
- observe what the LLM adds vs what the deterministic renderer always produces
- use the [Deterministic vs LLM-Assisted comparison table](STRATEGY-FRAMEWORKS.md#deterministic-vs-llm-assisted-strategy-generation-this-repo)

6. Inspect what happens when the LLM is unreachable:
- set `--provider ollama --model does-not-exist`
- observe exit code `3` and that a valid strategy document is still written
- understand why the fallback chain matters for reliability

7. Try artifact-folder ingestion:
- use `benchmarks/artifact-brownfield/` as input
- compare the output to the equivalent YAML input path
- read the manifest and understand how document types map to input fields

8. Apply the [Anti-Patterns](STRATEGY-ANTI-PATTERNS.md) as a diagnostic tool:
- read the quick reference table
- for a team or project you know, identify which anti-patterns are present
- for each one, use the "what to do instead" section to draft an improvement action

9. Design a test strategy for [Edge Case A — Greenfield System, Brownfield Organisation](SITUATIONS-CATALOGUE.md#edge-case-a--greenfield-system-brownfield-organisation):
- use the [Automation Viability Check](STRATEGY-FRAMEWORKS.md#the-automation-viability-check) to decide what to automate first
- use the [Assumption Visibility Rule](STRATEGY-FRAMEWORKS.md#the-assumption-visibility-rule) to document what the strategy depends on
- use the [Shift-Left / Shift-Right Balance Check](STRATEGY-FRAMEWORKS.md#the-shift-left--shift-right-balance-check) to design the quality gate model

## Expected Learning Outcome

By working through this repo, you should learn:
- how to form a strategy from context
- how strategy changes with risk and constraints
- how automation fits into the bigger lifecycle
- how AI can assist without replacing judgment
- how bounded LLM synthesis differs from open-ended generation
- how to design a system that degrades gracefully when LLM providers fail
- how artifact-folder ingestion maps unstructured documents to a structured strategy context
