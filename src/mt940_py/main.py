import sys
import io

# Fix for libraries that expect sys.stdout/stderr to be present (like mt-940)
# especially when compiled with --noconsole
if sys.stdout is None:
    sys.stdout = io.StringIO()
if sys.stderr is None:
    sys.stderr = io.StringIO()

import argparse
import os
from mt940_py.validator import MT940Validator
from mt940_py.converter import MT940Converter
from mt940_py.exporter import MT940ToCSVExporter

def main():
    parser = argparse.ArgumentParser(description="Narzędzie MT940: CLI & GUI.")
    subparsers = parser.add_subparsers(dest="command", help="Komenda do wykonania")

    # CLI commands
    subparsers.add_parser("validate", help="Waliduje plik MT940").add_argument("file")
    
    conv_parser = subparsers.add_parser("convert", help="Konwertuje CSV to MT940")
    conv_parser.add_argument("input")
    conv_parser.add_argument("output")

    exp_parser = subparsers.add_parser("export", help="Eksportuje MT940 to CSV")
    exp_parser.add_argument("input")
    exp_parser.add_argument("output")

    # GUI command
    subparsers.add_parser("gui", help="Uruchamia interfejs graficzny")

    args = parser.parse_args()

    if args.command == "gui":
        from mt940_py.gui import main as run_gui
        run_gui()
    elif args.command == "validate":
        validator = MT940Validator()
        results = validator.validate_file(args.file)
        if results["is_valid"]:
            print(f"SUCCESS: {results['statements_count']} wyciągów, {results['transactions_count']} transakcji.")
        else:
            print("FAILURE: Błędy:")
            for err in results["errors"]: print(f" - {err}")
            sys.exit(1)
    elif args.command == "convert":
        try:
            with open(args.input, 'r', encoding='cp1250', errors='replace') as f:
                mt940_res = MT940Converter().convert(f.read())
            # Zapisujemy jako UTF-8 z BOM (utf-8-sig)
            with open(args.output, 'w', encoding='utf-8-sig') as f:
                f.write(mt940_res)
            print(f"SUCCESS: {args.output}")
        except Exception as e:
            print(f"ERROR: {e}")
            sys.exit(1)
    elif args.command == "export":
        try:
            csv_res = MT940ToCSVExporter().export(args.input)
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(csv_res)
            print(f"SUCCESS: {args.output}")
        except Exception as e:
            print(f"ERROR: {e}")
            sys.exit(1)
    else:
        # Default to GUI if no command
        from mt940_py.gui import main as run_gui
        run_gui()

if __name__ == "__main__":
    main()
