# AI Test Strategy Generator - V1 Input Template

Last Updated: 2026-04-08

## Purpose

Define the minimum structured input needed for the v1 strategy generator.

This template is designed for MVP use.
It favors a small number of source types and a predictable structure over broad ingestion complexity.

## MVP Recommendation

For v1, support two input modes only:

1. Structured manual input
- a single markdown or JSON file filled using this template

2. Artifact-folder input
- a small `artifacts/` folder with a few supported files plus a short manifest

Do not start v1 with direct Jira, Xray, Zephyr, Confluence, or live API integrations.

Why:
- lower build complexity
- easier validation
- easier demos
- easier learning
- avoids spending phase 1 on connectors instead of strategy logic

## Recommended V1 Source Types

Support these first:

1. Project brief or RFP summary
2. Requirement or scope summary
3. System landscape summary
4. Optional API or interface summary
5. Optional current test / automation summary

Everything else can be added later.

## V1 Input Fields

## 1. Engagement Metadata

- `engagement_name`
- `domain`
- `delivery_model`
  - example: agile, waterfall, hybrid
- `project_posture`
  - `greenfield` or `brownfield`
- `timeline_pressure`
  - `low`, `medium`, `high`

## 2. Business And Quality Context

- `business_goal`
- `quality_goal`
- `release_expectation`
- `critical_business_flows`

## 3. System Landscape

- `system_type`
  - example: UI-heavy, API-first, microservices, data-heavy, legacy enterprise
- `applications_in_scope`
- `key_integrations`
- `platform_notes`

## 4. Current-State Maturity

- `existing_test_process`
- `existing_automation_state`
  - `none`, `limited`, `partial`, `strong`, `unknown`
- `ci_cd_maturity`
  - `none`, `manual`, `partial`, `mature`, `unknown`
- `environment_maturity`
  - `weak`, `moderate`, `strong`, `unknown`
- `test_data_maturity`
  - `weak`, `moderate`, `strong`, `unknown`

## 5. Constraints And Risks

- `known_constraints`
- `regulatory_or_compliance_needs`
- `delivery_risks`
- `missing_information`

## 6. Available Inputs

- `requirements_available`
  - yes/no + short note
- `api_docs_available`
  - yes/no + short note
- `existing_test_cases_available`
  - yes/no + short note
- `automation_assets_available`
  - yes/no + short note
- `production_or_operational_feedback_available`
  - yes/no + short note

## 7. AI Posture

- `ai_adoption_posture`
  - `supportive`, `cautious`, `restricted`, `unknown`
- `ai_governance_constraints`
- `human_review_expectations`

## 8. Output Intent

- `strategy_depth`
  - `light`, `standard`, `detailed`
- `primary_audience`
  - example: QE lead, engineering manager, delivery head, presales, client stakeholder
- `desired_output_format`
  - `markdown` for v1

## Minimal Example

```yaml
engagement_name: Claims Modernization QE Strategy
domain: Insurance
delivery_model: Agile
project_posture: brownfield
timeline_pressure: high

business_goal: Modernize claims platform without increasing release risk
quality_goal: Improve release confidence and reduce regression leakage
release_expectation: Bi-weekly release readiness with clear quality gates
critical_business_flows:
  - claim creation
  - claim adjudication
  - payout processing

system_type: API-first with supporting UI
applications_in_scope:
  - claims portal
  - claims service layer
  - payment integration
key_integrations:
  - policy platform
  - payment gateway
platform_notes: Existing services are partly modernized; some legacy UI remains

existing_test_process: Manual-heavy with some regression support
existing_automation_state: partial
ci_cd_maturity: partial
environment_maturity: moderate
test_data_maturity: weak

known_constraints:
  - limited QE capacity
  - incomplete documentation
regulatory_or_compliance_needs:
  - auditability
  - privacy-sensitive test data handling
delivery_risks:
  - integration instability
  - weak regression confidence
missing_information:
  - current API contract coverage
  - production defect leakage trend

requirements_available: yes - epics and feature summaries exist
api_docs_available: yes - partial OpenAPI coverage
existing_test_cases_available: yes - spreadsheet-based manual regression pack
automation_assets_available: yes - limited API and UI suite exists
production_or_operational_feedback_available: no - not yet collected

ai_adoption_posture: cautious
ai_governance_constraints:
  - human approval required for strategy sign-off
human_review_expectations:
  - all AI-generated strategy sections reviewed by QE lead

strategy_depth: standard
primary_audience: QE lead and delivery leadership
desired_output_format: markdown
```

## Artifact-Folder Variant

Recommended v1 folder:

```text
artifacts/
  manifest.yaml
  project-summary.md
  system-landscape.md
  requirements-summary.md
  api-summary.md
  current-test-state.md
```

Where:
- `manifest.yaml` maps files to the above fields
- missing files are allowed, but the generator must surface assumptions and gaps

## Binary Validation For V1 Input

An input package passes v1 validation only if:
- `engagement_name` exists
- `project_posture` exists
- `system_type` exists
- at least one business goal or quality goal exists
- at least one constraint or risk exists
- `existing_automation_state` is provided, even if `unknown`
- `ci_cd_maturity` is provided, even if `unknown`

If these are missing, the generator should fail fast and ask for minimum context.
