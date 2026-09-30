"""
===========================================================================
 Assiut Smart Traffic Dashboard — Entry Point
===========================================================================

   python dashboard/main.py
   python dashboard/main.py --mode fixed      # run Fixed-Time baseline
   python dashboard/main.py --no-gui          # headless SUMO
   python dashboard/main.py --seed 42


===========================================================================
"""

import sys
import os
import argparse

# ── Put app/ and simulation/ on the path so every module resolves ──
_APP_DIR   = os.path.dirname(os.path.abspath(__file__))      # app/
_REPO_ROOT = os.path.dirname(_APP_DIR)                       # repository root/
for _p in (_APP_DIR, os.path.join(_REPO_ROOT, "simulation")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore    import Qt
from PyQt5.QtGui     import QFont

from window import MainWindow
from worker import SimWorker


def parse_args():
    p = argparse.ArgumentParser(description="Assiut Smart Traffic Dashboard")
    p.add_argument("--mode",   choices=["mappo", "fixed"], default="mappo",
                   help="Start in MAPPO or Fixed-Time mode (default: mappo)")
    p.add_argument("--seed",   type=int, default=42,
                   help="Random seed — must match both MAPPO and Fixed-Time")
    p.add_argument("--steps",  type=int, default=None,
                   help="Override total_steps (default: from MAPPOConfig)")
    p.add_argument("--no-gui", action="store_true",
                   help="Run SUMO headless (no sumo-gui.exe)")
    return p.parse_args()


def main():
    args = parse_args()

    # ── Qt application ──────────────────────────────────────────────
    # High-DPI support
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps,    True)

    app = QApplication(sys.argv)
    app.setApplicationName("Assiut Smart Traffic Control")
    app.setOrganizationName("Sphinx University — AI Lab")

    # Global font
    font = QFont("Segoe UI", 9)
    app.setFont(font)

    # ── Worker (simulation thread) ───────────────────────────────────
    worker = SimWorker(
        mode     = args.mode,
        seed     = args.seed,
        steps    = args.steps,
        use_gui  = not args.no_gui,
    )

    # ── Main window ──────────────────────────────────────────────────
    window = MainWindow(worker)
    window.setWindowTitle("Assiut Smart Traffic — MAPPO-CTDE Dashboard")
    window.resize(1600, 900)
    window.show()

    # ── Start simulation in background ───────────────────────────────
    worker.start()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
