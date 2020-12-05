import threading
import subprocess
import os
import socket
import socketserver
import sys
import time
import pyaudio
import atexit
import wave
import datetime
import webrtcvad
import pause
from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth

from tcp_sync import tcpSlave
from upload import upload_file
from multirec import record2disk
from voice_activity_detection import vad_record
from DOA import beamformer


import pickle
from math import pi, sin
from matrix_lite import led
from collections import deque

# run on python3
# for clients


class Main(threading.Thread):

    def __init__(self):

        threading.Thread.__init__(self)

        # initialize color arrays

        self.green = ['green', 'black', 'black', 'black', 'black', 'black', 'black', 'green', 'black', 'black', 'black', 'black', 'black', 'black', 'green', 'black', 'black',
                      'black', 'black', 'black', 'black', 'green', 'black', 'black', 'black', 'black', 'black', 'black', 'green', 'black', 'black', 'black', 'black', 'black', 'black']
        self.red = ['red', 'black', 'black', 'black', 'black', 'black', 'black', 'red', 'black', 'black', 'black', 'black', 'black', 'black', 'red', 'black', 'black',
                    'black', 'black', 'black', 'black', 'red', 'black', 'black', 'black', 'black', 'black', 'black', 'red', 'black', 'black', 'black', 'black', 'black', 'black']
        self.blue = ['blue', 'black', 'black', 'black', 'black', 'black', 'black', 'blue', 'black', 'black', 'black', 'black', 'black', 'black', 'blue', 'black', 'black',
                     'black', 'black', 'black', 'black', 'blue', 'black', 'black', 'black', 'black', 'black', 'black', 'blue', 'black', 'black', 'black', 'black', 'black', 'black']
        self.blue2 = ['black', 'black', 'black', 'blue', 'black', 'black', 'black', 'black', 'black', 'black', 'blue', 'black', 'black', 'black', 'black', 'black', 'black',
                      'blue', 'black', 'black', 'black', 'black', 'black', 'black', 'blue', 'black', 'black', 'black', 'black', 'black', 'black', 'blue', 'black', 'black', 'black']
        self.gold = [(255, 215, 0), 'black', 'black', 'black', 'black', 'black', 'black', (255, 215, 0), 'black', 'black', 'black', 'black', 'black', 'black', (255, 215, 0), 'black', 'black',
                     'black', 'black', 'black', 'black', (255, 215, 0), 'black', 'black', 'black', 'black', 'black', 'black', (255, 215, 0), 'black', 'black', 'black', 'black', 'black', 'black']
        self.pink = [(255, 153, 153), 'black', 'black', 'black', 'black', 'black', 'black', (255, 153, 153), 'black', 'black', 'black', 'black', 'black', 'black', (255, 153, 153), 'black', 'black',
                     'black', 'black', 'black', 'black', (255, 153, 153), 'black', 'black', 'black', 'black', 'black', 'black', (255, 153, 153), 'black', 'black', 'black', 'black', 'black', 'black']
        self.purple = [(200, 0, 200, 0), 'black', 'black', 'black', 'black', 'black', 'black', (200, 0, 200, 0), 'black', 'black', 'black', 'black', 'black', 'black', (200, 0, 200, 0), 'black',
                       'black', 'black', 'black', 'black', 'black', (200, 0, 200, 0), 'black', 'black', 'black', 'black', 'black', 'black', (200, 0, 200, 0), 'black', 'black', 'black', 'black', 'black', 'black']
        self.purple2 = ['black', 'black', 'black', (200, 0, 200, 0), 'black', 'black', 'black', 'black', 'black', 'black', (200, 0, 200, 0), 'black', 'black', 'black', 'black', 'black',
                        'black', (200, 0, 200, 0), 'black', 'black', 'black', 'black', 'black', 'black', (200, 0, 200, 0), 'black', 'black', 'black', 'black', 'black', 'black', (200, 0, 200, 0), 'black', 'black', 'black']

        self.status = 'I'  # initialized to Idle state
        self.offset = 0
        self.network_available = False  # to check if wifi connections are available
        # flag to check if current pimatrix device is connected or not
        self.pc_connected = False
        self.TCP_IP = "0.0.0.0"
        self.TCP_PORT = 8000
        self.mutex = threading.Lock()
        self.recording = False  # flag for starting and stopping recording
        self.commandArgument = ''
        self.connection = False  # flag to check if pimatrix device is connected to a network
        self.record_time_start = 0
        self.sync_vad_flag = False  # flag to coordinate synced vad
        self.udpConnection = None  # reference UDP Connection
        self.controller_ip = None  # Store ip address of controller phone/device
        # to store all files created in this session to use to upload later
        self.session_file_list = []
        self.drive = None #to be authenticated
        self.shared_buffer = deque([]) # to share audio data among threads
        self.beamforming_processing_flag = False

        while (self.connection == False):
            ps = subprocess.Popen(
                ['iwgetid'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            try:
                output = subprocess.check_output(
                    ('grep', 'ESSID'), stdin=ps.stdout)
                print(output)
                self.connection = True
                ntp_loop = ["black"] * led.length
                ntp_loop[0] = 'pink'
                led.set(ntp_loop)
                
                sub1 = subprocess.Popen(["sudo chronyc -a 'burst 4/4'"], shell=True)
                sub1.wait()
                time.sleep(10)
                sub3 = subprocess.Popen(["sudo chronyc -a 'makestep'"], shell=True)
                sub3.wait()
                
                led.set(self.gold)
            except subprocess.CalledProcessError:
                print("No wireless networks connected")
                led.set(self.red)
                time.sleep(0.5)
                led.set('black')
                time.sleep(0.5)
                led.set(self.red)

        atexit.register(self.script_exit)

        # called by main program to keep this class running

    def keep_main_alive(self):

        while True:
            time.sleep(1)

    def initialize_threads(self):

        # thread creation
        UDP_server_thread = threading.Thread(
            target=self.udpBroadcastReceiver, name="UDP_server_thread")
        TCP_server_thread = threading.Thread(
            target=self.tcpReceiver, name="TCP_server_thread")

        kill_thread = threading.Thread(
            target=self.kill_script, name="kill_thread")

        TCP_sync_thread = threading.Thread(
            target=tcpSlave, args=[self], name="TCP_sync_thread")

        # set threads as Daemons
        UDP_server_thread.daemon = True
        TCP_server_thread.daemon = True
        TCP_sync_thread.daemon = True
        kill_thread.daemon = True

        # start threads
        UDP_server_thread.start()
        TCP_server_thread.start()
        TCP_sync_thread.start()
        kill_thread.start()

    def script_exit(self):
        
        led.set('black')
        

    def call_hotword(self):
        led.set('black')
        os.system('python3 /home/pi/Desktop/PiMatrix_firmware/PiMatrix/wakeword/Snowboy/wakeword.py &')

    def kill_script(self):

        while True:
            key = input("Type esc to end the program: \n")
            if (key == "esc"):
                print("terminating script...")
                self.script_exit()
                os._exit(1)
            elif (key == "restart"):
                self.call_hotword()
                os._exit(1)

    def udpBroadcastReceiver(self):

        ### Waits for the appropriate signal and then responds to the sender of that signal ###
        ### Used for Initial connection ###
        hostname = socket.gethostname()
        UDP_IP = "0.0.0.0"
        UDP_PORT = 8001
        UDPServer = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        UDPServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        UDPServer.bind((UDP_IP, UDP_PORT))

        self.udpConnection = UDPServer

        print("%s UDP server listening on port 8001" % hostname)

        while True:
            try:
                data, addr = UDPServer.recvfrom(32)
                trimdata = data.decode("UTF-8").rstrip()
                print(trimdata)
                client_IP = addr[0]
                client_PORT = addr[1]
                print(addr)
                self.controller_ip = client_IP
                if((self.pc_connected == False) & (trimdata == 'live long and prosper')):
                    print("Remote PC at %s " % client_IP)
                    reply = str.encode("peace and long life"+"|"+str(hostname))
                    UDPServer.sendto(reply, addr)
                    led.set(self.green)
                    time.sleep(1)
                    led.set('black')
                    time.sleep(1)
                    led.set(self.green)

                    ### authenticate to gdrive ###
                    try:
                        gauth = GoogleAuth()
                        gauth.LoadCredentialsFile(
                            "/home/pi/Desktop/mycreds.txt")
                        if gauth.credentials is None:
                            # Authenticate if they're not there
                            gauth.LocalWebserverAuth()
                        elif gauth.access_token_expired:
                            # Refresh them if expired
                            gauth.Refresh()
                        else:
                            # Initialize the saved creds
                            gauth.Authorize()
                        # Save the current credentials to a file
                        gauth.SaveCredentialsFile(
                            "/home/pi/Desktop/mycreds.txt")
                        self.drive = GoogleDrive(gauth)

                    except:
                        print("authentication error!")

            except socket.timeout:
                print()

    def tcpReceiver(self):

        hostname = socket.gethostname()
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        tcp_socket.bind((self.TCP_IP, self.TCP_PORT))
        tcp_socket.listen(1)
        while True:
            print("TCP waiting for connection at port 8000")
            tcp_connection, tcp_client = tcp_socket.accept()
            # print(tcp_client)
            print("accepted connection from " + tcp_client[0])
            if(tcp_connection):
                self.pc_connected = True
                sysInfo = (self.status + hostname).encode('utf-8')
                tcp_connection.send(sysInfo)
                while True:
                    # led.set(self.gold)
                    data = tcp_connection.recv(4096)
                    command = str(data.decode())
                    command_array = command.split("|")
                    command = command_array[0]
                    extra_param = 0

                    if (len(command_array) > 1):
                        try:
                            extra_param = float(command_array[1])
                        except:
                            flush_data = tcp_connection.recv(200000)

                    print(command)
                    if (command == 'N'):

                        if (self.status == 'I'):
                            self.status = 'N'
                            print("start recorder thread")
                            temp_commandArgument = tcp_connection.recv(
                                64, socket.MSG_WAITALL)
                            print(temp_commandArgument)

                    elif (command == 'L'):
                        # Record Command
                        if (self.status == 'I'):
                            self.status = "L"
                            print("start record to disk thread")
                            if (extra_param != 0):
                                self.record_time_start = extra_param
                            self.recording = True
                            record2disk_thread = threading.Thread(
                                target=record2disk,args=[self], name="record2disk_thread")
                            #beamformer_thread = threading.Thread(
                            #    target=beamformer.beamform,args=[self],name="beamformer_thread")
                            
                            record2disk_thread.daemon = True
                            #beamformer_thread.daemon = True
                            record2disk_thread.start()
                            #beamformer_thread.start()
                            
                            print("recording initiated")

                    elif (command == 'F'):
                        # vad sync flag
                        if(self.status == "V"):
                            print("received VAD sync flag")  # testing
                            if (extra_param != 0):
                                self.record_time_start = extra_param
                                pause.until(time.time()+self.record_time_start)
                                self.sync_vad_flag = True

                    elif (command == "V"):
                        # Live VAD record Command
                        if(self.status == "I"):
                            self.status = "V"
                            print("Start VAD live record")
                            self.recording = True
                            vad_thread = threading.Thread(
                                target=vad_record,args=[self], name="vad_thread")
                            vad_thread.daemon = True
                            vad_thread.start()

                    elif (command == 'G'):
                        if(self.status == "I"):
                            self.status = "G"
                            upload_file(self)
                            self.status = "I"

                    elif (command == 'I'):
                        # stop command
                        print("Stopping...")
                        self.recording = False
                        self.status = 'I'

                    elif (command == 'S'):
                        # sync command
                        print("Syncing...")
                        led.set(self.red)

                    elif (command == 'T'):
                        # shutdown command
                        print("Shutting Down...")
                        led.set(self.red)
                        time.sleep(1)
                        self.script_exit()
                        os._exit(1)

                    else:
                        print("Error input, waiting for next input ")





if __name__ == "__main__":
    realRun = Main()
    realRun.initialize_threads()
    realRun.keep_main_alive()


# 1.1 : Implemented double buffer with deques
# 1.2 : Implemented VAD record thread
# 1.3 : Implemented Sync Functionality
# 1.4 : Implemented Sync VAD Functionality
# 1.5 : Implemented OAuth and upload file to server
# 1.6 : Implemented Wake word
# 1.7 : Implemented DOA and Beamformer

# TODO:




