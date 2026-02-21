import os
import json
from datetime import datetime, timezone
from dateutil import tz
import gspread
from google.oauth2.service_account import Credentials

def main():
    sa_json = os.environ["GSHEET_SERVICE_ACCOUNT_JSON"]
    spreadsheet_id = os.environ["SPREADSHEET_ID"]
    sheet_name = os.environ.get("SHEET_NAME", "Sheet1")

    info = json.loads(sa_json)

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_info(info, scopes=scopes)
    gc = gspread.authorize(creds)

    sh = gc.open_by_key(spreadsheet_id)
    ws = sh.worksheet(sheet_name)

    now_utc = datetime.now(timezone.utc)
    now_pacific = now_utc.astimezone(tz.gettz("America/Los_Angeles"))

    # Escribe en A2 y B2 siempre (modo “heartbeat”)
    ws.update("A2", [[now_utc.isoformat()]])
    ws.update("B2", [[now_pacific.strftime("%Y-%m-%d %H:%M:%S %Z")]])

    print("Updated:", now_utc.isoformat())

if __name__ == "__main__":
    main()