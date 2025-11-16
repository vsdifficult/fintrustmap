"""
GUI launcher convenience wrapper.

`app.py` already contains `FinTrustHeatmapApp`. This module provides a
callable `run_gui()` to launch the existing Tkinter application programmatically.
"""
import sys
from PyQt5.QtWidgets import QApplication

from .app import FinTrustHeatmapApp


def run_gui():
    """Launch the PyQt5 GUI application"""
    app = QApplication(sys.argv)
    window = FinTrustHeatmapApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    run_gui()
