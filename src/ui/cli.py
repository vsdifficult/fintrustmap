"""
Command-line interface for FinTrustMap.

Usage examples:
  python run.py --cli --file data.xlsx --method pca
  python run.py --cli --file data.xlsx --method min_max_normalized --export out.xlsx
"""
import argparse
import sys
from pathlib import Path
import pandas as pd

from src.core.data_loader import DataLoader, DataLoadError
from src.core.calculator import IndexCalculator, CalculationError


def print_stats(calc: IndexCalculator, df: pd.DataFrame):
    stats = calc.get_statistics(df)
    if not stats:
        print("No 'Индекс' column found in result.")
        return
    print("Index statistics:")
    for k, v in stats.items():
        print(f"  {k}: {v:.3f}")


def run_cli(argv=None):
    parser = argparse.ArgumentParser(description="FinTrustMap CLI")
    parser.add_argument("--file", "-f", required=True, help="Path to Excel file with data")
    parser.add_argument("--method", "-m", default="min_max_normalized", help="Calculation method")
    parser.add_argument("--export", "-e", help="Optional export path (.xlsx)")
    parser.add_argument("--top", "-t", type=int, default=10, help="Show top N regions")

    args = parser.parse_args(argv)

    file_path = Path(args.file)
    if not file_path.exists():
        print(f"File not found: {file_path}")
        return 2

    loader = DataLoader()
    try:
        df = loader.load_excel(str(file_path))
    except DataLoadError as e:
        print(f"Error loading data: {e}")
        return 3

    calc = IndexCalculator(df)
    try:
        result = calc.calculate_index(method=args.method)
    except CalculationError as e:
        print(f"Calculation error: {e}")
        return 4

    # Print basic info
    print(f"Loaded: {file_path.name} | regions: {len(result)} | method: {args.method}")
    print_stats(calc, result)

    # Show top N
    if 'Индекс' in result.columns:
        out = result.sort_values('Индекс', ascending=False).reset_index(drop=True)
        out.index = out.index + 1
        print(f"\nTop {args.top} regions by Индекс:")
        print(out[['Регион', 'Индекс']].head(args.top).to_string(index=True))

    # Export if requested
    if args.export:
        try:
            p = Path(args.export)
            if p.suffix == '':
                p = p.with_suffix('.xlsx')
            out.to_excel(p)
            print(f"Exported results to {p}")
        except Exception as e:
            print(f"Failed to export: {e}")
            return 5

    return 0


if __name__ == '__main__':
    raise SystemExit(run_cli())
