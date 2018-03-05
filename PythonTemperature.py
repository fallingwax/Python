#!/usr/bin/env python
import os
import glob
import time
import datetime
import schedule
import smtplib
from threading import Timer
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

def time_stamp():
	ts = datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M%p")
 	return ts

def read_temp_raw():
	f = open(device_file, 'r')
	lines = f.readlines()
	f.close()
	return lines

def read_temp():
	lines = read_temp_raw()
	while lines[0].strip()[-3:] != 'YES':
		time.sleep(0.2)
		lines = read_temp_raw()
	equals_pos = lines[1].find('t=')
	if equals_pos != -1:
		temp_string = lines[1][equals_pos+2:]
		temp_c = float(temp_string) / 1000.0
		temp_f = temp_c * 9.0 / 5.0 + 32.0
		return temp_f	

def write_temp():
	temp = read_temp()
	path = '/home/pi/tempalert.txt'
	f =  open(path, 'w+')	
	ts = time_stamp()	
	f.write("Temp is: " + str(temp) + "The time is: " + ts + "\n\r")
	f.close()

def email():
	USER = 'user@test.com'
	PW = 'mypassword'
	#set up smtp server
	con = smtplib.SMTP(host='smtp.office365.com', port=587)
	con.starttls()
	con.login(USER,PW)

	msg = MIMEMultipart()
	msg['From']=USER
	msg['To']=USER
	msg['Subject']='Temp Alert in Server Room'

	with open('tempalert.txt', 'r') as alert:
		contents = alert.read()
	msg.attach(MIMEText(contents,'plain'))	
	con.sendmail(USER,USER,msg.as_string())
					
def alert():
	temp = read_temp()
	if temp >= 70:
		email()
	else:
		time.sleep(1)

schedule.every(10).minutes.do(alert)

while True:
	write_temp()
	schedule.run_pending()
	time.sleep(1)
