"""Path/bootstrap helpers. Importing this module makes ``src`` importable.

Layout:
    D:\\研究项目\\LLMWorld\\dashboard\\backend\\paths.py   <- this file
    D:\\研究项目\\LLMWorld\\dashboard\\                    <- DASHBOARD_DIR
    D:\\研究项目\\LLMWorld\\                               <- LLMWORLD_ROOT
    D:\\研究项目\\LLMWorld\\src\\                           <- SRC_DIR  (put on sys.path)
    D:\\研究项目\\LLMWorld\\output\\                        <- OUTPUT_DIR
"""

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
DASHBOARD_DIR = os.path.dirname(_HERE)
LLMWORLD_ROOT = os.path.dirname(DASHBOARD_DIR)
SRC_DIR = os.path.join(LLMWORLD_ROOT, "src")
OUTPUT_DIR = os.path.join(LLMWORLD_ROOT, "output")
SIMULATION_DIR = os.path.join(OUTPUT_DIR, "simulation")
WORLDS_DIR = os.path.join(OUTPUT_DIR, "worlds")
WEB_DIR = os.path.join(DASHBOARD_DIR, "web")
WEB_DIST = os.path.join(WEB_DIR, "dist")
JOBS_DIR = os.path.join(DASHBOARD_DIR, "jobs")
VENV_PYTHON = os.path.join(LLMWORLD_ROOT, ".venv", "Scripts", "python.exe")

# run.py itself does this; importing analyze.* requires the same.
for _p in (SRC_DIR, LLMWORLD_ROOT):
    if _p not in sys.path:
        sys.path.insert(0, _p)
