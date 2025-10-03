#!/usr/bin/env python3
"""
Simple launcher script for the Summit - AI Learning Accelerator GUI.
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from retention.gui.main import main

if __name__ == "__main__":
    main()
    