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


if __name__ == "__main__":
    unittest.main()
