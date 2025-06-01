#Импортируем необходимые модули
from PyPDF2 import PdfReader as pd

def readPDF(name):
    pdfText = ""
    with open(name, 'rb') as pdf_file:
        pdf_open_reader = pd(pdf_file)
        pdfPages = len(pdf_open_reader.pages)

        for page in range(pdfPages):
            if len(pdfText) <= 2048:
                page_obj = pdf_open_reader.pages[page]
                pdfText += page_obj.extract_text()
    return pdfText  # Возвращаем строку, а не список