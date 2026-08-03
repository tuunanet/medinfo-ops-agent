# story: e01s01
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
LINT_SCRIPT = REPOSITORY_ROOT / "scripts/run-lint.sh"


class LintCommandContractTests(unittest.TestCase):
    def test_lint_checks_python_format_and_typescript(self) -> None:
        self.assertTrue(LINT_SCRIPT.is_file())

        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_path = Path(temporary_directory)
            fake_bin = temporary_path / "bin"
            fake_bin.mkdir()
            command_log = temporary_path / "commands.log"
            self._write_fake_tool(fake_bin / "uv")
            self._write_fake_tool(fake_bin / "npm")
            environment = os.environ | {
                "COMMAND_LOG": str(command_log),
                "PATH": f"{fake_bin}:/usr/bin:/bin",
            }

            result = subprocess.run(
                ["make", "lint"],
                cwd=REPOSITORY_ROOT,
                env=environment,
                capture_output=True,
                text=True,
                check=False,
            )
            commands = command_log.read_text()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("uv run --locked ruff check .", commands)
        self.assertIn("uv run --locked ruff format --check .", commands)
        self.assertIn("npm run lint", commands)

    def _write_fake_tool(self, path: Path) -> None:
        path.write_text(
            "#!/usr/bin/env bash\n"
            "set -euo pipefail\n"
            'echo "$(basename "$0") $*" >> "$COMMAND_LOG"\n'
        )
        path.chmod(0o755)


if __name__ == "__main__":
    unittest.main()
