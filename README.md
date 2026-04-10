# AI Test Strategy Generator

`ai-test-strategy-generator` generates full-lifecycle QE strategy documents from structured engagement context.

It supports two generation modes:
- **Deterministic mode** — explicit rules, fully reproducible, no LLM required
- **LLM-assisted mode** — bounded synthesis through OpenAI-compatible, Gemini, or Ollama providers, with automatic deterministic fallback on failure

Both modes share the same input contract, validation pipeline, benchmark assertion layer, and output contract.

Key capabilities:
- Input validation with fast failure on missing or malformed fields
- Context classification across greenfield, brownfield, and partial-automation scenarios
- Deterministic rule engine producing engagement-specific strategies
- Artifact-folder ingestion: load project summaries, API docs, test-state files, and requirements from a folder
- Versioned prompt templates with per-scenario specialization (greenfield, brownfield, compliance-heavy, incomplete-context)
- LLM-assisted synthesis over a normalized context bundle, with automatic repair and deterministic fallback
- Four-layer provider configuration (built-in defaults → config file → env vars → CLI flags)
- Benchmark-driven pass/fail evaluation on all scenarios — structural and content-level assertions
- Side-by-side deterministic vs LLM comparison with `--compare`
- 268+ automated tests; 100% pass rate required before merge

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

## Quick Start

Set `PYTHONPATH` once:

```powershell
$env:PYTHONPATH='src'
```

Deterministic path — structured YAML input:

```powershell
python -m ai_test_strategy_generator.cli benchmarks\brownfield-partial-automation.input.yaml
```

Deterministic path — artifact folder:

```powershell
python -m ai_test_strategy_generator.cli --artifact-folder benchmarks\artifact-brownfield --assertions benchmarks\artifact-brownfield.assertions.yaml
```

LLM-assisted path — Ollama:

```powershell
python -m ai_test_strategy_generator.cli benchmarks\brownfield-partial-automation.input.yaml --assertions benchmarks\brownfield-partial-automation.assertions.yaml --provider ollama --model glm-5:cloud
```

LLM-assisted path — OpenAI:

```powershell
$env:STRATEGY_LLM_API_KEY='sk-...'
python -m ai_test_strategy_generator.cli benchmarks\brownfield-partial-automation.input.yaml --provider openai --model gpt-4o
```

LLM-assisted path — with side-by-side comparison report:

```powershell
python -m ai_test_strategy_generator.cli benchmarks\brownfield-partial-automation.input.yaml `
  --mode llm_assisted --provider ollama --model glm-5:cloud `
  --assertions benchmarks\brownfield-partial-automation.assertions.yaml `
  --output output\strategy-llm.md `
  --compare output\comparison.md
```

Run the test suite (excluding live provider tests):

```powershell
python -m pytest tests/ -k "not live" -q
```

Run live Ollama benchmarks (requires a running Ollama instance):

```powershell
python -m pytest tests/test_live_ollama.py -v
```

## Configuration

Provider defaults can be placed in a `strategy.config.yaml` file:

```yaml
provider: ollama
model: glm-5:cloud
base_url: http://localhost:11434
temperature: 0.0
max_tokens: 4096
```

API keys must always come from the `STRATEGY_LLM_API_KEY` environment variable, never from config files.

CLI flags (`--provider`, `--model`, `--base-url`, `--temperature`, `--max-tokens`) override everything.

## Documentation

### Usage and Reference
- [Usage Guide](docs/USAGE-GUIDE.md)
- [Prompt Engineering](docs/PROMPT-ENGINEERING.md)
- [Validation Harness](docs/VALIDATION-HARNESS.md)
- [Decision Rules](docs/DECISION-RULES.md)
- [Input Template](docs/V1-INPUT-TEMPLATE.md)
- [Output Template](docs/V1-OUTPUT-TEMPLATE.md)
- [Publishing Checklist](docs/PUBLISHING-CHECKLIST.md)

### Learning
- [Learning Guide](docs/LEARNING-GUIDE.md) — navigator for all learning content
- [Situations Catalogue](docs/SITUATIONS-CATALOGUE.md) — 12 core + 8 edge case scenarios, full case-study depth
- [Strategy Anti-Patterns](docs/STRATEGY-ANTI-PATTERNS.md) — 8 named mistakes with diagnosis and remediation
- [Strategy Frameworks](docs/STRATEGY-FRAMEWORKS.md) — portable mental models and comparison tables

### Testing Type Deep-Dives
- [Contract Testing](docs/TESTING-TYPE-CONTRACT.md)
- [Performance Testing](docs/TESTING-TYPE-PERFORMANCE.md)
- [Security Testing in the Pipeline](docs/TESTING-TYPE-SECURITY.md)
- [Exploratory Testing](docs/TESTING-TYPE-EXPLORATORY.md)
- [Accessibility Testing](docs/TESTING-TYPE-ACCESSIBILITY.md)
- [Chaos and Resilience Testing](docs/TESTING-TYPE-CHAOS.md)

## Development Status

As of Phase 7 (2026-04-09):
- 240 non-live automated tests passing
- Live Ollama integration validated with `glm-5:cloud`
- OpenAI-compatible and Gemini clients implemented (live tests deferred)
- Artifact-folder ingestion: 100% statement coverage
- All four benchmark scenarios pass deterministically; artifact-brownfield and artifact-greenfield pass end-to-end

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
