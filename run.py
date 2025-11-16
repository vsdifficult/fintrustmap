#!/usr/bin/env python
"""
FinTrustMap launcher. Run from project root.

Usage:
  python run.py              # Launch GUI
  python run.py --cli --file data.xlsx --method pca --export out.xlsx
"""
import sys
import argparse

# Now we can safely import src as a package
from src.ui import run_gui, run_cli


def main(argv=None):
    parser = argparse.ArgumentParser(prog='fintrustmap', description='FinTrustMap launcher')
    parser.add_argument('--cli', action='store_true', help='Run in CLI mode (non-GUI)')
    parser.add_argument('--file', '-f', help='Excel file for CLI mode')
    parser.add_argument('--method', '-m', default='min_max_normalized', help='Calculation method for CLI')
    parser.add_argument('--export', '-e', help='Export path for CLI results')
    args = parser.parse_args(argv)

    if args.cli:
        cli_argv = []
        if args.file:
            cli_argv += ['--file', args.file]
        if args.method:
            cli_argv += ['--method', args.method]
        if args.export:
            cli_argv += ['--export', args.export]
        return run_cli(cli_argv)
    else:
        run_gui()
        return 0


if __name__ == '__main__':
    sys.exit(main())
