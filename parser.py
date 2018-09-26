import PyPDF2
import nltk, os, subprocess, code, glob, re, traceback, sys, inspect
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO
from docx import Document
import re
import itertools
#open the file

pdf_files = glob.glob("./Sample/*.pdf")

# filePath = './Sample/PulkitGera.pdf'

def getText(path):
	text = ""
	if extension == False:
	    pdfObject = open(path,'rb')
	    pdfReader = PyPDF2.PdfFileReader(pdfObject)

	    for i in range(0,pdfReader.numPages):
	    	pageObj = pdfReader.getPage(0)
	    	text += pageObj.extractText()

	    text = " ".join(text.replace(u"\xa0", " ").strip().split())
	return text

def convertPDFToText(path):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    fp = open(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos=set()
    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)
    fp.close()
    device.close()
    string = retstr.getvalue()
    retstr.close()
    return string

def convertDocxToText(path):
    document = Document(path)
    return "\n".join([para.text for para in document.paragraphs])

def getName(text):
		tokens = word_tokenize(text)
		# print(tokens)
		# print("--------------------------------------------")
		punctuations = ['(',')',';',':','[',']',',']
		stop_words = stopwords.words('english')

		# print(stop_words)
		# print("--------------------------------------------")
		filtered = [i for i in tokens if not i in stop_words]
		# print(filtered)
		# print("--------------------------------------------")

		name  = str(filtered[0])+' ' +str(filtered[1])
		return name
	
def cc(s):
    return (''.join(t) for t in itertools.product(*zip(s.lower(), s.upper())))

def getMobile(text):
		r = re.compile(r'([+(]?\d+[)\-]?[ \t\r\f\v]*[(]?\d{2,}[()\-]?[ \t\r\f\v]*\d{2,}[()\-]?[ \t\r\f\v]*\d*[ \t\r\f\v]*\d*[ \t\r\f\v]*)')
		phone_numbers = r.findall(text)
		return [re.sub(r'\D', '', number) for number in phone_numbers]

def getEmail(text):

		email = ""
		match_mail = re.search(r'[\w\.-]+@[\w\.-]+', text)
		#handling the cases when mobile number is not given
		if(match_mail != None):
		    email = match_mail.group(0)
		return email


for i in pdf_files:
	print(i)
	extension = i.lower().endswith(('.docx'))
	text  = ""
	filePath = i
	text = getText(filePath)
	if text == "":
	    if extension == False:
	        text = convertPDFToText(filePath)
	    else:
	        text = convertDocxToText(filePath)

	print(getMobile(text))
	print(getEmail(text))
  
