import os, json
from datetime import datetime, timezone
from dateutil import tz
import gspread
from gspread.exceptions import APIError
from google.oauth2.service_account import Credentials

def main():
    sa_json = os.environ.get("GSHEET_SERVICE_ACCOUNT_JSON", "")
    spreadsheet_id = os.environ.get("SPREADSHEET_ID", "")
    sheet_name = os.environ.get("SHEET_NAME", "Sheet1")

    print("Spreadsheet ID present:", bool(spreadsheet_id), "len:", len(spreadsheet_id))
    print("Sheet name:", sheet_name)
    print("SA json present:", bool(sa_json), "len:", len(sa_json))

    info = json.loads(sa_json)
    print("Service account:", info.get("client_email"))

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_info(info, scopes=scopes)
    gc = gspread.authorize(creds)

    try:
        sh = gc.open_by_key(spreadsheet_id)
        ws = sh.worksheet(sheet_name)

        now_utc = datetime.now(timezone.utc)
        now_pacific = now_utc.astimezone(tz.gettz("America/Los_Angeles"))

        if ws.acell("A1").value in (None, ""):
            ws.update("A1:D1", [["idx", "last_update_utc", "last_update_pacific", "run_source"]])

        idx = max(len(ws.get_all_values()) - 1, 0) + 1

        ws.append_row(
            [idx, now_utc.isoformat(), now_pacific.strftime("%Y-%m-%d %H:%M:%S %Z"), "github-actions"],
            value_input_option="RAW",
        )

        print("OK updated:", now_utc.isoformat())

    except APIError as e:
        resp = getattr(e, "response", None)
        if resp is not None:
            print("APIError status:", getattr(resp, "status_code", "unknown"))
            txt = getattr(resp, "text", "")
            print("APIError body head:", txt[:500])
        print("Full error:", str(e))
        raise

if __name__ == "__main__":
    main()