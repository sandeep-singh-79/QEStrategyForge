from __future__ import annotations

import unittest
from pathlib import Path

from ai_test_strategy_generator.models import (
    ArtifactBundle,
    ArtifactDocument,
    ArtifactManifest,
    ArtifactReference,
)


class ArtifactMappingTests(unittest.TestCase):
    def make_bundle(self) -> ArtifactBundle:
        root = Path("artifacts")
        manifest = ArtifactManifest(
            source_path=root / "manifest.yaml",
            engagement_name="Claims Modernization QE Strategy",
            domain="Insurance",
            project_posture="brownfield",
            artifacts=[
                ArtifactReference("project_summary", Path("project-summary.md")),
                ArtifactReference("requirements_summary", Path("requirements-summary.md")),
                ArtifactReference("system_landscape", Path("system-landscape.md")),
                ArtifactReference("api_summary", Path("api-summary.json")),
                ArtifactReference("current_test_state", Path("current-test-state.md")),
            ],
            overrides={
                "ai_adoption_posture": "cautious",
                "strategy_depth": "standard",
            },
        )
        documents = [
            ArtifactDocument(
                "project_summary",
                root / "project-summary.md",
                "md",
                "\n".join(
                    [
                        "Delivery Model: Agile",
                        "Timeline Pressure: high",
                        "Business Goal: Modernize claims processing without increasing regression risk",
                        "Quality Goal: Improve release confidence and reduce leakage",
                        "Release Expectation: Bi-weekly release readiness with quality gates",
                        "Primary Audience: QE lead and delivery leadership",
                    ]
                ),
            ),
            ArtifactDocument(
                "requirements_summary",
                root / "requirements-summary.md",
                "md",
                "\n".join(
                    [
                        "Critical Business Flows:",
                        "- claim creation",
                        "- claim adjudication",
                        "- payout processing",
                        "Delivery Risks:",
                        "- integration instability",
                        "- weak regression confidence",
                        "Missing Information:",
                        "- production defect leakage trend",
                    ]
                ),
            ),
            ArtifactDocument(
                "system_landscape",
                root / "system-landscape.md",
                "md",
                "\n".join(
                    [
                        "System Type: API-first with supporting UI",
                        "Applications In Scope:",
                        "- claims portal",
                        "- claims service layer",
                        "Key Integrations:",
                        "- policy platform",
                        "- payment gateway",
                        "Platform Notes: Legacy UI still exists around a partly modernized service layer",
                    ]
                ),
            ),
            ArtifactDocument(
                "api_summary",
                root / "api-summary.json",
                "json",
                {
                    "api_docs_available": "yes - partial OpenAPI coverage",
                    "requirements_available": "yes - feature summaries available",
                },
            ),
            ArtifactDocument(
                "current_test_state",
                root / "current-test-state.md",
                "md",
                "\n".join(
                    [
                        "Existing Test Process: Manual-heavy with some automation support",
                        "Existing Automation State: partial",
                        "CI/CD Maturity: partial",
                        "Environment Maturity: moderate",
                        "Test Data Maturity: weak",
                        "Known Constraints:",
                        "- incomplete documentation",
                        "- limited QE capacity",
                    ]
                ),
            ),
        ]
        return ArtifactBundle(root_path=root, manifest=manifest, documents=documents)

    def test_map_artifact_bundle_produces_input_package(self) -> None:
        from ai_test_strategy_generator.artifact_mapping import map_artifact_bundle

        input_package = map_artifact_bundle(self.make_bundle())

        self.assertEqual(input_package.normalized["engagement_name"], "Claims Modernization QE Strategy")
        self.assertEqual(input_package.normalized["project_posture"], "brownfield")
        self.assertEqual(input_package.normalized["delivery_model"], "Agile")
        self.assertEqual(input_package.normalized["system_type"], "API-first with supporting UI")
        self.assertEqual(input_package.normalized["existing_automation_state"], "partial")
        self.assertEqual(input_package.normalized["ci_cd_maturity"], "partial")
        self.assertEqual(input_package.normalized["ai_adoption_posture"], "cautious")
        self.assertEqual(input_package.normalized["strategy_depth"], "standard")
        self.assertEqual(input_package.normalized["critical_business_flows"][0], "claim creation")
        self.assertIn("incomplete documentation", input_package.normalized["known_constraints"])

    def test_map_artifact_bundle_raises_for_conflicting_scalar_values(self) -> None:
        from ai_test_strategy_generator.artifact_mapping import ArtifactMappingError, map_artifact_bundle

        bundle = self.make_bundle()
        bundle.documents.append(
            ArtifactDocument(
                "project_summary",
                Path("artifacts/project-summary-override.md"),
                "md",
                "Delivery Model: Waterfall",
            )
        )

        with self.assertRaises(ArtifactMappingError) as exc:
            map_artifact_bundle(bundle)

        self.assertIn("conflicting values", str(exc.exception).lower())

    def test_map_artifact_bundle_applies_manifest_overrides_last(self) -> None:
        from ai_test_strategy_generator.artifact_mapping import map_artifact_bundle

        bundle = self.make_bundle()
        bundle.manifest.overrides["delivery_model"] = "Hybrid"

        input_package = map_artifact_bundle(bundle)

        self.assertEqual(input_package.normalized["delivery_model"], "Hybrid")

    def test_map_artifact_bundle_raises_for_unsupported_document_format(self) -> None:
        from ai_test_strategy_generator.artifact_mapping import ArtifactMappingError, map_artifact_bundle

        bundle = self.make_bundle()
        bundle.documents[0] = ArtifactDocument("project_summary", Path("artifacts/project-summary.txt"), "txt", "bad")

        with self.assertRaises(ArtifactMappingError) as exc:
            map_artifact_bundle(bundle)

        self.assertIn("unsupported artifact document format", str(exc.exception).lower())

    def test_map_artifact_bundle_raises_for_conflict_between_structured_and_markdown_sources(self) -> None:
        from ai_test_strategy_generator.artifact_mapping import ArtifactMappingError, map_artifact_bundle

        bundle = self.make_bundle()
        bundle.documents.append(
            ArtifactDocument(
                "api_summary",
                Path("artifacts/api-summary-override.json"),
                "json",
                {"delivery_model": "Waterfall"},
            )
        )

        with self.assertRaises(ArtifactMappingError) as exc:
            map_artifact_bundle(bundle)

        self.assertIn("conflicting values", str(exc.exception).lower())


class ArtifactMappingCoverageHardeningTests(unittest.TestCase):
    """Targeted tests for previously uncovered branches in artifact_mapping.py."""

    def _minimal_bundle(self, documents: list) -> "ArtifactBundle":
        from ai_test_strategy_generator.models import ArtifactBundle, ArtifactManifest
        manifest = ArtifactManifest(
            source_path=Path("artifacts/manifest.yaml"),
            engagement_name="Test Engagement",
            domain="Tech",
            project_posture="greenfield",
            artifacts=[],
            overrides={},
        )
        return ArtifactBundle(
            root_path=Path("artifacts"),
            manifest=manifest,
            documents=documents,
        )

    # -- line 69: md document with non-string content --
    def test_md_document_with_non_string_content_raises(self) -> None:
        from ai_test_strategy_generator.artifact_mapping import ArtifactMappingError, _map_document
        doc = ArtifactDocument("project_summary", Path("p.md"), "md", 123)
        with self.assertRaises(ArtifactMappingError) as ctx:
            _map_document(doc)
        self.assertIn("text content", str(ctx.exception).lower())

    # -- line 73: yaml/json document with non-dict content --
    def test_json_document_with_non_dict_content_raises(self) -> None:
        from ai_test_strategy_generator.artifact_mapping import ArtifactMappingError, _map_document
        doc = ArtifactDocument("api_summary", Path("a.json"), "json", "unexpected string")
        with self.assertRaises(ArtifactMappingError) as ctx:
            _map_document(doc)
        self.assertIn("mapping content", str(ctx.exception).lower())

    # -- lines 86-87: blank lines interspersed in markdown --
    def test_markdown_with_blank_lines_parsed_correctly(self) -> None:
        from ai_test_strategy_generator.artifact_mapping import _map_markdown_document
        text = "\nDelivery Model: Agile\n\nTimeline Pressure: high\n\n"
        result = _map_markdown_document(text)
        self.assertEqual(result["delivery_model"], "Agile")
        self.assertEqual(result["timeline_pressure"], "high")

    # -- line 100: inline value on a list-field line (e.g. "Critical Business Flows: flow1") --
    def test_inline_list_value_captured(self) -> None:
        from ai_test_strategy_generator.artifact_mapping import _map_markdown_document
        text = "Critical Business Flows: claims intake\n- claim adjudication\n"
        result = _map_markdown_document(text)
        self.assertIn("claims intake", result["critical_business_flows"])
        self.assertIn("claim adjudication", result["critical_business_flows"])

    # -- line 108: line containing ":" but matching neither scalar nor list map (fallthrough) --
    def test_unrecognised_label_silently_ignored(self) -> None:
        from ai_test_strategy_generator.artifact_mapping import _map_markdown_document
        # "Unknown Label" is not in either map; must not raise and must not pollute result
        text = "Unknown Label: some value\nDelivery Model: Agile\n"
        result = _map_markdown_document(text)
        self.assertEqual(result["delivery_model"], "Agile")
        self.assertNotIn("Unknown Label", result)

    # -- line 108 branch: line WITHOUT ":" entirely --
    def test_markdown_line_without_colon_ignored(self) -> None:
        from ai_test_strategy_generator.artifact_mapping import _map_markdown_document
        text = "## Heading\nDelivery Model: Agile\nsome plain text line\n"
        result = _map_markdown_document(text)
        self.assertEqual(result["delivery_model"], "Agile")

    # -- lines 121-122 + 133-139: list merge when both documents contribute to a list field --
    def test_list_field_merged_across_two_documents(self) -> None:
        from ai_test_strategy_generator.artifact_mapping import map_artifact_bundle
        bundle = self._minimal_bundle([
            ArtifactDocument(
                "requirements_summary",
                Path("artifacts/req1.md"),
                "md",
                "Critical Business Flows:\n- flow A\n",
            ),
            ArtifactDocument(
                "system_landscape",
                Path("artifacts/req2.md"),
                "md",
                "Critical Business Flows:\n- flow B\n",
            ),
        ])
        result = map_artifact_bundle(bundle)
        flows = result.normalized["critical_business_flows"]
        self.assertIn("flow A", flows)
        self.assertIn("flow B", flows)

    def test_merge_lists_deduplication(self) -> None:
        from ai_test_strategy_generator.artifact_mapping import _merge_lists
        merged = _merge_lists(["a", "b"], ["b", "c"])
        self.assertEqual(merged, ["a", "b", "c"])

    def test_merge_lists_non_list_existing(self) -> None:
        from ai_test_strategy_generator.artifact_mapping import _merge_lists
        merged = _merge_lists("a", ["b", "c"])
        self.assertIn("a", merged)
        self.assertIn("b", merged)

    def test_merge_lists_non_list_incoming(self) -> None:
        from ai_test_strategy_generator.artifact_mapping import _merge_lists
        merged = _merge_lists(["a"], "b")
        self.assertIn("a", merged)
        self.assertIn("b", merged)

    # -- line 144: _is_empty with None value --
    def test_is_empty_none(self) -> None:
        from ai_test_strategy_generator.artifact_mapping import _is_empty
        self.assertTrue(_is_empty(None))

    # -- lines 147-148: _is_empty with empty/blank string --
    def test_is_empty_blank_string(self) -> None:
        from ai_test_strategy_generator.artifact_mapping import _is_empty
        self.assertTrue(_is_empty(""))
        self.assertTrue(_is_empty("   "))
        self.assertFalse(_is_empty("value"))

    # -- lines 149-150: _is_empty with list --
    def test_is_empty_list(self) -> None:
        from ai_test_strategy_generator.artifact_mapping import _is_empty
        self.assertTrue(_is_empty([]))
        self.assertFalse(_is_empty(["item"]))

    def test_is_empty_non_string_non_list(self) -> None:
        from ai_test_strategy_generator.artifact_mapping import _is_empty
        # integers, dicts, etc. are not empty
        self.assertFalse(_is_empty(0))
        self.assertFalse(_is_empty({}))

    # -- _merge_partial fills in empty-string and None fields --
    def test_merge_partial_fills_empty_string_field(self) -> None:
        from ai_test_strategy_generator.artifact_mapping import _merge_partial
        target: dict = {"delivery_model": ""}
        _merge_partial(target, {"delivery_model": "Agile"})
        self.assertEqual(target["delivery_model"], "Agile")

    def test_merge_partial_fills_none_field(self) -> None:
        from ai_test_strategy_generator.artifact_mapping import _merge_partial
        target: dict = {"delivery_model": None}
        _merge_partial(target, {"delivery_model": "Waterfall"})
        self.assertEqual(target["delivery_model"], "Waterfall")

    def test_merge_partial_fills_empty_list_field(self) -> None:
        from ai_test_strategy_generator.artifact_mapping import _merge_partial
        target: dict = {"critical_business_flows": []}
        _merge_partial(target, {"critical_business_flows": ["claim creation"]})
        self.assertIn("claim creation", target["critical_business_flows"])

    # -- allow_override=False; same value does not raise --
    def test_merge_partial_same_value_no_conflict(self) -> None:
        from ai_test_strategy_generator.artifact_mapping import _merge_partial
        target: dict = {"delivery_model": "Agile"}
        _merge_partial(target, {"delivery_model": "Agile"})  # must not raise
        self.assertEqual(target["delivery_model"], "Agile")


if __name__ == "__main__":
    unittest.main()
