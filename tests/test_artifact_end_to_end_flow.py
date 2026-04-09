from __future__ import annotations

import json
import unittest
from pathlib import Path
from uuid import uuid4


class ArtifactEndToEndFlowTests(unittest.TestCase):
    def make_workspace(self) -> Path:
        workspace = Path("tests") / ".tmp" / "artifact-end-to-end" / str(uuid4())
        workspace.mkdir(parents=True, exist_ok=True)
        return workspace

    def write_text(self, root: Path, relative_path: str, content: str) -> None:
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def build_artifact_folder(self, root: Path) -> Path:
        artifact_dir = root / "claims-artifacts"
        artifact_dir.mkdir(parents=True, exist_ok=True)
        self.write_text(
            artifact_dir,
            "manifest.yaml",
            "\n".join(
                [
                    "engagement_name: Claims Modernization QE Strategy",
                    "domain: Insurance",
                    "project_posture: brownfield",
                    "artifacts:",
                    "  - type: project_summary",
                    "    path: project-summary.md",
                    "  - type: requirements_summary",
                    "    path: requirements-summary.md",
                    "  - type: system_landscape",
                    "    path: system-landscape.md",
                    "  - type: api_summary",
                    "    path: api-summary.json",
                    "  - type: current_test_state",
                    "    path: current-test-state.md",
                    "overrides:",
                    "  ai_adoption_posture: cautious",
                    "  strategy_depth: standard",
                ]
            ),
        )
        self.write_text(
            artifact_dir,
            "project-summary.md",
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
        )
        self.write_text(
            artifact_dir,
            "requirements-summary.md",
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
        )
        self.write_text(
            artifact_dir,
            "system-landscape.md",
            "\n".join(
                [
                    "System Type: API-first with supporting UI",
                    "Applications In Scope:",
                    "- claims portal",
                    "- claims service layer",
                    "- payment integration",
                    "Key Integrations:",
                    "- policy platform",
                    "- payment gateway",
                    "Platform Notes: Legacy UI still exists around a partly modernized service layer",
                ]
            ),
        )
        self.write_text(
            artifact_dir,
            "api-summary.json",
            json.dumps(
                {
                    "api_docs_available": "yes - partial OpenAPI coverage",
                    "requirements_available": "yes - feature summaries available",
                },
                indent=2,
            ),
        )
        self.write_text(
            artifact_dir,
            "current-test-state.md",
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
        )
        return artifact_dir

    def test_run_artifact_benchmark_flow_generates_output_and_passes_assertions(self) -> None:
        from ai_test_strategy_generator.artifact_end_to_end_flow import run_artifact_benchmark_flow

        workspace = self.make_workspace()
        artifact_dir = self.build_artifact_folder(workspace)
        output_path = workspace / "outputs" / "strategy.md"

        result = run_artifact_benchmark_flow(
            artifact_dir,
            Path("benchmarks/brownfield-partial-automation.assertions.yaml"),
            output_path,
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["exit_code"], 0)
        self.assertTrue(output_path.exists())
        self.assertEqual(result["validation_errors"], [])
        self.assertEqual(result["assertion_errors"], [])

    def test_run_artifact_benchmark_flow_passes_for_committed_benchmark_folder(self) -> None:
        from ai_test_strategy_generator.artifact_end_to_end_flow import run_artifact_benchmark_flow

        workspace = self.make_workspace()
        output_path = workspace / "outputs" / "artifact-benchmark-strategy.md"

        result = run_artifact_benchmark_flow(
            Path("benchmarks/artifact-brownfield"),
            Path("benchmarks/artifact-brownfield.assertions.yaml"),
            output_path,
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["exit_code"], 0)
        self.assertTrue(output_path.exists())

    def test_run_artifact_benchmark_flow_fails_when_artifact_folder_is_invalid(self) -> None:
        from ai_test_strategy_generator.artifact_end_to_end_flow import run_artifact_benchmark_flow

        workspace = self.make_workspace()
        output_path = workspace / "outputs" / "strategy.md"

        result = run_artifact_benchmark_flow(
            workspace / "missing-folder",
            Path("benchmarks/brownfield-partial-automation.assertions.yaml"),
            output_path,
        )

        self.assertFalse(result["success"])
        self.assertEqual(result["exit_code"], 1)

    def test_run_artifact_benchmark_flow_fails_when_mapped_input_is_incomplete(self) -> None:
        from ai_test_strategy_generator.artifact_end_to_end_flow import run_artifact_benchmark_flow

        workspace = self.make_workspace()
        artifact_dir = workspace / "incomplete-artifacts"
        artifact_dir.mkdir(parents=True, exist_ok=True)
        self.write_text(
            artifact_dir,
            "manifest.yaml",
            "\n".join(
                [
                    "engagement_name: Minimal QE Strategy",
                    "domain: SaaS",
                    "project_posture: greenfield",
                    "artifacts:",
                    "  - type: project_summary",
                    "    path: project-summary.md",
                    "overrides:",
                    "  strategy_depth: standard",
                    "  ai_adoption_posture: supportive",
                ]
            ),
        )
        self.write_text(
            artifact_dir,
            "project-summary.md",
            "\n".join(
                [
                    "Delivery Model: Agile",
                    "Business Goal: launch fast",
                ]
            ),
        )

        output_path = workspace / "outputs" / "incomplete-strategy.md"
        result = run_artifact_benchmark_flow(
            artifact_dir,
            Path("benchmarks/brownfield-partial-automation.assertions.yaml"),
            output_path,
        )

        self.assertFalse(result["success"])
        self.assertEqual(result["exit_code"], 2)
        self.assertTrue(any("Missing required field" in error for error in result["validation_errors"]))


if __name__ == "__main__":
    unittest.main()
