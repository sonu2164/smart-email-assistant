import os
from pathlib import Path

# Import for Gmail toolkit
from langchain_google_community import GmailToolkit
from langchain_google_community.gmail.utils import (
    get_gmail_credentials,
    build_resource_service,
)
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

def get_gmail_tools():
    """
    Initialize Gmail toolkit and return its tools
    """
    # Define scopes
    SCOPES = [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.modify",
        "https://www.googleapis.com/auth/gmail.send",
    ]
    
    # Define paths
    token_path = "token.json"
    client_secrets_file = "credentials.json"  # renamed from client_secret.json
    
    # Check if token.json exists and is valid
    creds = None
    if os.path.exists(token_path):
        try:
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        except ValueError:
            # If token is invalid, we'll create a new one
            creds = None
    
    # If no valid credentials, run the OAuth flow
    if not creds or not creds.valid:
        if os.path.exists(client_secrets_file):
            flow = InstalledAppFlow.from_client_secrets_file(
                client_secrets_file, SCOPES
            )
            creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
        else:
            raise FileNotFoundError(f"Client secrets file '{client_secrets_file}' not found. Please rename your client_secret.json to credentials.json")
    
    # Build the Gmail API resource
    api_resource = build_resource_service(credentials=creds)
    
    # Create the toolkit with the API resource
    gmail_toolkit = GmailToolkit(api_resource=api_resource)
    
    # Get all Gmail tools
    return gmail_toolkit.get_tools()

def get_all_tools():
    """
    Assemble all tools:
      1) Gmail toolkit tools
    """
    # Get Gmail tools
    gmail_tools = get_gmail_tools()
    
    # For now, return just Gmail tools
    return gmail_tools
