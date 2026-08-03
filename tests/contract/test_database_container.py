# story: e01s01
import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path
from urllib.parse import urlsplit

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DATABASE_SCRIPT = REPOSITORY_ROOT / "scripts/database-container.sh"


class DatabaseContainerContractTests(unittest.TestCase):
    def test_start_and_stop_use_rootless_podman_and_preserve_data(self) -> None:
        self.assertTrue(DATABASE_SCRIPT.is_file())

        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_path = Path(temporary_directory)
            fake_bin = temporary_path / "bin"
            fake_bin.mkdir()
            command_log = temporary_path / "podman.log"
            self._write_fake_podman(fake_bin / "podman")
            environment = os.environ | {
                "DATABASE_PORT": "55432",
                "MEDINFO_RUNTIME_DIR": str(temporary_path / "runtime"),
                "PATH": f"{fake_bin}:/usr/bin:/bin",
                "PODMAN_LOG": str(command_log),
            }

            start = self._run("start", environment)
            stop = self._run("stop", environment)
            commands = command_log.read_text()
            runtime_modes = tuple(
                stat.S_IMODE(path.stat().st_mode)
                for path in (temporary_path / "runtime").iterdir()
            )

        self.assertEqual(start.returncode, 0, start.stderr)
        self.assertEqual(stop.returncode, 0, stop.stderr)
        self.assertIn("volume create medinfo-ops-postgres-data", commands)
        self.assertIn("run --detach --replace", commands)
        self.assertIn("127.0.0.1:55432:5432", commands)
        self.assertIn(
            "docker.io/pgvector/pgvector:0.8.6-pg18-trixie",
            commands,
        )
        self.assertIn("exec medinfo-ops-postgres", commands)
        self.assertIn("stop --time 5 medinfo-ops-postgres", commands)
        self.assertNotIn("volume rm", commands)
        self.assertNotIn("sudo", commands)
        self.assertNotIn("privileged", commands)
        self.assertNotIn("compose", commands)
        self.assertTrue(runtime_modes)
        for mode in runtime_modes:
            self.assertEqual(mode, 0o600)

    def test_failed_start_stops_created_container(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_path = Path(temporary_directory)
            fake_bin = temporary_path / "bin"
            fake_bin.mkdir()
            command_log = temporary_path / "podman.log"
            runtime_path = temporary_path / "invalid-runtime"
            self._write_runtime_config(runtime_path, "invalid", 55436)
            self._write_fake_podman(fake_bin / "podman")
            environment = os.environ | {
                "DATABASE_PORT": "55436",
                "MEDINFO_RUNTIME_DIR": str(runtime_path),
                "PATH": f"{fake_bin}:/usr/bin:/bin",
                "PODMAN_LOG": str(command_log),
            }

            start = self._run("start", environment)
            commands = command_log.read_text()

        self.assertEqual(start.returncode, 1)
        self.assertIn("Database container configuration is invalid", start.stderr)
        self.assertIn("run --detach --replace", commands)
        self.assertIn("stop --time 5 medinfo-ops-postgres", commands)

    def test_fresh_runtime_credentials_match_preserved_database(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_path = Path(temporary_directory)
            fake_bin = temporary_path / "bin"
            fake_bin.mkdir()
            command_log = temporary_path / "podman.log"
            database_password = temporary_path / "database-password"
            password_sequence = temporary_path / "password-sequence"
            self._write_fake_podman(fake_bin / "podman")
            self._write_fake_password_generator(fake_bin / "python3")
            base_environment = os.environ | {
                "PASSWORD_SEQUENCE": str(password_sequence),
                "PATH": f"{fake_bin}:/usr/bin:/bin",
                "PODMAN_DATABASE_PASSWORD": str(database_password),
                "PODMAN_LOG": str(command_log),
            }

            published_passwords = []
            for sequence, database_port in enumerate((55432, 55433), start=1):
                runtime_path = temporary_path / f"runtime-{sequence}"
                environment = base_environment | {
                    "DATABASE_PORT": str(database_port),
                    "MEDINFO_RUNTIME_DIR": str(runtime_path),
                }

                start = self._run("start", environment)
                self.assertEqual(start.returncode, 0, start.stderr)
                published_password = self._read_application_password(runtime_path)
                published_passwords.append(published_password)
                self.assertEqual(
                    database_password.read_text().strip(),
                    published_password,
                )

            commands = command_log.read_text()

        self.assertNotEqual(published_passwords[0], published_passwords[1])
        for password in published_passwords:
            self.assertNotIn(password, commands)

    def _run(
        self,
        command: str,
        environment: dict[str, str],
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [DATABASE_SCRIPT, command],
            cwd=REPOSITORY_ROOT,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )

    def _read_application_password(self, runtime_path: Path) -> str:
        config_line = (runtime_path / "application.env").read_text().strip()
        database_url = config_line.removeprefix("DATABASE_URL=")
        password = urlsplit(database_url).password
        self.assertIsNotNone(password)
        return password or ""

    def _write_runtime_config(
        self,
        runtime_path: Path,
        password: str,
        database_port: int,
    ) -> None:
        runtime_path.mkdir(mode=0o700)
        container_env = runtime_path / "postgres.env"
        application_env = runtime_path / "application.env"
        container_env.write_text(
            "POSTGRES_DB=medinfo\n"
            "POSTGRES_USER=medinfo\n"
            f"POSTGRES_PASSWORD={password}\n"
        )
        application_env.write_text(
            f"DATABASE_URL=postgresql://medinfo:{password}"
            f"@127.0.0.1:{database_port}/medinfo\n"
        )
        container_env.chmod(0o600)
        application_env.chmod(0o600)

    def _write_fake_password_generator(self, path: Path) -> None:
        path.write_text(
            """#!/usr/bin/env bash
set -euo pipefail
sequence=0
if [[ -f "$PASSWORD_SEQUENCE" ]]; then
  sequence=$(<"$PASSWORD_SEQUENCE")
fi
sequence=$((sequence + 1))
printf '%s' "$sequence" > "$PASSWORD_SEQUENCE"
if [[ "$sequence" -eq 1 ]]; then
  echo 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
else
  echo 'BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB'
fi
"""
        )
        path.chmod(0o755)

    def _write_fake_podman(self, path: Path) -> None:
        path.write_text(
            """#!/usr/bin/env bash
set -euo pipefail
echo "$*" >> "$PODMAN_LOG"
if [[ "$*" == "volume exists"* ]]; then exit 1; fi
if [[ "$1" == "run" && -n "${PODMAN_DATABASE_PASSWORD:-}" ]]; then
  previous=""
  for argument in "$@"; do
    if [[ "$previous" == "--env-file" && ! -f "$PODMAN_DATABASE_PASSWORD" ]]; then
      awk -F= '$1 == "POSTGRES_PASSWORD" {print substr($0, index($0, "=") + 1)}' \
        "$argument" > "$PODMAN_DATABASE_PASSWORD"
    fi
    previous="$argument"
  done
fi
if [[ "$1" == "inspect" ]]; then echo healthy; fi
if [[ "$1" == "exec" ]]; then
  if [[ " $* " == *" --interactive "* ]]; then
    sql=$(cat)
    if [[ -n "${PODMAN_DATABASE_PASSWORD:-}" && \
      "$sql" == *"ALTER ROLE medinfo PASSWORD '"* ]]; then
      printf '%s\n' "$sql" | \
        awk -F"'" '/ALTER ROLE medinfo PASSWORD/ {print $2}' \
        > "$PODMAN_DATABASE_PASSWORD"
    fi
  fi
  echo 0.8.6
fi
"""
        )
        path.chmod(0o755)


if __name__ == "__main__":
    unittest.main()
