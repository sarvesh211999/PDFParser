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
import spacy
from spacy import displacy
import en_core_web_sm
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


for i in scan:
	print(i)
	extension = i.lower().endswith(('.docx'))
	text  = ""
	filePath = i
	if extension == False:
		text = convertPDFToText(filePath)
	else:
		text = convertDocxToText(filePath)

	print("Name :" + getName(text))
	print("Email : " + getEmail(text))
	if getMobile(text) is not None:
		print("Mobile : " + getMobile(text).replace("\n","").replace(" ","").replace(chr(160),""))
	else:
		print("None")

	print("Language :",list(getKnownLanguage(text)))

	mobile_array.append(getMobile(text))


for i in range(0,len(mobile_array)):
	if mobile_array[i] is not None:
		mobile_array[i]=mobile_array[i].replace("\n","").replace(" ","").replace(chr(160),"")



