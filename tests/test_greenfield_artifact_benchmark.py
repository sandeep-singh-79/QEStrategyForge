"""Integration tests for the greenfield artifact benchmark (Slice 7.9).

Binary pass/fail condition:
- run_artifact_benchmark_flow succeeds (exit_code == 0)
- output file is non-empty
- output passes validate_output
- brownfield-specific content is absent from the output
"""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from ai_test_strategy_generator.artifact_end_to_end_flow import run_artifact_benchmark_flow
from ai_test_strategy_generator.output_validator import validate_output

_BENCHMARK_ROOT = Path(__file__).parent.parent / "benchmarks"
_ARTIFACT_FOLDER = _BENCHMARK_ROOT / "artifact-greenfield"
_ASSERTIONS = _BENCHMARK_ROOT / "artifact-greenfield.assertions.yaml"


class TestGreenfieldArtifactBenchmark(unittest.TestCase):
    """End-to-end flow through the committed greenfield artifact folder."""

    def setUp(self) -> None:
        self._tmp = tempfile.NamedTemporaryFile(suffix=".md", delete=False)
        self._tmp.close()
        self._output_path = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._output_path.unlink(missing_ok=True)

    def test_greenfield_artifact_benchmark_exits_zero(self) -> None:
        result = run_artifact_benchmark_flow(
            _ARTIFACT_FOLDER,
            _ASSERTIONS,
            self._output_path,
        )
        self.assertEqual(
            result["exit_code"],
            0,
            msg=f"Expected exit_code 0, got {result['exit_code']}.\n"
                f"Validation errors: {result['validation_errors']}\n"
                f"Assertion errors: {result['assertion_errors']}",
        )

    def test_output_file_is_non_empty(self) -> None:
        run_artifact_benchmark_flow(_ARTIFACT_FOLDER, _ASSERTIONS, self._output_path)
        self.assertGreater(self._output_path.stat().st_size, 0)

    def test_output_passes_structural_validation(self) -> None:
        run_artifact_benchmark_flow(_ARTIFACT_FOLDER, _ASSERTIONS, self._output_path)
        markdown = self._output_path.read_text(encoding="utf-8")
        result = validate_output(markdown)
        self.assertTrue(
            result.is_valid,
            msg=f"Output failed structural validation: {result.errors}",
        )

    def test_output_contains_greenfield_posture(self) -> None:
        run_artifact_benchmark_flow(_ARTIFACT_FOLDER, _ASSERTIONS, self._output_path)
        markdown = self._output_path.read_text(encoding="utf-8")
        self.assertIn("Project Posture: greenfield", markdown)

    def test_output_does_not_contain_brownfield_content(self) -> None:
        run_artifact_benchmark_flow(_ARTIFACT_FOLDER, _ASSERTIONS, self._output_path)
        markdown = self._output_path.read_text(encoding="utf-8")
        self.assertNotIn("Project Posture: brownfield", markdown)
        self.assertNotIn("Brownfield Transition Strategy:", markdown)
        self.assertNotIn("assess_reuse_stabilize_retire_replace", markdown)

    def test_engagement_name_context_present_in_output(self) -> None:
        """The engagement context (domain/goal) should surface in the output."""
        run_artifact_benchmark_flow(_ARTIFACT_FOLDER, _ASSERTIONS, self._output_path)
        markdown = self._output_path.read_text(encoding="utf-8")
        # The business goal from the project-summary artifact is rendered verbatim
        self.assertIn("Launch a scalable real-time payments platform", markdown)


class TestGreenfieldArtifactFolderLoad(unittest.TestCase):
    """Verify the artifact folder itself loads cleanly before flow runs."""

    def test_artifact_folder_loads_without_error(self) -> None:
        from ai_test_strategy_generator.artifact_loader import load_artifact_folder
        bundle = load_artifact_folder(_ARTIFACT_FOLDER)
        self.assertEqual(bundle.manifest.project_posture, "greenfield")
        self.assertEqual(bundle.manifest.engagement_name, "Payments Platform QE Strategy")
        self.assertEqual(len(bundle.documents), 5)

    def test_artifact_bundle_maps_to_input_package(self) -> None:
        from ai_test_strategy_generator.artifact_loader import load_artifact_folder
        from ai_test_strategy_generator.artifact_mapping import map_artifact_bundle
        bundle = load_artifact_folder(_ARTIFACT_FOLDER)
        pkg = map_artifact_bundle(bundle)
        self.assertEqual(pkg.normalized["project_posture"], "greenfield")
        self.assertEqual(pkg.normalized["ai_adoption_posture"], "supportive")
        self.assertIn("payment initiation", pkg.normalized["critical_business_flows"])

    def test_greenfield_artifact_assertions_file_exists(self) -> None:
        self.assertTrue(
            _ASSERTIONS.exists(),
            msg=f"Assertions file not found: {_ASSERTIONS}",
        )


if __name__ == "__main__":
    unittest.main()
