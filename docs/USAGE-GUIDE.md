# Usage Guide

## Purpose

This guide explains how to run the system end-to-end in both deterministic and LLM-assisted modes.

## Supported Modes

| Mode | Input Type | LLM Required | Notes |
|---|---|---|---|
| `deterministic` | YAML file | No | Default mode, fully reproducible |
| `deterministic` | Artifact folder | No | Loads project docs, maps to YAML bundle |
| `llm_assisted` | YAML file | Yes | LLM synthesis with deterministic fallback |
| `llm_assisted` | Artifact folder | Yes | Artifact load → bundle → LLM synthesis |

## Supported Input Types

Structured YAML benchmark inputs:
- `benchmarks/brownfield-partial-automation.input.yaml`
- `benchmarks/greenfield-low-automation.input.yaml`
- `benchmarks/incomplete-context.input.yaml`
- `benchmarks/strong-automation-weak-governance.input.yaml`

Artifact folder inputs:
- `benchmarks/artifact-brownfield/` (with `benchmarks/artifact-brownfield.assertions.yaml`)
- `benchmarks/artifact-greenfield/` (with `benchmarks/artifact-greenfield.assertions.yaml`)

The full input contract is documented in:
- [V1-INPUT-TEMPLATE.md](V1-INPUT-TEMPLATE.md)

## Run Deterministic Mode — YAML Input

```powershell
$env:PYTHONPATH='src'
python -m ai_test_strategy_generator.cli benchmarks\brownfield-partial-automation.input.yaml
```

With benchmark assertions:

```powershell
python -m ai_test_strategy_generator.cli benchmarks\brownfield-partial-automation.input.yaml --assertions benchmarks\brownfield-partial-automation.assertions.yaml
```

With output written to a file:

```powershell
python -m ai_test_strategy_generator.cli benchmarks\brownfield-partial-automation.input.yaml --output output\strategy.md
```

Exit codes:
- `0` — success, all assertions passed
- `1` — input load or validation failure
- `2` — output structural validation failure
- `3` — deterministic fallback was used (LLM-assisted mode only)
- `4` — benchmark assertions not met

## Run Deterministic Mode — Artifact Folder

An artifact folder must contain a `manifest.yaml` that names all documents and declares overrides:

```powershell
python -m ai_test_strategy_generator.cli --artifact-folder benchmarks\artifact-brownfield --assertions benchmarks\artifact-brownfield.assertions.yaml
```

No `input_file` argument is needed when using `--artifact-folder`.

## Run LLM-Assisted Mode

LLM-assisted mode triggers when `--provider` is supplied. A running provider endpoint must be reachable.

**Ollama (local):**

```powershell
python -m ai_test_strategy_generator.cli benchmarks\brownfield-partial-automation.input.yaml --provider ollama --model glm-5:cloud --assertions benchmarks\brownfield-partial-automation.assertions.yaml
```

**OpenAI:**

```powershell
$env:STRATEGY_LLM_API_KEY='sk-...'
python -m ai_test_strategy_generator.cli benchmarks\brownfield-partial-automation.input.yaml --provider openai --model gpt-4o
```

**Gemini:**

```powershell
$env:STRATEGY_LLM_API_KEY='AIza...'
python -m ai_test_strategy_generator.cli benchmarks\brownfield-partial-automation.input.yaml --provider gemini --model gemini-2.0-flash
```

**LLM-assisted with artifact folder:**

```powershell
python -m ai_test_strategy_generator.cli --artifact-folder benchmarks\artifact-greenfield --provider ollama --model glm-5:cloud --assertions benchmarks\artifact-greenfield.assertions.yaml
```

Fallback behaviour: if the LLM call fails or produces invalid output, the system automatically falls back to the deterministic renderer and exits with code `3`.

## Provider Configuration

Provider settings resolve in this order (later wins):

1. Built-in defaults (`provider: ollama`, `model: glm4:latest`, `base_url: http://localhost:11434`, `temperature: 0.0`, `max_tokens: 4096`)
2. `strategy.config.yaml` in the current directory
3. Environment variables: `STRATEGY_LLM_PROVIDER`, `STRATEGY_LLM_MODEL`, `STRATEGY_LLM_BASE_URL`, `STRATEGY_LLM_TEMPERATURE`, `STRATEGY_LLM_MAX_TOKENS`
4. CLI flags: `--provider`, `--model`, `--base-url`, `--temperature`, `--max-tokens`

Example `strategy.config.yaml`:

```yaml
provider: ollama
model: glm-5:cloud
base_url: http://localhost:11434
temperature: 0.0
max_tokens: 4096
```

API keys must always come from `STRATEGY_LLM_API_KEY` environment variable. Writing an API key, token, password, or secret to `strategy.config.yaml` triggers a security warning and the value is ignored.

## Run The Test Suite

Full suite (excluding live provider tests):

```powershell
$env:PYTHONPATH='src'
python -m pytest tests/ --ignore=tests/test_live_ollama.py -q
```

All tests including live (requires a running Ollama instance):

```powershell
python -m pytest tests/ -v
```

Live tests only:

```powershell
python -m pytest tests/test_live_ollama.py -v
```

Expected baseline: 240 non-live tests passing. Live tests auto-skip when Ollama is unreachable.

## Benchmark Execution Flow

The end-to-end benchmark flows are exercised through:
- `tests/test_end_to_end_flow.py` — deterministic YAML input path
- `tests/test_artifact_end_to_end_flow.py` — deterministic artifact folder path
- `tests/test_benchmark_runner.py` — assertion runner unit tests
- `tests/test_live_ollama.py` — live LLM path end-to-end

The benchmark flow performs:
1. Input load (YAML file or artifact folder)
2. Input validation
3. Context classification
4. Rule application (deterministic) or LLM synthesis (LLM-assisted)
5. Markdown render + repair pass on invalid output
6. Structural output validation
7. Benchmark assertion checks
8. Output write to a file path (if `--output` given)

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
- live integration tests for OpenAI and Gemini providers (Ollama validated; others implemented but not live-tested)
- prompt versioning and per-scenario prompt specialization
- `.pdf`, `.docx`, `.xlsx` artifact readers (markdown, YAML, and JSON supported)
- Jira / Xray / Zephyr / Confluence connectors
- arbitrary RFP parsing
- content-level benchmark assertions on real LLM output
- UI
- multi-agent orchestration

## Phase History

| Phase | Delivered |
|---|---|
| Phase 4 | Python scaffold, input validation, context classifier, rule engine, renderer, output validator, benchmark runner, end-to-end flow |
| Phase 5 | Artifact-folder ingestion (manifest, loader, `.md/.yaml/.json` readers, mapping, merge, artifact-brownfield benchmark) |
| Phase 6 | Bounded LLM integration (prompt builder, LLMClient Protocol, FakeLLMClient, llm_flow, repair pass, CLI `--mode` flag) |
| Phase 7 | Real provider clients (Ollama, OpenAI, Gemini), client factory, config loader, ProviderConfig, CLI composition root, live Ollama tests, artifact-greenfield benchmark, 100% coverage on artifact modules |

## Development Workflow Files

This repo also contains development workflow files for local iterative work:
- `plan.md`
- `claude-memory/`
- `AGENTS.md`

They are not required for running the deterministic MVP, but they are useful for continuing the project across sessions.
