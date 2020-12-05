from matrix_lite import led
from collections import deque
import time
import datetime
import pause
import wave
import pyaudio
import os
import sys
import socket
import logging

from math import pi, sin



def record2disk(self):

    recording_array = ['darkturquoise', 'black', 'black', 'black', 'black', 'darkturquoise', 'black', 'black', 'black', 'darkturquoise', 'black', 'black', 'black', 'darkturquoise', 'black', 'black', 'black',
                    'darkturquoise', 'black', 'black', 'black', 'darkturquoise', 'black', 'black', 'black', 'darkturquoise', 'black', 'black', 'black', 'darkturquoise', 'black', 'black', 'black', 'darkturquoise', 'black']

    buffer1 = deque([], 2)
    buffer2 = deque([], 2)

    print("starting recording..")

    everloop = ['black'] * led.length
    everloop[0] = 'darkturquoise'
    
    led_count = 1

    # pause here by offset so that all devices start recording together
    print(self.record_time_start)
    pause.until(time.time()+self.record_time_start)

    # recording Configs:
    CHUNK = 2048 #each chunk around 0.5 sec of audio
    FORMAT = pyaudio.paInt16
    CHANNELS = 8
    RATE = 16000  # SAMPLE RATE
    RECORD_SECONDS = 5
    mic = pyaudio.PyAudio()
    stream = mic.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True, frames_per_buffer=CHUNK)

    frames = []
    loop_counter = 0
    
    #setup logger and filehandler

    log_file = ("/home/pi/Desktop/recordings/logger" +socket.gethostname()+"_"+str(
        datetime.datetime.now().strftime('%Y-%m-%d_%H:%M'))+".log")
    log = logging.basicConfig(filename=log_file, level=logging.DEBUG)

    # code start here #

    print("current time is: ")
    start_time = time.time_ns()
    print(start_time)
    led.set(recording_array)
    

    
    logging.info('Start of loop execution time is :')
    logging.info(str(start_time))
    loop_time = start_time
    while(self.recording):


               
        #for logging drift
        logging.info('Loop %s time:',loop_counter)
        new_time = time.time_ns()
        new_time_monotonic = time.monotonic_ns() #to ensure execution without clock adjustment
        loop_start_time = new_time % 100000000000
        logging.info('loop started at non monotonic time %s',loop_start_time)
        print("loop time is "+str(loop_time))

        #pause code to correct drift goes here
        #pause.until()
        #int(RATE / CHUNK * RECORD_SECONDS)
        for i in range(0,10 ):
            data = stream.read(CHUNK) #exception_on_overflow = False
            frames.append(data)
            self.shared_buffer.append(data)

        print("recording in progress..")
        loop_counter += 1
        execution_time_monotonic = time.monotonic_ns()-new_time_monotonic
        
        logging.info('time to sleep is: %s',(1280000000-execution_time_monotonic)) 
        time.sleep((1280000000-execution_time_monotonic)/1000000000.0) #sleep for x 
        total_elapsed_time = time.monotonic_ns()-new_time_monotonic
        logging.info('this loop took %s to execute:',total_elapsed_time)
    else:
        print("stopping recording..")

        led.set(['green', 'black', 'black', 'black', 'black', 'black', 'black', 'green', 'black', 'black', 'black', 'black', 'black', 'black', 'green', 'black', 'black',
                    'black', 'black', 'black', 'black', 'green', 'black', 'black', 'black', 'black', 'black', 'black', 'green', 'black', 'black', 'black', 'black', 'black', 'black'])

    stream.stop_stream()
    stream.close()
    mic.terminate()
    filename = ("/home/pi/Desktop/recordings/recording_"+socket.gethostname()+"_"+str(
        datetime.datetime.now().strftime('%Y-%m-%d_%H:%M'))+".wav")
    self.session_file_list.append(filename)
    self.session_file_list.append(log_file)
    outputFile = wave.open(filename, 'wb')
    outputFile.setnchannels(CHANNELS)
    outputFile.setsampwidth(mic.get_sample_size(FORMAT))
    outputFile.setframerate(RATE)
    outputFile.writeframes(b''.join(frames))
    outputFile.close()
    
    print("Recording successfully saved!")

    

    
    #led.set(['blue', 'black', 'black', 'black', 'black', 'black', 'black', 'blue', 'black', 'black', 'black', 'black', 'black', 'black', 'blue', 'black', 'black',
    #            'black', 'black', 'black', 'black', 'blue', 'black', 'black', 'black', 'black', 'black', 'black', 'blue', 'black', 'black', 'black', 'black', 'black', 'black'])
    while self.beamforming_processing_flag == True:
        temp_list = self.green[:]
        led.set(temp_list)
        time.sleep(0.25)
        led.set('black')
        temp_head = temp_list.pop(0)
        temp_list.append(temp_head)
        #print(temp_list)
        time.sleep(0.25)
        self.green=temp_list[:]
    sys.exit()  # deletes this thread safely
