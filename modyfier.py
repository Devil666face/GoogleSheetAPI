import re
from docxtpl import DocxTemplate
from collections import Counter
from morph import Morph


class Modyfier:
    def __init__(self, template_name,data):
        self.data = data
        self.template_name = template_name
        # template_name = 'templates/exam_template.docx'

    def save(self):
        template = DocxTemplate(self.template_name)
        
        teacher_list = self.make_teacher_list(self.data[3],self.data[13])
        student_list = self.make_student_list(self.data[12])
        print(teacher_list)
        tbl_contents = [*teacher_list,*student_list]
        context = {
            'place':self.get_place(self.data[4]),
            'date':self.data[5],
            'where':self.data[10],
            'starttime':self.get_normal_time(self.data[6]),
            'finishdate':self.data[7],
            'finishtime':self.get_normal_time(self.data[8]),
            'tbl_contents':tbl_contents,
            'mainteacher':Morph(self.data[3],2),
            'secondteacher':Morph(self.get_second_teacher(teacher_list),2),
            'metoditer':self.get_metoditier(student_list),
            'teacherlist_lessons':Morph(self.get_teacher_list(teacher_list),1),
            'teacherlist_visit':Morph(self.get_teacher_list(teacher_list),1),
            'teacherlist_pay':Morph(self.get_teacher_list(teacher_list),1),
            'teacherlist':self.get_teacher_list(teacher_list),
        }
        template.render(context)
        template.save(f'{str(self.data[4]).strip()}.docx')
        return (f'{str(self.data[4]).strip()}.docx')

    def get_place(self, place:str):
        replace_list = ['О посещении','посещение','Посещение']
        for word in replace_list:
            if place.find(word)!=-1:
                return place.replace(word,'')
        return place

    def get_teacher_list(self, teacher_list):
        return ", ".join(teacher['cols'][1] for teacher in teacher_list)
        # print(s)
        # for teacher in teacher_list:
        #     teacher['cols'][1]

    def get_metoditier(self, student_list):
        # print(student_list)
        # classmate = student_list[0]['cols'][2]
        number_list = []
        for classmate in student_list:
            s = [int(s) for s in re.findall(r'-?\d+\.?\d*', classmate['cols'][2])]
            try:
                number_list.append(s[0])
            except:
                pass
        if int(Counter(number_list).most_common(1)[0][0])<=4:
            return 'Н.Н. Рыбаковой'
        else:
            return 'Е.В. Велесовой'
        # return 'Н.Н. Рыбаковой' if int(Counter(number_list).most_common(1)[0][0])<=4 else 'Е.В. Велесовой'

    def get_second_teacher(self, teacher_list):
        if len(teacher_list)==1:
            print(teacher_list[0]['cols'][1])
            return teacher_list[0]['cols'][1]
        else:
            print(teacher_list[1]['cols'][1])
            return teacher_list[1]['cols'][1]

    def make_teacher_list(self, mainteacher_line, otherteacher_line):

        def make_main_teacher(mainteacher_line):
            teacher_dict={}
            teacher_dict['cols']=[' ',mainteacher_line,'учитель']
            # print(teacher_dict)
            return [teacher_dict]

        def make_other_teacher(mainteacher_line, otherteacher_line):
            other_teacher_list = []
            splited_otherteacher_line = []
            print(re.findall(r'\w+',otherteacher_line))
            for word in re.findall(r'\w+',otherteacher_line):
                if not word.isnumeric():
                    splited_otherteacher_line.append(word)
            print(splited_otherteacher_line)
            step = 4
            if len(splited_otherteacher_line)%3==0:
                step = 3
            for index in range(0,len(splited_otherteacher_line), step):
                try:
                    teacher_name = f'{splited_otherteacher_line[index]} {splited_otherteacher_line[index+1]} {splited_otherteacher_line[index+2]}'
                    other_teacher_dict = {}
                    # print(teacher_name)
                    if mainteacher_line.strip()!=teacher_name.strip():
                        other_teacher_dict['cols']=[' ',teacher_name,'учитель']
                        other_teacher_list.append(other_teacher_dict)
                except:
                    pass
            return other_teacher_list

        teacher_list = []
        teacher_list= [*make_main_teacher(mainteacher_line),*make_other_teacher(mainteacher_line,otherteacher_line)]
        # print(teacher_list)
        return teacher_list

        
    def make_student_list(self, data_in_one_cell:str):
        student_list = []
        number = 1
        for line in data_in_one_cell.split('\n'):
            try:
                if len(line)==0:
                    raise Exception
                name = self.get_student_name(line)
                if not name:
                    raise Exception
                
                classmate = self.get_student_classmate(line)
                line_dict = {}
                line_dict['cols']=[f'{number}',name,f'обучающийся {classmate}']
                student_list.append(line_dict)
                number+=1
            except Exception as ex:
                pass
        # print(student_list)
        return student_list

    def get_normal_time(self, time:str):
        return f'{time.split(":")[0]}:{time.split(":")[1]}'

    def get_student_name(self, student_line:str):
        # print(student_line)
        splited_line = re.findall(r'\w+',student_line)
        # print(splited_line)
        if len(splited_line)<=5:
            return False
        if len(splited_line)==11 or str(splited_line[4]).isnumeric():
            # print(f'{splited_line[1]} {splited_line[2]} {splited_line[3]}')
            return f'{splited_line[1]} {splited_line[2]} {splited_line[3]}'
        elif len(splited_line)>11:
            # print(f'{splited_line[1]} {splited_line[2]} {splited_line[3]} {splited_line[4]}')
            return f'{splited_line[1]} {splited_line[2]} {splited_line[3]} {splited_line[4]}'

    def get_student_classmate(self, student_line:str):
        splited_line = re.findall(r'\w+',student_line)
        # print(splited_line)
        if splited_line[7]=='обучающийся':
            return splited_line[8]
        elif len(splited_line)==11 or str(splited_line[4]).isnumeric():
            return splited_line[7]
        elif len(splited_line)>11:
            return splited_line[8]