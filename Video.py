from serial import *
import time
from serial.tools import list_ports
from time import sleep
import tkinter as tk
from tkinter import ttk
from tkinter import * 
from tkinter import messagebox
import os
from threading import *
import datetime
import psycopg2
from contextlib import contextmanager
import shutil
import subprocess
import easygui
#import asyncio, asyncssh, sys

status_dict = {'inward':'PASS','outward':'PASS','left':'PASS','right':'PASS'}


def mount_z(username='NTDISERVER', password="vvdn@1234", drive_letter='/mnt/Z'):

	cmd_parts = "mount -t cifs -o username=NTDISERVER,password=vvdn@1234, //172.17.192.104/ntdi_pts1_shared_dir/NTDI_PTS1_Server/NTDI_PTS1_Reports/video_validation /mnt/Z"

	text_box.config(state = tk.NORMAL)
	text_box.insert(tk.END, "\nMounting Drive..........\n")
	text_box.config(state = tk.DISABLED)
	root.update()
   
	os.system(cmd_parts)

def messageWindow12():
	global win12
	win12 = tk.Toplevel()
	win12.title('Message')
	win12.geometry("450x100")
	tk.Label(win12, text="Leftward camera is tuned?").pack(pady = 10, padx=10)
	tk.Button(win12, text='Yes', command= lambda : left_fail("PASS")).pack(side="right", padx =10)
	tk.Button(win12, text='No', command= lambda : left_fail("FAIL")).pack(side="right", padx =10)

def left_fail(string):
	global status_dict
	win12.destroy()
	if "FAIL" in string:
		status_dict['left'] = 'FAIL'
	Thread(target = start_recording).start()
	
	
def messageWindow13():
	global win13
	win13 = tk.Toplevel()
	win13.title('Message')
	win13.geometry("450x100")
	tk.Label(win13, text="Rightward camera is tuned?").pack(pady = 10, padx=10)
	tk.Button(win13, text='Yes', command= lambda : right_fail("PASS")).pack(side="right", padx =10)
	tk.Button(win13, text='No', command= lambda : right_fail("FAIL")).pack(side="right", padx =10)

def right_fail(string):
	win13.destroy()
	global status_dict
	if "FAIL" in string:
		status_dict['right'] = 'FAIL'
	next_button()

def messageWindow14():
	global win14
	win14 = tk.Toplevel()
	win14.title('Message')
	win14.geometry("450x100")
	tk.Label(win14, text="Outward camera is tuned?").pack(pady = 10, padx=10)
	tk.Button(win14, text='Yes', command= lambda : out_fail("PASS")).pack(side="right", padx =10)
	tk.Button(win14, text='No',  command= lambda : out_fail("FAIL")).pack(side="right", padx =10)

def out_fail(string):
	win14.destroy()
	global status_dict
	if "FAIL" in string:
		status_dict['outward'] = 'FAIL'
	next_button()
	
	

def messageWindow15():
	global win15
	win15 = tk.Toplevel()
	win15.title('Message')
	win15.geometry("450x100")
	tk.Label(win15, text="Inward camera is tuned?").pack(pady = 10, padx=10)
	tk.Button(win15, text='Yes',  command= lambda : in_fail("PASS")).pack(side="right", padx =10)
	tk.Button(win15, text='No',  command= lambda : in_fail("FAIL")).pack(side="right", padx =10)

def in_fail(string):
	win15.destroy()
	global status_dict
	if "FAIL" in string:
		status_dict['inward'] = 'FAIL'
	next_button()
	#update_database(dict1)

def next():
	if id == 0:
		messageWindow14()
	elif id == 1:
		messageWindow15()
		
	elif id == 2:
		messageWindow13()

		

def next_button():
	
	port.write("\x03".encode())
	sleep(0.5)
	port.write("\x03".encode())
	kill_gstreamer()
	port.close()
	sleep(0.5)
	port.open()
	sleep(0.5)
	if id == 0:
		Thread(target=video_streaming, args=(0,)).start()	#inward
	elif id == 1:
		Thread(target=video_streaming, args=(1,)).start()   #right
	elif id ==2:
		Thread(target=video_streaming, args=(2,)).start()   #left
		Next_button.config(state = tk.DISABLED)
		Stop_button.config(state = tk.NORMAL)
	
''' CHECKING SIZE OF VIDEO IS LESS THEN ONE MB OR NOT '''
def check_size(status):
	global status_dict
	sleep(0.9)
	file_size_in = (os.stat("/home/vvdn/Desktop/ov9732_in.mp4").st_size/ (1000 * 1000))
	print(file_size_in)
	if file_size_in <= 1:
		status_dict = {'inward':'FAIL','outward':'PASS','left':'PASS','right':'PASS','global':'FAIL'}
		print("test fail!")
		status = "FAIL"
	
		messagebox.showerror("Test Fail", "inward camera Vedio size is too small")
	file_size_left = (os.stat('/home/vvdn/Desktop/ov9732_left.mp4').st_size/ (1000 * 1000))
	print(file_size_left)
	if file_size_left <= 1:

		status_dict = {'inward':'PASS','outward':'PASS','left':'FAIL','right':'PASS','global':'FAIL'}
		print("test fail!")
		status = "FAIL"
	
		messagebox.showerror("Test Fail", "Leftward Vedio size is too small")
	file_size_right = (os.stat('/home/vvdn/Desktop/ov9732_right.mp4').st_size/ (1000 * 1000))
	
	print(file_size_right)
	if file_size_right <= 1:

		status_dict = {'inward':'PASS','outward':'PASS','left':'PASS','right':'FAIL','global':'FAIL'}
		print("test fail!")
		status = "FAIL"
	
		messagebox.showerror("Test Fail", "Rightward Vedio size is too small")
	file_size_out = (os.stat('/home/vvdn/Desktop/ov491_out.mp4').st_size/ (1000 * 1000))
	if file_size_out <= 1:
		
		status_dict = {'inward':'PASS','outward':'FAIL','left':'PASS','right':'PASS','global':'FAIL'}
		print("test fail!")
		status = "FAIL"
	
		messagebox.showerror("Test Fail", "Outward Vedio size is too small")
		messagebox.showerror("TEST FAIL"," VEDIO TEST FAIL")
	if id == 0:
		Thread(target=video_streaming, args=(0,)).start()	#inward
	elif id == 1:
		Thread(target=video_streaming, args=(1,)).start()   #right
	elif id ==2:
		Thread(target=video_streaming, args=(2,)).start()   #left
		Next_button.config(state = tk.DISABLED)
		Stop_button.config(state = tk.NORMAL)
	if status == 'FAIL':
		# scp_files(status)
		move_files(status)
		update_database(status_dict,status)
def send_files_to_server(status):
	global run_level
	global date_old
	global old_status
	date = datetime.datetime.now()
	date = date.strftime("%d-%b-%Y")
	
	file_name = "ov9732_in.mp4" 
	file_name1 = "ov9732_left.mp4" 
	file_name2 = "ov9732_right.mp4" 
	file_name3 = "ov491_out.mp4"
	text_box.config(state = tk.NORMAL)
	text_box.insert(tk.END, "Copying files to server..........")
	text_box.config(state = tk.DISABLED)
	root.update()
	
	if os.path.isdir(r"/mnt/") == False:
		os.mkdir(r"/mnt/")

	if os.path.isdir(r"/mnt/Z/") == False:
		os.mkdir(r"/mnt/Z/")

	mount_z()

	
	if os.path.isdir("/mnt/Z/"+status) == False:
		os.mkdir("/mnt/Z/"+status)
	

	if os.path.isdir("/mnt/Z/"+status+"/"+date) == False:
		os.mkdir("/mnt/Z/"+status+"/"+date)

	if os.path.isdir("/mnt/Z/"+status+"/"+date+"/"+Sr_no) == False:
		os.mkdir("/mnt/Z/"+status+"/"+date+"/"+Sr_no)

	if os.path.isdir("/mnt/Z/"+status+"/"+date+"/"+Sr_no+"/Run"+run_level) == False:
		os.mkdir("/mnt/Z/"+status+"/"+date+"/"+Sr_no+"/Run"+run_level)
	path = os.getcwd()
	file_path= path+"/validation_videos/"+status+"/"+date+"/"+Sr_no+"/Run"+run_level 
	shutil.copyfile(file_path+"/"+file_name, "/mnt/Z/"+status+"/"+date+"/"+Sr_no+"/Run"+run_level+"/"+file_name)
	shutil.copyfile(file_path+"/"+file_name1, "/mnt/Z/"+status+"/"+date+"/"+Sr_no+"/Run"+run_level+"/"+file_name1)
	shutil.copyfile(file_path+"/"+file_name2, "/mnt/Z/"+status+"/"+date+"/"+Sr_no+"/Run"+run_level+"/"+file_name2)
	shutil.copyfile(file_path+"/"+file_name3, "/mnt/Z/"+status+"/"+date+"/"+Sr_no+"/Run"+run_level+"/"+file_name3)
	shutil.move(path+"/dut_logs.txt", file_path+"/dut_logs.txt")
	shutil.copyfile(file_path+"/dut_logs.txt", "/mnt/Z/"+status+"/"+date+"/"+Sr_no+"/Run"+run_level+"/dut_logs.txt")
	write_to_GUI("Upload Success!\n\n")
	Sr_no_entry.delete("0",tk.END)
	try:
		if (date_old != date or old_status != status):
			os.system("mv /mnt/Z/"+old_status+"/"+date_old+"/"+Sr_no+"/*  /mnt/Z/"+status+"/"+date+"/"+Sr_no+"/")
			os.system("mv "+path+"/validation_videos/"+old_status+"/"+date_old+"/"+Sr_no+"/* "+path+"/validation_videos/"+status+"/"+date+"/"+Sr_no+"/")
			os.system("rm -rf /mnt/Z/"+old_status+"/"+date_old+"/"+Sr_no)
			os.system("rm -rf "+path+"/validation_videos/"+old_status+"/"+date_old+"/"+Sr_no)
	finally:
		start_button.config(state = tk.NORMAL)
		another_message()
	

def another_message():
	result = tk.Toplevel()
	result.title('Message')
	result.geometry("350x100")
	tk.Label(result, text="UPDATE SUCCESFULL").pack(pady = 10, padx=10)
	tk.Button(result, text='OK', command=result.destroy).pack(side="right")
	#tk.Button(result, text='FAIL', command=test_fail).pack(side="right", padx =10)



def stop_button():
	
	
	#Sr_no_entry.clear()
	
	Stop_button.config(state = tk.DISABLED)
	root.update()
	port.write("\x03".encode())
	sleep(0.5)
	port.write("\n".encode())
	sleep(0.5)
	kill_gstreamer()
	messageWindow12()
	
	

def messageWindow1():
	global result
	result = tk.Toplevel()
	result.title('Message')
	result.geometry("350x100")
	tk.Label(result, text="Video validation passed for scanned Camera?").pack(pady = 10, padx=10)
	tk.Button(result, text='PASS', command=test_pass).pack(side="right")
	tk.Button(result, text='FAIL', command=test_fail).pack(side="right", padx =10)


def kill_gstreamer():

	os.system("sudo pkill gst")

def get_system_ip(adapter_name):
	ip = subprocess.check_output("ifconfig "+adapter_name,stdin=subprocess.PIPE,stderr=subprocess.PIPE,shell=True).decode().split("\n")
	for line in ip:
		if "inet addr" in line:
			ip =  line.split(":")[1].split(" ")[0]
			return ip



def video_streaming(cam_name):
	
	root.update()
	port.write("\x03".encode())
	sleep(0.5)
	global id
	if cam_name == "outward_camera":
		id = 0
		print("outward")
		a = "gst-launch-1.0 -v v4l2src device=/dev/video0 ! 'video/x-raw , width=(int)1920 , height=(int)1080 , format=(string)UYVY' ! nvvidconv ! 'video/x-raw(memory:NVMM) , width=(int)1920 , height=(int)1080 , format=(string)NV12' ! omxh264enc ! 'video/x-h264,stream-format=(string)byte-stream' ! rtph264pay pt=96 ! udpsink host="+config[2]+" port=4000\n"
		port.write(a.encode())
		sleep(3)
		os.system("gst-launch-1.0 -v udpsrc port=4000 ! \"application/x-rtp, encoding-name=(string)H264,payload=(int)96\" ! rtpjitterbuffer ! rtph264depay ! avdec_h264 ! xvimagesink sync=false")
		root.update()
	
	elif cam_name == 0:
		id = 1
		print("Inward")
		a = "gst-launch-1.0 nvcamerasrc sensor-id=0 ! 'video/x-raw(memory:NVMM),width=1280, height=720, framerate=30/1, format=NV12' ! omxh264enc ! 'video/x-h264,stream-format=(string)byte-stream' ! rtph264pay pt=96 ! udpsink host="+config[2]+" port=4000\n"
		port.write(a.encode())
		sleep(0.5)
		port.write("\n".encode())
		sleep(3)
		os.system("gst-launch-1.0 -v udpsrc port=4000 ! \"application/x-rtp, encoding-name=(string)H264,payload=(int)96\" ! rtpjitterbuffer ! rtph264depay ! avdec_h264 ! xvimagesink sync=false")
		root.update()
		
	

	elif cam_name == 1:
		id = 2
		print("right")
		a = "gst-launch-1.0 nvcamerasrc sensor-id=2 ! 'video/x-raw(memory:NVMM),width=1280, height=720, framerate=30/1, format=NV12' ! omxh264enc ! 'video/x-h264,stream-format=(string)byte-stream' ! rtph264pay pt=96 ! udpsink host="+config[2]+" port=4000\n"
		port.write(a.encode())
		sleep(0.5)
		port.write("\n".encode())
		sleep(3)
		os.system("gst-launch-1.0 -v udpsrc port=4000 ! \"application/x-rtp, encoding-name=(string)H264,payload=(int)96\" ! rtpjitterbuffer ! rtph264depay ! avdec_h264 ! xvimagesink sync=false")
		sleep(2)
		root.update()
		
		

	elif cam_name == 2:
		id = 3
		print("left")
		a = "gst-launch-1.0 nvcamerasrc sensor-id=1 ! 'video/x-raw(memory:NVMM),width=1280, height=720, framerate=30/1, format=NV12' ! omxh264enc ! 'video/x-h264,stream-format=(string)byte-stream' ! rtph264pay pt=96 ! udpsink host="+config[2]+" port=4000\n"
		port.write(a.encode())
		sleep(0.5)
		port.write("\n".encode())
		sleep(3)
		os.system("gst-launch-1.0 -v udpsrc port=4000 ! \"application/x-rtp, encoding-name=(string)H264,payload=(int)96\" ! rtpjitterbuffer ! rtph264depay ! avdec_h264 ! xvimagesink sync=false")
		root.update()
		Next_button.config(state = tk.DISABLED)

def validate_sr_no(sr_no):
	
	Sr_no = sr_no.split(",")[0].split(":")[1]
	if len(Sr_no) == 8 or len(Sr_no) == 9:
		print(Sr_no)
		if len == 8:
			if (Sr_no[3] == 'A' or Sr_no[3] == 'B' or Sr_no[3] == 'C'):
				return Sr_no
			else:
				message()
		else:
			return Sr_no
	else:
		message()
	
def message():
	result = tk.Toplevel()
	result.title('Message')
	result.geometry("350x100")
	tk.Label(result, text="Please enter valid Enclosure Sr Number").pack(pady = 10, padx=10)
	tk.Button(result, text='Yes', command=result.destroy).pack(side="right")
	
	

def start_recording():
	dut_logs([b"logs for video streaming: \n"])
	result = port.readlines()
	dut_logs(result)
	port.close()
	sleep(0.5)
	port.open()
	sleep(0.5)
	a = "gst-launch-1.0 nvcamerasrc num-buffers=300 sensor-id=0 ! 'video/x-raw(memory:NVMM),width=1280, height=720, framerate=30/1, format=NV12' ! omxh264enc ! qtmux ! filesink location=ov9732_in.mp4 -ev nvcamerasrc num-buffers=300 sensor-id=1 ! 'video/x-raw(memory:NVMM),width=1280, height=720, framerate=30/1, format=NV12' ! omxh264enc ! qtmux ! filesink location=ov9732_left.mp4 -ev nvcamerasrc num-buffers=300 sensor-id=2 ! 'video/x-raw(memory:NVMM),width=1280, height=720, framerate=30/1, format=NV12' ! omxh264enc ! qtmux ! filesink location=ov9732_right.mp4 -ev v4l2src device=/dev/video0 num-buffers=300 do-timestamp=true ! 'video/x-raw , width=(int)1920 , height=(int)1080 , format=(string)UYVY' ! nvvidconv ! 'video/x-raw(memory:NVMM) , width=(int)1920 , height=(int)1080 , format=(string)NV12' ! omxh264enc ! qtmux ! filesink location=ov491_out.mp4 -ev\n"
	port.write(a.encode())
	print("Recording started!")
	sleep(12)
	#port.write("\x03".encode())
	print("recording ended!")
	sleep(1)
#	check_size("ov491_out.mp4")
#	check_size("ov9732_right.mp4")
#	check_size("ov9732_left.mp4")
#	check_size("ov9732_in.mp4")
	
	new()

def check_size_(file_):
	a = "du -csh "+file_+" | grep total"
	port.write(a.encode())
	size = port.readline().decode().split(" ")
	if "M" not in size:
		messagebox123()
	if "out" in file_:
		size_out = size[0].split("M")[0]

	if "in" in file_:
		size_in = size[0].split("M")[0]

	if "left" in file_:
		size_left = size[0].split("M")[0]

	if "right" in file_:
		size_right = size[0].split("M")[0]

def messagebox123():
	pass

global camera_name
camera_name = []
config = []
conf = open("config.txt","r")
data = conf.readlines()
print(data)
config.append(data[2].split(":")[1].strip(" ").strip("\n"))
config.append(data[4].split(":")[1].strip(" ").strip("\n"))
config.append(data[6].split(":")[1].strip(" ").strip("\n"))
config.append(data[8].split(":")[1].strip(" ").strip("\n"))
config.append(data[10].split(":")[1].strip(" ").strip("\n"))
config.append(data[12].split(":")[1].strip(" ").strip("\n"))

db_ip = config[4]
test_cont_tabl_1 = config[3]
test_cont_tabl_2 = config[5]
'''
config.append(data[8].split(":")[1].strip(" ").strip("\n"))
config.append(data[10].split(":")[1].strip(" ").strip("\n"))
config.append(data[12].split(":")[1].strip(" ").strip("\n"))
config.append(data[14].split("-")[1].strip(" ").strip("\n"))

if config[2] == "1":
	camera_name.append("out")
if config[3] == "1":
	camera_name.append("in")
if config[4] == "1":
	camera_name.append("left")
if config[5] == "1":
	camera_name.append("right")
	print(config)
print(camera_name)
''' 
def port_conf(config):	
	os.system("sudo systemctl stop ModemManager.service")
	os.system("fuser -k /dev/ttyACM0")
	for port,desc,hwid in list_ports.comports():
		if config[0] in desc:
			DUTport = Serial (port = port, baudrate = 115200, bytesize = EIGHTBITS, parity =PARITY_NONE,stopbits = 			 STOPBITS_ONE , timeout = 4, xonxoff=False, rtscts=False, writeTimeout=None, dsrdtr=False,interCharTimeout=None)
			
			print(DUTport)
			return DUTport
def login_dut():

	port.write("ubuntu\n".encode())
	sleep(0.5)
	port.write("ubuntu\n".encode())
	sleep(2)
	log_in = serial_read()
	print(log_in)
	return log_in

def serial_read():

	serial_buff = b""
	serial_data_ret = port.readline()
	while b"\n" in serial_data_ret:
		serial_data_ret = port.readline()
		serial_buff = b"".join([serial_buff,serial_data_ret])
		
	return serial_buff.decode()
		

def su_ubuntu_login():
	port.write("sudo su\n".encode())
	sleep(1)
	port.write("ubuntu\n".encode())
	sleep(3)
	ubuntu_log_in = serial_read()
	print(ubuntu_log_in)
	return ubuntu_log_in

def data_write(x):
	global ssid
	if "tegra-ubuntu login:" in x:
		x = login_dut()
	if "ubuntu@tegra-ubuntu:" in x:
		x = su_ubuntu_login()
	if "root@tegra-ubuntu:/home/ubuntu" in x:
		x = turn_wifi_on()
	if "Thank you! Visit again..." in x:
		ssid = get_ssid(x)
		return
	else:
		print("Device not responding")
		x = serial_read()
		data_write(x)

def turn_wifi_on():
	port.write("wifi_app ap\n".encode())
	port.readlines()
	port.write("n\n".encode())
	port.readlines()
	port.write(b"n\n")
	port.readlines()
	port.write(b"y\n")
	port.readlines()
	port.write(b"6\n")
	port.readlines()
	port.write(b"36\n")
	port.readlines()
	port.write(b"n\n")
	wifi_on = serial_read()
	print(wifi_on)
	return wifi_on

	

def get_ssid(x):
	x = x.split("\n")
	for line in x:
		print(line)		
		if "ssid" in line:
			print(line.split("\"")[1])			
			return line.split("\"")[1]
			
def wifi_connection(netwrok_name):
	global connection
	connection = 0
	os.system("nmcli d connect wlp2s0")

	os.system("nmcli d wifi connect "+netwrok_name)
	try:
		ss = subprocess.check_output("iwconfig | grep "+ssid,stdin=subprocess.PIPE,stderr=subprocess.PIPE,shell=True).decode()
		connection = 1
	except:
		wifi(ssid)

def wifi(netwrok_name):
	global resu	
	resu = tk.Toplevel()
	resu.title('Message')
	resu.geometry("550x100")
	tk.Label(resu, text="Unable to connect to wifi. Please connect to "+netwrok_name+" manually!").pack(pady = 10, padx=10)
	tk.Button(resu, text='OK', command=stream).pack(side="right")

def stream():
	resu.destroy()
	Thread(target=video_streaming, args=("outward_camera",)).start()
	root.update()	
	
def write_to_GUI(text):
	text_box.config(state = tk.NORMAL)
	text_box.insert(tk.END, text)
	text_box.config(state = tk.DISABLED)
	root.update()
	

def conncetion_db():
	global cur
	global conn
	text_box.config(state = tk.NORMAL)
	text_box.insert(tk.END, "\nConnecting Database.....")
	text_box.config(state = tk.DISABLED)
	conn = psycopg2.connect(database = "postgres", user = "postgres", host=db_ip , port=5432, password = "postgres")
	print ("Opened database successfully")
	cur = conn.cursor()

def check_database():
	stage = "video_validation"
	content = False
	global run_level , conn
	global date_old
	global old_status
	no = Sr_no
	cur.execute("SELECT * FROM \"VideoValidation\" WHERE enclosure_no = '{}' ORDER BY id DESC".format(no))
	content1 = cur.fetchall()
	cur.execute("SELECT * FROM \"thermal_stage\" WHERE enclosure_no = '{}' ORDER BY id DESC".format(no))
	content2 = cur.fetchall()
	cur.execute("SELECT * FROM \"debug\" WHERE hardware_id = '{}' ORDER BY id DESC".format(no))
	content3 = cur.fetchall()
	cur.execute("SELECT * FROM \""+test_cont_tabl_1+"\" WHERE stage_name = '{}'  ORDER BY id DESC".format(stage))
	
	serial_count = cur.fetchall()
 
	
	try:
		print(content1[0])
		old_status = content1[0][3]
		print(content1[0][3])
		print(content1[0][2])
		date_old = datetime.datetime.strftime(content1[0][2], "%d-%b-%Y")
		print(date_old)
		run_level = len(content1)
	except:
		print("No previous records found!")	
		run_level = 0
	
	try:

		if content2 != []:
			print(content2[0][3])
			if content2[0][3] != "PASS":
				if content3 != []:
					print("retyu")
					if content3[0][4]!= "fixed":
						print("Failed from debug")
						return "FAILED"
				else:
					return "FAILED"
	except:
		print("No records found!")
		

	try:
		print(serial_count)
		serial_count = serial_count[0]
		print(serial_count)
		if int(serial_count[2]) < run_level:
			print(serial_count)
			print("Run level is grater than entry in test count table")
			write_to_GUI("\nRun level is greater than entry in test count table\nChecking in test_count_device")
			cur.execute("SELECT * FROM \""+test_cont_tabl_2+"\" WHERE serial_no = '{}' AND stage_name = '{}'  ORDER BY id DESC LIMIT 1;".format(no,stage))

			count = cur.fetchall()
			print(count)
			if count == []:
				write_to_GUI("\nDevice is not present in test_count_device table")
				write_to_GUI("\nDevice cannot be tested report to debugging")
				easygui.msgbox("Device cannot be tested report to debugging")
				return "FAILED"

			if int(count[0][3]) < run_level: 
				print(count)
				print("Device cannot be tested report to debugging")
				write_to_GUI("\nDevice cannot be tested report to debugging")
				easygui.msgbox("Device cannot be tested report to debugging")
				return "FAILED"
			else:
				print("##########")
	except:
		print("Device is not in test_count_stage table")

	
	
	
	
	run_level = str(run_level)
	cur.execute("SELECT * FROM assembly_info WHERE enclosure_no = '{}' ORDER BY id DESC LIMIT 1".format(no))
	content = cur.fetchall()

	if content:
		print("Entry found!")
		print(content)
		print("Outward Camera "+content[0][3])
		print("Inward Camera "+content[0][4])
		print("left-ward Camera "+content[0][5])
		print("right-ward Camera "+content[0][6])
		cur.execute("SELECT * FROM inward_camera WHERE hw_serial_no = '{}' ORDER BY id DESC LIMIT 1".format(content[0][4]))
		content_inward = cur.fetchall()
		print (content_inward[0][37])		
		if content_inward[0][37]==True:
			cur.execute("SELECT * FROM outward_camera WHERE hw_serial_no = '{}' ORDER BY id DESC LIMIT 1".format(content[0][3]))
			content_outward = cur.fetchall()
			print (content_outward[0][37])
			if content_outward[0][37]==True:
				cur.execute("SELECT * FROM side_camera WHERE hw_serial_no = '{}' ORDER BY id DESC LIMIT 1".format(content[0][5]))
				content_left = cur.fetchall()
				print (content_left[0][37])
				if content_left[0][37]==True:
					cur.execute("SELECT * FROM side_camera WHERE hw_serial_no = '{}' ORDER BY id DESC LIMIT 1".format(content[0][5]))
					content_right = cur.fetchall()
					print(content_right[0][37])
					if content_right[0][37]==True:		
						return "PASS"
					else:
						cam_assembly_not_done("rightward camera")
				else:
					cam_assembly_not_done("leftward camera")
			else:
				cam_assembly_not_done("outward camera")
		else:
				cam_assembly_not_done("inward camera")
				
	else:
		write_to_GUI("\nAssembly information not updated for given Sr. number")
		cam_assembly_not_done("given Enclosure number")
		
		#Stop_button.config(state = tk.DISABLED)
		root.update()

	if conn.closed == 0:
		conn.close()

def cam_assembly_not_done(cam):
	win = tk.Toplevel()
	win.title('Message')
	win.geometry("450x100")
	tk.Label(win, text="Assembly is not True for "+cam).pack(pady = 10, padx=10)
	tk.Button(win, text='OK', command= win.destroy).pack(side="right", padx =10)
	start_button.config(state = tk.NORMAL)
		

def update_database(status,global_s):
	global ver_info , conn
	conncetion_db()
	print(status)
	now = datetime.datetime.now()
	# now = now.strftime("%d/%m/%Y, %H:%M:%S")
	
	now = str(now)
	print("End time : "+now)
	if Sr_no:
		insert_query = "INSERT INTO \"VideoValidation\" (enclosure_no , start_time , end_time , status , app_version , left_cam_status , right_cam_status , outward_cam_status , inward_cam_status ) values (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
	insert_values = (Sr_no,start,now,global_s,ver_info,status['left'],status['right'],status['outward'],status['inward'])
	cur.execute(insert_query,insert_values)
	conn.commit()
	conn.close()
	if conn.closed == 0:
		conn.close()
	Thread(target=send_files_to_server(global_s)).start()
	text_box.config(state = tk.NORMAL)
	text_box.insert(tk.END, "\nDatabase updated succesfully.....\n")
	text_box.config(state = tk.DISABLED)
	root.update()


def test_pass():
	result.destroy()
	print("test pass!")
	
	status = status_dict['global']	
	#move_files(status)
	Sr_no_entry.delete("0",tk.END)
	
	
	

def new():
	global status_dict
	if (status_dict['right'] == "FAIL" or status_dict['left'] == "FAIL" or status_dict['outward'] == "FAIL" or status_dict['inward'] == "FAIL"):
		status = "FAIL"
	else:
		status = "PASS"
	port.write(b"\n")
	scp_files(status)
	

def test_fail():
	result.destroy()
	global status
	status_dict = {'inward':'PASS','outward':'PASS','left':'PASS','right':'PASS','global':'FAIL'}
	print("test fail!")
	status = status_dict['global']


def move_files(status):
	global run_level

	path = "/home/vvdn/Desktop/"
	date = date = datetime.datetime.now()
	date = date.strftime("%d-%b-%Y")
	path1 = os.getcwd()
	print(path1)
	path_new = path1+"/validation_videos/"+status+"/"+date+"/"+Sr_no+"/Run"+run_level
	print(path_new)
	if os.path.isdir(path1+"/validation_videos/"+status+"/"+date+"/"+Sr_no) == False:
		os.mkdir(path1+"/validation_videos/"+status+"/"+date+"/"+Sr_no)
	if os.path.isdir(path1+"/validation_videos/"+status+"/"+date+"/"+Sr_no+"/Run"+run_level) == False:
		print(os.path.isdir(path1+"/validation_videos/"+status+"/"+date+"/"+Sr_no+"/Run"+run_level))
		os.mkdir(path1+"/validation_videos/"+status+"/"+date+"/"+Sr_no+"/Run"+run_level)
	os.system("mv "+path+"ov9732_in.mp4 "+path_new+"/")
	os.system("mv "+path+"ov9732_left.mp4 "+path_new+"/")
	os.system("mv "+path+"ov491_out.mp4 "+path_new+"/")
	os.system("mv "+path+"ov9732_right.mp4 "+path_new+"/")
	os.system("mv "+path+"dut_logs.txt "+path_new+"/")

def scp_files(status):
	
	global status_dict
	
	date = datetime.datetime.now()
	date = date.strftime("%d-%b-%Y")
	path = os.getcwd()
	if os.path.isdir(path+"/validation_videos/") == False:
		os.mkdir(path+"/validation_videos/")
	if os.path.isdir(path+"/validation_videos/"+status) == False:
		print(status)
		os.mkdir(path+"/validation_videos/"+status)
	if os.path.isdir(path+"/validation_videos/"+status+"/"+date) == False:
		os.mkdir(path+"/validation_videos/"+status+"/"+date)
	
	path = "~/Desktop/"
	file_name = "ov9732_in.mp4" 
	file_name1 = "ov9732_left.mp4" 
	file_name2 = "ov9732_right.mp4" 
	file_name3 = "ov491_out.mp4"
	data2 = []
	port.write(b"\n")
	sleep(3)
	data1 = port.readlines()
	dut_logs([b"\n logs for video recording : \n"])
	dut_logs(data1)
	print("sending scp command")
	a = "scp ov491_out.mp4 ov9732_left.mp4 ov9732_right.mp4 ov9732_in.mp4 vvdn@"+config[2]+":"+path+"\n"
	port.write(a.encode())
	sleep(0.5)
	print("scp command sent")
	data = port.readlines()
	for line in data:
		line = line.decode()
		print(line)
		enter_pwd(line)
	data1 = port.readline()
	s=0
	while b"/home/ubuntu#" not in data1:
		data1 = port.readline()
		print(data1)
		if data1 == b"":
			s += 1
			if s == 5:
				port.write(b"ssh-keygen -f ~/.ssh/known_hosts -R "+config[2])
				message_box(status)
				return
	port.write("\x03".encode())
	port.close()
	check_size(status)
	if (status_dict['right'] == "FAIL" or status_dict['left'] == "FAIL" or status_dict['outward'] == "FAIL" or status_dict['inward'] == "FAIL"):
		status = "FAIL"
	else:
		status = "PASS"
	root.update()
	move_files(status)
	update_database(status_dict,status)
def readline():
	s = port.readline()
	return s
def message_box(status):
	global box
	box = tk.Toplevel()
	box.title('Message')
	box.geometry("450x100")
	tk.Label(box, text="Retry File transfer?").pack(pady = 10, padx=10)
	tk.Button(box, text='OK', command= lambda : scp_retry(status)).pack(side="right", padx =10)
	
def scp_retry(status):
	global box
	box.destroy()
	port.write(b"\x03")
	sleep(0.5)
	scp_files(status)

def enter_pwd(data):	
	if "Are you sure you want to continue connecting" in data:
		port.write(b"yes\n")
		sleep(2)
		port.write(b"vvdntech\n")
	elif "'s password:" in data:
		port.write(b"vvdntech\n")
		sleep(1)
	else:
		return
		
def transfer_complete(file1):
	x = file1
	size = subprocess.check_output("du -csh "+file1+" | grep total",stdin=subprocess.PIPE,stderr=subprocess.PIPE,shell=True).decode().split("\n")		

	if "out" in file1:
		if size >= size_out:
			return
		else:
			sleep(5)
			transfer_complete(x)

	if "in" in file1:
		if size >= size_in:
			return
		else:
			sleep(5)
			transfer_complete(x)

	if "left" in file1:
		if size >= size_left:
			return
		else:
			sleep(5)
			transfer_complete(x)

	if "right" in file1:
		if size >= size_right:
			return
		else:
			sleep(5)
			transfer_complete(x)

def run():
	global Sr_no
	global start
	global status_dict
	status_dict = {'inward':'PASS','outward':'PASS','left':'PASS','right':'PASS'}
	s = sr_no.get()
	Sr_no = validate_sr_no(s)
	text_box.config(state = tk.NORMAL)
	text_box.insert(tk.END, "Scanned Serial Number is "+Sr_no+" \nIt may take upto 60 seconds for streaming to start\nPess STOP button when done with validation!")
	text_box.config(state = tk.DISABLED)
	print(Sr_no)
	start = datetime.datetime.now()
	start_button.config(state = tk.DISABLED)
	root.update()
	conncetion_db()
	value = check_database()
	if value == "PASS":
		global port
		id =subprocess.getstatusoutput('sudo systemctl stop serial-getty@USB*.service')
		print(id)	
		retry=0
		port = port_conf(config)
		print('sr_port',port)
		if 'None' ==str(port):
			title = "Video validation"
			button = "Ok"
			messagebox.showinfo('information','USB cable not connect properly' )
		else:
			port.write("\n".encode('Ascii'))
			sleep(0.5)
			port.write("\n".encode('Ascii'))
			sleep(0.5)
			read = serial_read()
			print(read)
			data_write(read)
			global system_ip
			system_ip = get_system_ip(config[1])
			#Stop_button.config(state = tk.NORMAL)
			Next_button.config(state = tk.NORMAL)
			for i in range(0,4):
				if wifi_off():
					break
			os.system("nmcli d disconnect wlo1")
			wifi(ssid)
	else:
		start_button.config(state = tk.NORMAL)
		Sr_no_entry.delete("0",tk.END)
def wifi_off():
	os.system("nmcli d disconnect "+config[1])
	
	size = subprocess.check_output("nmcli radio wifi",stdin=subprocess.PIPE,stderr=subprocess.PIPE,shell=True).decode().split("\n")
	if "enabled" in size:
		return False
	else:
		return True
	
def dut_logs(text):	
	file_object = open('dut_logs.txt', 'a')
	for i in text:	
		file_object.write(i.decode())
	file_object.close()

def get_ip():
	port.write("ifconfig wlan0\n".encode()) #FIXME
	data = port.readlines() 
	ip = data[2].decode().split(":")[1].split(" ")[0].strip(" ")
	print(ip)
	return ip


ver_info = "1.0.8"

root = tk.Tk()
root.geometry("680x800")
root.title("NTDI_ICDC : LENS TUNING")

title = tk.Label(root, text = "BAGHEERA - Video Validation Stage" , fg = "Blue", font=("Times", 30, "bold"))
title.grid(row= 0, column = 0, columnspan = 4, rowspan = 2)


text_box = tk.Text(root,font=("Times", 12),fg = "blue", state = tk.DISABLED)
text_box.grid_propagate(False)
text_box.grid(row=4 ,column=0, columnspan = 4, ipadx = 20, ipady = 20, rowspan = 6) ####



sr_no = tk.StringVar()
sr_no_label = ttk.Label(root, text = " Device Serial: ")
sr_no_label.grid(row=3, column=0 , sticky = tk.W , pady =20)


Sr_no_entry = ttk.Entry(root, width=12, textvariable=sr_no)
Sr_no_entry.grid(row=3, column=0, sticky = tk.E , pady =20)
Sr_no_entry.focus()

Sr_no_entry.columnconfigure(0, weight = 1)

start_button = ttk.Button(root, text="Start" , command=run)
start_button.grid(row=3, column=1, sticky = tk.W , pady =20, padx=10)

start_button.columnconfigure(1, weight = 1)

version = tk.Label(root , text = " Ver :"+ver_info , fg = "blue", font=("Times", 10, "bold"))
version.grid(row=13, columnspan = 3, sticky = tk.W)

Next_button = ttk.Button(root, text="Next" , command=next, state = tk.DISABLED)
Next_button.grid(row=3, column=1, sticky = tk.E , pady =20, padx=10)

Stop_button = ttk.Button(root, text="Stop" , command=stop_button, state = tk.DISABLED)
Stop_button.grid(row=3, column=2, sticky = tk.W , pady =20, padx=10)

copyright = tk.Label(root , text = "(c) 2020 VVDN Technologies, Manesar, Haryana, India", bg ="white" , fg = "blue", font=("Times", 10, "bold"))
copyright.grid(row=10, columnspan = 5)

root.mainloop()
