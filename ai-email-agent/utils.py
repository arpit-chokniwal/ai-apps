import re

def findAllEmailsInString(input_str):
    matches = re.findall(r'[\w\.-]+@[\w\.-]+', input_str)
    return matches

