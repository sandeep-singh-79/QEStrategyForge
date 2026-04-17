"""Cross-module contract tests.

These tests act as canaries for cross-module string drift — they catch cases where
heading/label/decision key strings diverge between the modules that produce them
(renderer, rule_engine) and the modules that validate or consume them
(output_validator, llm_flow, prompt_builder).

They do NOT test business logic; they enforce the integration contract between modules.
"""
from __future__ import annotations

import unittest
from pathlib import Path


class HeadingContractTests(unittest.TestCase):
    def test_every_renderer_heading_is_in_required_headings(self) -> None:
        """Every ## heading produced by build_strategy_document() must appear in REQUIRED_HEADINGS."""
        from ai_test_strategy_generator.input_loader import load_input
        from ai_test_strategy_generator.context_classifier import classify_context
        from ai_test_strategy_generator.rule_engine import apply_rules
        from ai_test_strategy_generator.renderer import build_strategy_document
        from ai_test_strategy_generator.output_validator import REQUIRED_HEADINGS

        input_package = load_input(
            Path("benchmarks/brownfield-partial-automation.input.yaml")
        )
        classifications = classify_context(input_package)
        decisions = apply_rules(classifications)
        doc = build_strategy_document(input_package, classifications, decisions)

        renderer_headings = {section.heading for section in doc.sections}
        required_set = set(REQUIRED_HEADINGS)
        drift = renderer_headings - required_set
        self.assertEqual(
            drift,
            set(),
            f"Renderer produces headings not in REQUIRED_HEADINGS: {drift}",
        )

    def test_required_headings_all_produced_by_renderer(self) -> None:
        """Each heading in REQUIRED_HEADINGS must appear in the renderer output."""
        from ai_test_strategy_generator.input_loader import load_input
        from ai_test_strategy_generator.context_classifier import classify_context
        from ai_test_strategy_generator.rule_engine import apply_rules
        from ai_test_strategy_generator.renderer import render_strategy
        from ai_test_strategy_generator.output_validator import REQUIRED_HEADINGS

        input_package = load_input(
            Path("benchmarks/brownfield-partial-automation.input.yaml")
        )
        classifications = classify_context(input_package)
        decisions = apply_rules(classifications)
        markdown = render_strategy(input_package, classifications, decisions)

        for heading in REQUIRED_HEADINGS:
            lines = markdown.splitlines()
            found = any(line.strip() == heading for line in lines)
            self.assertTrue(found, f"Renderer did not produce required heading: {heading!r}")


class LabelContractTests(unittest.TestCase):
    def test_every_required_label_prefix_is_produced_by_renderer(self) -> None:
        """Each label prefix in REQUIRED_LABELS must appear as a line start in renderer output."""
        from ai_test_strategy_generator.input_loader import load_input
        from ai_test_strategy_generator.context_classifier import classify_context
        from ai_test_strategy_generator.rule_engine import apply_rules
        from ai_test_strategy_generator.renderer import render_strategy
        from ai_test_strategy_generator.output_validator import REQUIRED_LABELS

        input_package = load_input(
            Path("benchmarks/brownfield-partial-automation.input.yaml")
        )
        classifications = classify_context(input_package)
        decisions = apply_rules(classifications)
        markdown = render_strategy(input_package, classifications, decisions)

        lines = markdown.splitlines()
        for label in REQUIRED_LABELS:
            found = any(line.strip().startswith(label) for line in lines)
            self.assertTrue(found, f"Renderer did not produce required label: {label!r}")

    def test_repair_label_map_covers_all_required_labels(self) -> None:
        """_build_label_values() must return a key for every entry in REQUIRED_LABELS."""
        from ai_test_strategy_generator.llm_flow import _build_label_values
        from ai_test_strategy_generator.output_validator import REQUIRED_LABELS
        from ai_test_strategy_generator.input_loader import load_input
        from ai_test_strategy_generator.context_classifier import classify_context
        from ai_test_strategy_generator.rule_engine import apply_rules

        input_package = load_input(
            Path("benchmarks/brownfield-partial-automation.input.yaml")
        )
        classifications = classify_context(input_package)
        decisions = apply_rules(classifications)
        label_map = _build_label_values(input_package.normalized, decisions)

        missing = [label for label in REQUIRED_LABELS if label not in label_map]
        self.assertEqual(
            missing,
            [],
            f"_build_label_values() is missing entries for: {missing}",
        )


class DecisionKeyContractTests(unittest.TestCase):
    def test_all_rule_engine_keys_consumed_by_format_decisions(self) -> None:
        """Every key returned by apply_rules() must be rendered by _format_decisions()."""
        from ai_test_strategy_generator.rule_engine import apply_rules
        from ai_test_strategy_generator.prompt_builder import _format_decisions

        # Use a classification that produces all decision keys including brownfield_transition
        classifications = {
            "project_posture": "brownfield",
            "automation_maturity": "partial",
            "ci_cd_maturity": "partial",
            "system_profile": "legacy",
            "regulatory_sensitivity": "high",
            "information_completeness": "partial",
        }
        decisions = apply_rules(classifications)
        formatted = _format_decisions(decisions)

        # Every non-not_applicable decision value should appear in the formatted string
        for key, value in decisions.items():
            if value != "not_applicable":
                self.assertIn(
                    value, formatted,
                    f"Decision key {key!r}={value!r} not rendered by _format_decisions()",
                )

    def test_scenario_selection_returns_only_existing_template_names(self) -> None:
        """_select_scenario() must return only names for which a prompts/v1/*.txt file exists."""
        from ai_test_strategy_generator.prompt_builder import _select_scenario

        prompts_dir = Path(__file__).parent.parent / "src" / "ai_test_strategy_generator" / "prompts" / "v1"
        existing_names = {p.stem for p in prompts_dir.glob("*.txt") if p.stem != "base"}

        for classifications, description in [
            ({"information_completeness": "incomplete"}, "incomplete_context"),
            ({"regulatory_sensitivity": "high"}, "compliance_heavy"),
            ({"project_posture": "greenfield"}, "greenfield"),
            ({}, "brownfield (default)"),
        ]:
            name = _select_scenario(classifications)
            self.assertIn(
                name,
                existing_names,
                f"_select_scenario({description}) returned {name!r} which has no .txt file",
            )


class ModelContractTests(unittest.TestCase):
    def test_flow_result_has_all_required_keys(self) -> None:
        """make_flow_result() must return a dict with all FlowResult keys."""
        from ai_test_strategy_generator.models import make_flow_result, FlowResult
        import typing

        result = make_flow_result(True, 0, [], [], "/tmp/out.md")
        required_keys = set(FlowResult.__annotations__.keys())
        self.assertEqual(set(result.keys()), required_keys)

    def test_exit_code_constants_are_distinct(self) -> None:
        """All EXIT_* constants must have unique integer values."""
        from ai_test_strategy_generator.models import (
            EXIT_SUCCESS,
            EXIT_LOAD_ERROR,
            EXIT_INPUT_INVALID,
            EXIT_OUTPUT_INVALID,
            EXIT_ASSERTIONS_FAILED,
        )
        codes = [EXIT_SUCCESS, EXIT_LOAD_ERROR, EXIT_INPUT_INVALID, EXIT_OUTPUT_INVALID, EXIT_ASSERTIONS_FAILED]
        self.assertEqual(len(codes), len(set(codes)), f"Duplicate exit code values: {codes}")


class RendererValidatorIntegrationTests(unittest.TestCase):
    """Integration: every committed benchmark input must produce structurally valid output.

    These are canary tests — if any benchmark exercises a renderer branch that
    produces a misplaced or duplicate label, these catch it immediately.
    """

    _BENCHMARKS = [
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

    def _render_and_validate(self, input_path: str):
        from ai_test_strategy_generator.input_loader import load_input
        from ai_test_strategy_generator.context_classifier import classify_context
        from ai_test_strategy_generator.rule_engine import apply_rules
        from ai_test_strategy_generator.renderer import render_strategy
        from ai_test_strategy_generator.output_validator import validate_output

        pkg = load_input(Path(input_path))
        classifications = classify_context(pkg)
        decisions = apply_rules(classifications)
        markdown = render_strategy(pkg, classifications, decisions)
        return validate_output(markdown)

    def test_all_benchmarks_produce_valid_output(self) -> None:
        """Each benchmark input must produce output that passes structural validation."""
        failures: dict[str, list[str]] = {}
        for path in self._BENCHMARKS:
            result = self._render_and_validate(path)
            if not result.is_valid:
                failures[path] = result.errors
        self.assertEqual(
            failures,
            {},
            f"Benchmarks produced invalid output:\n" +
            "\n".join(f"  {p}: {errs}" for p, errs in failures.items()),
        )

    def test_all_benchmarks_produce_no_duplicate_labels(self) -> None:
        """No required label should appear more than once in any benchmark output."""
        from ai_test_strategy_generator.output_validator import REQUIRED_LABELS
        from ai_test_strategy_generator.input_loader import load_input
        from ai_test_strategy_generator.context_classifier import classify_context
        from ai_test_strategy_generator.rule_engine import apply_rules
        from ai_test_strategy_generator.renderer import render_strategy

        duplicates: dict[str, list[str]] = {}
        for path in self._BENCHMARKS:
            pkg = load_input(Path(path))
            c = classify_context(pkg)
            d = apply_rules(c)
            md = render_strategy(pkg, c, d)
            dup = [label for label in REQUIRED_LABELS if md.count(label) > 1]
            if dup:
                duplicates[path] = dup
        self.assertEqual(
            duplicates,
            {},
            f"Duplicate labels found:\n" +
            "\n".join(f"  {p}: {labels}" for p, labels in duplicates.items()),
        )

    def test_all_benchmarks_produce_labels_in_correct_sections(self) -> None:
        """Each required label must appear under its declared section in every benchmark."""
        from ai_test_strategy_generator.output_validator import LABEL_SECTION_MAP
        from ai_test_strategy_generator.input_loader import load_input
        from ai_test_strategy_generator.context_classifier import classify_context
        from ai_test_strategy_generator.rule_engine import apply_rules
        from ai_test_strategy_generator.renderer import render_strategy
        from ai_test_strategy_generator.output_validator import _parse_sections

        misplacements: dict[str, list[str]] = {}
        for path in self._BENCHMARKS:
            pkg = load_input(Path(path))
            c = classify_context(pkg)
            d = apply_rules(c)
            md = render_strategy(pkg, c, d)
            sections = _parse_sections(md)
            errs = [
                f"'{label}' not in '{heading}'"
                for label, heading in LABEL_SECTION_MAP.items()
                if label in md and label not in sections.get(heading, "")
            ]
            if errs:
                misplacements[path] = errs
        self.assertEqual(
            misplacements,
            {},
            f"Labels in wrong sections:\n" +
            "\n".join(f"  {p}: {errs}" for p, errs in misplacements.items()),
        )


if __name__ == "__main__":
    unittest.main()
