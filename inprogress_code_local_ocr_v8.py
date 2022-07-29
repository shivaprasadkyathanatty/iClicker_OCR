# to upload files from local to s3 and mark them public: $aws s3 cp /home/shivaprasad/Downloads/iClicker_OCR/new_code/images/raw_image/ s3://iclicker-ocr/raw_image/ --acl public-read --recursive
''' refer:
https://towardsdatascience.com/getting-started-with-tesseract-part-i-2a6a6b1cf75e
https://www.freecodecamp.org/news/getting-started-with-tesseract-part-ii-f7f9a0899b3f/
'''
# importing libraries
import cv2
import os
import numpy as np
import pytesseract
import mysql.connector
import time
import sys
#from tesserocr import PyTessBaseAPI
import tesserocr
#import boto3
#import botocore
#for reload
import importlib

#import paramiko (not required for local)
#from IPython.core.debugger import Pdb
#ipdb = Pdb()
#ipdb.set_trace()
#connecting to aws
''' (not required for local)
key = paramiko.RSAKey.from_private_key_file("/home/ubuntu/ace-aws1.pem")
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
'''

''' (not required for local)
#connecting to be1 rds
def mysql_be_con():
	cnx = mysql.connector.connect(user='aceuser', password='aceuserbe1',
								  host='docpipe-be1.cxen17t6uhqr.us-east-1.rds.amazonaws.com',
								  database='iclicker_ocr',autocommit=True)
	return cnx
'''
# mysql configurations
config = {
  'user': 'root',
  'password': 'password',
  'host': '127.0.0.1',
  'database': 'sample',
  'raise_on_warnings': True,
  'autocommit':True
}

# setup mysql connection
def mysql_be_con():
	cnx = mysql.connector.connect(**config)
	return cnx

#addressing patterns
def address_pattern(tmp,img_file_name,low_confidence_score_count,high_confidence_score_count,
pA,pB,pC,pD,pE,pF,pG,pH):
	file=img_file_name
	qA=tmp.find(pA)
	qB=tmp.find(pB)
	qC=tmp.find(pC)
	qD=tmp.find(pD)
	qE=tmp.find(pE)
	qF=tmp.find(pF)
	qG=tmp.find(pG)
	qH=tmp.find(pH)

	if qA != -1:
		qApos=tmp.find(pA)
	else:
		qApos="NA"
		qAcont="NULL"
		qcont=tmp[:]

	if qB != -1:
		qBpos=tmp.find(pB)
	else:
		qBpos="NA"
		qBcont="NULL"

	if qC != -1:
		qCpos=tmp.find(pC)
	else:
		qCpos="NA"
		qCcont="NULL"

	if qD != -1:
		qDpos=tmp.find(pD)
	else:
		qDpos="NA"
		qDcont="NULL"

	if qE != -1:
		qEpos=tmp.find(pE)
	else:
		qEpos="NA"
		qEcont="NULL"

	if qF != -1:
		qFpos=tmp.find(pF)
	else:
		qFpos="NA"
		qFcont="NULL"

	if qG != -1:
		qGpos=tmp.find(pG)
	else:
		qGpos="NA"
		qGcont="NULL"

	if qH != -1:
		qHpos=tmp.find(pH)
	else:
		qHpos="NA"
		qHcont="NULL"

	if qHpos!="NA":
		qHcont=tmp[qHpos+4:]

	if qGpos!="NA":
		if qHpos=="NA":
			qGcont=tmp[qGpos+4:]
		else:
			qGcont=tmp[qGpos+4:qHpos]

	if qFpos!="NA":
		if qGpos=="NA":
			qFcont=tmp[qFpos+4:]
		else:
			qFcont=tmp[qFpos+4:qGpos]

	if qEpos!="NA":
		if qFpos=="NA":
			qEcont=tmp[qEpos+4:]
		else:
			qEcont=tmp[qEpos+4:qFpos]

	if qDpos!="NA":
		if qEpos=="NA":
			qDcont=tmp[qDpos+4:]
		else:
			qDcont=tmp[qDpos+4:qEpos]

	if qCpos!="NA":
		if qDpos=="NA":
			qCcont=tmp[qCpos+4:]
		else:
			qCcont=tmp[qCpos+4:qDpos]

	if qBpos!="NA":
		if qCpos=="NA":
			qBcont=tmp[qBpos+4:]
		else:
			qBcont=tmp[qBpos+4:qCpos]

	if qApos!="NA":
		qcont=tmp[:qApos]
		if qBpos=="NA":
			qAcont=tmp[qApos+4:]

		else:
			qAcont=tmp[qApos+4:qBpos]

	lst = []
	lst.extend(strip_print(qcont,qAcont,qBcont,qCcont,qDcont,qEcont,qFcont,qGcont,qHcont))
	insert_data(file,lst[0],lst[1],lst[2],lst[3],lst[4],lst[5],lst[6],lst[7],lst[8],low_confidence_score_count,high_confidence_score_count)
	lst.clear()


# strip space and print on the console
def strip_print(qcont,qAcont,qBcont,qCcont,qDcont,qEcont,qFcont,qGcont,qHcont):
	qcont=qcont.strip()
	qAcont=qAcont.strip()
	qBcont=qBcont.strip()
	qCcont=qCcont.strip()
	qDcont=qDcont.strip()
	qEcont=qEcont.strip()
	qFcont=qFcont.strip()
	qGcont=qGcont.strip()
	qHcont=qHcont.strip()

	print ("Question:\t"+qcont)
	print ("Option 1:\t"+qAcont)
	print ("Option 2:\t"+qBcont)
	print ("Option 3:\t"+qCcont)
	print ("Option 4:\t"+qDcont)
	print ("Option 5:\t"+qEcont)
	print ("Option 6:\t"+qFcont)
	print ("Option 7:\t"+qGcont)
	print ("Option 8:\t"+qHcont)

	return qcont,qAcont,qBcont,qCcont,qDcont,qEcont,qFcont,qGcont,qHcont


# inserting data to table
def insert_data(file,qcont,qAcont,qBcont,qCcont,qDcont,qEcont,qFcont,qGcont,qHcont,low_confidence_score_count,high_confidence_score_count):
	mysqlcon=mysql_be_con()
	cursor=mysqlcon.cursor()
	cursor.execute('insert into iclicker_ocr.iclicker (file,question,optionA,optionB,optionC,optionD,optionE,optionF,optionG,optionH,low_confidence_score_count,high_confidence_score_count) values ("{0}","{1}","{2}","{3}","{4}","{5}","{6}","{7}","{8}","{9}","{10}","{11}");'.format(file,qcont,qAcont,qBcont,qCcont,qDcont,qEcont,qFcont,qGcont,qHcont,low_confidence_score_count,high_confidence_score_count))
	time.sleep(1)
	cursor.close()
	mysqlcon.close()

# removing records from sql table if they produced only one option in sql result or if they produced infrequent values for options
def delete_data(options):
	mysqlcon=mysql_be_con()
	cursor=mysqlcon.cursor()
	for option in options:
		if option[3]== "NULL":
			cursor.execute('delete from iclicker_ocr.iclicker where file="{0}";'.format(option[0]))
		elif option[9]!="NULL" and option[8]=="NULL":
			cursor.execute('delete from iclicker_ocr.iclicker where file="{0}";'.format(option[0]))
		elif option[8]!="NULL" and option[7]=="NULL":
			cursor.execute('delete from iclicker_ocr.iclicker where file="{0}";'.format(option[0]))
		elif option[7]!="NULL" and option[6]=="NULL":
			cursor.execute('delete from iclicker_ocr.iclicker where file="{0}";'.format(option[0]))
		elif option[6]!="NULL" and option[5]=="NULL":
			cursor.execute('delete from iclicker_ocr.iclicker where file="{0}";'.format(option[0]))
		elif option[5]!="NULL" and option[4]=="NULL":
			cursor.execute('delete from iclicker_ocr.iclicker where file="{0}";'.format(option[0]))
		elif option[4]!="NULL" and option[3]=="NULL":
			cursor.execute('delete from iclicker_ocr.iclicker where file="{0}";'.format(option[0]))
		elif option[3]!="NULL" and option[2]=="NULL":
			cursor.execute('delete from iclicker_ocr.iclicker where file="{0}";'.format(option[0]))
		elif option[2]!="NULL" and option[1]=="NULL":
			cursor.execute('delete from iclicker_ocr.iclicker where file="{0}";'.format(option[0]))
		elif option[9]!="" and option[8]=="":
			cursor.execute('delete from iclicker_ocr.iclicker where file="{0}";'.format(option[0]))
		elif option[8]!="" and option[7]=="":
			cursor.execute('delete from iclicker_ocr.iclicker where file="{0}";'.format(option[0]))
		elif option[7]!="" and option[6]=="":
			cursor.execute('delete from iclicker_ocr.iclicker where file="{0}";'.format(option[0]))
		elif option[6]!="" and option[5]=="":
			cursor.execute('delete from iclicker_ocr.iclicker where file="{0}";'.format(option[0]))
		elif option[5]!="" and option[4]=="":
			cursor.execute('delete from iclicker_ocr.iclicker where file="{0}";'.format(option[0]))
		elif option[4]!="" and option[3]=="":
			cursor.execute('delete from iclicker_ocr.iclicker where file="{0}";'.format(option[0]))
		elif option[3]!="" and option[2]=="":
			cursor.execute('delete from iclicker_ocr.iclicker where file="{0}";'.format(option[0]))
		elif option[2]!="" and option[1]=="":
			cursor.execute('delete from iclicker_ocr.iclicker where file="{0}";'.format(option[0]))
	cursor.close()
	mysqlcon.close()

# selecting answer options from table
def get_options():
	mysqlcon=mysql_be_con()
	cursor=mysqlcon.cursor()
	cursor.execute('select * from iclicker_ocr.iclicker;')
	options=cursor.fetchall()
	cursor.close()
	mysqlcon.close()
	return options

# selecting file names from table
def get_file():
	mysqlcon=mysql_be_con()
	cursor=mysqlcon.cursor()
	cursor.execute('select distinct file from iclicker_ocr.iclicker;')
	file_names = cursor.fetchall()
	cursor.close()
	mysqlcon.close()
	return file_names

# find pattern of multiple choice questions and send them for respective functions to parsing
def call_patterns(tmp,img_file_name,low_confidence_score_count,high_confidence_score_count):
	pattern=tmp.find(" A. ")
	if pattern !=-1:
		address_pattern(tmp,img_file_name,low_confidence_score_count,high_confidence_score_count,
		pA=" A. ",pB=" B. ",pC=" C. ",pD=" D. ",pE=" E. ",pF=" F. ",pG=" G. ",pH=" H. ")

	pattern=tmp.find(" a. ")
	if pattern !=-1:
		address_pattern(tmp,img_file_name,low_confidence_score_count,high_confidence_score_count,
		pA=" a. ",pB=" b. ",pC=" c. ",pD=" d. ",pE=" e. ",pF=" f. ",pG=" g. ",pH=" h. ")

	pattern=tmp.find(" A) ")
	if pattern !=-1:
		address_pattern(tmp,img_file_name,low_confidence_score_count,high_confidence_score_count,
		pA=" A) ",pB=" B) ",pC=" C) ",pD=" D) ",pE=" E) ",pF=" F) ",pG=" G) ",pH=" H) ")

	pattern=tmp.find(" a) ")
	if pattern !=-1:
		address_pattern(tmp,img_file_name,low_confidence_score_count,high_confidence_score_count,
		pA=" a) ",pB=" b) ",pC=" c) ",pD=" d) ",pE=" e) ",pF=" f) ",pG=" g) ",pH=" h) ")


# process ocr for each image in raw_image_path_folder
def process_ocr(raw_image_path_folder,formatted_image_path_folder,text_file_path):
	for imge in os.listdir(raw_image_path_folder):
		# retain raw_image_path for str manipulation
		#raw_image_path=imge
		#img=imge
		# Read image using opencv
		raw_image_path = os.path.join(raw_image_path_folder,imge)
		img=cv2.imread(raw_image_path)
		# Rescale the image, if needed. Tesseract works best on images that are 300 dpi, or more.
		img = cv2.resize(img, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)
		# Noise removal
		# Convert to gray
		img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
		# Apply dilation and erosion to remove some noise
		kernel = np.ones((1, 1), np.uint8)
		img = cv2.dilate(img, kernel, iterations=1)
		img = cv2.erode(img, kernel, iterations=1)
		# Apply blur to smooth out the edges
		img = cv2.GaussianBlur(img, (5, 5), 0)
		# Binarization
		# Apply threshold to get image with only b&w (binarization)
		img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
		# Extract the file name without the file extension
		img_file_name = imge
		print ("Image file that is getting processed is: "+img_file_name)
		# Create a directory for outputs
		img_save_path = formatted_image_path_folder+img_file_name+".jpg"
		# Write the file to output file
		cv2.imwrite(img_save_path, img)
		# Recognize text with tesseract for python
		extracted_text = pytesseract.image_to_string(img_save_path, lang="eng")
		print ("Text extracted from the image file {img_file_name} is: \n"+extracted_text)
		# insert extracted text into a file
		extract_file=text_file_path+img_file_name+".txt"
		# open text file to insert extracted text
		with open(extract_file,"wb") as f:
			f.write(extracted_text.encode('utf-8'))
		# remove new lines from the text file
		fd=tmp=None
		file = open(extract_file,"r") #changed
		fd = file.read()
		#fd=file(extract_file,"rb").read()
		tmp=fd.replace("\n"," ").replace("\x0C"," ").replace("iClicker"," ").replace("Question @"," ").replace("%"," ")
		tmp=" ".join([e for e in tmp.split(" ")if e.strip()])
		file = open(extract_file,"w") #added
		file.write(tmp)

		# find confidence score of ocr text and send it to sql table
		confidence_score=[]
		with tesserocr.PyTessBaseAPI() as api:
			api.SetImageFile(img_save_path)
			confidence_score=api.AllWordConfidences()
		low_confidence_score=[]
		high_confidence_score=[]
		for score in confidence_score:
			if score < 90:
				low_confidence_score.append(score)
			else:
				high_confidence_score.append(score)
		low_confidence_score_count=len(low_confidence_score)
		high_confidence_score_count=len(high_confidence_score)

		if low_confidence_score_count < 10:
			# find pattern of multiple choice questions and send them for respective functions to parsing
			call_patterns(tmp,img_file_name,low_confidence_score_count,high_confidence_score_count)

def print_stats(raw_image_path_folder,text_file_path):

	# stats
	print ("Overall stats:")
	totalcounter=0
	for f in os.listdir(raw_image_path_folder):
		totalcounter=totalcounter+1
	print ("Total image files sent for ocr and text extraction are: "+str(totalcounter))

	# get names of all files that produced result
	sql_file_names=get_file()
	sql_file_names=list(sql_file_names)
	ocrcounter=0
	for f in sql_file_names:
		ocrcounter=ocrcounter+1
	print ("Total image files that produced good ocr: "+str(ocrcounter))
	print ('Names of the image files that produced result are: \n',sql_file_names)

	sql_file_names_list=[]
	for f in sql_file_names:
		sql_file_names_list.append(f[0])

	#print sql_file_names_list
	extract_file_names=[]
	for f in os.listdir(text_file_path):
		extract_file_names.append(os.path.splitext(f)[0])

	# files that didnt produce result
	badocrcounter=totalcounter-ocrcounter
	print ("\nTotal image files that didnt produce good ocr: "+str(badocrcounter))

	diff_list=list(set(extract_file_names)-set(sql_file_names_list))
	print ("Names of the image files that didnt produce good ocr:\n",diff_list)

def main():
	#ipdb = Pdb()
	#ipdb.set_trace()
	#setup system

	'''  (not required for local)
	# connecting to ec2
	client.connect(hostname="10.54.198.91", username="ubuntu", pkey=key)

	# copying image files from s3 to local
	stdin, stdout, stderr = client.exec_command("sudo rm -rf /mnt/iclicker_ocr/raw_images/*")
	stdin, stdout, stderr = client.exec_command("aws s3 cp s3://iclicker-ocr/raw_image/ /mnt/iclicker_ocr/raw_images/ --recursive")
	time.sleep(10)
	'''

	importlib.reload(sys)
	#sys.setdefaultencoding('utf-8')
	mysqlcon=mysql_be_con()
	cursor=mysqlcon.cursor()

	#clean the mysql table
	cursor.execute('delete from iclicker_ocr.iclicker;')

	# define raw input image file path
	#raw_image_path_folder = "/mnt/iclicker_ocr/raw_images/"
	raw_image_path_folder = "/home/shivaprasad/Documents/iClicker_OCR/process/raw_images"

	# define formatted input file path
	#formatted_image_path_folder = "/mnt/iclicker_oc/formatted_images/"
	formatted_image_path_folder = "/home/shivaprasad/Documents/iClicker_OCR/process/formatted_images/"

	# delete all files from formatted_image_path_folder
	for f in os.listdir(formatted_image_path_folder):
		os.remove(os.path.join(formatted_image_path_folder,f))

	# define output text file path
	#text_file_path="/mnt/iclicker_ocr/extracted_text/"
	text_file_path="/home/shivaprasad/Documents/iClicker_OCR/process/extracted_text/"

	# delete all files from text_file_path
	for f in os.listdir(text_file_path):
		os.remove(os.path.join(text_file_path,f))

	# process ocr for each image in raw_image_path_folder
	process_ocr(raw_image_path_folder,formatted_image_path_folder,text_file_path)

	# removing records from sql table if they produced only one option in sql result or if they produced infrequent values for options
	options=get_options()
	delete_data(options)

	# print stats of the OCR
	print_stats(raw_image_path_folder,text_file_path)

	cursor.close()
	mysqlcon.close()

if __name__ == '__main__':
	main()
