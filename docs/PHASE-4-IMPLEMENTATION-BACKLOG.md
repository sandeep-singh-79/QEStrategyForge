# AI Test Strategy Generator - Phase 4 Implementation Backlog

Last Updated: 2026-04-08

## Purpose

Turn the planning foundation into a working generator in small, testable increments.

This backlog is intentionally detailed.
Each item should be small enough to validate with binary pass/fail checks.

Engineering rules for all slices:
- keep implementation simple
- prefer reuse before adding new abstractions
- refactor when complexity increases
- do not mark a slice complete until its code is tested
- report test results and coverage after each tested slice
- follow red, green, refactor in practice

## Phase 4 Goal

Build the first working generator flow that:
- reads structured input
- validates the input deterministically
- classifies engagement context
- applies deterministic decision rules
- renders a markdown strategy using the v1 output contract
- can be checked against benchmark assertions

## Phase 4 Success Condition

Phase 4 is complete only if:
- a CLI command can read one benchmark input file
- the generator produces a markdown strategy document
- the output passes structural validation
- the output passes at least one benchmark assertion set

## Delivery Slices

## Slice 4.1 - Repo Runtime Foundation

Status:
- Complete

Goal:
Create the minimal code/runtime structure required to run the generator locally.

Deliverables:
- Python project scaffold
- source folder structure
- CLI entry point
- output folder convention

Tasks:
- create `pyproject.toml`
- create `src/ai_test_strategy_generator/`
- create `src/ai_test_strategy_generator/__init__.py`
- create `src/ai_test_strategy_generator/cli.py`
- create `src/ai_test_strategy_generator/main.py`
- decide local run command

Binary validation:
- passes if a local command starts the CLI without import errors

Current evidence:
- package scaffold created under `src/ai_test_strategy_generator/`
- CLI entrypoint created
- local validation command runs successfully with `PYTHONPATH=src`
- tested via `python -m unittest discover -s tests -v`
- CLI module coverage: 100%

## Slice 4.2 - Input Loading

Status:
- Complete

Goal:
Read v1 structured input files reliably.

Deliverables:
- YAML input loader
- normalized in-memory input model

Tasks:
- create `input_loader.py`
- load YAML safely
- normalize absent optional lists to empty lists where needed
- preserve original values for validation and error reporting

Binary validation:
- passes if benchmark `.input.yaml` files load without parser errors

Current evidence:
- YAML loader implemented in `input_loader.py`
- benchmark input successfully loaded through the CLI flow
- input loader coverage: 100%

## Slice 4.3 - Input Validation

Status:
- Complete

Goal:
Validate input deterministically before any strategy generation begins.

Deliverables:
- input validator
- explicit validation errors

Tasks:
- create `validators/input_validator.py`
- enforce required fields from `docs/V1-INPUT-TEMPLATE.md`
- enforce enum-like values:
  - `project_posture`
  - `existing_automation_state`
  - `ci_cd_maturity`
  - `ai_adoption_posture`
  - `strategy_depth`
- fail fast on invalid inputs

Binary validation:
- passes if valid benchmark inputs pass and malformed inputs fail predictably

Current evidence:
- deterministic validator implemented in `validators/input_validator.py`
- `brownfield-partial-automation.input.yaml` passes validation
- validator coverage: 100%

Test results for Slices 4.1 to 4.9:
- `python -m unittest discover -s tests -v`
- Result: 39 tests run, 39 passed, 0 failed

Negative and edge-case coverage included:
- missing file
- unsupported extension
- invalid YAML
- non-mapping YAML
- scalar-to-list normalization
- invalid enum values
- non-string enum values
- blank required strings
- missing required CLI argument
- invalid input returning non-zero validation status

Coverage details for tested code:
- `ai_test_strategy_generator.benchmark_runner`: 100%
- `ai_test_strategy_generator.cli`: 100%
- `ai_test_strategy_generator.context_classifier`: 100%
- `ai_test_strategy_generator.input_loader`: 100%
- `ai_test_strategy_generator.main`: 100%
- `ai_test_strategy_generator.models`: 100%
- `ai_test_strategy_generator.output_validator`: 100%
- `ai_test_strategy_generator.renderer`: 100%
- `ai_test_strategy_generator.rule_engine`: 100%
- `ai_test_strategy_generator.validators.input_validator`: 100%

## Slice 4.4 - Context Classification

Status:
- Complete

Goal:
Convert raw input into explicit strategy-driving classifications.

Deliverables:
- context classifier
- normalized classification object

Tasks:
- create `context_classifier.py`
- classify:
  - posture
  - automation maturity
  - CI/CD maturity
  - system architecture emphasis
  - regulatory sensitivity
  - information completeness
- ensure outputs are machine-readable

Binary validation:
- passes if the same input always produces the same classification result

Current evidence:
- `context_classifier.py` implemented
- context classifier tests added
- deterministic classifier behavior verified across greenfield, brownfield, legacy, regulated, and incomplete-context cases

## Slice 4.5 - Decision Rule Engine

Status:
- Complete

Goal:
Apply deterministic strategy rules to the classified context.

Deliverables:
- rule engine
- strategy decision object

Tasks:
- create `rule_engine.py`
- encode rules from `docs/DECISION-RULES.md`
- produce explicit outputs such as:
  - shift-left stance
  - layering priority
  - brownfield transition strategy
  - automation adoption path
  - CI/CD posture
  - AI usage posture
- separate current-state observations from target-state recommendations

Binary validation:
- passes if benchmark scenarios produce the required rule consequences

Current evidence:
- `rule_engine.py` implemented
- deterministic rule tests added for:
  - greenfield + no automation
  - brownfield + partial automation
  - strong automation + mature CI/CD
  - incomplete context
- rule outputs now include:
  - shift-left stance
  - layering priority
  - brownfield transition strategy
  - automation adoption path
  - CI/CD posture
  - governance depth
  - reporting emphasis
  - assumption mode
  - strategy confidence

## Slice 4.6 - Output Model

Status:
- Complete

Goal:
Represent the v1 strategy output in a structured internal form before markdown rendering.

Deliverables:
- output model or structured dictionary contract

Tasks:
- create `models.py` or equivalent output schema module
- define fields matching `docs/V1-OUTPUT-TEMPLATE.md`
- map rule-engine outputs into section-ready content

Binary validation:
- passes if all 14 required sections can be represented internally before rendering

Current evidence:
- lightweight output model added in `models.py`
- `StrategyDocument` and `StrategySection` now represent renderer output structure
- renderer refactored to build a structured document before markdown conversion
- tests added for output model markdown rendering and structured section creation

## Slice 4.7 - Deterministic Renderer

Status:
- Complete

Goal:
Render a first working markdown strategy without depending on an LLM yet.

Deliverables:
- markdown renderer
- required headings and labels emitted exactly

Tasks:
- create `renderer.py`
- render exact section headings from `docs/V1-OUTPUT-TEMPLATE.md`
- render exact machine-checkable labels
- render assumptions and missing-information blocks explicitly

Binary validation:
- passes if all required headings and labels exist exactly in generated markdown

Current evidence:
- `renderer.py` implemented
- renderer tests added for:
  - required headings and labels
  - rule-output reflection
  - missing-information and open-question surfacing
- renderer emits all required v1 section headings and machine-checkable labels

## Slice 4.8 - Structural Output Validator

Status:
- Complete

Goal:
Check the generated markdown against the v1 output contract.

Deliverables:
- output validator

Tasks:
- create `validators/output_validator.py`
- verify required headings
- verify required labels
- verify presence of current vs target-state labels
- verify assumptions block appears when missing input exists

Binary validation:
- passes if structurally incomplete outputs fail every time

Current evidence:
- `output_validator.py` implemented
- validator tests added for:
  - valid complete structure
  - missing heading failure
  - missing label failure
  - missing-information label failure
- validator checks required headings and labels against the v1 output contract

## Slice 4.9 - Benchmark Assertion Runner

Status:
- Complete

Goal:
Run deterministic assertions against benchmark outputs.

Deliverables:
- benchmark runner
- assertion parser

Tasks:
- create `benchmark_runner.py`
- load `.assertions.yaml`
- check:
  - required headings
  - required labels
  - required substrings
  - forbidden substrings
- emit pass/fail summary

Binary validation:
- passes if one benchmark run returns a reliable pass/fail result

Current evidence:
- `benchmark_runner.py` implemented
- assertion-runner tests added for:
  - successful assertion pass
  - missing required content failure
  - forbidden substring failure
  - invalid assertions file failure
- benchmark assertions can now be checked deterministically from YAML

## Slice 4.10 - End-to-End First Flow

Status:
- Complete

Goal:
Run one benchmark scenario end-to-end.

Deliverables:
- executable end-to-end flow
- sample output artifact

Tasks:
- wire CLI -> input loader -> validator -> classifier -> rule engine -> renderer -> output validator
- run against `benchmarks/brownfield-partial-automation.input.yaml`
- save result under `outputs/`

Binary validation:
- passes if the benchmark strategy output is generated and passes its assertions

Current evidence:
- `end_to_end_flow.py` implemented
- end-to-end tests added for:
  - brownfield partial automation
  - greenfield low automation
  - incomplete context
  - strong automation with weak governance
  - assertion failure path
- benchmark outputs now pass deterministic structural validation and benchmark assertions end-to-end

## Slice 4.11 - Phase 4 Hardening

Status:
- Complete

Goal:
Increase reliability before LLM-assisted generation is added.

Deliverables:
- improved error messages
- second and third benchmark passing
- clearer logging

Tasks:
- run greenfield benchmark
- run incomplete-context benchmark
- fix deterministic branching gaps
- document remaining known limitations

Binary validation:
- passes if at least 3 benchmarks pass deterministically

Current evidence:
- 4 benchmark scenarios now pass deterministically end-to-end:
  - `brownfield-partial-automation`
  - `greenfield-low-automation`
  - `incomplete-context`
  - `strong-automation-weak-governance`
- hardening fix applied in `renderer.py`:
  - brownfield transition guidance is emitted only when applicable
  - explicit `quality gate`, `release`, and `reporting` language is present for benchmarkable governance output
- `python -m unittest discover -s tests -v`
- Result: 46 tests run, 46 passed, 0 failed

Coverage details for the hardening run:
- traced production modules in `.tracecov/` with `0` missing lines:
  - `benchmark_runner.py`
  - `cli.py`
  - `context_classifier.py`
  - `end_to_end_flow.py`
  - `input_loader.py`
  - `models.py`
  - `output_validator.py`
  - `renderer.py`
  - `rule_engine.py`
  - `validators/input_validator.py`
- targeted `main.py` trace in `.tracecov-main-harden/` shows:
  - `main.py`: 22 executed lines, 0 missing lines
  - `input_loader.py`: 29 executed lines, 0 missing lines
  - `models.py`: 14 executed lines, 0 missing lines
  - `validators/input_validator.py`: 38 executed lines, 0 missing lines

## Slice 4.12 - Initial README

Status:
- Complete

Goal:
Provide a clear starting point for execution and first-time usage.

Deliverables:
- repository `README.md`

Tasks:
- explain what the repo does
- explain current phase and current implementation status
- explain how to run the validator CLI
- explain where planning, rules, benchmarks, and memory files live

Binary validation:
- passes if a new reader can locate setup, run command, and core docs from the README alone

Current evidence:
- root `README.md` added
- README covers purpose, current phase status, run command, test command, repo layout, and core docs

## Slice 4.13 - Detailed Usage Guide

Status:
- Complete

Goal:
Provide a deeper operator guide for local execution and future extensions.

Deliverables:
- detailed usage guide under `docs/`

Tasks:
- document input modes
- document benchmark execution flow
- document deterministic validation flow
- document expected output contract
- document current limitations and next expansion points

Binary validation:
- passes if the guide explains how to execute the current flow end-to-end without relying on chat history

Current evidence:
- `docs/USAGE-GUIDE.md` added
- usage guide covers:
  - current execution model
  - input mode
  - CLI usage
  - full test execution
  - benchmark flow
  - deterministic validation layers
  - output contract
  - current limitations
  - next expansion points

## Deferred From Phase 4

These items are intentionally not in the first working flow:
- live LLM integration
- artifact-folder ingestion
- Jira / Xray / Zephyr / Confluence connectors
- direct RFP parsing from arbitrary documents
- multi-agent orchestration
- UI

## Recommended Implementation Order

1. Slice 4.1
2. Slice 4.2
3. Slice 4.3
4. Slice 4.4
5. Slice 4.5
6. Slice 4.7
7. Slice 4.8
8. Slice 4.9
9. Slice 4.10
10. Slice 4.11
11. Slice 4.12
12. Slice 4.13

Note:
Slice 4.6 can be done lightly in parallel with 4.5 and 4.7 if a formal model feels heavy for the first pass.

## Binary Milestone Gates

### Gate A - Foundation Ready
Passes if:
- CLI runs
- benchmark input loads
- input validation works

### Gate B - Rule Engine Ready
Passes if:
- context classification is deterministic
- rule engine emits posture-specific decisions

### Gate C - Renderer Ready
Passes if:
- markdown output contains all required headings and labels

### Gate D - First Flow Ready
Passes if:
- one benchmark passes end-to-end

### Gate E - Phase 4 Stable
Passes if:
- three benchmarks pass end-to-end
- known failures are documented

Current status:
- Passed

## Learning Focus During Implementation

This phase should teach:
- how strategy logic can be encoded as deterministic rules
- how classification affects output posture
- how to separate rule-driven behavior from later LLM-assisted synthesis
- how to build evaluation-first systems rather than intuition-first systems
