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


if __name__ == "__main__":
    unittest.main()
