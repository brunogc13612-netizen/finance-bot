from google.oauth2 import service_account
from googleapiclient.discovery import build
import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_PATH = os.path.join(BASE_DIR, "credentials.json")

def salvar_no_sheets(dados):
    
    cred_json = json.loads(os.getenv("GOOGLE_CREDENTIALS"))

    creds = service_account.Credentials.from_service_account_info(
    cred_json,
    scopes=["https://www.googleapis.com/auth/spreadsheets"]
)

    service = build("sheets", "v4", credentials=creds)

    values = [[
        dados.get("data"),
        dados.get("pessoa"),
        dados.get("categoria"),
        dados.get("descricao"),
        dados.get("valor")
    ]]

    service.spreadsheets().values().append(
        spreadsheetId="1exQDyQurJtmhNlPb6sNlUIASSZG3fgGkr1icXL-T7e8",
        range="A:E",
        valueInputOption="RAW",
        body={"values": values}
    ).execute()

def ler_gastos():
    creds = service_account.Credentials.from_service_account_file(
        CREDENTIALS_PATH,
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )

    service = build("sheets", "v4", credentials=creds)

    result = service.spreadsheets().values().get(
        spreadsheetId="1exQDyQurJtmhNlPb6sNlUIASSZG3fgGkr1icXL-T7e8",
        range="A:E"
    ).execute()

    return result.get("values", [])