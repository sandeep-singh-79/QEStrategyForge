# Usage Guide

## Purpose

This guide explains how to run the current deterministic MVP end-to-end without relying on chat history.

## Current Execution Model

The current flow is:

1. Load structured YAML input
2. Validate input deterministically
3. Classify engagement context
4. Apply deterministic decision rules
5. Build a structured strategy document
6. Render markdown output
7. Validate output structure
8. Run benchmark assertions

This is intentionally pre-LLM.

## Supported Input Mode

Current MVP input mode:
- structured `.yaml` input file

Current benchmark examples:
- `benchmarks/brownfield-partial-automation.input.yaml`
- `benchmarks/greenfield-low-automation.input.yaml`
- `benchmarks/incomplete-context.input.yaml`
- `benchmarks/strong-automation-weak-governance.input.yaml`

The full input contract is documented in:
- [V1-INPUT-TEMPLATE.md](V1-INPUT-TEMPLATE.md)

## Run Validation Only

```powershell
$env:PYTHONPATH='src'
python -m ai_test_strategy_generator.cli benchmarks\brownfield-partial-automation.input.yaml
```

Current behavior:
- returns success for structurally valid input
- returns non-zero for invalid input or load failures

## Run The Full Test Suite

```powershell
$env:PYTHONPATH='src'
python -m unittest discover -s tests -v
```

This is the primary binary validation gate for current development.

## Benchmark Execution Flow

The end-to-end benchmark flow is currently exercised through tests in:
- `tests/test_end_to_end_flow.py`

The benchmark flow performs:
- input load
- input validation
- context classification
- rule application
- markdown render
- structural output validation
- benchmark assertion checks
- output write to a temporary file path

## Deterministic Validation Flow

There are three deterministic validation layers:

1. Input validation
- required fields
- enum-like field values
- fast failure on malformed or incomplete critical input

2. Structural output validation
- required headings
- required labeled lines
- missing-information handling

3. Benchmark assertion validation
- required substrings
- forbidden substrings
- posture-specific checks

The benchmark and output rules are documented in:
- [VALIDATION-HARNESS.md](VALIDATION-HARNESS.md)
- [V1-OUTPUT-TEMPLATE.md](V1-OUTPUT-TEMPLATE.md)

## Output Contract

The current output is markdown with required sections such as:
- executive summary
- engagement context
- lifecycle posture
- layered test strategy
- automation strategy
- CI/CD and quality gates
- AI usage model
- assumptions, gaps, and open questions

The renderer uses a lightweight internal output model:
- `StrategyDocument`
- `StrategySection`

This keeps the output structured without overcomplicating the MVP.

## Current Limitations

Not included yet:
- live LLM integration
- artifact-folder ingestion
- Jira / Xray / Zephyr / Confluence connectors
- arbitrary RFP parsing
- UI
- multi-agent orchestration

## Recommended Next Expansion Points

After Phase 4, the most reasonable next steps are:

1. Introduce artifact-folder ingestion in a constrained way
2. Decide whether the lightweight output model needs to grow before LLM use
3. Add bounded LLM-assisted synthesis behind the deterministic evaluator
4. Preserve benchmark-driven validation as the acceptance gate

## Development Workflow Files

This repo also contains development workflow files for local iterative work:
- `plan.md`
- `claude-memory/`
- `AGENTS.md`

They are not required for running the deterministic MVP, but they are useful for continuing the project across sessions.
