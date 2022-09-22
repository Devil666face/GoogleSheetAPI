from modyfier import Modyfier

class DocumentController:
    exam_tag = ['ЕГЭ','ОГЭ','основной государственный экзамен','основного государственного экзамена','экзамен','экзамена']
    def __init__(self, data):
        self.data = data
        # for i,cell in enumerate(self.data):
        #     print(i,cell,'\n')

    def generate_document(self):
        if self.what_document_type(self.data[4]):
            return self.make_document_for_exam()
        else:
            return self.make_other_document()

    def what_document_type(self, event_name:str):
        for tag in self.exam_tag:
            if str(event_name).find(tag)!=-1:
                return True
        return False

    def make_document_for_exam(self):
        print('Make document for exam')
        document = Modyfier('templates/exam_template.docx',self.data)
        doc_name = document.save()
        return doc_name

    def make_other_document(self):
        print('Make other document')
        document = Modyfier('templates/other_template.docx',self.data)
        doc_name = document.save()
        return doc_name




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