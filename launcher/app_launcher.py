from __future__ import annotations

import argparse
import json
import os
import shutil
import signal
import sqlite3
import subprocess
import sys
import time
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path


APP_NAME = "Dasha Astro"
FRONTEND_URL = "http://localhost:3000"
BACKEND_URL = "http://127.0.0.1:8000"


def project_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[1]


ROOT = project_root()
BACKEND_DIR = ROOT / "backend"
FRONTEND_DIR = ROOT / "frontend"
DATA_DIR = ROOT / "data"
LOG_DIR = ROOT / "logs"
BACKEND_ENV = BACKEND_DIR / ".env"


def log(message: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {message}", flush=True)


def http_get(url: str, timeout: int = 3) -> tuple[int | None, str]:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return response.status, response.read().decode("utf-8", errors="replace")
    except Exception as exc:
        return None, str(exc)


def http_post_json(url: str, payload: dict, timeout: int = 60) -> tuple[int | None, str]:
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", errors="replace")
    except Exception as exc:
        return None, str(exc)


def wait_for(url: str, seconds: int, label: str) -> bool:
    deadline = time.time() + seconds
    while time.time() < deadline:
        status, _ = http_get(url)
        if status and 200 <= status < 500:
            return True
        time.sleep(1)
    log(f"{label} did not become ready within {seconds}s.")
    return False


def read_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def upsert_env(path: Path, key: str, value: str) -> None:
    lines: list[str] = []
    found = False
    if path.exists():
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            if raw_line.startswith(f"{key}="):
                lines.append(f"{key}={value}")
                found = True
            else:
                lines.append(raw_line)
    if not found:
        lines.append(f"{key}={value}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def ensure_local_files() -> None:
    LOG_DIR.mkdir(exist_ok=True)
    DATA_DIR.mkdir(exist_ok=True)

    db_path = DATA_DIR / "vedic_astrology.db"
    sqlite3.connect(db_path).close()

    if not BACKEND_ENV.exists() and (BACKEND_DIR / ".env.example").exists():
        shutil.copyfile(BACKEND_DIR / ".env.example", BACKEND_ENV)

    for env_name in [".env", ".env.local"]:
        target = FRONTEND_DIR / env_name
        example = FRONTEND_DIR / ".env.local.example"
        if not target.exists() and example.exists():
            shutil.copyfile(example, target)


def start_process(
    command: list[str],
    cwd: Path,
    stdout_name: str,
    stderr_name: str,
) -> subprocess.Popen:
    stdout = open(LOG_DIR / stdout_name, "a", encoding="utf-8")
    stderr = open(LOG_DIR / stderr_name, "a", encoding="utf-8")
    creation_flags = 0
    if os.name == "nt":
        creation_flags = subprocess.CREATE_NEW_PROCESS_GROUP
    return subprocess.Popen(
        command,
        cwd=str(cwd),
        stdout=stdout,
        stderr=stderr,
        stdin=subprocess.DEVNULL,
        creationflags=creation_flags,
    )


def ensure_gemini_configured() -> bool:
    env = read_env(BACKEND_ENV)
    if env.get("GEMINI_API_KEY"):
        log(f"Gemini model: {env.get('GEMINI_MODEL', 'gemini-2.5-flash')}")
        return True
    log("GEMINI_API_KEY is not configured in backend/.env.")
    return False


def init_backend_db() -> None:
    python = BACKEND_DIR / ".venv" / "Scripts" / "python.exe"
    if not python.exists():
        log("Backend virtualenv is missing. Run backend setup from README first.")
        return
    subprocess.run(
        [str(python), "-m", "app.init_db"],
        cwd=str(BACKEND_DIR),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )


def ensure_backend(processes: list[subprocess.Popen]) -> None:
    status, _ = http_get(f"{BACKEND_URL}/health", timeout=3)
    if status == 200:
        log("FastAPI backend is already running.")
        return

    python = BACKEND_DIR / ".venv" / "Scripts" / "python.exe"
    if not python.exists():
        raise FileNotFoundError(f"Missing backend Python venv: {python}")

    log("Starting FastAPI backend...")
    processes.append(
        start_process(
            [str(python), "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
            BACKEND_DIR,
            "backend.out.log",
            "backend.err.log",
        )
    )
    wait_for(f"{BACKEND_URL}/health", 20, "FastAPI backend")


def ensure_frontend(processes: list[subprocess.Popen]) -> None:
    status, _ = http_get(FRONTEND_URL, timeout=3)
    if status == 200:
        log("Next.js frontend is already running.")
        return

    npm = shutil.which("npm.cmd") or shutil.which("npm")
    if not npm:
        raise FileNotFoundError("npm was not found on PATH.")

    if not (FRONTEND_DIR / "node_modules").exists():
        log("Installing frontend dependencies. This can take a minute...")
        subprocess.run([npm, "install"], cwd=str(FRONTEND_DIR), check=False)

    log("Starting Next.js frontend...")
    processes.append(start_process([npm, "run", "dev"], FRONTEND_DIR, "frontend.out.log", "frontend.err.log"))
    wait_for(FRONTEND_URL, 40, "Next.js frontend")


def status_report() -> int:
    ensure_local_files()
    gemini_ok = bool(read_env(BACKEND_ENV).get("GEMINI_API_KEY"))
    backend_ok = http_get(f"{BACKEND_URL}/health", timeout=3)[0] == 200
    frontend_ok = http_get(FRONTEND_URL, timeout=3)[0] == 200
    model = read_env(BACKEND_ENV).get("GEMINI_MODEL", "gemini-2.5-flash")

    log(f"Gemini:  {'CONFIGURED' if gemini_ok else 'MISSING API KEY'}")
    log(f"Backend: {'OK' if backend_ok else 'NOT RUNNING'}")
    log(f"Frontend: {'OK' if frontend_ok else 'NOT RUNNING'}")
    log(f"Model:   {model}")
    return 0 if gemini_ok and backend_ok and frontend_ok else 1


def stop_children(processes: list[subprocess.Popen]) -> None:
    for process in reversed(processes):
        if process.poll() is not None:
            continue
        try:
            if os.name == "nt":
                process.send_signal(signal.CTRL_BREAK_EVENT)
                time.sleep(1)
            process.terminate()
        except Exception:
            pass


def main() -> int:
    parser = argparse.ArgumentParser(description=f"{APP_NAME} launcher")
    parser.add_argument("--status", action="store_true", help="Print service status and exit.")
    parser.add_argument("--check-llm", action="store_true", help="Check Gemini API key configuration, then exit.")
    args = parser.parse_args()

    if args.status:
        return status_report()

    ensure_local_files()
    processes: list[subprocess.Popen] = []

    try:
        log(f"Starting {APP_NAME} from {ROOT}")
        gemini_ready = ensure_gemini_configured()

        if args.check_llm:
            return 0 if gemini_ready else 1

        init_backend_db()
        ensure_backend(processes)
        ensure_frontend(processes)

        log(f"Opening {FRONTEND_URL}")
        webbrowser.open(FRONTEND_URL)
        log("App is running. Keep this window open. Press Ctrl+C to stop processes started by this launcher.")

        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        log("Stopping...")
    except Exception as exc:
        log(f"Startup failed: {exc}")
        log("Check the logs folder for details.")
        return 1
    finally:
        stop_children(processes)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
