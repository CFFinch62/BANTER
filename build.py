"""
build.py — BANTER packaging helper
===================================
Cleans previous build artefacts, then calls PyInstaller to produce a
self-contained binary in dist/BANTER/.

The script adds the project venv's site-packages to sys.path BEFORE
invoking PyInstaller so that dependencies are found even when the
system Python (rather than the activated venv) runs this file.

Note: this bundles the IDE only. The end user still needs a Smalltalk
interpreter installed and the toolbar's Command field pointed at it.

Usage:
    python3 build.py          # with or without venv activated
"""

import os
import pathlib
import platform
import shutil
import sys

APP_NAME    = "BANTER"
ENTRY_POINT = "main.py"
SCRIPT_DIR  = pathlib.Path(__file__).parent.resolve()


# ──────────────────────────────────────────────────────────────────────
# 1. Ensure the venv site-packages are on sys.path so PyInstaller can
#    find all project dependencies regardless of how this script was run.
# ──────────────────────────────────────────────────────────────────────

def _inject_venv_paths() -> None:
    venv_dir = SCRIPT_DIR / "venv"
    if not venv_dir.exists():
        return
    py_ver = f"python{sys.version_info.major}.{sys.version_info.minor}"
    site_pkgs = venv_dir / "lib" / py_ver / "site-packages"
    if site_pkgs.exists() and str(site_pkgs) not in sys.path:
        sys.path.insert(0, str(site_pkgs))
        print(f"[build] Added venv site-packages to path: {site_pkgs}")

_inject_venv_paths()


# ──────────────────────────────────────────────────────────────────────
# 2. Now import PyInstaller (may come from venv after the path injection)
# ──────────────────────────────────────────────────────────────────────

import PyInstaller.__main__  # noqa: E402  (must be after path injection)


# ──────────────────────────────────────────────────────────────────────
# 3. Helpers
# ──────────────────────────────────────────────────────────────────────

def clean_build_dirs() -> None:
    print("Cleaning build directories...")
    for d in ["build", "dist"]:
        if os.path.exists(d):
            shutil.rmtree(d)


def get_args() -> list[str]:
    system = platform.system()
    sep    = ";" if system == "Windows" else ":"  # PyInstaller --add-data separator

    args = [
        "--name",    APP_NAME,
        "--clean",
        "--noconfirm",
        "--windowed",
        "--hidden-import", "PyQt6",
        "--icon", "banter_icon.png",
        "--add-data", f"banter_icon.svg{sep}.",
        "--add-data", f"banter_banner.svg{sep}.",
        "--add-data", f"themes{sep}themes",
        "--add-data", f"docs{sep}docs",
    ]

    if system == "Darwin":
        args += ["--target-architecture", "universal2"]

    args.append(ENTRY_POINT)
    return args


# ──────────────────────────────────────────────────────────────────────
# 4. Build
# ──────────────────────────────────────────────────────────────────────

def build() -> None:
    clean_build_dirs()

    args = get_args()

    print(f"Building {APP_NAME} for {platform.system()} …")
    print()

    try:
        PyInstaller.__main__.run(args)
        print()
        print(f"Build complete!  →  dist/{APP_NAME}/")
    except Exception as exc:
        print(f"Build failed: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    build()
