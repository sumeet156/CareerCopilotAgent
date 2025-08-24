"""Direct Google Sheets integration as a fallback option."""
import os
import json
from typing import List, Any, Dict, Optional
from pydantic import BaseModel, Field
import pandas as pd
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

class SheetWriteInput(BaseModel):
    sheet_id: str = Field(..., description="The ID of the Google Sheet")
    tab_name: str = Field(..., description="The name of the tab/worksheet")
    data: List[List[Any]] = Field(..., description="The data to write as a list of rows")
    include_headers: bool = Field(True, description="Whether to include headers in the first row")
    headers: Optional[List[str]] = Field(None, description="Optional headers to use")

class SheetWriteOutput(BaseModel):
    success: bool = Field(..., description="Whether the operation was successful")
    rows_written: int = Field(..., description="Number of rows written")
    message: str = Field(..., description="Status message")

def get_google_sheets_credentials():
    """Get Google Sheets credentials from OAuth flow or cached token."""
    creds = None
    
    # Check for environment variable based OAuth
    client_id = os.environ.get("GOOGLE_CLIENT_ID")
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET")
    redirect_uri = os.environ.get("GOOGLE_REDIRECT_URI", "http://localhost:8501")
    
    if client_id and client_secret:
        # Use OAuth flow
        flow = InstalledAppFlow.from_client_config(
            {
                "installed": {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "redirect_uris": [redirect_uri],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token"
                }
            },
            SCOPES
        )
        creds = flow.run_local_server(port=8501)
    
    return creds

def write_to_sheets(input_data: SheetWriteInput) -> SheetWriteOutput:
    """Write data directly to Google Sheets using the Sheets API."""
    try:
        # Get credentials
        creds = get_google_sheets_credentials()
        if not creds:
            return SheetWriteOutput(
                success=False,
                rows_written=0,
                message="Failed to get Google Sheets credentials"
            )
        
        # Build the Sheets API service
        service = build('sheets', 'v4', credentials=creds)
        
        # First check if the sheet exists
        try:
            sheet_metadata = service.spreadsheets().get(
                spreadsheetId=input_data.sheet_id
            ).execute()
            
            # Check if the tab exists
            sheet_exists = False
            for sheet in sheet_metadata.get('sheets', []):
                if sheet.get('properties', {}).get('title') == input_data.tab_name:
                    sheet_exists = True
                    break
            
            if not sheet_exists:
                # Create the sheet tab
                request = {
                    'addSheet': {
                        'properties': {
                            'title': input_data.tab_name
                        }
                    }
                }
                service.spreadsheets().batchUpdate(
                    spreadsheetId=input_data.sheet_id,
                    body={'requests': [request]}
                ).execute()
        
        except HttpError as error:
            if error.resp.status == 404:
                return SheetWriteOutput(
                    success=False,
                    rows_written=0,
                    message=f"Spreadsheet with ID {input_data.sheet_id} not found"
                )
            raise
        
        # Prepare the data to write
        values = input_data.data
        
        # Write the data
        result = service.spreadsheets().values().append(
            spreadsheetId=input_data.sheet_id,
            range=f"{input_data.tab_name}!A1",
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body={"values": values}
        ).execute()
        
        rows_written = result.get('updates', {}).get('updatedRows', 0)
        
        return SheetWriteOutput(
            success=True,
            rows_written=rows_written,
            message=f"Successfully wrote {rows_written} rows to Google Sheet"
        )
        
    except Exception as e:
        return SheetWriteOutput(
            success=False,
            rows_written=0,
            message=f"Error writing to Google Sheet: {str(e)}"
        )

def direct_gmail_to_sheets(email_data_json: str, sheet_id: str, sheet_tab: str) -> Dict[str, Any]:
    """Parse email data JSON and write directly to Google Sheets."""
    try:
        # Parse the JSON data
        if email_data_json.startswith("```json"):
            # Extract the JSON content from code blocks
            start_idx = email_data_json.find("[")
            end_idx = email_data_json.rfind("]") + 1
            if start_idx > 0 and end_idx > 0:
                email_data_json = email_data_json[start_idx:end_idx]
        
        email_data = json.loads(email_data_json)
        
        # Convert to rows for sheets
        headers = ["Date", "Company", "Role", "Source", "URL", "Deadline"]
        rows = [headers]  # Start with headers
        
        for item in email_data:
            rows.append([
                item.get("date", ""),
                item.get("company", ""),
                item.get("role", ""),
                item.get("source", ""),
                item.get("url", ""),
                item.get("deadline", "")
            ])
        
        # Write to Google Sheets
        result = write_to_sheets(SheetWriteInput(
            sheet_id=sheet_id,
            tab_name=sheet_tab,
            data=rows,
            include_headers=True
        ))
        
        return {
            "success": result.success,
            "rows_written": result.rows_written,
            "message": result.message
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
