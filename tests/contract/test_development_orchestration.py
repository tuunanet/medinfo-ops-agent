# story: e01s01
import os
import signal
import subprocess
import tempfile
import time
import unittest
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DEVELOPMENT_SCRIPT = REPOSITORY_ROOT / "scripts/dev.sh"


class DevelopmentOrchestrationContractTests(unittest.TestCase):
    def test_host_failure_stops_workspace_and_propagates_status(self) -> None:
        self.assertTrue(DEVELOPMENT_SCRIPT.is_file())

        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_path = Path(temporary_directory)
            fake_bin = temporary_path / "bin"
            fake_bin.mkdir()
            command_log = temporary_path / "commands.log"
            web_started = temporary_path / "web-started"
            self._write_fake_tools(fake_bin)
            environment = os.environ | {
                "API_PORT": "18000",
                "COMMAND_LOG": str(command_log),
                "DATABASE_PORT": "55432",
                "MEDINFO_RUNTIME_DIR": str(temporary_path / "runtime"),
                "PATH": f"{fake_bin}:/usr/bin:/bin",
                "WEB_PORT": "13000",
                "WEB_STARTED": str(web_started),
            }

            result = subprocess.run(
                [DEVELOPMENT_SCRIPT],
                cwd=REPOSITORY_ROOT,
                env=environment,
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
            commands = command_log.read_text()

        self.assertEqual(result.returncode, 23, result.stderr)
        self.assertIn("Host process exited with status 23", result.stderr)
        self.assertIn("run --detach --replace", commands)
        self.assertIn(
            "uv run --locked uvicorn services.api.medinfo_api.main:app "
            "--host 127.0.0.1 --port 18000",
            commands,
        )
        self.assertIn(
            "npm run dev --workspace @medinfo/web -- --hostname 127.0.0.1 --port 13000",
            commands,
        )
        self.assertIn("npm terminated", commands)
        self.assertIn("stop --time 5 medinfo-ops-postgres", commands)

    def test_termination_stops_descendant_processes_and_database(self) -> None:
        self.assertTrue(DEVELOPMENT_SCRIPT.is_file())

        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_path = Path(temporary_directory)
            fake_bin = temporary_path / "bin"
            fake_bin.mkdir()
            api_started = temporary_path / "api-started"
            api_worker_pid = temporary_path / "api-worker.pid"
            command_log = temporary_path / "commands.log"
            web_started = temporary_path / "web-started"
            self._write_fake_tools(fake_bin)
            environment = os.environ | {
                "API_STARTED": str(api_started),
                "API_WORKER_PID": str(api_worker_pid),
                "COMMAND_LOG": str(command_log),
                "HOST_MODE": "wait",
                "MEDINFO_RUNTIME_DIR": str(temporary_path / "runtime"),
                "PATH": f"{fake_bin}:/usr/bin:/bin",
                "SIGNAL_SETUP_DELAY": "0.2",
                "WEB_STARTED": str(web_started),
            }
            stdout_path = temporary_path / "dev.stdout"
            stderr_path = temporary_path / "dev.stderr"
            with stdout_path.open("w") as stdout, stderr_path.open("w") as stderr:
                process = subprocess.Popen(
                    [DEVELOPMENT_SCRIPT],
                    cwd=REPOSITORY_ROOT,
                    env=environment,
                    stdout=stdout,
                    stderr=stderr,
                    text=True,
                )
                worker_pid: int | None = None
                worker_stopped = False
                try:
                    self._wait_for_files(api_started, api_worker_pid, web_started)
                    worker_pid = int(api_worker_pid.read_text())
                    process.terminate()
                    process.wait(timeout=5)
                    worker_stopped = self._wait_for_process_stop(worker_pid)
                finally:
                    if process.poll() is None:
                        process.kill()
                        process.wait(timeout=5)
                    if worker_pid is not None and not worker_stopped:
                        os.kill(worker_pid, signal.SIGKILL)
            commands = command_log.read_text()
            stderr_output = stderr_path.read_text()

        self.assertEqual(process.returncode, 143, stderr_output)
        self.assertTrue(worker_stopped, "API descendant process remained alive")
        self.assertIn("uv worker terminated", commands)
        self.assertIn("npm terminated", commands)
        self.assertIn("stop --time 5 medinfo-ops-postgres", commands)

    def _write_fake_tools(self, fake_bin: Path) -> None:
        self._write_executable(
            fake_bin / "uv",
            """if [[ "$*" == "run --locked python --version" ]]; then
  echo 'Python 3.14.6'
  exit 0
fi
echo "uv $*" >> "$COMMAND_LOG"
if [[ "${HOST_MODE:-fail}" == "wait" ]]; then
  trap 'echo "uv terminated" >> "$COMMAND_LOG"; exit 0' TERM INT
  (
    trap 'echo "uv worker terminated" >> "$COMMAND_LOG"; exit 0' TERM INT
    touch "$API_STARTED"
    sleep "${SIGNAL_SETUP_DELAY:-0}"
    while true; do sleep 0.1; done
  ) &
  echo "$!" > "$API_WORKER_PID"
  while true; do sleep 0.1; done
fi
for _ in $(seq 1 100); do
  [[ -f "$WEB_STARTED" ]] && exit 23
  sleep 0.01
done
exit 23
""",
        )
        self._write_executable(
            fake_bin / "node",
            """echo 'v24.18.1'
""",
        )
        self._write_executable(
            fake_bin / "npm",
            """if [[ "${1:-}" == "--version" ]]; then
  echo '11.16.0'
  exit 0
fi
echo "npm $*" >> "$COMMAND_LOG"
trap 'echo "npm terminated" >> "$COMMAND_LOG"; exit 0' TERM INT
touch "$WEB_STARTED"
sleep "${SIGNAL_SETUP_DELAY:-0}"
while true; do sleep 0.1; done
""",
        )
        self._write_executable(
            fake_bin / "podman",
            """echo "podman $*" >> "$COMMAND_LOG"
case "${1:-}" in
  version) echo '5.7.0' ;;
  info) echo 'true' ;;
  volume)
    if [[ "${2:-}" == "exists" ]]; then exit 1; fi
    ;;
  inspect) echo 'healthy' ;;
  exec) echo '0.8.6' ;;
  container) exit 0 ;;
esac
""",
        )

    def _write_executable(self, path: Path, body: str) -> None:
        path.write_text(f"#!/usr/bin/env bash\nset -euo pipefail\n{body}")
        path.chmod(0o755)

    def _wait_for_files(self, *paths: Path) -> None:
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            if all(path.is_file() for path in paths):
                return
            time.sleep(0.01)
        self.fail(f"Development processes did not start: {paths}")

    def _wait_for_process_stop(self, process_id: int) -> bool:
        deadline = time.monotonic() + 2
        while time.monotonic() < deadline:
            try:
                os.kill(process_id, 0)
            except ProcessLookupError:
                return True
            time.sleep(0.01)
        return False


if __name__ == "__main__":
    unittest.main()
