import docx2txt

def readDOCX(name):
    text = docx2txt.process(name)
    return text