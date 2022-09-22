
import os.path
import datetime
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from database import Database
from document import DocumentController

DEBUG_MODE=False

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
            self.values = result.get('values', [])[1:]
            if not self.values:
                return False

            last_line_index, last_date_value = self.find_last_date_line()
            print(last_line_index, last_date_value, self.database.get_last_record())

            if self.database.get_last_record()!=last_date_value or DEBUG_MODE:
                self.database.update_last_record(last_date_value)
                return self.create_doc(last_line_index)
            else:
                print(f'Its not new record {last_date_value}')
                return False

        except HttpError as err:
            print(err)

    def create_doc(self, last_line_index):
        last_line = self.values[last_line_index]
        if self.organization_check(last_line[2]):
            return(last_line)
        else:
            return False
    
    def find_last_date_line(self):
        # for date_value in self.values:
        date_dict = {index:date_value[0] for index, date_value in enumerate(self.values)}
        # print(self.date_dict)
        ordered_data = sorted(date_dict.items(), key = lambda x:datetime.strptime(x[1], "%d.%m.%Y %H:%M:%S"), reverse=True)
        # print(ordered_data[0][0],ordered_data[0][1])
        return ordered_data[0][0],ordered_data[0][1]
        

    def organization_check(self, value):
        if DEBUG_MODE:
            return True
        if str(value).find('№10 (уд. Анны Ахматовой, д.18) - школа')!=-1:
            return True
        if str(value).find('детский сад')!=-1:
            return True
        return False

def make_document():
    API = SheetAPI(Database())
    last_line = API.gat_values_from_sheet()
    if not last_line:
        return False
    replacer = DocumentController(last_line)
    doc_name = replacer.make_document()
    return doc_name


    # start_bot()
    # print(make_document())
    # loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(loop)
    # asyncio.run(start_polling())
