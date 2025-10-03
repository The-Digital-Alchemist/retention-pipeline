from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
SPEC_FILE = PROJECT_ROOT / "retention_pipeline.spec"
BUILD_DIR = PROJECT_ROOT / "build"
DIST_DIR = PROJECT_ROOT / "dist"
EXE_PATH = DIST_DIR / "SummitAccelerator.exe"
LAUNCHER_PATH = DIST_DIR / "run_summit_ai_learning_accelerator.bat"


def _print(message: str) -> None:
    print(f"[build] {message}")


def ensure_pyinstaller() -> None:
    try:
        import PyInstaller  # type: ignore # noqa: F401
    except ImportError as exc:  # pragma: no cover
        raise SystemExit(
            "PyInstaller is not installed. Install it with 'pip install pyinstaller' and retry."
        ) from exc


def clean_previous_build() -> None:
    for target in (BUILD_DIR, DIST_DIR):
        if target.exists():
            _print(f"Removing {target.relative_to(PROJECT_ROOT)}/")
            shutil.rmtree(target)


def run_pyinstaller() -> None:
    if not SPEC_FILE.exists():
        raise SystemExit(f"Spec file not found: {SPEC_FILE}")

    cmd = [sys.executable, "-m", "PyInstaller", str(SPEC_FILE)]
    _print("Running PyInstaller")
    result = subprocess.run(cmd, cwd=PROJECT_ROOT, text=True)
    if result.returncode != 0:
        raise SystemExit("PyInstaller failed. Check the log above for details.")


def create_launcher() -> None:
    if not EXE_PATH.exists():
        _print("Executable not found; skipping launcher creation.")
        return

    content = (
        "@echo off\n"
        "echo Starting Summit - AI Learning Accelerator...\n"
        "cd /d \"%~dp0\"\n"
        "SummitAccelerator.exe\n"
    )
    LAUNCHER_PATH.write_text(content, encoding="ascii")
    _print(f"Launcher created: {LAUNCHER_PATH.relative_to(PROJECT_ROOT)}")


def main() -> None:
    _print("Preparing build environment")
    ensure_pyinstaller()
    clean_previous_build()
    run_pyinstaller()

    if EXE_PATH.exists():
        _print(f"Build succeeded: {EXE_PATH.relative_to(PROJECT_ROOT)}")
    else:
        _print("Build finished but the executable was not found.")

    create_launcher()
    _print("Done.")


if __name__ == "__main__":
    try:
        main()
    except SystemExit as exc:
        _print(str(exc))
        raise
