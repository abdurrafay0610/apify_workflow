import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gspread.exceptions import WorksheetNotFound
from typing import List

def authenticate_sheets_only(creds_file: str):
    scope = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file, scope)
    return gspread.authorize(creds)

def append_or_create_tab_by_id(sheet_name: str, rows: List[List]) -> None:

    """
    Function Definition: This function will receive the sheet name and the value to add to it
    If the sheet does not exist, it will create it and add the value to it.
    Also the values that will arrive will have the headers with them, so if the sheet is created the headers will be added as well.
    Otherwise the headers will be ignored and only the values will be added.
    :param sheet_name:
    :param rows:
    :return:
    """

    client = authenticate_sheets_only("credentials.json")
    spreadsheet_id = "1wZK1Gt8160w_eAie8rTHR_PxZztpwN8U-8grhAO4izc"

    ss = client.open_by_key(spreadsheet_id)
    try:
        ws = ss.worksheet(sheet_name)
    except WorksheetNotFound:
        ws = ss.add_worksheet(title=sheet_name, rows=100, cols=20)
        ws.append_row(rows[0])
    if rows:
        ws.append_row(rows[1])