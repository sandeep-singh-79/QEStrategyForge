# AI Test Strategy Generator - Phased Implementation

Last Updated: 2026-04-08

## Recommendation

Build this product in phases that increase value in this order:

1. structured thinking
2. deterministic output shape
3. constrained generation
4. artifact-folder ingestion
5. stronger validation and scenario coverage
6. optional external connectors later

This keeps the MVP useful while avoiding connector-first overbuild.

## Phase 1 - Product Definition

Goal:
Define exactly what the product will generate and what inputs it needs.

Deliverables:
- implementation plan
- learning guide
- scenario library
- v1 input template
- v1 output skeleton

Validation:
- passes if the product purpose, input model, output model, and non-goals are documented

Current status:
- Complete

Evidence:
- `docs/IMPLEMENTATION-PLAN.md`
- `docs/LEARNING-GUIDE.md`
- `docs/SCENARIO-LIBRARY.md`
- `docs/V1-INPUT-TEMPLATE.md`
- `docs/V1-OUTPUT-TEMPLATE.md`

## Phase 2 - V1 Strategy Schema

Goal:
Define the exact structure of the strategy document.

Deliverables:
- section-by-section output template
- required sections list
- assumption and gap-handling rules
- shift-left, layered testing, automation maturity, and AI posture fields in schema

Validation:
- passes if one reviewer can inspect the template and clearly tell what the generator must produce

Current status:
- Complete

Evidence:
- `docs/V1-OUTPUT-TEMPLATE.md`

## Phase 3 - Rules And Decision Logic

Goal:
Capture deterministic strategy rules before heavy generation logic.

Examples:
- if `greenfield`, strengthen shift-left and lower-layer automation emphasis
- if `brownfield`, strengthen regression containment and transition planning
- if `existing_automation_state = strong`, reduce emphasis on “build more scripts” and increase governance/optimization emphasis
- if `ci_cd_maturity = none`, avoid pretending full pipeline quality gates already exist

Deliverables:
- decision rules document
- edge-case handling rules
- input validation rules

Validation:
- passes if the same input always yields the same rule decisions

Current status:
- Not started

Next move:
- create a decision-rules document covering posture, maturity, edge cases, and assumption handling

Updated status:
- Complete

Evidence:
- `docs/DECISION-RULES.md`

## Phase 4 - First Working Generator

Goal:
Generate a usable markdown strategy from structured input.

Scope:
- read a single structured file
- produce markdown output
- include assumptions and missing info section
- include AI, automation, lifecycle, reporting, and governance sections

Validation:
- passes if one sample input produces a complete markdown strategy with all required sections present

Current status:
- Not started

## Phase 5 - Artifact-Folder MVP

Goal:
Support a small `artifacts/` folder instead of only a single structured file.

Scope:
- read `manifest.yaml`
- read a few known file types
- map them into the v1 schema
- produce the same strategy output

Recommended supported files:
- project summary
- requirements summary
- system landscape
- API summary
- current test state summary

Validation:
- passes if the same scenario can be run via structured input and artifact-folder input with equivalent output shape

Current status:
- Not started

## Phase 6 - Learning And Scenario Deepening

Goal:
Make the repo educational and portfolio-ready.

Deliverables:
- scenario comparison outputs
- why-the-strategy-changed explanations
- greenfield vs brownfield examples
- automation maturity comparison examples

Validation:
- passes if at least 4 scenarios produce meaningfully different strategies for explainable reasons

Current status:
- In progress

Evidence:
- `docs/LEARNING-GUIDE.md`
- `docs/SCENARIO-LIBRARY.md`

Gap remaining:
- sample strategy outputs and direct scenario comparisons are not yet created

## Phase 7 - Optional Connector Expansion

Goal:
Add direct external-source ingestion only after the core strategy flow works.

Possible later sources:
- Jira
- Xray / Zephyr
- OpenAPI specs
- test case repositories
- proposal / RFP documents

Recommendation:
- start with file-based exports or summaries before live API integrations

Validation:
- passes if connector-based input maps cleanly into the same internal schema without changing the core strategy logic

Current status:
- Intentionally deferred

## MVP Recommendation

For the MVP, support:
- one structured input file
- one optional artifact folder
- one markdown output

Do not support in the first MVP:
- live Jira integration
- direct RFP parsing from many unstructured formats
- direct test management connectors
- broad multi-agent orchestration
- UI app before the strategy engine works

## Why This MVP

It gives you:
- faster learning
- easier debugging
- clearer validation
- stronger demoability
- less platform drag

It also matches your current goal:
learn strategy formation while building something showcase-worthy.

## Where We Stand Now

Overall status:
- strong planning foundation established
- input and output contracts are defined
- learning layer exists
- implementation logic has not started yet

Immediate next phase:
- Phase 4 - First Working Generator

Recommended next concrete artifact:
- first generator implementation using the defined input, output, and rule contracts

Why:
- the planning foundation is now strong enough to start building
