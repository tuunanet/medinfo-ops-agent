# story: e01s01
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
PREFLIGHT_SCRIPT = REPOSITORY_ROOT / "scripts/run-preflight.sh"


class PreflightCommandContractTests(unittest.TestCase):
    def test_preflight_checks_runtime_locks_gates_and_blocks_paid_calls(self) -> None:
        self.assertTrue(PREFLIGHT_SCRIPT.is_file())

        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_path = Path(temporary_directory)
            fake_bin = temporary_path / "bin"
            fake_bin.mkdir()
            command_log = temporary_path / "commands.log"
            self._write_fake_tools(fake_bin)
            environment = os.environ | {
                "AZURE_OPENAI_API_KEY": "fictional-azure-key",
                "COMMAND_LOG": str(command_log),
                "MEDINFO_ALLOW_PAID_PROVIDER_CALLS": "true",
                "OPENAI_API_KEY": "fictional-openai-key",
                "PATH": f"{fake_bin}:/usr/bin:/bin",
            }

            result = subprocess.run(
                [PREFLIGHT_SCRIPT],
                cwd=REPOSITORY_ROOT,
                env=environment,
                capture_output=True,
                text=True,
                check=False,
            )
            commands = command_log.read_text().splitlines()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("uv lock --check", commands)
        self.assertIn(
            "uv run --locked python scripts/check-npm-acquisition-policy.py",
            commands,
        )
        self.assertIn(
            "npm ci --ignore-scripts --dry-run --no-audit --no-fund --min-release-age=30 --allow-directory=none --allow-file=none --allow-git=none --allow-remote=none --strict-ssl=true --registry=https://registry.npmjs.org/",
            commands,
        )
        self.assertLess(
            commands.index(
                "uv run --locked python scripts/check-npm-acquisition-policy.py"
            ),
            commands.index(
                "npm ci --ignore-scripts --dry-run --no-audit --no-fund --min-release-age=30 --allow-directory=none --allow-file=none --allow-git=none --allow-remote=none --strict-ssl=true --registry=https://registry.npmjs.org/",
            ),
        )
        self.assertLess(commands.index("make lint"), commands.index("make test"))
        self.assertLess(commands.index("make test"), commands.index("make build"))
        self.assertNotIn("provider access enabled", commands)

    def _write_fake_tools(self, fake_bin: Path) -> None:
        self._write_executable(
            fake_bin / "uv",
            """echo "uv $*" >> "$COMMAND_LOG"
if [[ "$*" == "run --locked python --version" ]]; then
  echo 'Python 3.14.6'
fi
""",
        )
        self._write_executable(
            fake_bin / "node",
            """echo "node $*" >> "$COMMAND_LOG"
echo 'v24.18.1'
""",
        )
        self._write_executable(
            fake_bin / "npm",
            """echo "npm $*" >> "$COMMAND_LOG"
if [[ "${1:-}" == "--version" ]]; then echo '11.16.0'; fi
""",
        )
        self._write_executable(
            fake_bin / "podman",
            """echo "podman $*" >> "$COMMAND_LOG"
if [[ "${1:-}" == "info" ]]; then echo 'true'; else echo '5.7.0'; fi
""",
        )
        self._write_executable(
            fake_bin / "make",
            """if [[ -v OPENAI_API_KEY || -v AZURE_OPENAI_API_KEY ||
      "${MEDINFO_ALLOW_PAID_PROVIDER_CALLS:-}" != "false" ]]; then
  echo 'provider access enabled' >> "$COMMAND_LOG"
  exit 41
fi
echo "make $*" >> "$COMMAND_LOG"
""",
        )

    def _write_executable(self, path: Path, body: str) -> None:
        path.write_text(f"#!/usr/bin/env bash\nset -euo pipefail\n{body}")
        path.chmod(0o755)


if __name__ == "__main__":
    unittest.main()
