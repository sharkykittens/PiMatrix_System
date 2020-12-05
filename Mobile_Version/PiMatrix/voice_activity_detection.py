
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
import pickle
import webrtcvad
from math import pi, sin

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

        

        #Configuration Code starts here

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
        CHUNK = 3840
        FORMAT = pyaudio.paInt16
        CHANNELS = 8
        RATE = 16000  # SAMPLE RATE
        RECORD_SECONDS = 5
        mic = pyaudio.PyAudio()
        stream = mic.open(format=FORMAT, channels=CHANNELS,
                          rate=RATE, input=True, frames_per_buffer=CHUNK)
        collected_VAD = []  # buffer to store collected frames
        combined_VAD = [] #buffer to store the total combined audio
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

        combined_filename = ("/home/pi/Desktop/recordings/Combined_VAD_"+socket.gethostname() +
                        "_"+timestamp+".wav")

        while(self.recording):
            for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                data = stream.read(CHUNK)
                buffer2.append(data)
        
                if len(buffer2) == 1:
                    streamdata = buffer2.popleft()  # this data to be used by any processing thread
                    framesgenerated = frame_generator(20, streamdata, RATE) #converts chunk of 2048 into frames of 20ms
                    framesgenerated = list(framesgenerated)
                    print("length of frames generated is " + str(len(framesgenerated))) #debug

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
                            combined_VAD.extend(collected_VAD)
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
        combined_VAD.extend(collected_VAD)
        #save the last chunk of VAD audio
        filename = ("/home/pi/Desktop/recordings/VAD_"+socket.gethostname()+"_" +
                    str(datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S'))+".wav")
        self.session_file_list.append(filename)
        outputFile = wave.open(filename, 'wb')
        outputFile.setnchannels(CHANNELS)
        outputFile.setsampwidth(mic.get_sample_size(FORMAT))
        outputFile.setframerate(RATE)
        outputFile.writeframes(b''.join(collected_VAD))
        outputFile.close()

        #save the combined chunks of VAD audio
        self.session_file_list.append(combined_filename)
        outputCombinedFile = wave.open(combined_filename,'wb')
        outputCombinedFile.setnchannels(CHANNELS)
        outputCombinedFile.setsampwidth(mic.get_sample_size(FORMAT))
        outputCombinedFile.setframerate(RATE)
        outputCombinedFile.writeframes(b''.join(combined_VAD))
        outputCombinedFile.close()

        print("Recording successfully saved!")
        time.sleep(2)
        led.set(['blue', 'black', 'black', 'black', 'black', 'black', 'black', 'blue', 'black', 'black', 'black', 'black', 'black', 'black', 'blue', 'black', 'black',
                 'black', 'black', 'black', 'black', 'blue', 'black', 'black', 'black', 'black', 'black', 'black', 'blue', 'black', 'black', 'black', 'black', 'black', 'black'])

        sys.exit()  # deletes this thread safely