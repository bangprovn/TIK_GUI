#!/usr/bin/env python
"""
TIK5 GUI Entry Point.

Launch the graphical interface for TIK5 Android ROM Tool.
Usage: python gui_main.py
"""
import os
import sys

# Ensure we're running from the TIK root directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)

# Set environment before importing anything that uses Rich or run.py
os.environ["TERM"] = "dumb"
os.environ["NO_COLOR"] = "1"
os.environ["TIK_GUI_MODE"] = "1"


def main():
    try:
        import customtkinter
    except ImportError:
        print("ERROR: customtkinter is not installed.")
        print("Install it with: pip install customtkinter")
        sys.exit(1)

    from gui.app import TIKApp

    app = TIKApp()
    app.start()


if __name__ == "__main__":
    main()
