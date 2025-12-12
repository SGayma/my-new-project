"""Entry point for the Log Analyzer executable."""
import sys
import os

# Ensure the script directory is in the path so we can import 'src'
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from src.log_analyzer import main

if __name__ == '__main__':
    main()
