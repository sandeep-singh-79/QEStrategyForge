# AI Test Strategy Generator - Scenario Library

Last Updated: 2026-04-08

## Purpose

Capture common situations the product should handle and use them as both design inputs and learning cases.

## Scenario 1 - Insurance Platform Modernization

Context:
- insurance domain
- multiple integrated systems
- moderate regulatory sensitivity
- partial automation maturity

Strategy emphasis:
- integration coverage
- policy / claims business flow risk
- auditability
- test data controls
- targeted automation acceleration
- phased shift-left improvement

## Scenario 2 - Legacy Internal Enterprise App

Context:
- brittle UI
- weak environments
- little structured automation
- undocumented edge cases in SME memory

Strategy emphasis:
- exploratory support
- critical-path regression baseline
- gradual automation plan
- stronger defect triage and knowledge capture
- brownfield transition rather than clean-slate automation assumptions

## Scenario 2A - Greenfield Digital Product

Context:
- new product or new platform
- opportunity to embed quality early
- architecture and delivery practices are still being shaped

Strategy emphasis:
- shift-left quality controls
- layered automation from lower layers upward
- CI/CD-native quality gates
- prevention and fast feedback over late heavy regression

## Scenario 3 - API-First Digital Product

Context:
- service-heavy architecture
- CI/CD maturity is high
- UI is light relative to API surface

Strategy emphasis:
- contract and integration testing
- environment dependency management
- observability-backed validation
- risk-based regression selection
- stronger lower-layer and API-first confidence model

## Scenario 4 - Tight Timeline Transformation

Context:
- compressed deadlines
- stakeholder pressure
- limited QE capacity

Strategy emphasis:
- minimum viable quality baseline
- strong tradeoff communication
- smoke and critical-path focus
- phased automation strategy

## Scenario 5 - AI-Low-Trust Enterprise

Context:
- leadership interest in AI is cautious
- governance and explainability concerns are high

Strategy emphasis:
- low-risk AI usage first
- explicit HITL controls
- audit trail and traceability
- no autonomous quality decisions

## Scenario 6 - Strong Automation, Weak Governance

Context:
- many scripts already exist
- release decisions remain subjective
- reporting is fragmented

Strategy emphasis:
- release readiness model
- KPI and risk reporting
- quality gate design
- regression optimization before more framework growth

## Scenario 7 - Existing Automation, Brownfield Upgrade

Context:
- automation already exists
- quality is uneven
- CI/CD integration may be partial or unreliable

Strategy emphasis:
- assess reuse vs retire vs refactor
- align automation to target architecture and lifecycle needs
- improve CI/CD execution reliability
- define the target automation end-state before adding more coverage
