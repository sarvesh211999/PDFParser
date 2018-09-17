import PyPDF2
import nltk

pdfObject = open('./Sample/Chandraprakash-Soni007.pdf','rb')
pdfReader = PyPDF2.PdfFileReader(pdfObject)

pageObj = pdfReader.getPage(0) 
text = ""
for i in range(pdfReader.numPages):
	pageObj = pdfReader.getPage(0)
	text += pageObj.extractText()

if text != "":
   text = text.replace('\n','')

grammer

print(text)