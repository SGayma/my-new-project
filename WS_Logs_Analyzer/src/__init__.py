"""`src` package for Log Analyzer.

This is a small package shim so `from src.log_analyzer import main`
works when running `log_analyzer_main.py`. Replace `log_analyzer.py`
with the real application module from your source tree.
"""

__all__ = ["log_analyzer"]
