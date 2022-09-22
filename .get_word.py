import re
with open('data.txt','r') as file:
    s = file.read()
    result = re.findall('\(.*?\)', s)
    print(set(result))
   