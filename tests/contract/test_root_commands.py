# story: e01s01
import json
import os
import re
import subprocess
import tempfile
import tomllib
import unittest
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
REQUIRED_MAKE_TARGETS = ("dev", "test", "build", "lint", "preflight")


class RootCommandContractTests(unittest.TestCase):
    def test_repository_declares_pinned_runtimes_and_root_commands(self) -> None:
        self.assertEqual(
            (REPOSITORY_ROOT / ".python-version").read_text().strip(),
            "3.14.6",
        )
        self.assertEqual(
            (REPOSITORY_ROOT / ".nvmrc").read_text().strip(),
            "24.18.1",
        )

        pyproject = tomllib.loads((REPOSITORY_ROOT / "pyproject.toml").read_text())
        self.assertEqual(pyproject["project"]["requires-python"], "==3.14.6")

        package = json.loads((REPOSITORY_ROOT / "package.json").read_text())
        self.assertEqual(package["engines"]["node"], "24.18.1")
        self.assertEqual(package["engines"]["npm"], "11.16.0")

        makefile = (REPOSITORY_ROOT / "Makefile").read_text()
        for target in REQUIRED_MAKE_TARGETS:
            self.assertRegex(makefile, rf"(?m)^{re.escape(target)}:")

        self.assertTrue((REPOSITORY_ROOT / "uv.lock").is_file())
        self.assertTrue((REPOSITORY_ROOT / "package-lock.json").is_file())

    def test_runtime_check_accepts_the_pinned_rootless_toolchain(self) -> None:
        result = self._run_runtime_check()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Runtime contract OK", result.stdout)

    def test_runtime_check_rejects_unsupported_versions_with_details(self) -> None:
        cases = (
            (
                {"python_version": "3.14.4"},
                "Python version mismatch: required 3.14.6, detected 3.14.4",
            ),
            (
                {"node_version": "26.4.0"},
                "Node.js version mismatch: required 24.18.1, detected 26.4.0",
            ),
            (
                {"npm_version": "11.17.0"},
                "npm version mismatch: required 11.16.0, detected 11.17.0",
            ),
            (
                {"podman_version": "5.6.2"},
                "Podman version mismatch: required at least 5.7.0, detected 5.6.2",
            ),
            (
                {"podman_rootless": "false"},
                "Podman must run rootless: detected false",
            ),
        )

        for overrides, expected_error in cases:
            with self.subTest(overrides=overrides):
                result = self._run_runtime_check(**overrides)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(expected_error, result.stderr)

    def _run_runtime_check(
        self,
        python_version: str = "3.14.6",
        node_version: str = "24.18.1",
        npm_version: str = "11.16.0",
        podman_version: str = "5.7.0",
        podman_rootless: str = "true",
    ) -> subprocess.CompletedProcess[str]:
        runtime_check = REPOSITORY_ROOT / "scripts/check-runtime-versions.sh"
        self.assertTrue(runtime_check.is_file())

        with tempfile.TemporaryDirectory() as temporary_directory:
            fake_bin = Path(temporary_directory)
            self._write_fake_tool(fake_bin / "uv", f"echo 'Python {python_version}'")
            self._write_fake_tool(fake_bin / "node", f"echo 'v{node_version}'")
            self._write_fake_tool(fake_bin / "npm", f"echo '{npm_version}'")
            self._write_fake_tool(
                fake_bin / "podman",
                'if [[ "$1" == info ]]; then '
                f"echo '{podman_rootless}'; else echo '{podman_version}'; fi",
            )
            environment = os.environ | {
                "PATH": f"{fake_bin}:/usr/bin:/bin",
            }
            return subprocess.run(
                [runtime_check],
                cwd=REPOSITORY_ROOT,
                env=environment,
                capture_output=True,
                text=True,
                check=False,
            )

    def _write_fake_tool(self, path: Path, behavior: str) -> None:
        path.write_text(f"#!/usr/bin/env bash\n{behavior}\n")
        path.chmod(0o755)


if __name__ == "__main__":
    unittest.main()
