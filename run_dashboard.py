#!/usr/bin/env python3
"""Launch Streamlit with project root on PYTHONPATH (recommended entry point)."""

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

if __name__ == "__main__":
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    raise SystemExit(
        subprocess.call(
            [
                sys.executable,
                "-m",
                "streamlit",
                "run",
                str(ROOT / "dashboard" / "app.py"),
                "--server.maxUploadSize",
                "1024",
            ],
            cwd=ROOT,
            env=env,
        )
    )
