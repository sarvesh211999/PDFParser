import PyPDF2
import nltk
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


filePath = './Sample/Resume for SVB.pdf'
extension = filePath.lower().endswith(('.docx', '.doc'))
text  = ""
if extension == False:
    pdfObject = open(filePath,'rb')
    pdfReader = PyPDF2.PdfFileReader(pdfObject)

    for i in range(0,pdfReader.numPages):
    	pageObj = pdfReader.getPage(0)
    	text += pageObj.extractText()

    text = " ".join(text.replace(u"\xa0", " ").strip().split())

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



if text == "":
    if extension == False:
        text = convertPDFToText(filePath)
    else:
        text = convertDocxToText(filePath)

print(text)

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
print ("Name : " + name)

# print(text)

######################################################################
#mobile

def cc(s):
    return (''.join(t) for t in itertools.product(*zip(s.lower(), s.upper())))
mobile = ""
for item in mystring.split("\n"):
  if "token" in item:
     print item.strip()
match_mobile = re.search(r'((?:\(?\+91\)?)?\d{9})',text)
#handling the cases when mobile number is not given
if(match_mobile != None):
    mobile = match_mobile.group(0)
print ("Mobile : " +  mobile)