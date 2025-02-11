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
#SERVICE_ACCOUNT_FILE = 'amrajsd-ad5fd088004e.json'  # Replace with the path to your service account JSON file

def get_service_account_credentials():
    """Retrieve service account credentials from environment variables."""
    try:
        service_account_info = {
            "type": "service_account",
            "project_id": os.getenv("GCP_PROJECT_ID"),
            "private_key_id": os.getenv("GCP_PRIVATE_KEY_ID"),
            "private_key": os.getenv("GCP_PRIVATE_KEY").replace('\\n', '\n'),  # Ensure correct formatting
            "client_email": os.getenv("GCP_CLIENT_EMAIL"),
            "client_id": os.getenv("GCP_CLIENT_ID"),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": os.getenv("GCP_CLIENT_X509_CERT_URL"),
            "universe_domain": "googleapis.com"
        }

        return service_account.Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
    
    except Exception as e:
        print(f"Failed to load service account credentials: {e}")
        return None

def authenticate_google_drive():
    """Authenticate with Google Drive API using a service account."""
    try:
        # Load service account credentials In dev
        # creds = service_account.Credentials.from_service_account_file(
        #     SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        
        creds = get_service_account_credentials()
        
        # Build the Google Drive service
        return build('drive', 'v3', credentials=creds)
    except Exception as e:
        print(f"Failed to authenticate with Google Drive: {e}")
        return None

def authenticate_google_sheets():
    """Authenticate with Google Sheets API using a service account."""
    try:
        #In dev
        # creds = service_account.Credentials.from_service_account_file(
        #     SERVICE_ACCOUNT_FILE, scopes=SCOPES
        # )
        
        creds = get_service_account_credentials()
        
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