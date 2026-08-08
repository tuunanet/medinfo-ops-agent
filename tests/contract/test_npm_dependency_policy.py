# story: e08s01
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
NPM_CONFIG = REPOSITORY_ROOT / ".npmrc"
SOURCE_POLICY_CHECK = REPOSITORY_ROOT / "scripts" / "check-npm-acquisition-policy.py"
VALID_SHA512_INTEGRITY = "sha512-" + ("A" * 86) + "=="
SOURCE_CASES = {
    "directory": ("file:../source", "directory"),
    "file": ("source.tgz", "file"),
    "git": ("git+https://example.invalid/source.git", "git"),
    "git_shorthand": ("unreviewed/source", "git"),
    "remote": ("https://example.invalid/source.tgz", "remote"),
}


class NpmDependencyPolicyContractTests(unittest.TestCase):
    def test_project_configuration_enforces_a_30_day_maturity_hold(self) -> None:
        configuration = self._read_project_configuration()

        self.assertEqual(configuration["min-release-age"], "30")

        result = subprocess.run(
            ["npm", "config", "get", "min-release-age", "--location=project"],
            cwd=REPOSITORY_ROOT,
            capture_output=True,
            check=False,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "30")

    def test_direct_workspace_dependencies_are_exact_and_locked(self) -> None:
        lockfile = json.loads((REPOSITORY_ROOT / "package-lock.json").read_text())
        root_manifest_path = REPOSITORY_ROOT / "package.json"
        root_manifest = json.loads(root_manifest_path.read_text())
        workspace_paths = tuple(
            workspace_path.relative_to(REPOSITORY_ROOT).as_posix()
            for pattern in root_manifest["workspaces"]
            for workspace_path in REPOSITORY_ROOT.glob(pattern)
            if (workspace_path / "package.json").is_file()
        )
        manifests = (("", root_manifest_path),) + tuple(
            (workspace_path, REPOSITORY_ROOT / workspace_path / "package.json")
            for workspace_path in workspace_paths
        )

        for workspace_path, manifest_path in manifests:
            with self.subTest(manifest_path=manifest_path):
                manifest = json.loads(manifest_path.read_text())
                locked_manifest = lockfile["packages"][workspace_path]

                for dependency_type in (
                    "dependencies",
                    "devDependencies",
                    "optionalDependencies",
                    "peerDependencies",
                ):
                    dependencies = manifest.get(dependency_type, {})
                    for package_name, specification in dependencies.items():
                        self.assertRegex(specification, r"^\d+\.\d+\.\d+$")
                        self.assertEqual(
                            locked_manifest[dependency_type][package_name],
                            specification,
                        )
                        self.assertEqual(
                            lockfile["packages"][f"node_modules/{package_name}"][
                                "version"
                            ],
                            specification,
                        )

    def test_acquisition_policy_denies_unreviewed_sources_and_preflight_checks_it(
        self,
    ) -> None:
        self._assert_acquisition_settings(self._read_project_configuration())
        self._assert_lockfile_sources_and_integrity()

        preflight = (REPOSITORY_ROOT / "scripts/run-preflight.sh").read_text()
        self.assertIn(
            "npm ci --ignore-scripts --dry-run --no-audit --no-fund --min-release-age=30 --allow-directory=none --allow-file=none --allow-git=none --allow-remote=none --strict-ssl=true --registry=https://registry.npmjs.org/",
            preflight,
        )

    def test_source_policy_cli_rejects_each_alternate_source(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            for source_type, (specification, expected_error) in SOURCE_CASES.items():
                with self.subTest(source_type=source_type):
                    result = self._run_source_policy(
                        self._write_source_fixture(
                            fixture_root / source_type,
                            specification,
                        ),
                    )
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(expected_error, result.stderr)

    def test_npm_rejects_directory_dependency_with_project_policy(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            source_directory = fixture_root / "source"
            source_directory.mkdir()
            (source_directory / "package.json").write_text(
                '{"name":"source-fixture","version":"1.0.0"}',
            )
            installation_root = fixture_root / "installation"
            installation_root.mkdir()
            (installation_root / ".npmrc").write_text(NPM_CONFIG.read_text())
            (installation_root / "package.json").write_text(
                '{"name":"installation-fixture","version":"1.0.0",'
                '"dependencies":{"source-fixture":"file:../source"}}',
            )

            result = subprocess.run(
                [
                    "npm",
                    "install",
                    "--ignore-scripts",
                    "--package-lock=false",
                    "--no-audit",
                    "--no-fund",
                ],
                cwd=installation_root,
                capture_output=True,
                check=False,
                text=True,
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("EALLOWDIRECTORY", result.stderr)

    def test_source_policy_cli_allows_the_declared_workspace_link(self) -> None:
        result = subprocess.run(
            [sys.executable, SOURCE_POLICY_CHECK],
            cwd=REPOSITORY_ROOT,
            capture_output=True,
            check=False,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)

    def _assert_acquisition_settings(self, configuration: dict[str, str]) -> None:
        expected_settings = {
            "allow-directory": "none",
            "allow-file": "none",
            "allow-git": "none",
            "allow-remote": "none",
            "engine-strict": "true",
            "ignore-scripts": "true",
            "package-lock": "true",
            "registry": "https://registry.npmjs.org/",
            "save-exact": "true",
            "strict-peer-deps": "true",
            "strict-ssl": "true",
        }
        self.assertEqual(
            {key: configuration[key] for key in expected_settings},
            expected_settings,
        )
        self.assertFalse(
            any(key.rstrip("[]") == "min-release-age-exclude" for key in configuration),
        )

    def _assert_lockfile_sources_and_integrity(self) -> None:
        lockfile = json.loads((REPOSITORY_ROOT / "package-lock.json").read_text())
        for package_path, package in lockfile["packages"].items():
            if not package_path or package_path == "apps/web" or package.get("link"):
                continue
            with self.subTest(package_path=package_path):
                self.assertTrue(
                    package["resolved"].startswith("https://registry.npmjs.org/"),
                )
                self.assertTrue(package["integrity"].startswith("sha512-"))

    def _run_source_policy(
        self, fixture_root: Path
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, SOURCE_POLICY_CHECK, "--root", fixture_root],
            capture_output=True,
            check=False,
            text=True,
        )

    def _write_source_fixture(
        self,
        fixture_root: Path,
        specification: str,
    ) -> Path:
        fixture_root.mkdir()
        manifest = {
            "name": "policy-fixture",
            "version": "1.0.0",
            "dependencies": {"source-fixture": specification},
        }
        lockfile = {
            "name": "policy-fixture",
            "lockfileVersion": 3,
            "packages": {
                "": manifest,
                "node_modules/source-fixture": {
                    "version": "1.0.0",
                    "resolved": "https://registry.npmjs.org/source-fixture/-/source-fixture-1.0.0.tgz",
                    "integrity": VALID_SHA512_INTEGRITY,
                },
            },
        }
        (fixture_root / ".npmrc").write_text(NPM_CONFIG.read_text())
        (fixture_root / "package.json").write_text(json.dumps(manifest))
        (fixture_root / "package-lock.json").write_text(json.dumps(lockfile))
        return fixture_root

    def _read_project_configuration(self) -> dict[str, str]:
        lines = NPM_CONFIG.read_text().splitlines()
        settings = (line for line in lines if "=" in line)
        return dict(setting.split("=", maxsplit=1) for setting in settings)


if __name__ == "__main__":
    unittest.main()
