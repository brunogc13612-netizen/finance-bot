from google.oauth2 import service_account
from googleapiclient.discovery import build
import os
import json

# 🔐 pega credenciais do Render
credenciais_json = os.getenv("GOOGLE_CREDENTIALS")

if not credenciais_json:
    raise Exception("GOOGLE_CREDENTIALS não configurado")

credenciais_dict = json.loads(credenciais_json)

creds = service_account.Credentials.from_service_account_info(
    credenciais_dict,
    scopes=["https://www.googleapis.com/auth/spreadsheets"]
)

service = build("sheets", "v4", credentials=creds)

SHEET_ID = "1exQDyQurJtmhNlPb6sNlUIASSZG3fgGkr1icXL-T7e8"


def salvar_no_sheets(dados):
    values = [[
        dados.get("data"),
        dados.get("pessoa"),
        dados.get("categoria"),
        dados.get("descricao"),
        dados.get("valor")
    ]]

    service.spreadsheets().values().append(
        spreadsheetId=SHEET_ID,
        range="A:E",
        valueInputOption="RAW",
        body={"values": values}
    ).execute()


def ler_gastos():
    result = service.spreadsheets().values().get(
        spreadsheetId=SHEET_ID,
        range="A:E"
    ).execute()

    return result.get("values", [])
