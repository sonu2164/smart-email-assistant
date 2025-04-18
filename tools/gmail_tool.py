import os
import json
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from langchain.tools import BaseTool
from langchain.pydantic_v1 import Field

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.send",
]

class GmailTool(BaseTool):
    name = "gmail_tool"
    description = "Manage Gmail: list, summarize, delete/archive, create rules."

    creds: Credentials = Field(default=None)
    token_path: Path = Field(default=Path("token.json"))
    client_secret_file: Path = Field(default=Path("client_secret.json"))

    def __init__(self):
        super().__init__()
        self._load_credentials()
        self.service = build("gmail", "v1", credentials=self.creds, cache_discovery=False)

    def _load_credentials(self):
        # 1) load token.json if exists
        if self.token_path.exists():
            self.creds = Credentials.from_authorized_user_file(str(self.token_path), SCOPES)
        else:
            # 2) run OAuth flow
            flow = InstalledAppFlow.from_client_secrets_file(
                str(self.client_secret_file), SCOPES
            )
            self.creds = flow.run_local_server(port=0)
            # 3) save for next time
            with open(self.token_path, "w") as f:
                f.write(self.creds.to_json())

    def _list_threads(self, query: str = "is:unread", max_results: int = 10):
        resp = self.service.users().threads().list(
            userId="me", q=query, maxResults=max_results
        ).execute()
        return resp.get("threads", [])

    def run(self, query: str):
        threads = self._list_threads(query)
        return f"Found {len(threads)} threads."

    def summarize_thread(self, thread_id: str):
        msgs = self.service.users().threads().get(
            userId="me", id=thread_id
        ).execute()["messages"]
        bodies = []
        for m in msgs:
            part = m["payload"].get("body", {}).get("data", "")
            bodies.append(part)
        return "\n\n".join(bodies)

    def delete_marketing(self, older_than_days: int = 30):
        q = f"category:promotions before:{older_than_days}d"
        threads = self._list_threads(q, max_results=100)
        for t in threads:
            self.service.users().threads().trash(userId="me", id=t["id"]).execute()
        return f"Trashed {len(threads)} marketing threads older than {older_than_days} days."

    def create_filter(self, criteria: dict, action: dict):
        body = {"criteria": criteria, "action": action}
        flt = self.service.users().settings().filters().create(
            userId="me", body=body
        ).execute()
        return f"Created filter id={flt['id']}"