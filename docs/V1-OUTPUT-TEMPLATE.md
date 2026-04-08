# AI Test Strategy Generator - V1 Output Template

Last Updated: 2026-04-08

## Purpose

Define the exact markdown structure that the v1 generator should produce.

This is the target output contract for the first usable version of the product.

## V1 Output Principles

- Produce one complete markdown strategy document.
- Cover the full lifecycle in a concise but structured way.
- Be explicit about assumptions, missing information, and tradeoffs.
- Make AI usage visible, bounded, and explainable.
- Adapt emphasis based on context such as greenfield vs brownfield, automation maturity, and CI/CD maturity.

## Required V1 Sections

A v1 strategy output passes structural validation only if all sections below are present.

1. `## Executive Summary`
2. `## Engagement Context`
3. `## Quality Objectives And Risk Priorities`
4. `## Lifecycle Posture`
5. `## Layered Test Strategy`
6. `## Test Types And Coverage Focus`
7. `## Automation Strategy`
8. `## CI/CD And Quality Gates`
9. `## Test Data Strategy`
10. `## Environment Strategy`
11. `## Defect, Triage, And Reporting Model`
12. `## AI Usage Model`
13. `## Assumptions, Gaps, And Open Questions`
14. `## Recommended Next Steps`

## Required Machine-Checkable Labels

To support deterministic validation, v1 output must include these exact labels somewhere in the appropriate sections:

- `Project Posture:`
- `Delivery Model:`
- `System Type:`
- `Current Automation State:`
- `Target Automation State:`
- `Current CI/CD Maturity:`
- `Target CI/CD Posture:`
- `AI Adoption Posture:`
- `Human Review Boundaries:`
- `Missing Information:`
- `Recommended Immediate Actions:`

## Section Template

## 1. Executive Summary

Purpose:
- summarize the recommended strategy in plain business language

Must include:
- project posture summary
- major quality focus
- automation posture summary
- AI posture summary

## 2. Engagement Context

Must include:
- domain
- delivery model
- greenfield or brownfield posture
- system type
- critical business flows
- key constraints

Required labels:
- `Project Posture:`
- `Delivery Model:`
- `System Type:`

## 3. Quality Objectives And Risk Priorities

Must include:
- primary quality objectives
- major release risks
- risk ranking or prioritization
- any regulatory or compliance emphasis

## 4. Lifecycle Posture

Must include:
- shift-left stance
- shift-right stance where relevant
- prevention vs detection balance
- lifecycle checkpoints from requirement to release

## 5. Layered Test Strategy

Must include:
- recommended confidence by layer
- unit / component / integration / API / UI / system / regression posture
- why each layer matters for this context
- warnings against misplaced reliance on a single layer

## 6. Test Types And Coverage Focus

Must include:
- functional coverage
- regression approach
- exploratory coverage
- non-functional priorities where relevant
- domain-specific or context-specific coverage notes

## 7. Automation Strategy

Must include:
- current automation maturity
- target automation end-state
- what to automate first
- what to keep manual for now
- phased automation adoption path

Required labels:
- `Current Automation State:`
- `Target Automation State:`

## 8. CI/CD And Quality Gates

Must include:
- current CI/CD maturity
- recommended integration posture
- test execution role in pipeline
- quality gates or release checks
- limitations if current maturity is low

Required labels:
- `Current CI/CD Maturity:`
- `Target CI/CD Posture:`

## 9. Test Data Strategy

Must include:
- data needs
- masking / privacy needs
- synthetic data recommendations if relevant
- data refresh or control concerns

## 10. Environment Strategy

Must include:
- environment needs
- dependency and integration considerations
- service virtualization need where relevant
- environment constraints and risks

## 11. Defect, Triage, And Reporting Model

Must include:
- triage approach
- ownership expectations
- reporting signals
- release-readiness or risk reporting approach
- KPI recommendations

## 12. AI Usage Model

Must include:
- where AI should help
- where AI should not be trusted alone
- human-review boundaries
- explainability and governance expectations

Required labels:
- `AI Adoption Posture:`
- `Human Review Boundaries:`

## 13. Assumptions, Gaps, And Open Questions

Must include:
- assumptions made due to missing input
- information gaps
- unresolved decisions
- risk if unanswered

Required labels:
- `Missing Information:`

## 14. Recommended Next Steps

Must include:
- immediate next actions
- medium-term actions
- suggested validation or discovery steps

Required labels:
- `Recommended Immediate Actions:`

## V1 Output Style

- markdown only
- concise but structured
- business-readable, not overly academic
- no invented details
- assumptions clearly labeled

## Binary Validation For V1 Output

A generated output passes v1 validation only if:
- all 14 required sections exist
- greenfield or brownfield posture is explicitly reflected
- automation current state and target state are both stated
- CI/CD posture is explicitly stated
- AI usage includes both allowed and constrained uses
- assumptions or gaps are surfaced when input is incomplete
- all required machine-checkable labels exist exactly as defined

If any of the above is missing, the output fails validation.
