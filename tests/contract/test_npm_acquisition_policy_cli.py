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
OFFICIAL_REGISTRY = (
    "https://registry.npmjs.org/source-fixture/-/source-fixture-1.0.0.tgz"
)
VALID_SHA512_INTEGRITY = "sha512-" + ("A" * 86) + "=="


class NpmAcquisitionPolicyCliContractTests(unittest.TestCase):
    def test_cli_validates_manifest_and_lockfile_without_an_npmrc_parser(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = self._write_fixture(Path(temporary_directory) / "no-npmrc")
            (root / ".npmrc").unlink()
            result = subprocess.run(
                [sys.executable, SOURCE_POLICY_CHECK, "--root", root],
                capture_output=True,
                check=False,
                text=True,
            )

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_cli_rejects_legacy_and_non_object_lock_records(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            legacy_lock = {
                "lockfileVersion": 1,
                "dependencies": {"source-fixture": {"version": "1.0.0"}},
            }
            self._assert_rejected(
                self._write_fixture(fixture_root / "legacy", lockfile=legacy_lock),
                "lockfileVersion 3",
            )

            malformed_lock = {"lockfileVersion": 3, "packages": {"node_modules/x": []}}
            self._assert_rejected(
                self._write_fixture(
                    fixture_root / "malformed", lockfile=malformed_lock
                ),
                "package record",
            )

    def test_cli_rejects_override_and_alternate_source_spellings(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            override_manifest = self._manifest()
            override_manifest["overrides"] = {
                "source-fixture": {"nested": "git+https://example.invalid/source.git"},
            }
            self._assert_rejected(
                self._write_fixture(fixture_root / "override", override_manifest),
                "git",
            )

            for name, specification, expected_error in (
                ("http-colon", "http:attacker.invalid/source", "remote"),
                ("dot-directory", ".", "directory"),
                ("backslash-directory", r"..\source", "directory"),
                ("gist", "gist:123456", "git"),
                ("windows-directory", r"C:\source", "directory"),
                ("windows-drive-relative", r"C:source", "directory"),
                ("scp-git", "deploy@example.invalid:repo.git", "git"),
                ("scp-git-default-user", "example.invalid:repo.git", "git"),
            ):
                with self.subTest(name=name):
                    manifest = self._manifest(specification)
                    self._assert_rejected(
                        self._write_fixture(fixture_root / name, manifest),
                        expected_error,
                    )

    def test_cli_rejects_malformed_dependency_and_override_shapes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            malformed_cases = (
                (
                    "dependency-field",
                    {"optionalDependencies": []},
                    "optionalDependencies",
                ),
                (
                    "dependency-null",
                    {"optionalDependencies": None},
                    "optionalDependencies",
                ),
                (
                    "dependency-specification",
                    {"dependencies": {"source-fixture": 1}},
                    "source-fixture",
                ),
                ("override-list", {"overrides": {"source-fixture": []}}, "overrides"),
                ("override-number", {"overrides": {"source-fixture": 1}}, "overrides"),
            )
            for name, malformed_value, expected_error in malformed_cases:
                with self.subTest(name=name):
                    manifest = self._manifest()
                    manifest.update(malformed_value)
                    self._assert_rejected(
                        self._write_fixture(fixture_root / name, manifest),
                        expected_error,
                    )

    def test_cli_rejects_forged_workspace_links(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            manifest = self._manifest()
            manifest["workspaces"] = ["apps/*"]
            lockfile = {
                "lockfileVersion": 3,
                "packages": {
                    "": manifest,
                    "apps/web": {"name": "@reviewed/web", "version": "1.0.0"},
                    "node_modules/@forged/web": {"resolved": "apps/web", "link": True},
                },
            }
            root = self._write_fixture(fixture_root / "forged-link", manifest, lockfile)
            workspace_manifest = root / "apps" / "web" / "package.json"
            workspace_manifest.parent.mkdir(parents=True)
            workspace_manifest.write_text('{"name":"@reviewed/web","version":"1.0.0"}')

            self._assert_rejected(root, "unreviewed workspace link")

    def test_cli_requires_exact_declared_workspace_links(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            for name, workspace_record, workspace_target in (
                ("missing-link", None, {"name": "@reviewed/web", "version": "1.0.0"}),
                (
                    "non-link",
                    {
                        "version": "1.0.0",
                        "resolved": OFFICIAL_REGISTRY,
                        "integrity": VALID_SHA512_INTEGRITY,
                    },
                    {"name": "@reviewed/web", "version": "1.0.0"},
                ),
                (
                    "forged-workspace-target-link",
                    {
                        "resolved": "apps/web",
                        "link": True,
                    },
                    {"link": True, "resolved": "../unreviewed"},
                ),
            ):
                with self.subTest(name=name):
                    manifest = self._manifest()
                    manifest["workspaces"] = ["apps/*"]
                    packages = {
                        "": manifest,
                        "apps/web": workspace_target,
                    }
                    if workspace_record is not None:
                        packages["node_modules/@reviewed/web"] = workspace_record
                    root = self._write_fixture(
                        fixture_root / name,
                        manifest,
                        {"lockfileVersion": 3, "packages": packages},
                    )
                    workspace_manifest = root / "apps" / "web" / "package.json"
                    workspace_manifest.parent.mkdir(parents=True)
                    workspace_manifest.write_text(
                        '{"name":"@reviewed/web","version":"1.0.0"}'
                    )
                    self._assert_rejected(root, "exact workspace link")

    def test_cli_allows_exact_declared_workspace_links(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            manifest = self._manifest()
            manifest["workspaces"] = ["apps/*"]
            lockfile = {
                "lockfileVersion": 3,
                "packages": {
                    "": manifest,
                    "apps/web": {"name": "@reviewed/web", "version": "1.0.0"},
                    "node_modules/@reviewed/web": {
                        "resolved": "apps/web",
                        "link": True,
                    },
                },
            }
            root = self._write_fixture(
                fixture_root / "declared-link", manifest, lockfile
            )
            workspace_manifest = root / "apps" / "web" / "package.json"
            workspace_manifest.parent.mkdir(parents=True)
            workspace_manifest.write_text('{"name":"@reviewed/web","version":"1.0.0"}')
            result = subprocess.run(
                [sys.executable, SOURCE_POLICY_CHECK, "--root", root],
                capture_output=True,
                check=False,
                text=True,
            )

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_cli_rejects_malformed_integrity_and_link_values(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            for name, integrity in (
                ("empty-integrity", "sha512-"),
                ("malformed-integrity", "sha512-not-base64!"),
                ("wrong-length-integrity", "sha512-AA=="),
            ):
                with self.subTest(name=name):
                    lockfile = self._lockfile()
                    lockfile["packages"]["node_modules/source-fixture"]["integrity"] = (
                        integrity
                    )
                    self._assert_rejected(
                        self._write_fixture(fixture_root / name, lockfile=lockfile),
                        "SHA-512",
                    )

            manifest = self._manifest()
            manifest["workspaces"] = ["apps/*"]
            lockfile = {
                "lockfileVersion": 3,
                "packages": {
                    "": manifest,
                    "apps/web": {"name": "@reviewed/web", "version": "1.0.0"},
                    "node_modules/@reviewed/web": {
                        "resolved": "apps/web",
                        "link": "true",
                    },
                },
            }
            root = self._write_fixture(fixture_root / "string-link", manifest, lockfile)
            workspace_manifest = root / "apps" / "web" / "package.json"
            workspace_manifest.parent.mkdir(parents=True)
            workspace_manifest.write_text('{"name":"@reviewed/web","version":"1.0.0"}')
            self._assert_rejected(root, "npm-registry resolution")

            lockfile = self._lockfile()
            lockfile["packages"]["node_modules/source-fixture"]["link"] = None
            self._assert_rejected(
                self._write_fixture(fixture_root / "null-link", lockfile=lockfile),
                "link value",
            )

    def test_cli_rejects_npm_shrinkwrap(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            root = self._write_fixture(fixture_root / "root-shrinkwrap")
            (root / "npm-shrinkwrap.json").write_text(
                '{"lockfileVersion":3,"packages":{}}'
            )
            self._assert_rejected(root, "npm-shrinkwrap.json")

            manifest = self._manifest()
            manifest["workspaces"] = ["apps/*"]
            root = self._write_fixture(fixture_root / "workspace-shrinkwrap", manifest)
            workspace_root = root / "apps" / "web"
            workspace_root.mkdir(parents=True)
            (workspace_root / "package.json").write_text(
                '{"name":"@reviewed/web","version":"1.0.0"}'
            )
            (workspace_root / "npm-shrinkwrap.json").write_text(
                '{"lockfileVersion":3,"packages":{}}'
            )
            self._assert_rejected(root, "apps/web/npm-shrinkwrap.json")

    def test_cli_rejects_non_registry_or_non_sha512_lock_entries(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture_root = Path(temporary_directory)
            for name, resolved, integrity, expected_error in (
                (
                    "non-registry",
                    "https://example.invalid/source.tgz",
                    VALID_SHA512_INTEGRITY,
                    "non-registry",
                ),
                ("non-sha512", OFFICIAL_REGISTRY, "sha1-fixture", "SHA-512"),
            ):
                with self.subTest(name=name):
                    lockfile = self._lockfile()
                    package = lockfile["packages"]["node_modules/source-fixture"]
                    package["resolved"] = resolved
                    package["integrity"] = integrity
                    self._assert_rejected(
                        self._write_fixture(fixture_root / name, lockfile=lockfile),
                        expected_error,
                    )

    def _assert_rejected(self, root: Path, expected_error: str) -> None:
        result = subprocess.run(
            [sys.executable, SOURCE_POLICY_CHECK, "--root", root],
            capture_output=True,
            check=False,
            text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(expected_error, result.stderr)

    def _manifest(self, specification: str = "1.0.0") -> dict[str, object]:
        return {
            "name": "policy-fixture",
            "version": "1.0.0",
            "dependencies": {"source-fixture": specification},
        }

    def _lockfile(self) -> dict[str, object]:
        return {
            "lockfileVersion": 3,
            "packages": {
                "": self._manifest(),
                "node_modules/source-fixture": {
                    "version": "1.0.0",
                    "resolved": OFFICIAL_REGISTRY,
                    "integrity": VALID_SHA512_INTEGRITY,
                },
            },
        }

    def _write_fixture(
        self,
        fixture_root: Path,
        manifest: dict[str, object] | None = None,
        lockfile: dict[str, object] | None = None,
        configuration_append: str = "",
    ) -> Path:
        fixture_root.mkdir()
        manifest = self._manifest() if manifest is None else manifest
        lockfile = self._lockfile() if lockfile is None else lockfile
        if "packages" in lockfile and isinstance(lockfile["packages"], dict):
            lockfile["packages"][""] = manifest
        (fixture_root / ".npmrc").write_text(
            NPM_CONFIG.read_text() + configuration_append
        )
        (fixture_root / "package.json").write_text(json.dumps(manifest))
        (fixture_root / "package-lock.json").write_text(json.dumps(lockfile))
        return fixture_root


if __name__ == "__main__":
    unittest.main()
