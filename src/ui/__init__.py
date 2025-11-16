"""
UI package for FinTrustMap

Provides a simple CLI wrapper and a GUI launcher.
"""
from .cli import run_cli
from .gui import run_gui

__all__ = ["run_cli", "run_gui"]
