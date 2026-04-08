# AI Test Strategy Generator - Decision Rules

Last Updated: 2026-04-08

## Purpose

Make the strategy engagement-specific through explicit rules.

This document is the bridge between:
- input context
- strategy logic
- output emphasis

It borrows the useful pattern from `Agents & Skills`:
- classify first
- apply explicit rules
- do not silently invent unsupported detail

## Core Rule

The generator must not produce a generic strategy.

It must first classify the engagement context, then adapt:
- lifecycle posture
- layer emphasis
- automation path
- CI/CD posture
- governance depth
- AI posture

## Rule Groups

## 1. Engagement Posture Rules

### Rule EP-1 - Greenfield
If `project_posture = greenfield`:
- increase shift-left emphasis
- emphasize unit, component, API, and contract layers early
- recommend CI/CD-native quality gates from the beginning
- treat automation as a foundational delivery capability

### Rule EP-2 - Brownfield
If `project_posture = brownfield`:
- require current-state assessment
- emphasize regression protection and transition sequencing
- classify existing automation as reuse / stabilize / retire / replace
- avoid clean-slate assumptions

## 2. Automation Maturity Rules

### Rule AM-1 - No Automation
If `existing_automation_state = none`:
- recommend phased automation introduction
- do not assume broad CI/CD quality gates immediately
- include foundational work in the strategy

### Rule AM-2 - Limited Or Partial Automation
If `existing_automation_state = limited` or `partial`:
- assess coverage gaps by layer
- identify what to stabilize vs expand
- recommend phased scaling rather than blanket rewrite

### Rule AM-3 - Strong Automation
If `existing_automation_state = strong`:
- reduce emphasis on “build more scripts”
- increase emphasis on optimization, reporting, quality gates, and release decision support

## 3. CI/CD Maturity Rules

### Rule CD-1 - No CI/CD
If `ci_cd_maturity = none`:
- do not present automated pipeline quality gates as current-state reality
- recommend staged CI/CD integration
- call out dependency on delivery-engineering maturity

### Rule CD-2 - Partial CI/CD
If `ci_cd_maturity = partial`:
- recommend achievable early gates
- separate current-state capability from target-state capability

### Rule CD-3 - Mature CI/CD
If `ci_cd_maturity = mature`:
- integrate automation strategy tightly with pipeline execution
- emphasize fast feedback, quality gates, and reporting signals

## 4. Architecture / System-Type Rules

### Rule AR-1 - API-First / Microservices
If `system_type` indicates API-first, service-heavy, or microservices:
- increase API, contract, and integration emphasis
- recommend observability-backed validation
- reduce unnecessary UI-heavy coverage posture

### Rule AR-2 - UI-Heavy Legacy
If `system_type` indicates UI-heavy and legacy:
- prioritize critical-path regression protection
- recommend selective UI automation, not blanket UI coverage
- favor service/API coverage where recovery path exists

### Rule AR-3 - Data-Heavy / Integration-Heavy
If `system_type` indicates data-heavy or integration-heavy:
- increase data integrity, reconciliation, and integration-risk emphasis
- strengthen environment and test-data sections

## 5. Delivery Constraint Rules

### Rule DC-1 - High Timeline Pressure
If `timeline_pressure = high`:
- prioritize critical-path, smoke, and release-risk coverage
- make tradeoffs explicit
- avoid pretending full target-state maturity is immediate

### Rule DC-2 - Missing Information
If required inputs are missing:
- generate a conditional strategy
- list assumptions explicitly
- separate confirmed facts from inferred guidance

## 6. Domain / Compliance Rules

### Rule DM-1 - High-Regulation Domain
If `domain` is insurance, banking, healthcare, or equivalent regulated context:
- strengthen auditability, traceability, test-data control, and approval checkpoints
- increase human-review boundaries around AI-supported output

### Rule DM-2 - Unknown Regulatory Context
If compliance needs are unclear:
- do not invent named obligations
- state that regulatory confirmation is required

## 7. AI Posture Rules

### Rule AI-1 - Supportive AI Posture
If `ai_adoption_posture = supportive`:
- allow broader AI-assisted drafting, gap analysis, and reporting support
- still require human approval for final strategy acceptance

### Rule AI-2 - Cautious Or Restricted AI Posture
If `ai_adoption_posture = cautious` or `restricted`:
- narrow AI use to low-risk assistance
- increase HITL, explainability, and governance language
- avoid autonomous framing

## 8. Output Safety Rules

### Rule OS-1 - No Silent Invention
If an input is missing:
- the output must either:
  - label it as an assumption
  - label it as unknown
  - call it out as an open question

### Rule OS-2 - Current Vs Target State Separation
The strategy must distinguish:
- what exists today
- what is recommended as the target
- what transition path is needed

### Rule OS-3 - Evidence-Like Honesty
The generator must not imply certainty beyond available input.

If the context is thin:
- the strategy should become conditional, not fake-complete

## 9. Section Activation Rules

### Rule SA-1 - Shift-Right Depth
Increase shift-right coverage only when:
- production validation is relevant
- observability or operational feedback is available
- release risk warrants post-release monitoring guidance

### Rule SA-2 - Non-Functional Depth
Increase non-functional strategy depth when:
- performance, security, accessibility, or resilience is explicitly important
- the domain or architecture implies these are central risks

### Rule SA-3 - Reporting And Governance Depth
Increase reporting and governance depth when:
- automation is already mature
- release decisions are subjective
- domain sensitivity is high

## Recommended Implementation Pattern

For v1, apply rules in this order:

1. validate minimum input
2. classify posture and maturity
3. apply branching rules
4. generate section emphasis
5. generate assumptions and gaps
6. render markdown output

## Binary Validation

The decision-rules layer passes only if:
- each major context variable has at least one explicit rule
- greenfield and brownfield produce meaningfully different strategy emphasis
- strong and weak automation maturity produce meaningfully different automation strategy sections
- missing inputs produce assumptions or open questions instead of silent invention
