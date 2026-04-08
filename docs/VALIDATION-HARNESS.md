# AI Test Strategy Generator - Deterministic Validation Harness

Last Updated: 2026-04-08

## Purpose

Define deterministic pass/fail validation for strategy outputs.

This harness exists so future improvements can be measured mechanically.
If a result cannot be checked deterministically, it does not belong in the core validation gate.

## Validation Philosophy

Use only binary checks in the core harness:
- pass
- fail

Do not use:
- subjective scoring
- “looks good”
- stylistic preference
- vague LLM-as-judge opinions

Those can exist later as secondary review, but not in the core gate.

## Validation Layers

## Layer 1 - Input Validation

Checks:
- required minimum fields exist
- required enum-like values are valid
- unsupported combinations are flagged

Examples:
- `project_posture` must be `greenfield` or `brownfield`
- `existing_automation_state` must be one of `none`, `limited`, `partial`, `strong`, `unknown`
- `ci_cd_maturity` must be one of `none`, `manual`, `partial`, `mature`, `unknown`

Result:
- fail fast if invalid

## Layer 2 - Structural Output Validation

Checks:
- all required section headings exist exactly
- all required machine-checkable labels exist exactly

Source of truth:
- `docs/V1-OUTPUT-TEMPLATE.md`

Result:
- fail if any required section or label is missing

## Layer 3 - Rule-Conformance Validation

Checks:
- output reflects deterministic rule consequences for the given input

Examples:
- if `project_posture = greenfield`, output must reflect stronger shift-left posture
- if `project_posture = brownfield`, output must include current-state assessment / transition emphasis
- if `existing_automation_state = strong`, output must mention optimization/governance posture, not only “build automation”
- if `ci_cd_maturity = none`, output must not imply mature current-state pipeline quality gates
- if `missing_information` is non-empty, output must surface missing information explicitly

Result:
- fail if required rule consequence is absent

## Layer 4 - Contradiction Validation

Checks:
- output must not contradict known input posture

Examples:
- input says `greenfield`; output says “existing brittle suite requires stabilization”
- input says `existing_automation_state = none`; output says “expand existing automation estate”
- input says `ci_cd_maturity = none`; output says “current pipeline gates already enforce release quality”

Result:
- fail on contradiction

## Layer 5 - Scenario-Difference Validation

Checks:
- different benchmark scenarios must produce different required emphasis markers

Examples:
- greenfield benchmark and brownfield benchmark must not produce identical lifecycle posture markers
- strong-automation scenario and no-automation scenario must not produce identical automation-state markers

Result:
- fail if scenario outputs collapse into generic sameness

## Required Deterministic Markers

To make rule-conformance checkable, the generator should emit explicit markers or labeled lines.

Recommended v1 markers:
- `Project Posture: ...`
- `Current Automation State: ...`
- `Target Automation State: ...`
- `Current CI/CD Maturity: ...`
- `Target CI/CD Posture: ...`
- `AI Adoption Posture: ...`
- `Missing Information: ...`

Recommended rule markers:
- `Shift-Left Stance: ...`
- `Layering Priority: ...`
- `Brownfield Transition Strategy: ...`
- `Automation Adoption Path: ...`

These are not only presentation choices; they are validation anchors.

## Benchmark Set

The harness should run against a small fixed benchmark set.

Initial benchmark categories:
- greenfield + low automation
- brownfield + partial automation
- strong automation + weak governance
- incomplete input / constrained context

Each benchmark must include:
- input file
- expected pass conditions
- expected fail conditions

## What The Harness Should Check First

Minimum deterministic checks for v1:

1. input schema validity
2. required headings present
3. required labels present
4. posture-specific markers present
5. contradiction markers absent
6. missing-information handling present when input is incomplete

## What The Harness Should Not Check Yet

Do not try to validate these deterministically in v1:
- writing elegance
- business persuasiveness
- nuanced domain sophistication
- whether the strategy is “smart”

These are important, but they are not suitable for the first deterministic gate.

## Success Condition

The deterministic harness is considered usable when:
- benchmark scenarios can run repeatably
- the same correct output passes every time
- rule violations fail every time
- generic or contradictory outputs fail reliably

Only after this should an autoresearch-like loop be considered.
