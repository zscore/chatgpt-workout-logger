# main.py  –  Google Cloud Functions (Gen 2), Python 3.12
import base64
import json
import os
from datetime import datetime, timezone

from flask import jsonify
import functions_framework                          # <-- required wrapper

from google.oauth2 import service_account
from googleapiclient.discovery import build


# ── lazy-init Google Sheets client ─────────────────────────────────
_sheets = None
def get_sheets():
    global _sheets
    if _sheets:
        return _sheets

    raw = os.environ.get("SA_KEY_JSON")
    if not raw:
        raise RuntimeError("SA_KEY_JSON env var missing")

    try:
        # Allow raw JSON or base64-encoded blob
        json_str = raw if raw.lstrip().startswith("{") else base64.b64decode(raw).decode()
        info = json.loads(json_str)
    except Exception as e:
        raise RuntimeError(f"Bad SA_KEY_JSON: {e}")

    creds = service_account.Credentials.from_service_account_info(
        info,
        scopes=["https://www.googleapis.com/auth/spreadsheets"],
    )
    _sheets = build("sheets", "v4", credentials=creds)
    return _sheets


# ── helper: WorkoutEntry → row list ────────────────────────────────
REQ = ("exercise", "weight", "reps", "sets")        # required fields
def to_row(entry: dict) -> list:
    now_iso = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    return [
        entry.get("exercise", ""),
        entry.get("weight",   ""),
        entry.get("reps",     ""),
        entry.get("sets",     ""),
        entry.get("comment",  ""),
        entry.get("datetime", now_iso) or now_iso,  # default timestamp
    ]


# ── HTTP-triggered Cloud Function ─────────────────────────────────
@functions_framework.http
def log_workout(request):
    """
    POST JSON body:
      - single WorkoutEntry  or
      - array[WorkoutEntry]

    Responds: 200 {ok: true, rowsInserted: N}
    """
    body = request.get_json(silent=True)
    if body is None:
        return jsonify(error="Expected application/json"), 400

    entries = body if isinstance(body, list) else [body]

    for i, e in enumerate(entries):
        missing = [k for k in REQ if k not in e]
        if missing:
            return jsonify(error=f"Entry {i} missing {missing}"), 400

    values = [to_row(e) for e in entries]

    sheet_id = os.environ.get("SHEET_ID")
    if not sheet_id:
        return jsonify(error="SHEET_ID env var missing"), 500

    get_sheets().spreadsheets().values().append(
        spreadsheetId=sheet_id,
        range="workouts!A1",            # 👈 change tab name if needed
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body={"values": values},
    ).execute()

    return jsonify(ok=True, rowsInserted=len(values))