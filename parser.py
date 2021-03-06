import numpy as np
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
import csv
import pickle
from wand.image import Image as Img
from PIL import Image
import pyocr
import pyocr.builders
import io
import pytesseract
import datefinder
import unicodedata
# ################## model #########################
# nlp = spacy.load('./NER')
# ##################################################
# #open the file

pdf_files = glob.glob("./Sample/*.pdf")
docx_files = glob.glob("./Sample/*.docx")
scan = []
for i in pdf_files:
	scan.append(i)
for i in docx_files:
	scan.append(i)

def preprocess(self, document):
        '''
        Information Extraction: Preprocess a document with the necessary POS tagging.
        Returns three lists, one with tokens, one with POS tagged lines, one with POS tagged sentences.
        Modules required: nltk
        '''
        try:
            # Try to get rid of special characters
            try:
                document = document.decode('ascii', 'ignore')
            except:
                document = document.encode('ascii', 'ignore')
            # Newlines are one element of structure in the data
            # Helps limit the context and breaks up the data as is intended in resumes - i.e., into points
            lines = [el.strip() for el in document.split("\n") if len(el) > 0]  # Splitting on the basis of newlines 
            lines = [nltk.word_tokenize(el) for el in lines]    # Tokenize the individual lines
            lines = [nltk.pos_tag(el) for el in lines]  # Tag them
            # Below approach is slightly different because it splits sentences not just on the basis of newlines, but also full stops 
            # - (barring abbreviations etc.)
            # But it fails miserably at predicting names, so currently using it only for tokenization of the whole document
            sentences = nltk.sent_tokenize(document)    # Split/Tokenize into sentences (List of strings)
            sentences = [nltk.word_tokenize(sent) for sent in sentences]    # Split/Tokenize sentences into words (List of lists of strings)
            tokens = sentences
            sentences = [nltk.pos_tag(sent) for sent in sentences]    # Tag the tokens - list of lists of tuples - each tuple is (<word>, <tag>)
            # Next 4 lines convert tokens from a list of list of strings to a list of strings; basically stitches them together
            dummy = []
            for el in tokens:
                dummy += el
            tokens = dummy
            # tokens - words extracted from the doc, lines - split only based on newlines (may have more than one sentence)
            # sentences - split on the basis of rules of grammar
            return tokens, lines, sentences
        except Exception as e:
            print (e) 

def tokenize(self, inputString):
    try:
        self.tokens, self.lines, self.sentences = self.preprocess(inputString)
        return self.tokens, self.lines, self.sentences
    except Exception as e:
        print (e)

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

def convertPDFToOCR(path):
	os.system("rm sample_scan*")
	text = ""
	pdfObject = open(path,'rb')
	pdfReader = PyPDF2.PdfFileReader(pdfObject)
	pages = pdfReader.numPages
	with Img(filename=path, resolution=300) as img:
		img.compression_quality = 0
		img.save(filename="sample_scan.jpg")

	if pages == 1:
		text = pytesseract.image_to_string(Image.open('sample_scan.jpg'))
	else:
		for i in range(0,pages):
			temp = pytesseract.image_to_string(Image.open('sample_scan-' +str(i) +'.jpg'))
			text +=temp

	return text

def getName(text):
		tokens = word_tokenize(text)
		# print(tokens)
		# print("--------------------------------------------")

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
		# r = re.compile(r'([+(]?\d+[)\-]?[ \t\r\f\v]*[(]?\d{2,}[()\-]?[ \t\r\f\v]*\d{2,}[()\-]?[ \t\r\f\v]*\d*[ \t\r\f\v]*\d*[ \t\r\f\v]*)')
		# r = re.compile('?:\s+|)((0|(?:(\+|)91))(?:\s|-)*(?:(?:\d(?:\s|-)*\d{9})|(?:\d{2}(?:\s|-)*\d{8})|(?:\d{3}(?:\s|-)*\d{7}))|\d{10})(?:\s+|))')
		# regex = '(?:\s+|)((0|(?:(\+|)91))(?:\s|-)*(?:(?:\d(?:\s|-)*\d{9})|(?:\d{2}(?:\s|-)*\d{8})|(?:\d{3}(?:\s|-)*\d{7}))|\d{10})(?:\s+|)'
		phone_numbers = re.search('(?:\s+|)((0|(?:(\+|)91))(?:\s|-)*(?:(?:\d(?:\s|-)*\d{9})|(?:\d{2}(?:\s|-)*\d{8})|(?:\d{3}(?:\s|-)*\d{7}))|\d{10})(?:\s+|)',text)
		# phone_numbers = r.findall(text)
		# phone_numbers = [re.sub(r'[,.]', '', el) for el in phone_numbers if len(re.sub(r'[()\-.,\s+]', '', el))>6]
		# phone_numbers = [re.sub(r'\D$', '', el).strip() for el in phone_numbers]
		# phone_numbers = [el for el in phone_numbers if len(re.sub(r'\D','',el)) <= 15]
		# return [re.sub(r'\D', '', number) for number in phone_numbers]
		if phone_numbers != None:
			return phone_numbers.group(0)
		else:
			return None

def getMobileTry2(text):
		pattern = re.compile(r'\+?\d[\d -]{8,12}\d')
		phone_numbers = pattern.findall(text)
		return [re.sub(r'\D','',number) for number in phone_numbers]

def getEmail(text):

		email = ""
		match_mail = re.search(r'[\w\.-]+@[\w\.-]+', text)
		if(match_mail != None):
		    email = match_mail.group(0)
		return email

def getSkills(text):
	programming = ["assembly", "bash", " c " "c++", "c#", "coffeescript", "emacs lisp",
         "go!", "groovy", "haskell", "java", "javascript", "matlab", "max MSP", "objective c", 
         "perl", "php","html", "xml", "css", "processing", "python", "ruby", "sml", "swift", 
         "latex" "unity", "unix" "visual basic" "wolfram language", "xquery", "sql", "node.js", 
         "scala", "kdb", "jquery", "mongodb"]

mobile_array=[]
langfile = open('language.txt', 'r')
s= []
for lang in langfile:
	s.append(lang.lower().replace(' ','').replace('\n','').replace('"',''))

def getKnownLanguage(text):
	skills = set()
	knownSet = nltk.word_tokenize(text.lower())
	for word in knownSet:
		if word in s:
			skills.add(word)

	return skills

def getDateOfBirth(text):
	dobRegex =  re.search(r'date.*of.*.birth.*',text, re.IGNORECASE)
	if dobRegex is None:
		return None

	temp = text[dobRegex.span()[0]:-1]
	temp = temp.replace(".","").replace(",","").replace("nd","").replace("th","")
	matches = datefinder.find_dates(temp)
	datesList = []

	for i in matches:
		datesList.append([i,i.year])

	minDate = datesList[0][0]
	minYear = None

	for i in range(len(datesList)):
		if minYear is None and datesList[i][1] > 1960:
			minYear = datesList[i][1]
			minDate = datesList[i][0]
		elif datesList[i][1] > 1960 and datesList[i][1] < minYear :
			minYear = datesList[i][1]
			minDate = datesList[i][0]

	return minDate

def getAddress(text):
	tokens = word_tokenize(text)
	stop_words = stopwords.words('english')
	filtered = [i for i in tokens if not i in stop_words]
	sentences = nltk.sent_tokenize(text)
	sentences = [nltk.word_tokenize(sent) for sent in sentences]
	sentences = [nltk.pos_tag(sent) for sent in sentences]
	print(sentences)

for i in scan:
	print(i)

	extension = i.lower().endswith(('.docx'))
	text  = ""
	filePath = i
	filePath = "./Sample/PulkitGera.pdf"
	if extension == False:
		text = convertPDFToText(filePath)
	else:
		text = convertDocxToText(filePath)

	getAddress(text)
	quit()

	
	# text = "MEGAVAT NAGENDRA PRASAD\nEMAIL: megavatnagendra@gmail.com Mobile: 9542104922\nCAREER OBJECTIVE\nTo work in a firm with a professional work driven environment where I can utilize and apply my\nknowledge, skills which would enable me as a fresh graduate to grow while fulfilling organizational\ngoals.\nACADEMIC CREDENTIALS\nQualification\nBoard/University\nYear\nPerce\nntage\nB.Tech (Computer Science Engineering)\n2013-17\n60\nJawaharlal Nehru Technical\nUniversity- Vizayanagar campus\nIntermediate\nKavitha College\n2013\n81\nHigh School\nALL SAINTS, CHILLAKALLU\n2011\n85\nTECHNICAL SKILLS\nBPM Tools\nProgramming Skills\nDatabase\nOS\nWeb\nIBM BPM 8.5.6\nJava, Python\nMySQL, Oracle\nWindows\nJavaScript, CSS\nPROFESSIONAL EXPERIENCE\nSoftpath technologies ,Hyderabad from Nov 1,2017 - Till date\nPROJECT 1-Application Database Services Process Platform\nEnvironment: IBM BPM 8.5.6, SQL Server.\nDescription: Application database services process platform enable to receive the database\nservice requests from across enterprise and route the requests to appropriate groups for\nfulfillment of request. Process will kick off by creating database service requests and creating\napproval tasks based on approval business rules.\n• Responsibilities:\n• Developed reusable Email Notification service which have been used across the project\n• Develop coach views for approvals tasks.\n Coach Validations and dynamic task assignments.\n•\n•\nEnd to End process testing\nPROJECT 1-DataFlow\nEnvironment: IBM BPM 8.5.6, SQL Server.\nDescription:\nDataflow is a Third Party Organisation which Provides Primary Source Verification\nServices for all types of Background Verification and provides a Report for the Applicants. Initial\nProcess starts from case initiation from many Customer Portals Veriflow,Core Component\ndeveloped in IBM BPM,Case is routed from based on the type of Verification. Based on the\nVerification Report is generated and Produced to the Applicant.\nResponsibilities:\n• Developed Human Services for a Component\n•\nImplementation of Validations and DataBase Operations.\nEnd to End Testing with different Test Scenarios.\n• Involved in enhancements of General System Services.\nINTERPERSONAL SKILL\nAbility to rapidly build relationship and set up trust.\nConfident and Determined\nAbility to cope up with different situations.\n*\nCO-/EXTRA -CURRICULAR ACTIVITIE\nExecutive Member of Tech Feast.\nExecutive Member of Event Organizing Committee in JNT University\n•\nPERSONAL PROFILE\nName:\nGender:\nDate of birth:\nMarital status:\nNationality:\nFather's Name:\nLinguistic Ability:\nAddress:\nNAGENDRA PRASAD MEGAVAT\nMale\n30-10-1996\nSingle\nIndian\nM. BALAJI\nEnglish, Telugu\nFlat No 303, SM Brundavanam Residency, Pragati\nNagar, Hyderabad-50072\n Declaration: I hereby declare that all the details furnished above are true to the best of my\nknowledge and belief.\nNagendra Prasad\n"
	# print(text)
	print("Name :" + getName(text))
	print("Email : " + getEmail(text))
	if getMobile(text) is not None:
		print("Mobile : " + getMobile(text).replace("\n","").replace(" ","").replace(chr(160),""))
	else:
		print("None")

	print("Language :",list(getKnownLanguage(text)))
	print("DOB :", getDateOfBirth(text))

	mobile_array.append(getMobile(text))

	# print(text)


for i in range(0,len(mobile_array)):
	if mobile_array[i] is not None:
		mobile_array[i]=mobile_array[i].replace("\n","").replace(" ","").replace(chr(160),"")



