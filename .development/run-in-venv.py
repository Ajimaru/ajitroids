#!/usr/bin/env python3
"""Run a local hook with the project interpreter without requiring activation."""

import os
import sys
from pathlib import Path


if __name__ == "__main__":
    venv = Path(__file__).resolve().parent.parent / ".venv"
    interpreter = venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if not interpreter.is_file():
        sys.exit("Missing project interpreter. Create .venv and install development dependencies first.")
    os.execv(str(interpreter), [str(interpreter), *sys.argv[1:]])
