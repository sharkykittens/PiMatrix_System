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

from .tcp_sync import tcpSlave


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

        while (self.connection == False):
            ps = subprocess.Popen(
                ['iwgetid'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            try:
                output = subprocess.check_output(
                    ('grep', 'ESSID'), stdin=ps.stdout)
                print(output)
                self.connection = True
                sub1 = subprocess.Popen(['sudo service ntp stop'], shell=True)
                sub1.wait()
                sub2 = subprocess.Popen(
                    ['sudo ntpdate -s time.nist.gov'], shell=True)
                sub2.wait()
                sub3 = subprocess.Popen(['sudo service ntp start'], shell=True)
                sub3.wait()
                ntp_loop = ["black"] * led.length
                for x in range(35):
                    ntp_loop[x] = 'pink'
                    led.set(ntp_loop)
                    time.sleep(1.5)
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
            target=tcpSlave(), name="TCP_sync_thread")

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

    def kill_script(self):

        while True:
            key = input("Type esc to end the program: \n")
            if (key == "esc"):
                print("terminating script...")
                self.script_exit()
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
                                target=self.record2disk, name="record2disk_thread")
                            record2disk_thread.daemon = True
                            record2disk_thread.start()

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
                                target=self.vad_record, name="vad_thread")
                            vad_thread.daemon = True
                            vad_thread.start()

                    elif (command == 'G'):
                        if(self.status == "I"):
                            self.status = "G"
                            self.upload_file()
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

    def vad_record(self):

        class Frame(object):
            """Represents a "frame" of audio data. Duration of frame must be 10,20 or 30"""

            def __init__(self, bytes, timestamp, duration):
                self.bytes = bytes
                self.timestamp = timestamp
                self.duration = duration

        def frame_generator(frame_duration_ms, audio, sample_rate):
            """Generates audio frames from PCM audio data.

            Takes the desired frame duration in milliseconds, the PCM data, and
            the sample rate.

            Yields Frames of the requested duration.
            """
            n = int(sample_rate * (frame_duration_ms / 1000.0) * 2)
            offset = 0
            timestamp = 0.0
            duration = (float(n) / sample_rate) / 2.0
            while offset + n < len(audio):
                yield Frame(audio[offset:offset + n], timestamp, duration)
                timestamp += duration
                offset += n

        def output_frame(timestamp, frame_array, CHANNELS, FORMAT, RATE):

            filename = ("/home/pi/Desktop/recordings/VAD_"+socket.gethostname() +
                        "_"+timestamp+".wav")

            self.session_file_list.append(filename)
            output = wave.open(filename, 'wb')
            output.setnchannels(CHANNELS)
            output.setsampwidth(mic.get_sample_size(FORMAT))
            output.setframerate(RATE)
            output.writeframes(b''.join(frame_array))
            output.close()
            print("VAD Chunk " + timestamp + " successfully saved!")

        buffer1 = deque([], maxlen=2)
        buffer2 = deque([], maxlen=2)

        print("starting recording..")
        # wait till offset to synchronize across all devices
        print(self.record_time_start)
        pause.until(time.time()+self.record_time_start)

        # VAD udp server
        UDP_IP = "0.0.0.0"
        UDP_VAD_PORT = 8641
        UDPVAD = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        UDPVAD.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        UDPVAD.bind((UDP_IP, 8641))

        # recording Configs:
        CHUNK = 2048
        FORMAT = pyaudio.paInt16
        CHANNELS = 8
        RATE = 16000  # SAMPLE RATE
        RECORD_SECONDS = 5
        mic = pyaudio.PyAudio()
        stream = mic.open(format=FORMAT, channels=CHANNELS,
                          rate=RATE, input=True, frames_per_buffer=CHUNK)
        collected_VAD = []  # buffer to store collected frames
        # stores up to 500 previous frames or about 1 second worth of audio data
        past_frames = deque([], maxlen=500)
        empty_frame_counter = 0
        frame_flag = False  # represents that the a current set of recording is ongoing
        framesgenerated = []
        last_empty_frame = b''
        vad = webrtcvad.Vad(3)
        status = 0
        # variable to be used to mark timestamps for VAD recordings
        timestamp = str(datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S'))

        while(self.recording):
            for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                data = stream.read(CHUNK)
                buffer1.append(data)
                if len(buffer1) == 2:

                    buffer2.append(buffer1.popleft())
                if len(buffer2) == 2:
                    streamdata = buffer2.popleft()  # this data to be used by any processing thread
                    framesgenerated = frame_generator(20, streamdata, RATE)
                    framesgenerated = list(framesgenerated)

                for frame in framesgenerated:
                    past_frames.append(frame.bytes)
                    speech_frame = vad.is_speech(frame.bytes, RATE)

                    if(speech_frame == True):
                        # when speech is detected, send a signal to the controller

                        UDPVAD.sendto('activate_VAD'.encode(),
                                      (self.controller_ip, UDP_VAD_PORT))

                    if(self.sync_vad_flag == True):
                        if(speech_frame != True):
                            empty_frame_counter = empty_frame_counter + 1
                        else:
                            # reset if no subsequent chain of empty frames
                            empty_frame_counter = 0

                        if(empty_frame_counter > 1000):
                            self.sync_vad_flag = False

                        led.set(self.green)
                        if(frame_flag == False):
                            timestamp = str(
                                datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S'))
                            led.set(self.green)
                            collected_VAD.extend(past_frames)
                            past_frames.clear()
                            # collected_VAD.append(last_empty_frame)
                            print("3", end='')
                            collected_VAD.append(frame.bytes)
                            print("1", end='')

                            frame_flag = True
                        else:
                            collected_VAD.append(frame.bytes)
                            print("1", end='')

                    else:
                        if(empty_frame_counter > 1000):
                            frame_flag = False
                            empty_frame_counter = 0
                            led.set('black')
                            print("0", end='')
                            frame_array = collected_VAD.copy()
                            output_frame(timestamp, frame_array,
                                         CHANNELS, FORMAT, RATE)
                            collected_VAD = []
                            past_frames.append(frame.bytes)

                            #last_empty_frame = frame.bytes

            print("recording in progress..")

        else:
            print("stopping recording..")
            while buffer2:
                collected_VAD.append(buffer2.popleft())
            led.set(['green', 'black', 'black', 'black', 'black', 'black', 'black', 'green', 'black', 'black', 'black', 'black', 'black', 'black', 'green', 'black', 'black',
                     'black', 'black', 'black', 'black', 'green', 'black', 'black', 'black', 'black', 'black', 'black', 'green', 'black', 'black', 'black', 'black', 'black', 'black'])

        stream.stop_stream()
        stream.close()
        mic.terminate()
        filename = ("/home/pi/Desktop/recordings/VAD_"+socket.gethostname()+"_" +
                    str(datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S'))+".wav")
        self.session_file_list.append(filename)
        outputFile = wave.open(filename, 'wb')
        outputFile.setnchannels(CHANNELS)
        outputFile.setsampwidth(mic.get_sample_size(FORMAT))
        outputFile.setframerate(RATE)
        outputFile.writeframes(b''.join(collected_VAD))
        outputFile.close()
        print("Recording successfully saved!")
        time.sleep(2)
        led.set(['blue', 'black', 'black', 'black', 'black', 'black', 'black', 'blue', 'black', 'black', 'black', 'black', 'black', 'black', 'blue', 'black', 'black',
                 'black', 'black', 'black', 'black', 'blue', 'black', 'black', 'black', 'black', 'black', 'black', 'blue', 'black', 'black', 'black', 'black', 'black', 'black'])

        sys.exit()  # deletes this thread safely

    def record2disk(self):

        buffer1 = deque([], 2)
        buffer2 = deque([], 2)

        print("starting recording..")

        everloop = ['black'] * led.length
        ledAdjust = 0.0
        if len(everloop) == 35:
            ledAdjust = 0.51  # MATRIX Creator
        else:
            ledAdjust = 1.01  # MATRIX Voice

        frequency = 0.375
        counter = 0.0
        tick = len(everloop) - 1

        # pause here by offset so that all devices start recording together
        print(self.record_time_start)
        pause.until(time.time()+self.record_time_start)

        # recording Configs:
        CHUNK = 2048
        FORMAT = pyaudio.paInt16
        CHANNELS = 8
        RATE = 16000  # SAMPLE RATE
        RECORD_SECONDS = 5
        mic = pyaudio.PyAudio()
        stream = mic.open(format=FORMAT, channels=CHANNELS,
                          rate=RATE, input=True, frames_per_buffer=CHUNK)

        frames = []
        print("current time is: ")
        print(time.time())
        while(self.recording):

            for i in range(len(everloop)):
                r = round(
                    max(0, (sin(frequency*counter+(pi/180*240))*155+100)/10))
                g = round(
                    max(0, (sin(frequency*counter+(pi/180*120))*155+100)/10))
                b = round(max(0, (sin(frequency*counter)*155+100)/10))

                counter += ledAdjust

                everloop[i] = {'r': r, 'g': g, 'b': b}

            # Slowly show rainbow
            if tick != 0:
                for i in reversed(range(tick)):
                    everloop[i] = {}
                tick -= 1

            led.set(everloop)

            time.sleep(.035)

            for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                data = stream.read(CHUNK)
                buffer1.append(data)
                if len(buffer1) == 2:

                    buffer2.append(buffer1.popleft())
                if len(buffer2) == 2:
                    streamdata = buffer2.popleft()  # this data to be used by any processing thread
                    frames.append(streamdata)

            print("recording in progress..")

        else:
            print("stopping recording..")
            while buffer2:
                frames.append(buffer2.popleft())
            led.set(['green', 'black', 'black', 'black', 'black', 'black', 'black', 'green', 'black', 'black', 'black', 'black', 'black', 'black', 'green', 'black', 'black',
                     'black', 'black', 'black', 'black', 'green', 'black', 'black', 'black', 'black', 'black', 'black', 'green', 'black', 'black', 'black', 'black', 'black', 'black'])

        stream.stop_stream()
        stream.close()
        mic.terminate()
        filename = ("/home/pi/Desktop/recordings/recording_"+socket.gethostname()+"_"+str(
            datetime.datetime.now().strftime('%Y-%m-%d_%H:%M'))+".wav")
        self.session_file_list.append(filename)
        outputFile = wave.open(filename, 'wb')
        outputFile.setnchannels(CHANNELS)
        outputFile.setsampwidth(mic.get_sample_size(FORMAT))
        outputFile.setframerate(RATE)
        outputFile.writeframes(b''.join(frames))
        outputFile.close()
        print("Recording successfully saved!")
        time.sleep(2)
        led.set(['blue', 'black', 'black', 'black', 'black', 'black', 'black', 'blue', 'black', 'black', 'black', 'black', 'black', 'black', 'blue', 'black', 'black',
                 'black', 'black', 'black', 'black', 'blue', 'black', 'black', 'black', 'black', 'black', 'black', 'blue', 'black', 'black', 'black', 'black', 'black', 'black'])

        sys.exit()  # deletes this thread safely

    def upload_file(self):
        # Find the specific file ID you want
        fileList = self.drive.ListFile(
            {'q': "'root' in parents and trashed=false"}).GetList()
        for file in fileList:
            print('Title: %s, ID: %s' % (file['title'], file['id']))
            # Get the folder ID that you want
            if(file['title'] == "FYP_PiMatrix_Recordings"):
                fileID = file['id']
        led.set(self.purple)
        for filename in self.session_file_list:
            file_title = filename[28:]
            audiofile = self.drive.CreateFile(
                {'parents': [{'id': fileID}], 'title': file_title})
            audiofile.SetContentFile(filename)
            try:
                audiofile.Upload()
            except:
                print("error uploading file")
                led.set(self.red)

        print("Uploading completed!")
        led.set(self.blue)


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

# TODO:
