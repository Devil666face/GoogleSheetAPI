from petrovich.main import Petrovich   
from petrovich.enums import Case, Gender

class Morph:
    def __init__(self, line, case_id) -> None:
        self.case_id = case_id
        # print(line)
        self.splited_line = line.split()
        # print(self.splited_line)
        self.cased_list = []
        # print(self.splited_line)
        for index in range(0,len(self.splited_line),3):
            try:
                self.cased_list.append(self.get_word([self.splited_line[index+0],self.splited_line[index+1],self.splited_line[index+2]]))
            except Exception as ex:
                # print(ex)
                pass

    def get_word(self, word):
        p = Petrovich()
        # print(word)
        try:
            case_lastname = p.lastname(word[0],self.case_id)
            case_firstname = p.firstname(word[1],self.case_id)
            case_middlename = p.middlename(word[2],self.case_id)
            # print(case_middlename)
            return f'{case_lastname} {case_firstname} {case_middlename}'
        except:
            return f'{word[0]} {word[1]} {word[2]}'
    
    def __str__(self) -> str:
        return " ".join(word for word in self.cased_list)
       
# import re
# import pymorphy2

# class Morph:
#     def __init__(self, line, case_id) -> None:
#         self.case_id = case_id
#         self.splited_line = line.split()
#         self.cased_list = []
#         for word in self.splited_line:
#             if word.istitle():
#                 self.cased_list.append(self.get_word(word, True))
#             else:
#                 self.cased_list.append(self.get_word(word, False))

#     def get_word(self, word, title):
#         morph = pymorphy2.MorphAnalyzer()
#         cases = morph.parse(word.strip())[0]
#         try:
#             # for index,word in enumerate(cases.lexeme):
#             #     print(index,word.word)
#             if title:
#                 return str(cases.lexeme[self.case_id].word).title()
#             return str(cases.lexeme[self.case_id].word)
#         except:
#             return word
        

#     def __str__(self) -> str:
#         return " ".join(word for word in self.cased_list)