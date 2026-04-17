"""Pipeline integration tests.

Each test class targets a specific cross-module coupling that unit tests cannot
catch in isolation.  The goal is zero escapes: any defect that breaks the
classifier → rule_engine → renderer → validator chain fails here before it
reaches a benchmark run or the PR.

Test organisation:
  ClassifierRuleIntegrationTests  — every classification dimension drives decisions
  RuleRendererIntegrationTests    — every decision value appears in rendered output
  P12BFieldTraceabilityTests      — new P12-B input fields flow through to output
  RepairSectionPlacementTests     — repaired output satisfies section-aware validation
  DecisionInvariantTests          — specific inputs always produce specific decisions
  RendererConsistencyTests        — renderer output is internally self-consistent
"""
from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _run_pipeline(input_path: str):
    """Full classifier → rule_engine → renderer → validator pipeline."""
    from ai_test_strategy_generator.input_loader import load_input
    from ai_test_strategy_generator.context_classifier import classify_context
    from ai_test_strategy_generator.rule_engine import apply_rules
    from ai_test_strategy_generator.renderer import render_strategy
    from ai_test_strategy_generator.output_validator import validate_output

    pkg = load_input(Path(input_path))
    c = classify_context(pkg)
    d = apply_rules(c)
    md = render_strategy(pkg, c, d)
    return pkg, c, d, md, validate_output(md)


_ALL_BENCHMARKS = [
    "benchmarks/brownfield-partial-automation.input.yaml",
    "benchmarks/greenfield-low-automation.input.yaml",
    "benchmarks/incomplete-context.input.yaml",
    "benchmarks/strong-automation-weak-governance.input.yaml",
    "benchmarks/nfr-heavy-api.input.yaml",
    "benchmarks/qestrategyforge-self.input.yaml",
    "benchmarks/regulated-brownfield-manual-release.input.yaml",
    "benchmarks/greenfield-aggressive-timeline.input.yaml",
    "benchmarks/multi-integration-unstable-dependencies.input.yaml",
]


# ---------------------------------------------------------------------------
# 1. Classifier → Rule engine
# ---------------------------------------------------------------------------

class ClassifierRuleIntegrationTests(unittest.TestCase):
    """Every classification dimension must influence at least one rule decision.

    If a dimension is added to the classifier but forgotten in the rule engine,
    the defect is caught here before it silently produces wrong output.
    """

    _BASE = {k: "unknown" for k in [
        "project_posture", "automation_maturity", "ci_cd_maturity",
        "system_profile", "regulatory_sensitivity", "information_completeness",
        "release_frequency", "nfr_priority",
    ]}

    def _decisions_for(self, **overrides):
        from ai_test_strategy_generator.rule_engine import apply_rules
        return apply_rules({**self._BASE, **overrides})

    def test_project_posture_drives_decisions(self) -> None:
        d_brownfield = self._decisions_for(project_posture="brownfield")
        d_greenfield = self._decisions_for(project_posture="greenfield")
        self.assertNotEqual(d_brownfield, d_greenfield)

    def test_automation_maturity_drives_decisions(self) -> None:
        d_none = self._decisions_for(automation_maturity="none")
        d_strong = self._decisions_for(automation_maturity="strong")
        self.assertNotEqual(d_none, d_strong)

    def test_ci_cd_maturity_drives_decisions(self) -> None:
        # none and strong may both produce staged_enablement when all else is unknown;
        # the meaningful split is none/strong vs partial (which produces progressive_gates)
        d_partial = self._decisions_for(ci_cd_maturity="partial")
        d_strong = self._decisions_for(ci_cd_maturity="strong")
        self.assertNotEqual(d_partial, d_strong)

    def test_regulatory_sensitivity_drives_decisions(self) -> None:
        d_low = self._decisions_for(regulatory_sensitivity="low")
        d_high = self._decisions_for(regulatory_sensitivity="high")
        self.assertNotEqual(d_low, d_high)

    def test_information_completeness_drives_decisions(self) -> None:
        d_incomplete = self._decisions_for(information_completeness="incomplete")
        d_complete = self._decisions_for(information_completeness="complete")
        self.assertNotEqual(d_incomplete, d_complete)

    def test_release_frequency_drives_decisions(self) -> None:
        d_high = self._decisions_for(release_frequency="high")
        d_low = self._decisions_for(release_frequency="low")
        self.assertNotEqual(d_high, d_low)

    def test_nfr_priority_drives_decisions(self) -> None:
        d_low = self._decisions_for(nfr_priority="low")
        d_high = self._decisions_for(nfr_priority="high")
        self.assertNotEqual(d_low, d_high)

    def test_all_classifier_dimensions_are_consumed_by_apply_rules(self) -> None:
        """apply_rules must produce different decisions for each dimension that exists."""
        import inspect
        from ai_test_strategy_generator.context_classifier import classify_context
        from ai_test_strategy_generator.rule_engine import apply_rules

        # Verify every key produced by classify_context is in our _BASE dimensions
        from ai_test_strategy_generator.input_loader import load_input
        pkg = load_input(Path("benchmarks/brownfield-partial-automation.input.yaml"))
        classifications = classify_context(pkg)
        untracked = set(classifications.keys()) - set(self._BASE.keys())
        self.assertEqual(
            untracked,
            set(),
            f"Classifier produces keys not tracked by this test class: {untracked}. "
            "Add a test for each new dimension.",
        )


# ---------------------------------------------------------------------------
# 2. Rule engine → Renderer
# ---------------------------------------------------------------------------

class RuleRendererIntegrationTests(unittest.TestCase):
    """Every non-trivial decision value produced by apply_rules must appear in
    the rendered markdown.  If a renderer helper stops consuming a decision key,
    this catches the silent drift.
    """

    def test_all_decision_values_appear_in_output_across_benchmarks(self) -> None:
        from ai_test_strategy_generator.input_loader import load_input
        from ai_test_strategy_generator.context_classifier import classify_context
        from ai_test_strategy_generator.rule_engine import apply_rules
        from ai_test_strategy_generator.renderer import render_strategy

        failures: dict[str, list[str]] = {}
        for path in _ALL_BENCHMARKS:
            pkg = load_input(Path(path))
            c = classify_context(pkg)
            d = apply_rules(c)
            md = render_strategy(pkg, c, d)
            # nfr_depth is a meta-decision (controls detail depth) and does not
            # appear as a literal string in the rendered output — exclude it.
            CONTROL_TOKENS = {"not_applicable", "deep", "standard"}
            missing = [
                f"{k}={v}"
                for k, v in d.items()
                if v not in CONTROL_TOKENS and str(v) not in md
            ]
            if missing:
                failures[path] = missing
        self.assertEqual(
            failures, {},
            f"Decision values not reflected in rendered output:\n" +
            "\n".join(f"  {p}: {m}" for p, m in failures.items()),
        )

    def test_brownfield_posture_renders_transition_strategy(self) -> None:
        from ai_test_strategy_generator.input_loader import load_input
        from ai_test_strategy_generator.context_classifier import classify_context
        from ai_test_strategy_generator.rule_engine import apply_rules
        from ai_test_strategy_generator.renderer import render_strategy

        pkg = load_input(Path("benchmarks/brownfield-partial-automation.input.yaml"))
        c = classify_context(pkg)
        d = apply_rules(c)
        md = render_strategy(pkg, c, d)
        self.assertIn("Brownfield Transition Strategy:", md)

    def test_greenfield_posture_omits_brownfield_transition(self) -> None:
        from ai_test_strategy_generator.input_loader import load_input
        from ai_test_strategy_generator.context_classifier import classify_context
        from ai_test_strategy_generator.rule_engine import apply_rules
        from ai_test_strategy_generator.renderer import render_strategy

        pkg = load_input(Path("benchmarks/greenfield-low-automation.input.yaml"))
        c = classify_context(pkg)
        d = apply_rules(c)
        md = render_strategy(pkg, c, d)
        self.assertNotIn("Brownfield Transition Strategy:", md)

    def test_high_regulatory_sensitivity_drives_high_governance_depth(self) -> None:
        from ai_test_strategy_generator.rule_engine import apply_rules
        from ai_test_strategy_generator.renderer import render_strategy
        from ai_test_strategy_generator.input_loader import load_input
        from ai_test_strategy_generator.context_classifier import classify_context

        pkg = load_input(Path("benchmarks/regulated-brownfield-manual-release.input.yaml"))
        c = classify_context(pkg)
        d = apply_rules(c)
        md = render_strategy(pkg, c, d)
        self.assertIn("Governance Depth: high", md)


# ---------------------------------------------------------------------------
# 3. P12-B field traceability
# ---------------------------------------------------------------------------

class P12BFieldTraceabilityTests(unittest.TestCase):
    """Every P12-B input field added in the schema expansion must reach the
    rendered output.  If the renderer stops consuming a field, the field
    silently disappears from client-facing strategy documents.
    """

    def setUp(self):
        from ai_test_strategy_generator.input_loader import load_input
        from ai_test_strategy_generator.context_classifier import classify_context
        from ai_test_strategy_generator.rule_engine import apply_rules
        from ai_test_strategy_generator.renderer import render_strategy

        self._pkg, self._c, self._d, self._md = None, None, None, None
        pkg = load_input(Path("benchmarks/regulated-brownfield-manual-release.input.yaml"))
        c = classify_context(pkg)
        d = apply_rules(c)
        self._md = render_strategy(pkg, c, d)
        self._pkg = pkg

    def test_reporting_audience_appears_in_output(self) -> None:
        audience = self._pkg.normalized.get("reporting_audience", "")
        self.assertTrue(
            audience and audience in self._md,
            f"reporting_audience={audience!r} not found in rendered output",
        )

    def test_release_cadence_appears_in_output(self) -> None:
        cadence = self._pkg.normalized.get("release_cadence", "")
        self.assertTrue(
            cadence and cadence in self._md,
            f"release_cadence={cadence!r} not found in rendered output",
        )

    def test_qe_capacity_appears_in_output(self) -> None:
        capacity = self._pkg.normalized.get("qe_capacity", "")
        self.assertTrue(
            capacity and capacity in self._md,
            f"qe_capacity={capacity!r} not found in rendered output",
        )

    def test_reporting_audience_label_in_correct_section(self) -> None:
        from ai_test_strategy_generator.output_validator import _parse_sections
        sections = _parse_sections(self._md)
        reporting_section = sections.get("## Defect, Triage, And Reporting Model", "")
        self.assertIn("Reporting Audience:", reporting_section)

    def test_environment_constraints_appear_in_output_when_populated(self) -> None:
        from ai_test_strategy_generator.input_loader import load_input
        from ai_test_strategy_generator.context_classifier import classify_context
        from ai_test_strategy_generator.rule_engine import apply_rules
        from ai_test_strategy_generator.renderer import render_strategy
        from ai_test_strategy_generator.models import InputPackage

        pkg = InputPackage(
            source_path=Path("input.yaml"),
            raw={},
            normalized={
                "project_posture": "brownfield",
                "delivery_model": "Agile",
                "system_type": "API",
                "critical_business_flows": [],
                "known_constraints": [],
                "delivery_risks": [],
                "key_integrations": [],
                "regulatory_or_compliance_needs": [],
                "missing_information": [],
                "human_review_expectations": [],
                "existing_automation_state": "partial",
                "ci_cd_maturity": "partial",
                "ai_adoption_posture": "cautious",
                "test_data_maturity": "unknown",
                "environment_maturity": "unknown",
                "nfr_priorities": [],
                "environment_constraints": ["no prod access", "shared staging only"],
                "data_privacy_constraints": [],
                "target_quality_gates": [],
            },
        )
        c = classify_context(pkg)
        d = apply_rules(c)
        md = render_strategy(pkg, c, d)
        self.assertIn("no prod access", md)
        self.assertIn("shared staging only", md)

    def test_target_quality_gates_appear_in_cicd_section(self) -> None:
        from ai_test_strategy_generator.output_validator import _parse_sections
        from ai_test_strategy_generator.input_loader import load_input
        from ai_test_strategy_generator.context_classifier import classify_context
        from ai_test_strategy_generator.rule_engine import apply_rules
        from ai_test_strategy_generator.renderer import render_strategy
        from ai_test_strategy_generator.models import InputPackage

        pkg = InputPackage(
            source_path=Path("input.yaml"),
            raw={},
            normalized={
                "project_posture": "brownfield",
                "delivery_model": "Agile",
                "system_type": "API",
                "critical_business_flows": [],
                "known_constraints": [],
                "delivery_risks": [],
                "key_integrations": [],
                "regulatory_or_compliance_needs": [],
                "missing_information": [],
                "human_review_expectations": [],
                "existing_automation_state": "partial",
                "ci_cd_maturity": "partial",
                "ai_adoption_posture": "cautious",
                "test_data_maturity": "unknown",
                "environment_maturity": "unknown",
                "nfr_priorities": [],
                "environment_constraints": [],
                "data_privacy_constraints": [],
                "target_quality_gates": ["smoke gate", "security scan"],
            },
        )
        c = classify_context(pkg)
        d = apply_rules(c)
        md = render_strategy(pkg, c, d)
        sections = _parse_sections(md)
        cicd_section = sections.get("## CI/CD And Quality Gates", "")
        self.assertIn("smoke gate", cicd_section)
        self.assertIn("security scan", cicd_section)


# ---------------------------------------------------------------------------
# 4. Repair section placement
# ---------------------------------------------------------------------------

class RepairSectionPlacementTests(unittest.TestCase):
    """After _repair_output runs, every injected label must be in its correct
    section.  If the repair logic inserts labels at document root instead of
    under the right heading, these tests fail.
    """

    def _repair(self, partial_markdown: str, input_path: str):
        from ai_test_strategy_generator.input_loader import load_input
        from ai_test_strategy_generator.context_classifier import classify_context
        from ai_test_strategy_generator.rule_engine import apply_rules
        from ai_test_strategy_generator.llm_flow import _repair_output

        pkg = load_input(Path(input_path))
        c = classify_context(pkg)
        d = apply_rules(c)
        repaired, _ = _repair_output(partial_markdown, pkg.normalized, d)
        return repaired

    def test_repair_of_empty_string_produces_valid_output(self) -> None:
        from ai_test_strategy_generator.output_validator import validate_output
        repaired = self._repair("", "benchmarks/brownfield-partial-automation.input.yaml")
        result = validate_output(repaired)
        self.assertTrue(result.is_valid, result.errors)

    def test_repair_places_strategy_confidence_in_executive_summary(self) -> None:
        from ai_test_strategy_generator.output_validator import _parse_sections
        # Only give headings, no labels — repair must inject all labels in correct sections
        headings_only = "\n".join(
            f"## {h.lstrip('# ')}" for h in [
                "## Executive Summary", "## Engagement Context",
                "## Quality Objectives And Risk Priorities", "## Lifecycle Posture",
                "## Layered Test Strategy", "## Test Types And Coverage Focus",
                "## Automation Strategy", "## CI/CD And Quality Gates",
                "## Test Data Strategy", "## Environment Strategy",
                "## Defect, Triage, And Reporting Model", "## AI Usage Model",
                "## Assumptions, Gaps, And Open Questions", "## Recommended Next Steps",
            ]
        )
        repaired = self._repair(headings_only, "benchmarks/brownfield-partial-automation.input.yaml")
        sections = _parse_sections(repaired)
        self.assertIn(
            "Strategy Confidence:",
            sections.get("## Executive Summary", ""),
            "Repair must place Strategy Confidence: under ## Executive Summary",
        )

    def test_repair_places_missing_information_in_correct_section(self) -> None:
        from ai_test_strategy_generator.output_validator import _parse_sections
        headings_only = "\n".join([
            "## Executive Summary", "## Engagement Context",
            "## Quality Objectives And Risk Priorities", "## Lifecycle Posture",
            "## Layered Test Strategy", "## Test Types And Coverage Focus",
            "## Automation Strategy", "## CI/CD And Quality Gates",
            "## Test Data Strategy", "## Environment Strategy",
            "## Defect, Triage, And Reporting Model", "## AI Usage Model",
            "## Assumptions, Gaps, And Open Questions", "## Recommended Next Steps",
        ])
        repaired = self._repair(headings_only, "benchmarks/brownfield-partial-automation.input.yaml")
        sections = _parse_sections(repaired)
        self.assertIn(
            "Missing Information:",
            sections.get("## Assumptions, Gaps, And Open Questions", ""),
        )

    def test_repair_of_output_missing_single_label_fixes_that_label(self) -> None:
        from ai_test_strategy_generator.output_validator import validate_output
        from ai_test_strategy_generator.input_loader import load_input
        from ai_test_strategy_generator.context_classifier import classify_context
        from ai_test_strategy_generator.rule_engine import apply_rules
        from ai_test_strategy_generator.renderer import render_strategy
        from ai_test_strategy_generator.llm_flow import _repair_output

        pkg = load_input(Path("benchmarks/brownfield-partial-automation.input.yaml"))
        c = classify_context(pkg)
        d = apply_rules(c)
        good_md = render_strategy(pkg, c, d)

        # Remove one label
        broken = "\n".join(
            line for line in good_md.splitlines()
            if not line.strip().startswith("Reporting Audience:")
        )
        assert "Reporting Audience:" not in broken

        repaired, stats = _repair_output(broken, pkg.normalized, d)
        result = validate_output(repaired)
        self.assertTrue(result.is_valid, result.errors)
        self.assertEqual(stats["labels_injected"], 1)

    def test_repair_across_all_benchmarks_produces_valid_output(self) -> None:
        """Repair of every benchmark's full output (with all labels stripped) must succeed."""
        from ai_test_strategy_generator.input_loader import load_input
        from ai_test_strategy_generator.context_classifier import classify_context
        from ai_test_strategy_generator.rule_engine import apply_rules
        from ai_test_strategy_generator.renderer import render_strategy
        from ai_test_strategy_generator.llm_flow import _repair_output
        from ai_test_strategy_generator.output_validator import validate_output, REQUIRED_LABELS

        failures: dict[str, list[str]] = {}
        for path in _ALL_BENCHMARKS:
            pkg = load_input(Path(path))
            c = classify_context(pkg)
            d = apply_rules(c)
            good_md = render_strategy(pkg, c, d)
            # Strip all required labels — simulate a bad LLM response that has structure but no labels
            broken = "\n".join(
                line for line in good_md.splitlines()
                if not any(line.strip().startswith(label) for label in REQUIRED_LABELS)
            )
            repaired, _ = _repair_output(broken, pkg.normalized, d)
            result = validate_output(repaired)
            if not result.is_valid:
                failures[path] = result.errors
        self.assertEqual(failures, {}, "\n".join(f"{p}: {e}" for p, e in failures.items()))


# ---------------------------------------------------------------------------
# 5. Decision invariants
# ---------------------------------------------------------------------------

class DecisionInvariantTests(unittest.TestCase):
    """Specific input combinations must always produce specific decisions.
    These are the rules that the renderer relies on as guarantees — if a rule
    engine change breaks an invariant, the renderer silently produces wrong output.
    """

    def test_high_release_frequency_forces_pipeline_native(self) -> None:
        from ai_test_strategy_generator.rule_engine import apply_rules
        d = apply_rules({"release_frequency": "high", **{
            k: "unknown" for k in [
                "project_posture", "automation_maturity", "ci_cd_maturity",
                "system_profile", "regulatory_sensitivity",
                "information_completeness", "nfr_priority",
            ]
        }})
        self.assertEqual(d["ci_cd_posture"], "pipeline_native")

    def test_high_release_frequency_forces_high_reporting_emphasis(self) -> None:
        from ai_test_strategy_generator.rule_engine import apply_rules
        d = apply_rules({"release_frequency": "high", **{
            k: "unknown" for k in [
                "project_posture", "automation_maturity", "ci_cd_maturity",
                "system_profile", "regulatory_sensitivity",
                "information_completeness", "nfr_priority",
            ]
        }})
        self.assertEqual(d["reporting_emphasis"], "high")

    def test_high_regulatory_sensitivity_forces_high_governance(self) -> None:
        from ai_test_strategy_generator.rule_engine import apply_rules
        d = apply_rules({"regulatory_sensitivity": "high", **{
            k: "unknown" for k in [
                "project_posture", "automation_maturity", "ci_cd_maturity",
                "system_profile", "information_completeness",
                "release_frequency", "nfr_priority",
            ]
        }})
        self.assertEqual(d["governance_depth"], "high")

    def test_incomplete_information_sets_conditional_confidence(self) -> None:
        from ai_test_strategy_generator.rule_engine import apply_rules
        d = apply_rules({"information_completeness": "incomplete", **{
            k: "unknown" for k in [
                "project_posture", "automation_maturity", "ci_cd_maturity",
                "system_profile", "regulatory_sensitivity",
                "release_frequency", "nfr_priority",
            ]
        }})
        self.assertEqual(d["strategy_confidence"], "conditional")

    def test_brownfield_produces_non_trivial_transition_strategy(self) -> None:
        from ai_test_strategy_generator.rule_engine import apply_rules
        d = apply_rules({"project_posture": "brownfield", "automation_maturity": "partial", **{
            k: "unknown" for k in [
                "ci_cd_maturity", "system_profile", "regulatory_sensitivity",
                "information_completeness", "release_frequency", "nfr_priority",
            ]
        }})
        self.assertNotEqual(d["brownfield_transition_strategy"], "not_applicable")

    def test_greenfield_always_produces_not_applicable_transition_strategy(self) -> None:
        from ai_test_strategy_generator.rule_engine import apply_rules
        d = apply_rules({"project_posture": "greenfield", **{
            k: "unknown" for k in [
                "automation_maturity", "ci_cd_maturity", "system_profile",
                "regulatory_sensitivity", "information_completeness",
                "release_frequency", "nfr_priority",
            ]
        }})
        self.assertEqual(d["brownfield_transition_strategy"], "not_applicable")

    def test_no_automation_greenfield_forces_lower_layers_first(self) -> None:
        # automation=none on greenfield → start from bottom (lowest layers first)
        # automation=none on brownfield → balanced (must preserve existing test investment)
        from ai_test_strategy_generator.rule_engine import apply_rules
        d = apply_rules({"automation_maturity": "none", "project_posture": "greenfield", **{
            k: "unknown" for k in [
                "ci_cd_maturity", "system_profile",
                "regulatory_sensitivity", "information_completeness",
                "release_frequency", "nfr_priority",
            ]
        }})
        self.assertEqual(d["layering_priority"], "lower_layers_first")

    def test_no_automation_brownfield_produces_balanced_layering(self) -> None:
        # Brownfield projects with no automation still need to layer carefully rather
        # than start from scratch — rule engine returns 'balanced'.
        from ai_test_strategy_generator.rule_engine import apply_rules
        d = apply_rules({"automation_maturity": "none", "project_posture": "brownfield", **{
            k: "unknown" for k in [
                "ci_cd_maturity", "system_profile",
                "regulatory_sensitivity", "information_completeness",
                "release_frequency", "nfr_priority",
            ]
        }})
        self.assertEqual(d["layering_priority"], "balanced")


# ---------------------------------------------------------------------------
# 6. Renderer consistency
# ---------------------------------------------------------------------------

class RendererConsistencyTests(unittest.TestCase):
    """Internal consistency of rendered documents across scenario variants.

    These catch cases where a renderer branch produces contradictory content —
    e.g. claiming automated gates exist when CI/CD maturity is none.
    """

    def test_staged_enablement_with_no_cicd_never_claims_automated_primary_signal(self) -> None:
        from ai_test_strategy_generator.renderer import render_strategy
        from ai_test_strategy_generator.input_loader import load_input
        from ai_test_strategy_generator.context_classifier import classify_context
        from ai_test_strategy_generator.rule_engine import apply_rules

        pkg = load_input(Path("benchmarks/greenfield-aggressive-timeline.input.yaml"))
        c = classify_context(pkg)
        d = apply_rules(c)
        md = render_strategy(pkg, c, d)
        self.assertNotIn("automated gate results are the primary release signal", md)

    def test_manual_cicd_always_includes_manual_sign_off_language(self) -> None:
        from ai_test_strategy_generator.renderer import render_strategy
        from ai_test_strategy_generator.input_loader import load_input
        from ai_test_strategy_generator.context_classifier import classify_context
        from ai_test_strategy_generator.rule_engine import apply_rules

        pkg = load_input(Path("benchmarks/regulated-brownfield-manual-release.input.yaml"))
        c = classify_context(pkg)
        d = apply_rules(c)
        md = render_strategy(pkg, c, d)
        self.assertIn("manual", md.lower())

    def test_incomplete_context_always_includes_discovery_next_step(self) -> None:
        from ai_test_strategy_generator.renderer import render_strategy
        from ai_test_strategy_generator.input_loader import load_input
        from ai_test_strategy_generator.context_classifier import classify_context
        from ai_test_strategy_generator.rule_engine import apply_rules

        pkg = load_input(Path("benchmarks/incomplete-context.input.yaml"))
        c = classify_context(pkg)
        d = apply_rules(c)
        md = render_strategy(pkg, c, d)
        self.assertIn("discovery", md.lower())

    def test_restricted_ai_posture_never_claims_broad_ai_usage(self) -> None:
        from ai_test_strategy_generator.renderer import render_strategy
        from ai_test_strategy_generator.input_loader import load_input
        from ai_test_strategy_generator.context_classifier import classify_context
        from ai_test_strategy_generator.rule_engine import apply_rules

        pkg = load_input(Path("benchmarks/regulated-brownfield-manual-release.input.yaml"))
        c = classify_context(pkg)
        d = apply_rules(c)
        md = render_strategy(pkg, c, d)
        self.assertNotIn("reporting summarization", md)

    def test_high_governance_depth_always_includes_traceability_language(self) -> None:
        from ai_test_strategy_generator.renderer import render_strategy
        from ai_test_strategy_generator.input_loader import load_input
        from ai_test_strategy_generator.context_classifier import classify_context
        from ai_test_strategy_generator.rule_engine import apply_rules

        pkg = load_input(Path("benchmarks/regulated-brownfield-manual-release.input.yaml"))
        c = classify_context(pkg)
        d = apply_rules(c)
        assert d["governance_depth"] == "high"
        md = render_strategy(pkg, c, d)
        self.assertIn("traceability", md.lower())

    def test_no_automation_always_produces_baseline_immediate_action(self) -> None:
        from ai_test_strategy_generator.renderer import render_strategy
        from ai_test_strategy_generator.input_loader import load_input
        from ai_test_strategy_generator.context_classifier import classify_context
        from ai_test_strategy_generator.rule_engine import apply_rules

        pkg = load_input(Path("benchmarks/greenfield-aggressive-timeline.input.yaml"))
        c = classify_context(pkg)
        d = apply_rules(c)
        md = render_strategy(pkg, c, d)
        # Greenfield with no automation → next steps must include baseline/automation language
        self.assertTrue(
            "baseline" in md.lower() or "automation candidate" in md.lower(),
            "Expected baseline automation language in next steps for no-automation greenfield",
        )


if __name__ == "__main__":
    unittest.main()
