from googleapiclient.discovery import build
from google.oauth2 import service_account

from src.models import Report


def _map_data_object_to_table_row(data: Report):
    services = '' if data.services is None else ', '.join(data.services)
    res = [data.provider_value, data.region_value, data.url, data.comment_value, data.status, data.time,
           _map_is_unknown(data.is_vpn_used), _map_is_unknown(data.vpn_provider), _map_is_unknown(data.vpn_protocol),
           _map_is_unknown(services)]
    return [res]


def _map_is_unknown(x):
    return 'Неизвестно' if x is None else x


class GoogleSheetStorageAdapter:
    def __init__(self, spreadsheet_id, range_name, service_account_file='credentials/service_account.json'):
        self.service_account_file = service_account_file
        self.spreadsheet_id = spreadsheet_id
        self.range_name = range_name
        self.sheets_service = self._create_sheets_service()

    def _create_sheets_service(self):
        creds = service_account.Credentials.from_service_account_file(
            self.service_account_file,
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        service = build('sheets', 'v4', credentials=creds)
        return service

    def insert(self, data: Report):
        values = _map_data_object_to_table_row(data)
        request = self.sheets_service.spreadsheets().values().append(
            spreadsheetId=self.spreadsheet_id,
            range=self.range_name,
            valueInputOption='RAW',
            body={'values': values},
            insertDataOption='INSERT_ROWS'
        )
        response = request.execute()
        return response
