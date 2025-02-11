import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account
from datetime import datetime
from googleapiclient.discovery import build
import re


# Google Drive constants
SCOPES = [
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/spreadsheets',
]
FOLDER_ID = '1fJL15MniB6TtOU2AtiN04VLeRRkCeWMg'  # Replace with your Google Drive folder ID
SERVICE_ACCOUNT_FILE = 'amrajsd-8e0f04ddb4ae.json'  # Replace with the path to your service account JSON file



def authenticate_google_drive():
    """Authenticate with Google Drive API using a service account."""
    try:
        # Load service account credentials
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        # Build the Google Drive service
        return build('drive', 'v3', credentials=creds)
    except Exception as e:
        print(f"Failed to authenticate with Google Drive: {e}")
        return None


def authenticate_google_sheets():
    """Authenticate with Google Sheets API using a service account."""
    try:
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES
        )
        return build('sheets', 'v4', credentials=creds)
    except Exception as e:
        print(f"Failed to authenticate with Google Sheets: {e}")
        return None


def log_task_to_sheet(username, user_id, handed_task, submission_date,sheet_id,thread_name):
    """Log the task submission details to a Google Sheet."""
    try:
        sheets_service = authenticate_google_sheets()
        if not sheets_service:
            print("Failed to access Google Sheets service.")
            return

        # Correct range syntax for appending data
        range_name = f"'{thread_name}'!A:D"  # Ensure the sheet name exists and matches exactly

        # Prepare data to append
        values = [[username, user_id, handed_task, submission_date]]
        body = {"values": values}

        # Append the data to the sheet
        sheets_service.spreadsheets().values().append(
            spreadsheetId=sheet_id,
            range=range_name,
            valueInputOption="USER_ENTERED",
            body=body
        ).execute()
        
        print(f"Task submission logged successfully for {username} ({user_id}).")
    except Exception as e:
        print(f"Failed to log task submission: {e}")


# know the team name => and based on name go to the team folder in drvie => open the sheet => create a tab with the trhead name 
#=> after this , when the one hand the task 
def create_tab_in_sheet(sheet_id: str, tab_name: str):
    """
    Creates a new tab in the specified Google Sheet with the given tab name.
    
    Args:
        sheet_id (str): The ID of the Google Sheet.
        tab_name (str): The name of the new tab to be created.
    
    Returns:
        None
    """
    try:
        # Authenticate Google Sheets API
        service = authenticate_google_sheets()  # Replace with your authentication function
        
        # Check if the tab name is valid (Google Sheets does not allow certain characters)
        safe_tab_name = re.sub(r'[<>:"/\\|?*]', '-', tab_name)

        # Add a new tab request
        requests = [
            {
                "addSheet": {
                    "properties": {
                        "title": safe_tab_name,  # Set the name of the new tab
                    }
                }
            }
        ]
        
        # Execute the batch update
        body = {"requests": requests}
        service.spreadsheets().batchUpdate(spreadsheetId=sheet_id, body=body).execute()
        print(f"Tab '{safe_tab_name}' created successfully in the sheet.")

    except Exception as e:
        print(f"An error occurred while creating the tab: {e}")



