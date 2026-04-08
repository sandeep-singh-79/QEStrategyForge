# AI Test Strategy Generator

`ai-test-strategy-generator` is a deterministic MVP that turns structured engagement context into a full-lifecycle QE strategy document.

It currently focuses on:
- input validation
- context classification
- deterministic rule application
- markdown strategy rendering
- structural validation
- benchmark-based pass/fail evaluation

This repo is part of the broader upskilling program in [`Agentic Upskilling`](C:/Data/IdeaProjects/Agentic%20Upskilling), but it has its own repo-local plan and memory layer.

## Current Status

Phase 4 implementation is complete for the deterministic MVP path.

Completed slices:
- 4.1 runtime foundation
- 4.2 input loading
- 4.3 input validation
- 4.4 context classification
- 4.5 decision rule engine
- 4.6 lightweight output model
- 4.7 deterministic renderer
- 4.8 structural output validator
- 4.9 benchmark assertion runner
- 4.10 end-to-end first flow
- 4.11 phase 4 hardening

Current baseline:
- 46 tests passed
- 0 failed
- 4 benchmark scenarios pass end-to-end

## Repo Layout

- `src/ai_test_strategy_generator/`
  Deterministic generator code.
- `tests/`
  Automated test suite.
- `benchmarks/`
  Benchmark inputs and assertion files.
- `docs/`
  Planning, rules, learning, and usage documentation.
- `claude-memory/`
  Durable repo memory for future sessions.
- `plan.md`
  Active session/cycle execution tracker.

## First-Time Usage

Use the CLI validation path:

```powershell
$env:PYTHONPATH='src'
python -m ai_test_strategy_generator.cli benchmarks\brownfield-partial-automation.input.yaml
```

Run the test suite:

```powershell
$env:PYTHONPATH='src'
python -m unittest discover -s tests -v
```

## Where To Look Next

- [docs/PHASE-4-IMPLEMENTATION-BACKLOG.md](C:/Data/IdeaProjects/Agentic%20Upskilling/ai-test-strategy-generator/docs/PHASE-4-IMPLEMENTATION-BACKLOG.md)
- [docs/VALIDATION-HARNESS.md](C:/Data/IdeaProjects/Agentic%20Upskilling/ai-test-strategy-generator/docs/VALIDATION-HARNESS.md)
- [docs/DECISION-RULES.md](C:/Data/IdeaProjects/Agentic%20Upskilling/ai-test-strategy-generator/docs/DECISION-RULES.md)
- [docs/USAGE-GUIDE.md](C:/Data/IdeaProjects/Agentic%20Upskilling/ai-test-strategy-generator/docs/USAGE-GUIDE.md)
- [claude-memory/memory.md](C:/Data/IdeaProjects/Agentic%20Upskilling/ai-test-strategy-generator/claude-memory/memory.md)
