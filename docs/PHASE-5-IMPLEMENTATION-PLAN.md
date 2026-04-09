# AI Test Strategy Generator - Phase 5 Implementation Plan

Last Updated: 2026-04-09

## Purpose

Phase 5 introduces artifact-folder ingestion so the generator can work from a small bundle of realistic project inputs instead of only one fully normalized YAML file.

The objective is not broad connector support.
The objective is to prove that multiple simple artifact sources can be mapped into the existing deterministic strategy pipeline without weakening validation.

## Phase 5 Goal

Support an `artifacts/` folder that:
- contains a small set of known files
- includes a `manifest.yaml`
- can be normalized into the same internal schema already used by the Phase 4 generator
- produces the same output shape and benchmarkable behavior as direct YAML input

## Why This Phase Matters

This phase helps with:
- more realistic engagement inputs
- better demo value
- stronger learning around strategy formation from partial source material
- a clean bridge to later connector work

It should still remain:
- deterministic
- small in scope
- easy to test
- easy to explain

## Phase 5 Design Principle

Do not parse everything.

Phase 5 should use:
- constrained file types
- constrained folder structure
- explicit manifest metadata
- deterministic mapping rules

It should not try to infer enterprise reality from arbitrary PDFs, DOCX files, screenshots, or live tools.

## Engineering Rules For Phase 5

Phase 5 implementation must follow these rules:

- deterministic validation first
- TDD in the order: red -> green -> refactor
- KISS by default
- DRY when duplication becomes meaningful
- YAGNI for all parsing and abstraction decisions
- SOLID where it improves maintainability and testability
- design patterns only when code complexity justifies them
- reuse the Phase 4 pipeline instead of creating a parallel strategy path

No Phase 5 slice is complete unless:
- deterministic tests exist
- negative and edge-case scenarios are covered where relevant
- pass/fail results are reported
- coverage details are reported for tested code

## Proposed Artifact Folder Contract

Example:

```text
artifacts/
  manifest.yaml
  project-summary.md
  requirements-summary.md
  system-landscape.md
  api-summary.yaml
  current-test-state.md
```

The `manifest.yaml` is mandatory.
All other files are optional, but missing files must be surfaced explicitly.

## Supported File Types For Phase 5 MVP

Phase 5 MVP should support only these file formats:

1. `.md`
- for human-authored summaries
- best for project summary, requirements summary, system landscape, test-state summary

2. `.yaml`
- for structured manifests and API/interface summaries
- best for `manifest.yaml` and structured metadata

3. `.yml`
- same treatment as `.yaml`

4. `.json`
- optional structured alternative for API summaries or exported structured metadata

## Not Supported In Phase 5 MVP

Do not support yet:
- `.pdf`
- `.docx`
- `.xlsx`
- `.csv`
- images
- HTML scraping
- Jira live connectors
- Xray / Zephyr live connectors
- arbitrary repository mining

These can come later if Phase 5 proves useful.

## Recommended Artifact Types

The MVP should support these logical artifact categories:

1. `project_summary`
- business goal
- delivery model
- timeline pressure
- release expectation
- audience

Recommended file:
- `project-summary.md`

2. `requirements_summary`
- critical flows
- in-scope features
- known exclusions
- missing requirement areas

Recommended file:
- `requirements-summary.md`

3. `system_landscape`
- applications in scope
- integrations
- architecture notes
- environment notes

Recommended file:
- `system-landscape.md`

4. `api_summary`
- API presence
- contract maturity
- key interfaces
- service boundaries

Recommended file:
- `api-summary.yaml` or `api-summary.json`

5. `current_test_state`
- existing automation state
- current test process
- environment maturity
- test data maturity
- known coverage or governance gaps

Recommended file:
- `current-test-state.md`

## Manifest Design

`manifest.yaml` should explicitly declare:
- engagement name
- domain
- project posture
- listed artifacts and their logical type
- optional overrides for critical structured fields

Example shape:

```yaml
engagement_name: Claims Modernization QE Strategy
domain: Insurance
project_posture: brownfield

artifacts:
  - type: project_summary
    path: project-summary.md
  - type: requirements_summary
    path: requirements-summary.md
  - type: system_landscape
    path: system-landscape.md
  - type: api_summary
    path: api-summary.yaml
  - type: current_test_state
    path: current-test-state.md

overrides:
  ai_adoption_posture: cautious
  strategy_depth: standard
```

## Mapping Strategy

Phase 5 should map artifacts into the existing input schema, not create a separate strategy path.

Target flow:

1. read `manifest.yaml`
2. validate allowed file types and required manifest fields
3. load each declared artifact
4. apply deterministic extraction rules per artifact type
5. merge extracted values into one normalized input package
6. pass that package into the existing Phase 4 pipeline

This keeps reuse high and complexity low.

## Extraction Rules

Phase 5 extraction should be intentionally simple:

- `.md` files
  - parsed as plain text
  - deterministic section-label extraction where labels exist
  - otherwise treated as summarized text inputs mapped by artifact type

- `.yaml` / `.yml`
  - parsed structurally
  - validated against expected keys for that artifact type

- `.json`
  - parsed structurally
  - validated against expected keys for that artifact type

No LLM extraction in Phase 5.

## Merge Rules

When multiple artifacts provide overlapping values:

1. explicit `manifest.yaml` overrides win
2. structured artifact fields win over free-text summaries
3. later artifact files do not silently overwrite earlier values
4. conflicting values must be surfaced as validation warnings or merge errors

## Required Validation

Phase 5 should add deterministic validation for:

- missing manifest
- unsupported file extension
- missing referenced file
- duplicate artifact type where only one is allowed
- conflicting values across artifacts
- invalid structured artifact schema
- artifact-folder-to-input-schema completeness

Phase 5 should also add deterministic tests for:

- valid artifact-folder happy path
- missing manifest
- missing referenced file
- unsupported file type
- invalid manifest schema
- duplicate artifact type handling
- conflicting values across artifacts
- invalid YAML / JSON structured artifact content
- markdown artifact with missing expected sections
- artifact-folder flow producing the same output shape as direct YAML input

## Binary Success Condition

Phase 5 passes only if:
- one artifact folder can be loaded successfully
- it maps into the existing internal input schema
- the existing deterministic pipeline produces a valid strategy output
- the output passes structural validation
- the output matches the same benchmark shape expected from direct YAML input

## Suggested Delivery Slices

1. `5.1 Artifact folder contract`
- define folder layout
- define manifest schema
- define supported artifact types

2. `5.2 Artifact loader`
- add folder loader
- validate manifest presence
- resolve relative file paths safely

3. `5.3 Artifact parsers`
- add `.md`, `.yaml/.yml`, `.json` readers
- validate supported extensions

4. `5.4 Artifact mappers`
- map each artifact type into partial input-schema fields

5. `5.5 Merge and normalization`
- merge partial inputs into one normalized package
- surface conflicts and gaps explicitly

6. `5.6 End-to-end artifact flow`
- pass merged package through the existing strategy pipeline

7. `5.7 Artifact benchmark set`
- create one or two artifact-folder benchmark scenarios
- compare shape equivalence with direct YAML input

8. `5.8 Hardening`
- expand deterministic negative and edge-case tests
- refactor only where complexity or duplication justifies it
- preserve reuse-first implementation choices

## Recommended First Benchmark Folder

Start with one brownfield scenario because:
- it uses more dimensions
- it exercises current-state reasoning
- it gives stronger coverage than the simplest greenfield case

## Recommended Phase 5 Output

At the end of Phase 5, the repo should support:
- direct structured YAML input
- artifact-folder input
- the same deterministic strategy output contract
- the same validation expectations

## Explicit Non-Goals For Phase 5

Do not add yet:
- LLM-assisted extraction
- OCR
- document parsing for arbitrary PDFs
- DOCX parsing
- spreadsheet ingestion
- live external connectors
- multi-agent orchestration

## Recommended Next Step After This Plan

Create a dedicated Phase 5 backlog, then implement in this order:

1. manifest schema
2. artifact folder loader
3. supported file readers
4. artifact mappers
5. merge layer
6. end-to-end tests
