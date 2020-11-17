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
    led.set(recording_array)
    while(self.recording):

 
        

        #time.sleep(.035)

        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            buffer1.append(data)
            if len(buffer1) == 2:
                
                buffer2.append(buffer1.popleft())

            if len(buffer2) == 2:
                streamdata = buffer2.popleft()  # this data to be used by any processing thread
                frames.append(streamdata)
                self.shared_buffer.append(streamdata)

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
