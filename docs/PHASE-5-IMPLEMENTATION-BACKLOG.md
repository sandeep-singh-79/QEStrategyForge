# AI Test Strategy Generator - Phase 5 Implementation Backlog

Last Updated: 2026-04-09

## Purpose

Turn the Phase 5 artifact-folder plan into a working, testable ingestion layer in small deterministic slices.

Engineering rules for all slices:
- keep implementation simple
- prefer reuse before adding abstractions
- follow TDD: red -> green -> refactor
- require deterministic tests for normal, negative, and edge-case paths
- report pass/fail and coverage before marking a slice complete
- refactor only when duplication or complexity becomes real

## Phase 5 Goal

Build an artifact-folder ingestion path that:
- reads `manifest.yaml`
- loads supported artifact files
- normalizes them into the existing input schema
- reuses the Phase 4 strategy pipeline
- preserves deterministic validation

## Phase 5 Success Condition

Phase 5 is complete only if:
- one artifact folder can be loaded successfully
- its contents map into the existing input schema
- the existing pipeline produces a valid strategy document
- the output passes structural validation
- at least one artifact-folder benchmark passes end-to-end

## Delivery Slices

## Slice 5.1 - Artifact Folder Contract

Status:
- Complete

Goal:
Define the explicit artifact-folder model and manifest contract.

Deliverables:
- manifest schema rules
- supported artifact type list
- supported file type list
- internal artifact dataclasses

Binary validation:
- passes if one valid manifest shape and multiple invalid manifest shapes can be checked deterministically

Current evidence:
- `artifact_loader.py` defines:
  - supported artifact types
  - supported file types
  - manifest dataclasses through `models.py`
- deterministic tests cover:
  - valid manifest
  - invalid manifest shape
  - duplicate artifact types
  - missing manifest
  - unsupported file type
  - missing referenced file

## Slice 5.2 - Artifact Loader

Status:
- Complete

Goal:
Load an artifact folder safely from disk.

Deliverables:
- folder loader
- manifest file resolution
- path safety and existence checks

Binary validation:
- passes if missing manifest, missing referenced files, and invalid folder inputs fail predictably

Current evidence:
- `load_artifact_folder(...)` implemented in `artifact_loader.py`
- folder loading validates:
  - folder existence
  - manifest presence
  - referenced file existence
  - duplicate artifact types
  - allowed file types

## Slice 5.3 - Artifact Readers

Status:
- Complete

Goal:
Read supported artifact file formats deterministically.

Deliverables:
- `.md` reader
- `.yaml/.yml` reader
- `.json` reader

Binary validation:
- passes if valid files load and invalid or unsupported formats fail deterministically

Current evidence:
- deterministic readers implemented for:
  - `.md`
  - `.yaml/.yml`
  - `.json`
- tests cover:
  - valid markdown, yaml, and json loads
  - invalid yaml failure
  - invalid json failure

Test results for Slices 5.1 to 5.3:
- `python -m unittest tests.test_artifact_loader -v`
- Result: 8 tests run, 8 passed, 0 failed
- `python -m unittest discover -s tests -v`
- Result: 56 tests run, 56 passed, 0 failed

Coverage details:
- `.tracecov-phase5-slice1/ai_test_strategy_generator.artifact_loader.cover`
  - 89 executed lines, 0 missing lines
- `.tracecov-phase5-slice1/ai_test_strategy_generator.models.cover`
  - 56 executed lines, 0 missing lines

## Slice 5.4 - Artifact Mappers

Status:
- Complete

Goal:
Map each artifact type into partial input-schema fields.

Deliverables:
- project summary mapper
- requirements summary mapper
- system landscape mapper
- API summary mapper
- current test state mapper

Binary validation:
- passes if each supported artifact type produces deterministic partial-schema fields

Current evidence:
- `artifact_mapping.py` implemented
- deterministic markdown label extraction supports:
  - scalar fields
  - list sections
- structured `.yaml/.json` artifacts are mapped directly into partial schema fields

## Slice 5.5 - Merge And Normalization

Status:
- Complete

Goal:
Merge partial artifact outputs into one normalized input package.

Deliverables:
- merge rules
- override application
- conflict detection
- gap surfacing

Binary validation:
- passes if overrides win deterministically and conflicting values are surfaced explicitly

Current evidence:
- partial artifact outputs now merge into one `InputPackage`
- manifest overrides are applied last
- conflicting scalar values fail deterministically
- list fields merge uniquely without silent duplication

Test results for Slices 5.4 to 5.5:
- `python -m unittest tests.test_artifact_mapping -v`
- Result: 4 tests run, 4 passed, 0 failed
- `python -m unittest discover -s tests -v`
- Result: 60 tests run, 60 passed, 0 failed

Coverage details:
- `.tracecov-phase5-slice2/ai_test_strategy_generator.artifact_loader.cover`
  - 89 executed lines, 0 missing lines
- `.tracecov-phase5-slice2/ai_test_strategy_generator.artifact_mapping.cover`
  - 99 executed lines, 0 missing lines
- `.tracecov-phase5-slice2/ai_test_strategy_generator.models.cover`
  - 46 executed lines, 0 missing lines

## Slice 5.6 - End-To-End Artifact Flow

Status:
- Complete

Goal:
Run the existing strategy pipeline from an artifact folder.

Deliverables:
- artifact-folder-to-strategy orchestration path
- output file generation
- structural validation reuse

Binary validation:
- passes if one artifact folder produces a valid strategy output through the existing pipeline

Current evidence:
- `artifact_end_to_end_flow.py` implemented
- direct YAML flow was refactored to reuse a shared `run_input_package_flow(...)`
- artifact-folder input now reuses the same validation, classification, rendering, structural validation, and assertion path as direct YAML input

## Slice 5.7 - Artifact Benchmarks

Status:
- Complete

Goal:
Add artifact-folder benchmarks that can be evaluated with deterministic assertions.

Deliverables:
- one brownfield benchmark folder
- optional second benchmark folder
- assertion flow reuse

Binary validation:
- passes if at least one artifact-folder benchmark passes end-to-end

Current evidence:
- committed benchmark folder added:
  - `benchmarks/artifact-brownfield/`
- committed artifact benchmark assertions added:
  - `benchmarks/artifact-brownfield.assertions.yaml`
- deterministic tests verify:
  - temp artifact-folder flow
  - committed artifact benchmark flow

Test results for Slices 5.6 to 5.7:
- `python -m unittest tests.test_artifact_end_to_end_flow -v`
- Result: 3 tests run, 3 passed, 0 failed
- `python -m unittest discover -s tests -v`
- Result: 63 tests run, 63 passed, 0 failed

Coverage details:
- `.tracecov-phase5-slice4/ai_test_strategy_generator.artifact_end_to_end_flow.cover`
  - 31 executed lines, 0 missing lines
- `.tracecov-phase5-slice4/ai_test_strategy_generator.artifact_loader.cover`
  - 90 executed lines, 0 missing lines
- `.tracecov-phase5-slice4/ai_test_strategy_generator.artifact_mapping.cover`
  - 99 executed lines, 0 missing lines
- `.tracecov-phase5-slice4/ai_test_strategy_generator.end_to_end_flow.cover`
  - 51 executed lines, 0 missing lines

## Slice 5.8 - Hardening

Status:
- Complete

Goal:
Strengthen negative and edge-case behavior before expanding scope.

Deliverables:
- stronger validation errors
- additional edge-case tests
- small refactors only where complexity justifies them

Binary validation:
- passes if the known Phase 5 edge cases fail or pass predictably

Current evidence:
- loader hardening now rejects:
  - invalid `project_posture` values in the manifest
  - empty artifact lists
  - referenced paths that resolve to directories instead of files
  - referenced paths outside the artifact root
- end-to-end hardening confirms incomplete artifact sets fail through the existing validation path
- no second ingestion pipeline was introduced; hardening kept reuse intact

Test results for Slice 5.8:
- `python -m unittest tests.test_artifact_loader -v`
- Result: 12 tests run, 12 passed, 0 failed
- `python -m unittest discover -s tests -v`
- Result: 69 tests run, 69 passed, 0 failed

Coverage details:
- `.tracecov-phase5-hardening/ai_test_strategy_generator.artifact_end_to_end_flow.cover`
  - 33 lines, 93% coverage
- `.tracecov-phase5-hardening/ai_test_strategy_generator.artifact_loader.cover`
  - 112 lines, 91% coverage
- `.tracecov-phase5-hardening/ai_test_strategy_generator.artifact_mapping.cover`
  - 118 lines, 83% coverage
- `.tracecov-phase5-hardening/ai_test_strategy_generator.end_to_end_flow.cover`
  - 55 lines, 87% coverage

## Immediate Implementation Order

1. Slice 5.1
2. Slice 5.2
3. Slice 5.3
4. Slice 5.4
5. Slice 5.5
6. Slice 5.6
7. Slice 5.7
8. Slice 5.8
