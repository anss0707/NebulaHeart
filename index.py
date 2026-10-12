#!/usr/bin/env python3
"""
Entrypoint wrapper for NEBULAHEART 3D (Space Gesture Controller).
Allows running via:
    python index.py
or:
    python nebula.py
"""
import sys
import os

# Ensure current directory is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nebula import NebulaApp

if __name__ == "__main__":
    app = NebulaApp()
    app.run()
