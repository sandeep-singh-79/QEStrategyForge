# Prompt Engineering Guide

This document explains how the prompt template system works, how to read and extend templates, how the output contract is enforced, and how to evaluate prompt quality using the `--compare` flag.

---

## Why Bounded Prompting

The LLM does not receive a free-form instruction to "write a test strategy."

It receives a fully assembled context bundle containing:
1. Normalized engagement context from the input file or artifact folder
2. Deterministic classification results (6 dimensions)
3. Deterministic rule decisions (9 decision keys)
4. An explicit output contract listing every required heading and label
5. Scenario-specific instructions targeting the engagement type

This bounds the LLM to the engagement at hand and to a defined output shape. It reduces hallucination risk and ensures the output can be validated structurally and for content.

---

## Template Architecture

Templates live in `src/ai_test_strategy_generator/prompts/v1/`.

There are two layers:

### Base Template (`base.txt`)

The structural wrapper. Assembled at runtime by `prompt_builder.py` using Python `str.format()`:

```
{engagement_context}       → normalized input fields
{classifications}          → 6 classification keys and values
{decisions}                → 9 deterministic decision keys and values
{required_headings}        → all 14 required section headings
{required_labels}          → all 18 required labeled lines
{scenario_instructions}    → content of the selected scenario template
```

The base template instructs the LLM to:
- include all required headings and labels verbatim
- embed every decision value as a labeled line in its natural section
- not invent information absent from the engagement context
- surface all assumptions explicitly

### Scenario Templates

Scenario templates provide additional instructions tuned to the engagement type. They are plain text with no placeholders — they are injected verbatim into `{scenario_instructions}`.

| Template | File | When Selected |
|---|---|---|
| Incomplete context | `incomplete_context.txt` | `information_completeness == incomplete` |
| Compliance-heavy | `compliance_heavy.txt` | `regulatory_sensitivity == high` |
| Greenfield | `greenfield.txt` | `project_posture == greenfield` |
| Brownfield | `brownfield.txt` | all other cases |

---

## Scenario Selection Logic

Selection follows a priority chain in `prompt_builder._select_scenario()`:

```
incomplete_context  →  highest priority
compliance_heavy    →  second
greenfield          →  third
brownfield          →  default fallback
```

Priority rationale:

- **incomplete_context** always wins because an under-specified engagement needs conditional language throughout the output, regardless of posture or regulation level. A greenfield-incomplete engagement gets `incomplete_context` instructions, not `greenfield`.
- **compliance_heavy** overrides posture because regulatory traceability requirements shape every section, not just governance. A greenfield-regulated engagement needs compliance framing even though it is new build.
- **greenfield** overrides `brownfield` because the two require opposite strategy patterns (build from scratch vs. assess and stabilize). Mixing them produces incoherent guidance.
- **brownfield** is the default because most real-world engagements involve existing systems, and defaulting to conservative posture is safer than defaulting to greenfield.

---

## Classification Dimensions That Drive Scenario Selection

| Dimension | Source Field | Values |
|---|---|---|
| `project_posture` | `project_posture` in input | `greenfield`, `brownfield`, or empty |
| `regulatory_sensitivity` | `domain` + `regulatory_or_compliance_needs` | `high`, `medium`, `low` |
| `information_completeness` | unknown/missing field count in input | `incomplete`, `partial`, `sufficient` |

`information_completeness` becomes `incomplete` when three or more of: `existing_automation_state`, `ci_cd_maturity`, `environment_maturity`, `test_data_maturity` are unknown, or when the `missing_information` list has three or more entries.

`regulatory_sensitivity` is `high` for regulated domains (insurance, banking, healthcare, fintech) regardless of explicit compliance fields.

---

## Output Contract

The base template embeds all required headings and required labels directly in the prompt:

**14 Required Headings** — every heading listed in `output_validator.REQUIRED_HEADINGS`. The LLM is instructed to include all of them.

**18 Required Labels** — every label listed in `output_validator.REQUIRED_LABELS`. These include all engagement context fields plus every deterministic decision value:

| Label Category | Labels |
|---|---|
| Engagement context | `Project Posture:`, `Delivery Model:`, `System Type:`, `Current Automation State:`, `Target Automation State:`, `Current CI/CD Maturity:`, `AI Adoption Posture:`, `Human Review Boundaries:`, `Missing Information:` |
| Infrastructure decisions | `Target CI/CD Posture:`, `Governance Depth:`, `Reporting Emphasis:` |
| Strategy decisions | `Shift-Left Stance:`, `Layering Priority:`, `Automation Adoption Path:`, `Assumption Mode:`, `Strategy Confidence:` |
| Next steps | `Recommended Immediate Actions:` |

The prompt explicitly maps each decision to its natural section (e.g., `Governance Depth:` goes in Defect, Triage, And Reporting Model; `Shift-Left Stance:` goes in Lifecycle Posture).

---

## Repair Mechanism

If the LLM omits required headings or labels, the system runs a repair pass before falling back to the deterministic renderer.

The repair injects actual values — not generic placeholders:

```python
"Project Posture:"          →  input_data["project_posture"]
"Governance Depth:"         →  decisions["governance_depth"]
"Automation Adoption Path:" →  decisions["automation_adoption_path"]
"Reporting Emphasis:"       →  decisions["reporting_emphasis"]
```

The brownfield transition strategy is only injected when its decision value is not `not_applicable`. This avoids "Brownfield Transition Strategy: not_applicable" appearing in greenfield strategies.

This makes repair output meaningfully correct (engagement-specific values) rather than structurally compliant but content-empty.

**Repair statistics** are counted per run and stored in `FlowResult.repair_stats`:

| Stat | Meaning |
|---|---|
| `headings_injected` | Number of required headings the repair pass had to add |
| `labels_injected` | Number of required labels the repair pass had to add |
| `total_headings` | Total required headings (14) |
| `total_labels` | Total required labels (18) |

A value of `headings_injected: 0, labels_injected: 0` means the LLM naturally produced a structurally complete document. Higher counts indicate how much relied on the repair safety net.

These statistics are surfaced in the comparison report Quality Indicators table when `--compare` is used.

---

## Benchmark Assertions

All six benchmark scenarios have two levels of assertions in `benchmarks/*.assertions.yaml`:

**Structural assertions** (required in all scenarios):
- `must_include_headings` — all 8 key section headings
- `must_include_labels` — engagement-specific label values

**Content assertions** (added in Phase 8):
- `must_include_substrings` — specific decision values (e.g., `phased_expansion`, `pipeline_native`, `Governance Depth: high`)
- `must_not_include_substrings` — cross-contamination guards (e.g., greenfield assertions check that brownfield transition language is absent)

The benchmark assertions pass at exit code `0`. Structural validity alone passes at exit code `0` as well (headings + labels enforced by the repair mechanism). What distinguishes a strong LLM pass from a repaired pass is whether the LLM naturally produced the content-level values before repair was needed.

---

## Evaluating Prompt Quality with `--compare`

The `--compare` flag runs both generation paths for the same input and writes a side-by-side comparison report:

```powershell
python -m ai_test_strategy_generator.cli benchmarks\greenfield-low-automation.input.yaml `
  --mode llm_assisted --provider ollama --model glm-5:cloud `
  --assertions benchmarks\greenfield-low-automation.assertions.yaml `
  --output output\strategy-llm.md `
  --compare output\comparison.md
```

The report (`comparison.md`) contains:
- A summary table: output lines, word count, section count for both paths
- A **Quality Indicators** table: headings and labels naturally produced by the LLM vs injected by the repair pass
- Full deterministic strategy
- Full LLM-assisted strategy

**Quality Indicators table example:**

| Metric | Value |
|---|---|
| Headings from LLM | 12 / 14 |
| Headings injected by repair | 2 |
| Labels from LLM | 18 / 18 |
| Labels injected by repair | 0 |

The Quality Indicators table only appears when the LLM-assisted path ran and returned repair statistics. When the deterministic fallback path was used (exit code `3`), `repair_stats` are not present and the table is omitted.

**What to look for in a comparison:**

| Quality Signal | What It Means |
|---|---|
| LLM word count significantly higher | LLM is adding narrative depth; check whether the narrative is accurate |
| LLM word count much lower | LLM may have truncated; check `max_tokens` and `--max-tokens` override |
| LLM missing sections present in deterministic | Repair passed; LLM skipped a section; prompt placement instruction may need strengthening |
| LLM contradicts decision values | Check that the `{decisions}` block appears early in the prompt and the instruction to not modify them is clear |
| LLM duplicates required labels in every section | The placement instructions may be too generic; add specificity to scenario template |

---

## How to Extend the Template System

**To modify existing scenario emphasis** — edit the relevant `.txt` file in `prompts/v1/`. No Python changes required.

**To add a new scenario** — for example, `performance_critical`:

1. Create `prompts/v1/performance_critical.txt` with the scenario instructions
2. Add a condition in `prompt_builder._select_scenario()`:
   ```python
   if classifications.get("system_profile") == "performance_critical":
       return "performance_critical"
   ```
3. Add the corresponding test in `tests/test_prompt_builder.py`
4. Update benchmark assertions if the scenario changes expected content

**To add a new template version** — create `prompts/v2/` with updated `.txt` files. Pass `version="v2"` to `load_template()`. The base version remains `v1` until explicitly changed in `prompt_builder.py`.

**To add a new required label** — add it to `REQUIRED_LABELS` in `output_validator.py`, add the repair mapping in `llm_flow._build_label_values()`, and add it to the prompt contract placement instructions in `base.txt`.

---

## Design Constraints

- Templates use Python `str.format()` only. No Jinja2, no external dependencies.
- Scenario templates contain **no placeholders**. They are stable instructions injected as-is.
- Required headings and labels in `output_validator.py` are the single source of truth. The prompt references them dynamically via `{required_headings}` and `{required_labels}`.
- `not_applicable` decision values are not injected into prompts. The decisions block only contains active decisions.
- API keys and provider credentials never appear in template files.

---

## Optimization Loop (Phase 10)

The optimization loop systematically searches for prompt templates that score higher than the current `prompts/v1/` baseline, using a binary scoring model and five mutation strategies.

### Binary Scoring Model

Every run produces an integer score — the count of binary checks that passed. There are no weights; every check is equal.

| Check | Source |
|---|---|
| `exit_code == 0` | `FlowResult` |
| `source == "llm"` (not repair) | `repair_stats["source"]` |
| Each individual assertion passed | `ValidationResult.total_checks - len(errors)` |
| Each required heading present natively | `total_headings - headings_injected` |
| Each required label present natively | `total_labels - labels_injected` |

Scores are summed across all benchmark scenarios. The optimization loop keeps a prompt only if its aggregate score strictly exceeds the best score seen so far.

### Mutation Strategies

All mutations operate on `base.txt` only. The five strategies registered in `prompt_mutations.ALL_MUTATIONS` are:

| Strategy | Effect |
|---|---|
| `emphasis_strengthening` | Adds `CRITICAL: ` prefix to `You MUST`, `It must include`, `Each section must` lines. Idempotent. |
| `emphasis_removal` | Removes `CRITICAL: ` prefixes (revert of above). |
| `instruction_reordering` | Shuffles the indented placement-bullet block in `base.txt`. |
| `example_injection` | Appends a labeled-line example fragment at the end of the template. Idempotent. |
| `example_removal` | Removes the example fragment (revert of above). |

Mutations cycle in order across iterations. If a mutation produces no improvement, the best-so-far template is unchanged and the next mutation is applied to that same best template (cumulative within a run).

### Running the Optimizer

```bash
python -m ai_test_strategy_generator.cli \
    --optimize \
    --optimize-iterations 5 \
    --optimize-timeout 300 \
    --optimize-output-dir optimization_runs/
```

- `--optimize-iterations` — number of total iterations including baseline (iter 0). Default: 5.
- `--optimize-timeout` — maximum wall-clock seconds per iteration. Default: 300.
- `--optimize-output-dir` — directory for experiment artifacts (`optimization_runs/` is `.gitignore`d).

### Scoreboard Format

After completion, the optimizer writes a `scoreboard.yaml` to `--optimize-output-dir`:

```yaml
baseline_aggregate: 240
best_aggregate: 252
best_iteration: 2
improvement_delta: 12
improved: true
best_prompt_dir: optimization_runs/best
iterations:
  - iteration: 0
    mutation: null
    aggregate: 240
    is_best: false
  - iteration: 1
    mutation: emphasis_strengthening
    aggregate: 238
    is_best: false
  - iteration: 2
    mutation: instruction_reordering
    aggregate: 252
    is_best: true
```

### Promoting a Winning Prompt

When `improved: true` and `best_prompt_dir` contains templates:

1. Review `optimization_runs/best/base.txt` — diff it against `prompts/v1/base.txt` to understand what changed.
2. Copy to `prompts/v2/` — **never** overwrite `prompts/v1/`:
   ```bash
   cp -r optimization_runs/best/ src/ai_test_strategy_generator/prompts/v2/
   ```
3. Update `prompt_builder.py` to load from `v2` by default.
4. Re-run the benchmark suite to confirm the improvement holds on fresh LLM calls.
5. Commit `prompts/v2/` and the updated `prompt_builder.py` — **not** `optimization_runs/`.
