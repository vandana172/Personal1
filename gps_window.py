from serial.tools import list_ports
import time
import datetime
from serial import *
import psycopg2
import easygui
import tkinter as tk
from threading import *
import yaml
import shutil
import os


class DUT:
    def __init__(self):
        self.path_file = ""
        self.config = ""
        self.read_config()
        self.port = ""
        self.result = ""
        self.logs = ""
        self.start_time = datetime.datetime.now()
        self.sr_no = ""
        self.port_conf()
        self.logs_db = ""
        self.run_level = ""


    def read_config(self):
        with open("config.yaml") as file:
            self.config = yaml.load(file, Loader=yaml.FullLoader)


    def port_conf(self):
        try:
            for port,desc,hwid in list_ports.comports():
                #print(port)
                #print(hwid)
                if self.config["HWID"] in hwid:
                    self.port = Serial (port = port, baudrate = 115200, bytesize = EIGHTBITS, parity =PARITY_NONE,stopbits = STOPBITS_ONE , timeout = 3, xonxoff=False, rtscts=False, writeTimeout=None, dsrdtr=False,interCharTimeout=None)
        except Exception as e:
            print("Unable to open communication with DUT because ", e)

    def update_database(self):
        conn = ""
        try:
            conn = psycopg2.connect(database = "postgres", user = "postgres", host="172.17.16.200", port=5432, password = "postgres")
            print ("Opened database successfully")
            cur = conn.cursor()
            insert_query = """INSERT INTO gps_stage (enclosure_no , start_time , end_time , global_status , log) values (%s,%s,%s,%s,%s)"""
            insert_values = (self.sr_no,self.start_time,datetime.datetime.now(),self.result,self.logs_db)
            print(insert_query,insert_values)
            cur.execute(insert_query,insert_values)
            conn.commit()
        except Exception as e:
            print("Unable to update database because ", e)
        finally:
            if conn != "":
                conn.close()
                print("db connection closed!")
    
    def port_write(self,command):
        try:
            command = command.encode()
            self.port.write(command+b"\n")
        except Exception as e:
            print("Unable to write to dut because ", e)

    def port_rl(self):
        try:
            d_data = []
            data = self.port.readlines()
            for i in data:
                i = i.decode()
                d_data.append(i)
            return d_data
        except Exception as e:
            print("Unable to readlines because " , e)
        
    def port_r(self, timeout):
        cr_time = time.time()
        data = ""
        try:
            while True:
                if (self.port.in_waiting>0):
                    read = self.port.read(self.port.in_waiting)
                data = data + read
                if cr_time + int(timeout) < time.time():
                    break
            return data
        except Exception as e:
            print("Unable to read data because ", e)

def login(obj):
    obj.port_write("\n")
    time.sleep(1)
    #tim = time.time()
    while True:
        obj.port_write("\n")
        time.sleep(2)
        resp = obj.port_rl()
        print(resp)
        if "tegra-ubuntu login:" in resp[-1]:
            obj.port_write("ubuntu")
            time.sleep(0.5)
            obj.port_write("ubuntu")
        elif "ubuntu@tegra-ubuntu:~$" in resp[-1]:
            obj.port_write("sudo su")
            time.sleep(1)
            obj.port_write("ubuntu")
        elif "Password"in resp[-1]:
            obj.port_write("\n")
            time.sleep(0.5)
        elif "root@tegra-ubuntu:/home/ubuntu#" in resp[-1]:
            return True
        else:
            print("Device not responing!")
            output = easygui.ynbox("Do you want to retry", "Device not responding!")
            if output != True:
                sys.exit(-1)
            else:
                Thread(target=init_window).start()


def enable_gps(obj):
    obj.port_write("lte_gps_test 'at!gpsautostart=1,1,255,100,1'")
    time.sleep(2)
    data = obj.port_rl()
    print(data)
    obj.logs = obj.logs + "\n".join(data)
    obj.port_write("lte_gps_test 'at!gpsonly=1'")
    time.sleep(2)
    obj.port_write("lte_gps_test 'at!RESET'")
    time.sleep(2)
    data = obj.port_rl()
    print(data)
    for i in data:
        if "OK" in i:
            return True
    return False

def gps_status(obj):
    var = 0
    obj.port_write("lte_gps_test 'at!gpsstatus?'")
    time.sleep(2)
    data = obj.port_rl()
    print(data)
    obj.logs = obj.logs + "\n".join(data)
    for line in data:
        if "Fix Session Status = ACTIVE" in line:
            #obj.logs_db = obj.logs_db + line
            var+=1
        if "No TTFF available" in line:
            #obj.logs = obj.logs_db + line
            obj.result = "FAIL"
            return True
    obj.port_write("lte_gps_test 'at!gpssatinfo?'")
    time.sleep(2)
    data = obj.port_rl()
    print(data)
    obj.logs = obj.logs + "\n".join(data)
    for line in data:
        if "Satellites in view" in line:
            #obj.logs_db = obj.logs_db + line
            
            line = line.split(":")[1].split("(")[0].strip()
            print("No. of satellites ",line)
            if int(line) > 8:
                var+=1

    obj.port_write("lte_gps_test 'at!gpsloc?'")
    time.sleep(2)
    data = obj.port_rl()
    obj.logs = obj.logs + "\n".join(data)
    print(data)       
    for line in data:
        if "HEPE:" in line:
            obj.logs_db =  line
            line = line.split("HEPE:")[1].strip().split(" ")[0]
            print("HEPE value is : ",line)
            if float(line) < 8:
                var+=1
    if var == 3:
        obj.result = "PASS"
    else:
        obj.result = "FAIL"
    return True

def validate_sr_no(obj):
    global serial_no_box
    obj.sr_no = serial_no_box.get().split(",")[0].split(":")[1]
    show_text(obj.sr_no)
    conn = ""
    try:
        conn = psycopg2.connect(database = "postgres", user = "postgres", host="172.17.16.200", port=5432, password = "postgres")
        print ("Opened database successfully")
        cur = conn.cursor()
        cur.execute("SELECT status FROM \"VideoValidation\" WHERE enclosure_no = '{}' ORDER BY id DESC LIMIT 1".format(obj.sr_no))
        content = cur.fetchall()
        cur.execute("SELECT * FROM gps_stage WHERE enclosure_no = '{}' ORDER BY id DESC LIMIT 1".format(obj.sr_no))
        content1 = cur.fetchall()
        content1 = len(obj.run_level)
        obj.run_level = str(obj.run_level)
    except Exception as e:
        print("Unable to update database because ", e)
    finally:
        if conn != "":
            conn.close()
            print("db connection closed!")

    content = content [0]
    if content[0].upper() == 'PASS':
        return True
    else:
        return False

def start():
    global serial_no_box
    #Lock.acquire()
    obj = DUT()
    obj.logs_db = ""
    obj.logs = str(datetime.datetime.now()) + "\n" 
    obj.result = "FAIL"
    obj.sr_no = ""
    status = validate_sr_no(obj)
    if status != True:
        easygui.msgbox("Unable to Validate Sr no. Please try again", "ERROR!")
        init_window()
    status = ""
    if obj.port != "":
        if login(obj) != True:
            easygui.msgbox("Unable to login into to Please try again", "ERROR!")
        #if enable_gps(obj) == True:
        #else:
        #    easygui.msgbox("Unable to login into to Please try again", "ERROR!")
        for i in range(int(obj.config['RETRY'])):
            time.sleep(int(obj.config['SLEEP_TIME']))
            status = gps_status(obj)
            if obj.result == "PASS":
                break
    else:
        print("Could not open port")
    print(obj.logs)
    mount_z()
    create_log_folder(obj)
    copy_folder_to_server(obj)
    obj.update_database()
    if obj.result == "PASS":
        easygui.msgbox("TEST PASS", "RESULT!")
    else:
        easygui.msgbox("TEST FAIL", "RESULT!")
    obj = ""
    print("New Test")
    canvas1.destroy()
    Thread(target=init_window).start()
    serial_no_box.delete('0',tk.END)


def copy_folder_to_server(obj):
    date = date = datetime.datetime.now()
    date = date.strftime("%m-%d-%Y")

    if os.path.isdir("Z:\\"+obj.result) == False:
        os.mkdir("Z:\\"+obj.result)

    if os.path.isdir("Z:\\"+obj.result+"/"+date) == False:
        os.mkdir("Z:\\"+obj.result+"/"+date)

    if os.path.isdir("Z:\\"+obj.result+"/"+date+"/"+obj.sr_no) == False:
        os.mkdir("Z:\\"+obj.result+"/"+date+"/"+obj.sr_no)
    os.system("del Z:\\"+obj.result+"/"+date+"/"+obj.sr_no+"/*")
    shutil.copyfile(obj.path_file+"/"+obj.sr_no+".txt", "Z:\\"+obj.result+"/"+date+"/"+obj.sr_no+"/"+obj.sr_no+".txt")


def create_log_folder(obj):
    date = date = datetime.datetime.now()
    date = date.strftime("%m-%d-%Y")
    if os.path.isdir("Logs/"+obj.result) == False:
        os.mkdir("Logs/"+obj.result)

    if os.path.isdir("Logs/"+obj.result+"/"+date) == False:
        os.mkdir("Logs/"+obj.result+"/"+date)

    if os.path.isdir("Logs/"+obj.result+"/"+date+"/"+obj.sr_no) == False:
        os.mkdir("Logs/"+obj.result+"/"+date+"/"+obj.sr_no)
    
    obj.path_file = "Logs/"+obj.result+"/"+date+"/"+obj.sr_no

    with open(obj.path_file+"/"+obj.sr_no+".txt", "a+") as myfile:
        myfile.write(obj.logs)

def mount_z():

	cmd_parts = "net use Z: \\\\172.17.16.200\\NTDI_PTS1_Shared_dir\\NTDI_PTS1_Server\\NTDI_PTS1_Reports\\Box_level_test\\GPS_logs /user:NTDISERVER vvdn@1234"
	print(cmd_parts)
	os.system(cmd_parts)


def show_text(txt, colour='black'):
    global width
    width = 180
    label = tk.Label(root, text= txt, font=('arial', 12))
    label.config(fg=colour, bg="white")
    canvas1.create_window(500, width, window=label)
    width += 30


def init_window():

    global serial_no_box, canvas1, label, txt, width

    width = 180

    canvas1 = tk.Canvas(root, width = 1320, height = 1080)
    canvas1.pack()
    label1 = tk.Label(root, text="GPS TEST" , fg='blue', font=('arial', 24,'bold'))
    canvas1.create_window(550, 30, window=label1)
    label = tk.Label(text=time.strftime("%d-%b-%y %H:%M:%S"), fg='blue', font=('arial', 12))
    update_clock()
    label2 = tk.Label(root, text="PTS App version : " + app_version, fg='blue', font=('arial', 12))
    canvas1.create_window(1200, 50, window=label2)
    label3 = tk.Label(root, text='Enclosure number', font=('arial', 14))
    canvas1.create_window(100, 180, window=label3)
    serial_no_box = tk.Entry(root, font=('arial', 12))
    serial_no_box.config(width=12)
    serial_no_box.focus_set()    
    canvas1.create_window(100, 210, window=serial_no_box)
    start_button = tk.Button(text='Start', command=start, font=('arial', 12, 'bold'))
    start_button.config(width=10)
    canvas1.create_window(100, 250, window=start_button)
    txt = tk.Text(root, height = 34, width= 110)
    txt.config(state="disabled")
    canvas1.create_window(700, 400, window=txt)
    show_text("Scan Enclosure serial number and start test","blue")

def update_clock():

    global label

    label.configure(text=time.strftime("%d-%b-%y %H:%M:%S"), fg='blue', font=('arial', 12))
    canvas1.create_window(1200, 20, window=label)
    root.after(1000, update_clock)

if __name__ == "__main__":
    serial_no = 0
    app_version = '1.0.0'
    serial_no_box = canvas1 = start_time = ''

    root= tk.Tk()
#    print(config_data)
    root.title("NTDI_ICDC")
    #root.wm_iconbitmap('VVDN_logo.ico')
    init_window()
    root.mainloop()
          
