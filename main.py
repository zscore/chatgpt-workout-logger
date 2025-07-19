import base64
import json
import os
from datetime import date
from flask import Flask, request, jsonify

from google.oauth2 import service_account
from googleapiclient.discovery import build

app = Flask(__name__)

# Lazy init so cold start only does this once
_sheets_service = None

def get_sheets():
    global _sheets_service
    if _sheets_service:
        return _sheets_service

    # Expect SA_KEY_JSON env var (either raw JSON or base64 of the JSON)
    raw = os.environ.get("SA_KEY_JSON")
    if not raw:
        raise RuntimeError("SA_KEY_JSON env var missing")

    # If it looks base64-encoded, decode
    try:
        if raw.strip().startswith("{"):
            decoded_json = raw
        else:
            decoded_json = base64.b64decode(raw).decode()
    except Exception as e:
        raise RuntimeError(f"Failed to decode SA_KEY_JSON: {e}")

    info = json.loads(decoded_json)

    creds = service_account.Credentials.from_service_account_info(
        info,
        scopes=["https://www.googleapis.com/auth/spreadsheets"],
    )

    _sheets_service = build("sheets", "v4", credentials=creds)
    return _sheets_service


def to_row(entry: dict) -> list:
    """Return columns in fixed order: exercise, weight, reps, sets, comment, date."""
    today = date.today().isoformat()
    return [
        entry.get("exercise", ""),
        entry.get("weight", ""),
        entry.get("reps", ""),
        entry.get("sets", ""),
        entry.get("comment", ""),
        entry.get("date", today) or today,
    ]


@app.post("/workout-entry")
def log_workout():
    """
    Accepts either one WorkoutEntry object or an array of them.
    """
    body = request.get_json(silent=True)
    if body is None:
        return jsonify(error="Expected JSON body"), 400

    entries = body if isinstance(body, list) else [body]

    # Basic validation
    required = ("exercise", "weight", "reps", "sets")
    for i, e in enumerate(entries):
        missing = [k for k in required if k not in e]
        if missing:
            return jsonify(error=f"Entry {i} missing required fields: {missing}"), 400

    values = [to_row(e) for e in entries]

    sheet_id = os.environ.get("SHEET_ID")
    if not sheet_id:
        return jsonify(error="SHEET_ID env var missing"), 500

    sheets = get_sheets()
    sheets.spreadsheets().values().append(
        spreadsheetId=sheet_id,
        range="Sheet1!A1",              # adjust tab name if different
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body={"values": values},
    ).execute()

    return jsonify(ok=True, rowsInserted=len(values))


# ---- Cloud Functions (Gen2) entry point ----
# For Cloud Functions, set --entry-point=app
# (Functions Gen2 can treat a Flask app as a target via Functions Framework.)
