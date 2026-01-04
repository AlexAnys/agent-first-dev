"""Gmail API client with OAuth2 authentication."""
import base64
from pathlib import Path
from typing import Optional, List, Dict, Any
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from .logger import logger
from .resilience import with_retry, handle_empty_results

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
CREDENTIALS_FILE = Path(__file__).parent.parent / "credentials.json"
TOKEN_FILE = Path(__file__).parent.parent / "token.json"


def authenticate() -> Credentials:
    """Perform OAuth2 authentication flow."""
    creds = None

    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
        logger.info("Loaded existing credentials from token.json")

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            logger.info("Refreshing expired credentials")
            creds.refresh(Request())
        else:
            if not CREDENTIALS_FILE.exists():
                raise FileNotFoundError(
                    f"credentials.json not found at {CREDENTIALS_FILE}. "
                    "Download from Google Cloud Console."
                )
            logger.info("Starting OAuth2 authentication flow")
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_FILE), SCOPES
            )
            creds = flow.run_local_server(port=0)

        TOKEN_FILE.write_text(creds.to_json())
        logger.info("Saved new credentials to token.json")

    return creds


def create_gmail_service():
    """Create authenticated Gmail API service."""
    creds = authenticate()
    service = build("gmail", "v1", credentials=creds)
    logger.info("Gmail service created successfully")
    return service


def extract_header(headers: List[Dict], name: str) -> str:
    """Extract header value by name from headers list."""
    return next(
        (h["value"] for h in headers if h["name"].lower() == name.lower()),
        ""
    )


def decode_body(data: str) -> str:
    """Decode base64url encoded message body."""
    if not data:
        return ""
    try:
        return base64.urlsafe_b64decode(data).decode("utf-8")
    except Exception as e:
        logger.warning(f"Failed to decode body: {e}")
        return ""


def extract_body_from_payload(payload: Dict) -> str:
    """Extract text body from message payload (handles multipart)."""
    if "body" in payload and payload["body"].get("data"):
        return decode_body(payload["body"]["data"])

    if "parts" in payload:
        for part in payload["parts"]:
            if part["mimeType"] == "text/plain":
                return decode_body(part.get("body", {}).get("data", ""))
            if part["mimeType"].startswith("multipart/"):
                return extract_body_from_payload(part)

    return ""


@with_retry(max_retries=3, base_delay=1.0)
async def search_messages_async(
    service,
    query: str,
    max_results: int = 10
) -> Dict[str, Any]:
    """Search Gmail messages with retry logic."""
    logger.info(f"Searching messages: query='{query}', max_results={max_results}")

    response = service.users().messages().list(
        userId="me",
        q=query,
        maxResults=min(max_results, 100)
    ).execute()

    message_ids = response.get("messages", [])

    empty_result = handle_empty_results(message_ids, query)
    if empty_result:
        return empty_result

    messages = []
    for msg_ref in message_ids:
        msg = service.users().messages().get(
            userId="me",
            id=msg_ref["id"],
            format="metadata",
            metadataHeaders=["From", "To", "Subject", "Date"]
        ).execute()

        headers = msg.get("payload", {}).get("headers", [])
        messages.append({
            "id": msg["id"],
            "threadId": msg["threadId"],
            "snippet": msg.get("snippet", ""),
            "subject": extract_header(headers, "Subject"),
            "from": extract_header(headers, "From"),
            "date": extract_header(headers, "Date")
        })

    logger.info(f"Found {len(messages)} messages")
    return {
        "messages": messages,
        "resultCount": len(messages),
        "hasMore": "nextPageToken" in response
    }


@with_retry(max_retries=3, base_delay=1.0)
async def get_message_async(
    service,
    message_id: str,
    format: str = "full"
) -> Dict[str, Any]:
    """Get full message details with retry logic."""
    logger.info(f"Getting message: id={message_id}, format={format}")

    msg = service.users().messages().get(
        userId="me",
        id=message_id,
        format=format
    ).execute()

    headers = msg.get("payload", {}).get("headers", [])
    body = extract_body_from_payload(msg.get("payload", {}))

    result = {
        "id": msg["id"],
        "threadId": msg["threadId"],
        "subject": extract_header(headers, "Subject"),
        "from": extract_header(headers, "From"),
        "to": extract_header(headers, "To"),
        "date": extract_header(headers, "Date"),
        "body": body,
        "labels": msg.get("labelIds", []),
        "snippet": msg.get("snippet", "")
    }

    logger.info(f"Retrieved message: subject='{result['subject']}'")
    return result
