import os
import xlsxwriter

from parser import SheetAPI
from database import Database
from modyfier import Modyfier
from collections import Counter
from fuzzywuzzy import fuzz

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class TeacherSheatAPI:
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    SAMPLE_SPREADSHEET_ID = '1JkBjOGajQ52_nGrWFqFCEB2fuVcmOOuQI6xaNyN3NHc'
    SAMPLE_RANGE_NAME = 'здание 10 АА18'

    def __init__(self):
        self.creds = None
        if os.path.exists('token_teachers.json'):
            self.creds = Credentials.from_authorized_user_file('token_teachers.json', self.SCOPES)
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', self.SCOPES)
                # Добавляем 8080 порт сюда и в разрешенные URI в OAuth googl-a http://localhost:8080 https://localhost:8080/
                self.creds = flow.run_local_server(port=8080)
            with open('token_teachers.json', 'w') as token:
                token.write(self.creds.to_json())

        try:
            service = build('sheets', 'v4', credentials=self.creds)
            sheet = service.spreadsheets()
            result = sheet.values().get(spreadsheetId=self.SAMPLE_SPREADSHEET_ID,range=self.SAMPLE_RANGE_NAME).execute()
            self.values = result.get('values', [])[1:]

        except HttpError as err:
            print(err)
    
    def get_classroom_teachers(self):
        classroom_teachers = list()
        for line in self.values:
            try:
                if line[0]!='' and line[0]!='класс':
                    classroom_teachers.append([line[0],line[2]])
            except Exception as ex:
                # print(f'{ex}\n{line}')
                pass
                
        return classroom_teachers


class MonthReport:
    def __init__(self, month_number:str) -> None:
        self.month_number = month_number
        self.values_for_month = self.get_values_for(month=month_number, organization='№10 (уд. Анны Ахматовой, д.18) - школа')
        self.list_for_record_none_check = self.make_data_for_table(values=self.values_for_month)
        # print(self.list_for_record_none_check)
        self.classroom_teachers = TeacherSheatAPI().get_classroom_teachers()
        self.data_for_record = self.check_classroom_teachers(values_for_record=self.list_for_record_none_check, classroom_teachers=self.classroom_teachers)
        # print(self.data_for_record)

    def get_month_name(self, month_number):
        month = {'1':'январь',
                 '2':'февраль',
                 '3':'март',
                 '4':'апрель',
                 '5':'май',
                 '6':'июнь',
                 '7':'июль',
                 '8':'август',
                 '9':'сентябрь',
                 '10':'октябрь',
                 '11':'ноябрь',
                 '12':'декабрь',}
        return month.get(month_number,month_number)

    def print(self):
        print(self.values_for_month)

    def write(self):
        file_name = f'{self.get_month_name(self.month_number)}.xlsx'
        workbook = xlsxwriter.Workbook(file_name)
        worksheet = workbook.add_worksheet(name=f'{self.get_month_name(self.month_number)}')
        for i,line in enumerate(self.data_for_record):
            for j,cell in enumerate(line):
                worksheet.write(i,j, cell)
        workbook.close()
        return file_name

    def get_values_for(self, month:str, organization:str) -> list:
        '''date = line[5] current_organization = line[2]'''
        values = list()
        for line in SheetAPI(Database()).values:
            if str(line[5]).split('.')[1]==month and str(line[2]).find(organization)!=-1:
                values.append(line)
        return values
    

    def make_data_for_table(self, values:list):
        list_for_record_none_check = list()
        for line in values:
            modyfier = Modyfier('',line)
            # teacher_list = modyfier.get_teacher_list(modyfier.make_teacher_list(line[3],line[13]))
            teacher_list = line[3]
            class_counter, class_count = self.get_class(modyfier.make_student_list(line[12]))
            date_arrive = line[5]
            time_arrive = line[6]
            # print(class_label)
            # for teacher in teacher_list.split(','):
            list_for_record_none_check.append([teacher_list,'нет',date_arrive,time_arrive,class_counter,class_count])
        
        return list_for_record_none_check
                
    def check_classroom_teachers(self, values_for_record, classroom_teachers):

        def s(value):
            return str(value).strip()
        
        for index, line in enumerate(values_for_record):
            teacher_list = line[0]
            class_label = line[4]
            # print(teacher_list, class_label)
            for teacher in teacher_list.split(','):
                
                for classroom_line in classroom_teachers:
                    true_class_label = classroom_line[0]
                    true_class_teacher = classroom_line[1]

                    if s(teacher)==s(true_class_teacher):
                        # Использую нечеткое сравнение. Порог истины 80%
                        if fuzz.ratio(s(class_label),s(true_class_label))>=80:
                            values_for_record[index][1] = 'да'
                            break
                break
        
        return values_for_record

    def get_class(self, class_list):

        def get_most_common(lable_list):
            # counter_class = Counter(class_label)
            # for item in counter_class:
            #     if len(str(item)) > 6:
            #         return counter_class.most_common(1)[0]
            return Counter(class_label).most_common(1)[0][0]

        class_label = list()
        for line in class_list:
            pupil = line.get('cols',None)
            if pupil is not None:
                class_label.append(str(pupil[2]).replace('обучающийся ','').upper())
        return get_most_common(class_label), len(class_list)
        

        