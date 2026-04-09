# AI Test Strategy Generator

`ai-test-strategy-generator` is a deterministic MVP that turns structured engagement context into a full-lifecycle QE strategy document.

It currently focuses on:
- input validation
- context classification
- deterministic rule application
- markdown strategy rendering
- structural validation
- benchmark-based pass/fail evaluation

The current implementation is intentionally pre-LLM. It focuses on making strategy logic explicit, testable, and benchmarkable before adding broader ingestion or synthesis layers.

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
- 48 tests passed
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
  Development memory files used for iterative local work.
- `plan.md`
  Development execution tracker.

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

- [Usage Guide](docs/USAGE-GUIDE.md)
- [Validation Harness](docs/VALIDATION-HARNESS.md)
- [Decision Rules](docs/DECISION-RULES.md)
- [Phase 4 Backlog](docs/PHASE-4-IMPLEMENTATION-BACKLOG.md)
- [Publishing Checklist](docs/PUBLISHING-CHECKLIST.md)

## Publishing Notes

Before publishing publicly:
- the repo uses the GNU Affero General Public License in [LICENSE](LICENSE)
- `claude-memory/`, `plan.md`, and `AGENTS.md` are intentionally kept public as part of the development workflow
- review benchmark and documentation content one more time for anything internal or proprietary

## License

This repository is licensed under the GNU Affero General Public License v3.0 or later.

- personal and commercial use are allowed under AGPL
- if modified versions are conveyed, they must remain under AGPL
- if a modified version is used for remote network interaction, AGPL requires the corresponding source to be made available to those users

See [LICENSE](LICENSE).
