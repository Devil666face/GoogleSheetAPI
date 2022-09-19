from multiprocessing import context
from docxtpl import DocxTemplate

class DocumentController:
    exam_tag = ['ЕГЭ','ОГЭ','основной государственный экзамен','основного государственного экзамена','экзамен','экзамена']
    def __init__(self, data):
        self.data = data
        # for i,cell in enumerate(self.data):
        #     print(i,cell,'\n')

    def make_document(self):
        if self.what_document_type(self.data[4]):
            self.make_document_for_exam()
        else:
            self.make_other_document()

    def what_document_type(self, event_name:str):
        for tag in self.exam_tag:
            if str(event_name).find(tag)!=-1:
                return True
        return False

    def make_document_for_exam(self):
        print('Make document for exam')
        document = Modyfier('templates/exam_template.docx',self.data)

    def make_other_document(self):
        print('Make other document')
        document = Modyfier('templates/other_template.docx',self.data)


class Modyfier:
    def __init__(self, template_name,data):
        self.data = data
        template = DocxTemplate(template_name)
        
        teacher_dict={}
        teacher_dict['cols']=[' ',self.data[3],'учитель']
        student_dict = self.make_student_list(self.data[12])

        student_dict.insert(0,teacher_dict)

        context = {
            'place':self.data[4],
            'date':self.data[5],
            'where':self.data[10],
            'starttime':self.data[6],
            'finishdate':self.data[7],
            'finishtime':self.data[8],
            'tbl_contents':student_dict,
            'mainteacher':self.data[3],
            'secondteacher':self.data
        }
        template.render(context)
        template.save('dynamic_table.docx')

    def make_student_list(self, data_in_one_cell:str):
        student_list = []
        for number,line in enumerate(data_in_one_cell.split('\n')):
            try:
                # print(line)
                name = str(line.split(',')[0]).split('.')[1]
                classmate = line.split(',')[2]
                line_dict = {}
                line_dict['cols']=[f'{number+1}',name,f'обучающийся {classmate}']
                student_list.append(line_dict)
            except Exception as ex:
                pass
        print(student_list)
        return student_list

# tpl = DocxTemplate('ОргПриказ - вариант 1.docx')

# context = {
# 'tbl_contents': [
#     {'cols': ['banana', 'capsicum', 'pyrite', 'taxi']},
#     {'cols': ['apple', 'tomato', 'cinnabar', 'doubledecker']},
#     {'cols': ['guava', 'cucumber', 'aventurine', 'card']},
#     ]
# }

# tpl.render(context)
# tpl.save('dynamic_table.docx')


# from docxtpl import DocxTemplate
# tpl = DocxTemplate('ОргПриказ - вариант 1.docx')

# context = {
# 'col_labels' : ['fruit', 'vegetable', 'stone', 'thing'],
# 'tbl_contents': [
#     {'label': 'yellow', 'cols': ['banana', 'capsicum', 'pyrite', 'taxi']},
#     {'label': 'red', 'cols': ['apple', 'tomato', 'cinnabar', 'doubledecker']},
#     {'label': 'green', 'cols': ['guava', 'cucumber', 'aventurine', 'card']},
#     ]
# }

# tpl.render(context)
# tpl.save('dynamic_table.docx')