#!/usr/bin/env python3
"""
Sheets OAuth + Append Smoke Test

Runs a minimal Portia plan that appends a test row to the configured
Google Sheet and Tab. This helps trigger Google Sheets OAuth (if not yet authorized)
and verifies write access independently of the Gmail flow.

Usage (PowerShell):
  python .\scripts\sheets_smoke.py
Optionally override via env:
  $env:SHEET_ID = "<YOUR_SHEET_ID>"
  $env:SHEET_TAB = "UpdateSheet"
"""
from __future__ import annotations
import os
from datetime import datetime
from dotenv import load_dotenv

# Portia SDK
from portia import Portia, Config, StorageClass, LogLevel, LLMProvider
from portia.cli import CLIExecutionHooks


def build_config() -> Config:
    """Prefer Google Gemini (avoids OpenAI quota issues)."""
    return Config.from_default(
        llm_provider=LLMProvider.GOOGLE,
        default_model="google/gemini-1.5-flash",
        storage_class=StorageClass.CLOUD if os.getenv("PORTIA_API_KEY") else StorageClass.MEMORY,
        default_log_level=LogLevel.DEBUG if os.getenv("PORTIA_API_KEY") else LogLevel.INFO,
    )


def main() -> None:
    load_dotenv()
    sheet_id = os.getenv("SHEET_ID", "").strip()
    sheet_tab = os.getenv("SHEET_TAB", "UpdateSheet").strip()
    if not sheet_id:
        print("Missing SHEET_ID. Set it in .env or as an environment variable.")
        raise SystemExit(2)

    cfg = build_config()
    portia = Portia(config=cfg, tools=None, execution_hooks=CLIExecutionHooks())

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    test_row = {
        "Date": now,
        "From": "sheets-smoke@test",
        "Subject": "OAuth/Write Test",
        "Company": "TestCo",
        "Role": "Test Role",
        "Source": "Smoke",
        "URL": "https://example.com",
        "Deadline": "",
        "EmailId": "",
        "Notes": "This is a test row appended by sheets_smoke.py",
    }

    headers = list(test_row.keys())

    prompt = f"""
You are an assistant with access to Google Sheets via Portia tools.
Task: Ensure the spreadsheet with id '{sheet_id}' contains a tab named '{sheet_tab}'.
- If the tab doesn't exist, create it.
- Ensure the first row (header) has these columns in order:
  {headers}
- Append exactly one new row with the following values mapped by header name:
  {test_row}
Return a concise confirmation with the A1 range that was written.
If authentication is required at any point, initiate OAuth and wait for completion, then continue.
"""

    print("Starting Sheets OAuth + append smoke test... If authentication is required, a link will appear below.")
    result = portia.run(prompt)
    print("---")
    if hasattr(result, "final_output"):
        print(result.final_output)
    else:
        print(result)


if __name__ == "__main__":
    main()
