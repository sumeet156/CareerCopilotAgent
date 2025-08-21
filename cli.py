#!/usr/bin/env python3
r"""CLI entrypoint to initiate Portia OAuth and run Gmail → Google Sheets workflow.

Usage (PowerShell):
    # Recommended: rely on .env loaded by the app
    python .\cli.py gmail-to-sheets

    # Or pass explicit values
    python .\cli.py gmail-to-sheets --sheet-id "<SHEET_ID>" --sheet-tab "<TAB>"

Note: Using $env:SHEET_ID as a value may expand to empty if not set in the shell.
If omitted, values are read from .env (SHEET_ID, SHEET_TAB).
This will create a plan in Portia which triggers OAuth flows in the terminal.
"""
import argparse
import os
from app.orchestrator import CareerCopilotOrchestrator


def main():
    parser = argparse.ArgumentParser(description="Career Copilot CLI")
    sub = parser.add_subparsers(dest="cmd")

    g2s = sub.add_parser("gmail-to-sheets", help="Scan Gmail and write rows to Google Sheet")
    # Accept optional values; if value omitted or empty, fall back to env loaded from .env
    g2s.add_argument("--sheet-id", nargs="?", default=None)
    g2s.add_argument("--sheet-tab", nargs="?", default=None)

    args = parser.parse_args()

    if args.cmd == "gmail-to-sheets":
        sheet_id = args.sheet_id or os.getenv("SHEET_ID", "")
        sheet_tab = args.sheet_tab or os.getenv("SHEET_TAB", "Applications")
        if not sheet_id:
            print("Missing Sheet ID. Either set SHEET_ID in .env or pass --sheet-id \"<SHEET_ID>\".")
            raise SystemExit(2)
        orch = CareerCopilotOrchestrator()
        print("Starting Gmail → Sheets run. If authentication is required, an OAuth link will appear below.")
        result = orch.gmail_to_sheets(sheet_id=sheet_id, sheet_tab=sheet_tab)
        print("Result:")
        print(result)
        return

    parser.print_help()


if __name__ == "__main__":
    main()
