from __future__ import annotations

import json
import unittest
from pathlib import Path
from uuid import uuid4


class ArtifactLoaderTests(unittest.TestCase):
    def make_artifact_dir(self) -> Path:
        artifact_dir = Path("tests") / ".tmp" / "artifacts" / str(uuid4())
        artifact_dir.mkdir(parents=True, exist_ok=True)
        return artifact_dir

    def write_text(self, root: Path, relative_path: str, content: str) -> None:
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def write_json(self, root: Path, relative_path: str, payload: dict[str, object]) -> None:
        self.write_text(root, relative_path, json.dumps(payload, indent=2))

    def test_load_artifact_folder_reads_manifest_and_supported_files(self) -> None:
        from ai_test_strategy_generator.artifact_loader import load_artifact_folder

        artifact_dir = self.make_artifact_dir()
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
                    "  - type: api_summary",
                    "    path: api-summary.json",
                    "overrides:",
                    "  strategy_depth: standard",
                ]
            ),
        )
        self.write_text(artifact_dir, "project-summary.md", "# Project Summary\nBusiness Goal: modernize claims")
        self.write_json(artifact_dir, "api-summary.json", {"api_style": "REST", "contract_maturity": "partial"})

        bundle = load_artifact_folder(artifact_dir)

        self.assertEqual(bundle.manifest.engagement_name, "Claims Modernization QE Strategy")
        self.assertEqual(bundle.manifest.domain, "Insurance")
        self.assertEqual(bundle.manifest.project_posture, "brownfield")
        self.assertEqual(bundle.manifest.overrides["strategy_depth"], "standard")
        self.assertEqual(len(bundle.documents), 2)
        self.assertEqual(bundle.documents[0].artifact_type, "project_summary")
        self.assertEqual(bundle.documents[0].format, "md")
        self.assertTrue(isinstance(bundle.documents[0].content, str))
        self.assertEqual(bundle.documents[1].artifact_type, "api_summary")
        self.assertEqual(bundle.documents[1].format, "json")
        self.assertEqual(bundle.documents[1].content["api_style"], "REST")

    def test_load_artifact_folder_fails_when_manifest_is_missing(self) -> None:
        from ai_test_strategy_generator.artifact_loader import ArtifactLoadError, load_artifact_folder

        artifact_dir = self.make_artifact_dir()

        with self.assertRaises(ArtifactLoadError) as exc:
            load_artifact_folder(artifact_dir)

        self.assertIn("manifest", str(exc.exception).lower())

    def test_load_artifact_folder_fails_for_missing_referenced_file(self) -> None:
        from ai_test_strategy_generator.artifact_loader import ArtifactLoadError, load_artifact_folder

        artifact_dir = self.make_artifact_dir()
        self.write_text(
            artifact_dir,
            "manifest.yaml",
            "\n".join(
                [
                    "engagement_name: Retail QE Strategy",
                    "domain: Retail",
                    "project_posture: greenfield",
                    "artifacts:",
                    "  - type: project_summary",
                    "    path: project-summary.md",
                ]
            ),
        )

        with self.assertRaises(ArtifactLoadError) as exc:
            load_artifact_folder(artifact_dir)

        self.assertIn("referenced artifact file not found", str(exc.exception).lower())

    def test_load_artifact_folder_fails_for_unsupported_artifact_extension(self) -> None:
        from ai_test_strategy_generator.artifact_loader import ArtifactLoadError, load_artifact_folder

        artifact_dir = self.make_artifact_dir()
        self.write_text(
            artifact_dir,
            "manifest.yaml",
            "\n".join(
                [
                    "engagement_name: Retail QE Strategy",
                    "domain: Retail",
                    "project_posture: brownfield",
                    "artifacts:",
                    "  - type: project_summary",
                    "    path: project-summary.txt",
                ]
            ),
        )
        self.write_text(artifact_dir, "project-summary.txt", "plain text")

        with self.assertRaises(ArtifactLoadError) as exc:
            load_artifact_folder(artifact_dir)

        self.assertIn("unsupported artifact file type", str(exc.exception).lower())

    def test_load_artifact_folder_fails_for_duplicate_artifact_type(self) -> None:
        from ai_test_strategy_generator.artifact_loader import ArtifactLoadError, load_artifact_folder

        artifact_dir = self.make_artifact_dir()
        self.write_text(
            artifact_dir,
            "manifest.yaml",
            "\n".join(
                [
                    "engagement_name: Retail QE Strategy",
                    "domain: Retail",
                    "project_posture: brownfield",
                    "artifacts:",
                    "  - type: project_summary",
                    "    path: project-summary.md",
                    "  - type: project_summary",
                    "    path: project-summary-2.md",
                ]
            ),
        )
        self.write_text(artifact_dir, "project-summary.md", "Summary one")
        self.write_text(artifact_dir, "project-summary-2.md", "Summary two")

        with self.assertRaises(ArtifactLoadError) as exc:
            load_artifact_folder(artifact_dir)

        self.assertIn("duplicate artifact type", str(exc.exception).lower())

    def test_load_artifact_folder_fails_for_path_outside_artifact_root(self) -> None:
        from ai_test_strategy_generator.artifact_loader import ArtifactLoadError, load_artifact_folder

        artifact_dir = self.make_artifact_dir()
        self.write_text(
            artifact_dir,
            "manifest.yaml",
            "\n".join(
                [
                    "engagement_name: Retail QE Strategy",
                    "domain: Retail",
                    "project_posture: brownfield",
                    "artifacts:",
                    "  - type: project_summary",
                    "    path: ..\\outside.md",
                ]
            ),
        )
        self.write_text(artifact_dir.parent, "outside.md", "outside")

        with self.assertRaises(ArtifactLoadError) as exc:
            load_artifact_folder(artifact_dir)

        self.assertIn("outside the artifact folder", str(exc.exception).lower())

    def test_load_artifact_folder_fails_for_invalid_manifest_shape(self) -> None:
        from ai_test_strategy_generator.artifact_loader import ArtifactLoadError, load_artifact_folder

        artifact_dir = self.make_artifact_dir()
        self.write_text(artifact_dir, "manifest.yaml", "- not: a mapping")

        with self.assertRaises(ArtifactLoadError) as exc:
            load_artifact_folder(artifact_dir)

        self.assertIn("manifest", str(exc.exception).lower())

    def test_load_artifact_folder_fails_for_invalid_project_posture(self) -> None:
        from ai_test_strategy_generator.artifact_loader import ArtifactLoadError, load_artifact_folder

        artifact_dir = self.make_artifact_dir()
        self.write_text(
            artifact_dir,
            "manifest.yaml",
            "\n".join(
                [
                    "engagement_name: API QE Strategy",
                    "domain: SaaS",
                    "project_posture: migration",
                    "artifacts:",
                    "  - type: project_summary",
                    "    path: project-summary.md",
                ]
            ),
        )
        self.write_text(artifact_dir, "project-summary.md", "Business Goal: launch fast")

        with self.assertRaises(ArtifactLoadError) as exc:
            load_artifact_folder(artifact_dir)

        self.assertIn("project_posture", str(exc.exception))

    def test_load_artifact_folder_fails_for_empty_artifact_list(self) -> None:
        from ai_test_strategy_generator.artifact_loader import ArtifactLoadError, load_artifact_folder

        artifact_dir = self.make_artifact_dir()
        self.write_text(
            artifact_dir,
            "manifest.yaml",
            "\n".join(
                [
                    "engagement_name: API QE Strategy",
                    "domain: SaaS",
                    "project_posture: greenfield",
                    "artifacts: []",
                ]
            ),
        )

        with self.assertRaises(ArtifactLoadError) as exc:
            load_artifact_folder(artifact_dir)

        self.assertIn("at least one artifact", str(exc.exception).lower())

    def test_load_artifact_folder_fails_for_invalid_json_artifact(self) -> None:
        from ai_test_strategy_generator.artifact_loader import ArtifactLoadError, load_artifact_folder

        artifact_dir = self.make_artifact_dir()
        self.write_text(
            artifact_dir,
            "manifest.yaml",
            "\n".join(
                [
                    "engagement_name: API QE Strategy",
                    "domain: SaaS",
                    "project_posture: greenfield",
                    "artifacts:",
                    "  - type: api_summary",
                    "    path: api-summary.json",
                ]
            ),
        )
        self.write_text(artifact_dir, "api-summary.json", "{ invalid json")

        with self.assertRaises(ArtifactLoadError) as exc:
            load_artifact_folder(artifact_dir)

        self.assertIn("json", str(exc.exception).lower())

    def test_load_artifact_folder_fails_for_invalid_yaml_artifact(self) -> None:
        from ai_test_strategy_generator.artifact_loader import ArtifactLoadError, load_artifact_folder

        artifact_dir = self.make_artifact_dir()
        self.write_text(
            artifact_dir,
            "manifest.yaml",
            "\n".join(
                [
                    "engagement_name: API QE Strategy",
                    "domain: SaaS",
                    "project_posture: greenfield",
                    "artifacts:",
                    "  - type: api_summary",
                    "    path: api-summary.yaml",
                ]
            ),
        )
        self.write_text(artifact_dir, "api-summary.yaml", "bad: [yaml")

        with self.assertRaises(ArtifactLoadError) as exc:
            load_artifact_folder(artifact_dir)

        self.assertIn("yaml", str(exc.exception).lower())

    def test_load_artifact_folder_fails_when_referenced_path_is_directory(self) -> None:
        from ai_test_strategy_generator.artifact_loader import ArtifactLoadError, load_artifact_folder

        artifact_dir = self.make_artifact_dir()
        (artifact_dir / "project-summary.md").mkdir(parents=True, exist_ok=True)
        self.write_text(
            artifact_dir,
            "manifest.yaml",
            "\n".join(
                [
                    "engagement_name: Retail QE Strategy",
                    "domain: Retail",
                    "project_posture: brownfield",
                    "artifacts:",
                    "  - type: project_summary",
                    "    path: project-summary.md",
                ]
            ),
        )

        with self.assertRaises(ArtifactLoadError) as exc:
            load_artifact_folder(artifact_dir)

        self.assertIn("must be a file", str(exc.exception).lower())


class ArtifactLoaderCoverageHardeningTests(unittest.TestCase):
    """Targeted tests for previously uncovered branches."""

    def make_artifact_dir(self) -> Path:
        from uuid import uuid4
        artifact_dir = Path("tests") / ".tmp" / "artifacts" / str(uuid4())
        artifact_dir.mkdir(parents=True, exist_ok=True)
        return artifact_dir

    def write_text(self, root: Path, relative_path: str, content: str) -> None:
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    # -- line 36: folder path does not exist --
    def test_nonexistent_folder_raises(self) -> None:
        from ai_test_strategy_generator.artifact_loader import ArtifactLoadError, load_artifact_folder
        with self.assertRaises(ArtifactLoadError) as ctx:
            load_artifact_folder("/nonexistent/path/that/cannot/exist")
        self.assertIn("artifact folder not found", str(ctx.exception).lower())

    # -- line 57: manifest YAML is a valid dict but missing required fields --
    def test_manifest_missing_required_fields_raises(self) -> None:
        from ai_test_strategy_generator.artifact_loader import ArtifactLoadError, load_artifact_folder
        artifact_dir = self.make_artifact_dir()
        self.write_text(artifact_dir, "manifest.yaml", "engagement_name: Test\ndomain: Tech\n")
        with self.assertRaises(ArtifactLoadError) as ctx:
            load_artifact_folder(artifact_dir)
        self.assertIn("missing required fields", str(ctx.exception).lower())

    # -- line 61: artifacts field is not a list --
    def test_artifacts_not_a_list_raises(self) -> None:
        from ai_test_strategy_generator.artifact_loader import ArtifactLoadError, load_artifact_folder
        artifact_dir = self.make_artifact_dir()
        self.write_text(
            artifact_dir, "manifest.yaml",
            "engagement_name: Test\ndomain: Tech\nproject_posture: greenfield\nartifacts: not_a_list\n"
        )
        with self.assertRaises(ArtifactLoadError) as ctx:
            load_artifact_folder(artifact_dir)
        self.assertIn("must be a list", str(ctx.exception).lower())

    # -- line 67: overrides is null — should silently become {} and load successfully --
    def test_overrides_null_treated_as_empty_dict(self) -> None:
        from ai_test_strategy_generator.artifact_loader import load_artifact_folder
        artifact_dir = self.make_artifact_dir()
        self.write_text(artifact_dir, "project-summary.md", "Business Goal: launch fast")
        self.write_text(
            artifact_dir, "manifest.yaml",
            "engagement_name: Test\ndomain: Tech\nproject_posture: greenfield\n"
            "artifacts:\n  - type: project_summary\n    path: project-summary.md\noverrides: null\n"
        )
        bundle = load_artifact_folder(artifact_dir)
        self.assertEqual(bundle.manifest.overrides, {})

    # -- line 69: overrides is not a dict --
    def test_overrides_not_a_dict_raises(self) -> None:
        from ai_test_strategy_generator.artifact_loader import ArtifactLoadError, load_artifact_folder
        artifact_dir = self.make_artifact_dir()
        self.write_text(
            artifact_dir, "manifest.yaml",
            "engagement_name: Test\ndomain: Tech\nproject_posture: greenfield\n"
            "artifacts:\n  - type: project_summary\n    path: p.md\noverrides: \"not_a_dict\"\n"
        )
        with self.assertRaises(ArtifactLoadError) as ctx:
            load_artifact_folder(artifact_dir)
        self.assertIn("mapping", str(ctx.exception).lower())

    # -- line 98: artifact entry is a scalar, not a dict --
    def test_artifact_entry_not_a_dict_raises(self) -> None:
        from ai_test_strategy_generator.artifact_loader import ArtifactLoadError, load_artifact_folder
        artifact_dir = self.make_artifact_dir()
        self.write_text(
            artifact_dir, "manifest.yaml",
            "engagement_name: Test\ndomain: Tech\nproject_posture: greenfield\n"
            "artifacts:\n  - project_summary\n"
        )
        with self.assertRaises(ArtifactLoadError) as ctx:
            load_artifact_folder(artifact_dir)
        self.assertIn("mapping", str(ctx.exception).lower())

    # -- line 103: artifact type not in SUPPORTED_ARTIFACT_TYPES --
    def test_unsupported_artifact_type_raises(self) -> None:
        from ai_test_strategy_generator.artifact_loader import ArtifactLoadError, load_artifact_folder
        artifact_dir = self.make_artifact_dir()
        self.write_text(
            artifact_dir, "manifest.yaml",
            "engagement_name: Test\ndomain: Tech\nproject_posture: greenfield\n"
            "artifacts:\n  - type: test_cases\n    path: test-cases.md\n"
        )
        with self.assertRaises(ArtifactLoadError) as ctx:
            load_artifact_folder(artifact_dir)
        self.assertIn("unsupported artifact type", str(ctx.exception).lower())

    # -- line 127: .yaml artifact file returns ArtifactDocument with format="yaml" --
    def test_yaml_artifact_file_loaded_as_yaml(self) -> None:
        from ai_test_strategy_generator.artifact_loader import load_artifact_folder
        artifact_dir = self.make_artifact_dir()
        self.write_text(
            artifact_dir, "manifest.yaml",
            "engagement_name: Test\ndomain: Tech\nproject_posture: greenfield\n"
            "artifacts:\n  - type: project_summary\n    path: project-summary.yaml\n"
        )
        self.write_text(
            artifact_dir, "project-summary.yaml",
            "delivery_model: Agile\nbusiness_goal: launch fast\n"
        )
        bundle = load_artifact_folder(artifact_dir)
        self.assertEqual(bundle.documents[0].format, "yaml")
        self.assertEqual(bundle.documents[0].content["delivery_model"], "Agile")

    # -- line 153: JSON file contains a valid array, not a dict --
    def test_json_array_artifact_raises(self) -> None:
        from ai_test_strategy_generator.artifact_loader import ArtifactLoadError, load_artifact_folder
        artifact_dir = self.make_artifact_dir()
        self.write_text(
            artifact_dir, "manifest.yaml",
            "engagement_name: Test\ndomain: Tech\nproject_posture: greenfield\n"
            "artifacts:\n  - type: api_summary\n    path: api-summary.json\n"
        )
        self.write_text(artifact_dir, "api-summary.json", '["endpoint1", "endpoint2"]')
        with self.assertRaises(ArtifactLoadError) as ctx:
            load_artifact_folder(artifact_dir)
        self.assertIn("mapping", str(ctx.exception).lower())

    # -- line 160: _require_non_blank_string when field is blank or wrong type --
    def test_blank_engagement_name_raises(self) -> None:
        from ai_test_strategy_generator.artifact_loader import ArtifactLoadError, load_artifact_folder
        artifact_dir = self.make_artifact_dir()
        self.write_text(
            artifact_dir, "manifest.yaml",
            "engagement_name: \"  \"\ndomain: Tech\nproject_posture: greenfield\n"
            "artifacts:\n  - type: project_summary\n    path: p.md\n"
        )
        with self.assertRaises(ArtifactLoadError) as ctx:
            load_artifact_folder(artifact_dir)
        self.assertIn("engagement_name", str(ctx.exception).lower())

    def test_integer_domain_raises(self) -> None:
        from ai_test_strategy_generator.artifact_loader import ArtifactLoadError, load_artifact_folder
        artifact_dir = self.make_artifact_dir()
        self.write_text(
            artifact_dir, "manifest.yaml",
            "engagement_name: Test\ndomain: 42\nproject_posture: greenfield\n"
            "artifacts:\n  - type: project_summary\n    path: p.md\n"
        )
        with self.assertRaises(ArtifactLoadError) as ctx:
            load_artifact_folder(artifact_dir)
        self.assertIn("domain", str(ctx.exception).lower())

    # -- line 132: dead-code guard in _load_artifact_document for unsupported suffix
    #    reached only by bypassing _build_artifact_reference pre-validation --
    def test_load_artifact_document_unsupported_suffix_raises(self) -> None:
        from ai_test_strategy_generator.artifact_loader import (
            ArtifactLoadError,
            _load_artifact_document,
        )
        from ai_test_strategy_generator.models import ArtifactReference
        artifact_dir = self.make_artifact_dir().resolve()
        # Write a file with an extension that passes the is_relative_to check
        # but is not .md / .yaml / .yml / .json — bypassing _build_artifact_reference
        csv_file = artifact_dir / "data.csv"
        csv_file.write_text("col1,col2\n", encoding="utf-8")
        # Use a relative path so the resolved artifact_path stays inside artifact_dir
        ref = ArtifactReference("project_summary", Path("data.csv"))
        with self.assertRaises(ArtifactLoadError) as ctx:
            _load_artifact_document(artifact_dir, ref)
        self.assertIn("unsupported artifact file type", str(ctx.exception).lower())


if __name__ == "__main__":
    unittest.main()
