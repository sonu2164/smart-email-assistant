import os
import json
import re
import base64
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from langchain.tools import BaseTool
import pandas as pd
import streamlit as st
from typing import Optional, List, Dict, Any

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.send",
]

class GmailTool(BaseTool):
    name: str = "gmail_tool"
    description: str = "Manage Gmail: list, summarize, delete/archive, create rules, find unsubscribe links."

    # Declare non-pydantic fields here
    creds: Any = None
    service: Any = None

    def _load_credentials(self, token_path: str, client_secret_file: str) -> Credentials:
        creds = None

        # Load saved token if it exists
        if os.path.exists(token_path):
            try:
                creds = Credentials.from_authorized_user_file(token_path, SCOPES)
            except Exception as e:
                print(f"Error loading credentials: {e}")

        # Refresh token if expired
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())
            except Exception as e:
                print(f"Error refreshing credentials: {e}")
                creds = None

        # Run OAuth if no valid credentials
        if not creds or not creds.valid:
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, SCOPES)
            creds = flow.run_local_server(port=0)
            with open(token_path, 'w') as token:
                token.write(creds.to_json())

        return creds

    @classmethod
    def create(cls, token_path="token.json", client_secret_file="credentials.json"):
        instance = cls()
        creds = instance._load_credentials(token_path, client_secret_file)
        service = build("gmail", "v1", credentials=creds, cache_discovery=False)

        instance.creds = creds
        instance.service = service
        return instance
    

    def _list_threads(self, query: str = "is:unread", max_results: int = 10):
        resp = self.service.users().threads().list(
            userId="me", q=query, maxResults=max_results
        ).execute()
        return resp.get("threads", [])

    def _run(self, query: str) -> str:
        """
        This is the required method that BaseTool looks for.
        It replaces the previous 'run' method.
        """
        threads = self._list_threads(query)
        return f"Found {len(threads)} threads."

    def summarize_thread(self, thread_id: str) -> str:
        msgs = self.service.users().threads().get(
            userId="me", id=thread_id
        ).execute()["messages"]
        bodies = []
        for m in msgs:
            part = m["payload"].get("body", {}).get("data", "")
            if part:
                decoded_bytes = base64.urlsafe_b64decode(part)
                decoded_str = decoded_bytes.decode("utf-8")
                bodies.append(decoded_str)
            else:
                # Handle multipart messages
                parts = m["payload"].get("parts", [])
                for part in parts:
                    if part.get("mimeType") == "text/plain" and part.get("body", {}).get("data"):
                        decoded_bytes = base64.urlsafe_b64decode(part["body"]["data"])
                        decoded_str = decoded_bytes.decode("utf-8")
                        bodies.append(decoded_str)
        return "\n\n".join(bodies)

    def delete_marketing(self, older_than_days: int = 30) -> str:
        q = f"category:promotions before:{older_than_days}d"
        threads = self._list_threads(q, max_results=100)
        for t in threads:
            self.service.users().threads().trash(userId="me", id=t["id"]).execute()
        return f"Trashed {len(threads)} marketing threads older than {older_than_days} days."

    def create_filter(self, criteria: dict, action: dict) -> str:
        body = {"criteria": criteria, "action": action}
        flt = self.service.users().settings().filters().create(
            userId="me", body=body
        ).execute()
        return f"Created filter id={flt['id']}"
    
    def find_unsubscribe_links(self, max_results: int = 20) -> List[Dict[str, Any]]:
        """
        Find emails with unsubscribe links either in the header or body.
        """
        query = "has:unsubscribe"
        threads = self._list_threads(query, max_results=max_results)
        
        newsletters = []
        
        for thread in threads:
            thread_id = thread["id"]
            thread_data = self.service.users().threads().get(userId="me", id=thread_id).execute()
            
            for message in thread_data["messages"]:
                msg_id = message["id"]
                msg_data = self.service.users().messages().get(userId="me", id=msg_id, format="full").execute()
                
                headers = msg_data["payload"]["headers"]
                sender = next((h["value"] for h in headers if h["name"].lower() == "from"), "Unknown")
                subject = next((h["value"] for h in headers if h["name"].lower() == "subject"), "No Subject")
                
                unsubscribe_url = None

                # --- 1. Try header ---
                unsubscribe_header = next((h["value"] for h in headers if h["name"].lower() == "list-unsubscribe"), None)
                if unsubscribe_header:
                    match = re.search(r'<(https?://[^>]+)>', unsubscribe_header)
                    if match:
                        unsubscribe_url = match.group(1)

                # --- 2. If no header found, try body ---
                if not unsubscribe_url:
                    body = ""

                    # Direct body
                    if msg_data["payload"].get("body", {}).get("data"):
                        body_data = msg_data["payload"]["body"]["data"]
                        try:
                            body = base64.urlsafe_b64decode(body_data).decode("utf-8")
                        except Exception:
                            continue

                    # Multipart
                    parts = msg_data["payload"].get("parts", [])
                    for part in parts:
                        if part.get("body", {}).get("data") and part.get("mimeType") in ["text/html", "text/plain"]:
                            try:
                                part_body = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8")
                                body += part_body
                            except Exception:
                                continue

                    # Regex search for unsubscribe-like links
                    unsubscribe_patterns = [
                        r'href=[\'"]?(https?://[^\'" >]+)[\'"]?[^>]*>([^<]*unsubscribe[^<]*)',
                        r'href=[\'"]?(https?://[^\'" >]+)[\'"]?[^>]*>([^<]*opt[ -]?out[^<]*)',
                        r'href=[\'"]?(https?://[^\'" >]+)[\'"]?[^>]*>([^<]*remove[^<]*)',
                        r'(https?://[^"\' >]*unsubscribe[^"\' >]*)'
                    ]

                    for pattern in unsubscribe_patterns:
                        matches = re.finditer(pattern, body, re.IGNORECASE)
                        for match in matches:
                            unsubscribe_url = match.group(1)
                            break
                        if unsubscribe_url:
                            break

                # Save result if found
                if unsubscribe_url:
                    newsletters.append({
                        "message_id": msg_id,
                        "thread_id": thread_id,
                        "sender": sender,
                        "subject": subject,
                        "unsubscribe_url": unsubscribe_url
                    })
                    break  # Only one message per thread

        return newsletters

    def display_unsubscribe_table(self):
        """
        Display a table of newsletters with unsubscribe links and buttons.
        Returns a DataFrame for further processing.
        """
        newsletters = self.find_unsubscribe_links()
        
        if not newsletters:
            st.warning("No newsletters with unsubscribe links found.")
            return None
        
        # Create DataFrame for display
        df = pd.DataFrame(newsletters)
        
        # Display table with unsubscribe buttons
        st.write(f"Found {len(newsletters)} newsletters with unsubscribe links:")
        
        # Create a more user-friendly display table
        display_df = df[["sender", "subject"]].copy()
        
        # Display the table
        st.dataframe(display_df)
        
        # Return the full dataframe for further processing
        return df
