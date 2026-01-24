# import gspread
# from google.oauth2.service_account import Credentials
# from datetime import datetime
# import os

# BASE_DIR = os.path.dirname(os.path.dirname(__file__))
# CREDS_FILE = os.path.join(BASE_DIR, "config", "google_service_account.json")


# SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
# CREDS_FILE = "google_service_account.json"  # keep this private
# SPREADSHEET_ID = "1pT2jbO4BjNMLXM6QiQ_WYgUAPuQhqpm48ghFtOKQufM"
# SHEET_NAME = "Verifications"


# def get_sheet():
#     creds = Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPES)
#     client = gspread.authorize(creds)
#     sheet = client.open_by_key(SPREADSHEET_ID)
#     return sheet.worksheet(SHEET_NAME)


# def save_user(member, first_name, last_name, email):
#     sheet = get_sheet()
#     sheet.append_row(
#         [
#             datetime.utcnow().isoformat(),
#             str(member.id),
#             member.name,
#             first_name,
#             last_name,
#             email,
#         ]
#     )


# import os
# import json
# import gspread
# from google.oauth2.service_account import Credentials
# from datetime import datetime

# SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# BASE_DIR = os.path.dirname(os.path.dirname(__file__))
# # CREDS_FILE = os.path.join(BASE_DIR, "config", "google_service_account.json")
# CREDS_FILE = json.loads(os.getenv("GOOGLE_CREDS_JSON"))

# SPREADSHEET_ID = "1pT2jbO4BjNMLXM6QiQ_WYgUAPuQhqpm48ghFtOKQufM"
# SHEET_NAME = "Verifications"

# HEADERS = [
#     "Timestamp",
#     "Discord ID",
#     "Discord Username",
#     "First Name",
#     "Last Name",
#     "Email",
# ]


# def get_sheet():
#     creds = Credentials.from_service_account_file(
#         CREDS_FILE,
#         scopes=SCOPES,
#     )
#     client = gspread.authorize(creds)
#     sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)
#     return sheet


# # def ensure_header(sheet):
# #     """
# #     Ensures the header row exists and is formatted.
# #     Runs only once per sheet.
# #     """
# #     existing = sheet.get_all_values()

# #     if existing:
# #         return  # Header already exists

# #     # Insert header row
# #     sheet.append_row(HEADERS)

# #     # Format header: bold + black
# #     sheet.format(
# #         "A1:F1",
# #         {
# #             "textFormat": {
# #                 "bold": True,
# #                 "foregroundColor": {
# #                     "red": 0,
# #                     "green": 0,
# #                     "blue": 0,
# #                 },
# #             }
# #         },
# #     )


# def ensure_header(sheet):
#     try:
#         first_row = sheet.row_values(1)
#     except Exception:
#         first_row = []

#     if first_row == HEADERS:
#         return  # Header already correct

#     # Insert header at row 1
#     sheet.insert_row(HEADERS, index=1)

#     # Format header
#     sheet.format(
#         "A1:F1",
#         {
#             "textFormat": {
#                 "bold": True,
#             }
#         },
#     )


# def save_user(member, first_name, last_name, email):
#     print("Opening sheet...")
#     sheet = get_sheet()

#     print("Ensuring header...")
#     ensure_header(sheet)

#     print("Appending row...")
#     sheet.append_row(
#         [
#             datetime.utcnow().isoformat(),
#             str(member.id),
#             member.name,
#             first_name,
#             last_name,
#             email,
#         ]
#     )

#     print("Row appended successfully")

import os
import json
from pathlib import Path
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# BASE_DIR = Path(__file__).resolve().parent.parent
# CREDS_FILE = BASE_DIR / "config" / "google_service_account.json"

# if not CREDS_FILE.exists():
#     raise FileNotFoundError(f"Google creds not found at {CREDS_FILE}")

CREDS_JSON = os.getenv("GOOGLE_CREDS_JSON")
if not CREDS_JSON:
    raise RuntimeError("GOOGLE_CREDS_JSON is not set")

SPREADSHEET_ID = "1pT2jbO4BjNMLXM6QiQ_WYgUAPuQhqpm48ghFtOKQufM"
SHEET_NAME = "Verifications"

HEADERS = [
    "Timestamp",
    "Discord ID",
    "Discord Username",
    "First Name",
    "Last Name",
    "Email",
]


def get_sheet():
    # creds = Credentials.from_service_account_file(
    #     CREDS_FILE,
    #     scopes=SCOPES,
    # )
    creds_info = json.loads(CREDS_JSON)
    creds = Credentials.from_service_account_info(creds_info, scopes=SCOPES)
    # client = gspread.authorize(creds)
    client = gspread.authorize(creds)
    return client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)


def ensure_header(sheet):
    try:
        first_row = sheet.row_values(1)
    except Exception:
        first_row = []

    if first_row == HEADERS:
        return

    sheet.insert_row(HEADERS, index=1)
    sheet.format("A1:F1", {"textFormat": {"bold": True}})


def save_user(member, first_name, last_name, email):
    sheet = get_sheet()
    ensure_header(sheet)

    sheet.append_row(
        [
            datetime.utcnow().isoformat(),
            str(member.id),
            member.name,
            first_name,
            last_name,
            email,
        ]
    )
