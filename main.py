import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from database import Database
from document import DocumentController

class SheetAPI:
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    SAMPLE_SPREADSHEET_ID = '18czznNPJKfFsAFNrAgL_Nvxgc_Lea4-ghwMNaHt-3aM'
    SAMPLE_RANGE_NAME = 'Ответы на форму (1)'
    
    def __init__(self, database:Database):
        self.creds = None
        self.database = database
        if os.path.exists('token.json'):
            self.creds = Credentials.from_authorized_user_file('token.json', self.SCOPES)
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', self.SCOPES)
                # Добавляем 8080 порт сюда и в разрешенные URI в OAuth googl-a http://localhost:8080 https://localhost:8080/
                self.creds = flow.run_local_server(port=8080)
            with open('token.json', 'w') as token:
                token.write(self.creds.to_json())

    def gat_values_from_sheet(self):
        '''self.values have all data from table'''
        try:
            service = build('sheets', 'v4', credentials=self.creds)
            sheet = service.spreadsheets()
            result = sheet.values().get(spreadsheetId=self.SAMPLE_SPREADSHEET_ID,range=self.SAMPLE_RANGE_NAME).execute()
            self.values = result.get('values', [])
            if not self.values:
                return False

            if self.database.get_last_record()!=self.values[-1][0]:
                self.database.update_last_record(self.values[-1][0])
                return self.create_doc()
            else:
                print('Its not new record')
                return False

        except HttpError as err:
            print(err)

    def create_doc(self):
        last_line = self.values[-1]
        if self.organization_check(last_line[2]):
            return(last_line)
        else:
            return False
        
    def organization_check(self, value):
        if str(value).find('№10 (уд. Анны Ахматовой, д.18) - школа')!=-1:
            return True
        if str(value).find('детский сад')!=-1:
            return True
        return False

def main():
    API = SheetAPI(Database())
    last_line = API.gat_values_from_sheet()
    if not last_line:
        return False
    replacer = DocumentController(last_line)
    replacer.make_document()

if __name__ == '__main__':
    main()