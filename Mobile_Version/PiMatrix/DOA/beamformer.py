"""
takes in audio, passes it to the DOA to get the corresponding direction of arrivals then adjusts the gain levels accordingly

"""
from __future__ import absolute_import, division, print_function
import numpy as np
#cimport numpy as cnp
#cimport cython
from collections import deque,Counter
from matrix_lite import led
import scipy
from scipy.io import wavfile
import socket
import time
import datetime
import numpy
import copy
import sys
import cProfile
import sys
from time import time
import itertools
import scipy.misc
import scipy.constants
from scipy import pi
from bisect import bisect




def beamform(self):

    def estimateDOA(arraydata,recording_array,mic_dict):

        peakvalues = []

        for i in range(len(arraydata)):
            for j in range(len(arraydata[i])):
                largest_data=max(arraydata[i],key=abs) #speedup
                #print(largest_data) #debug
                if abs(largest_data) > 1200: #this value can be changed depending on sensitivity
                    #templist = list(arraydata[i])
                    ind = arraydata[i].index(largest_data) #add the index of loudest mic into peakvalues
                    peakvalues.append(ind)

        try:
            loudest_mic = Counter(peakvalues).most_common(1) #speedup
            loudest_mic = loudest_mic[0][0]
            print("loudest mic index is " + str(loudest_mic)) #debug
            
        except:
            loudest_mic = None
        ###get the led array of the corresponding mics

        if loudest_mic != None:
            led.set(recording_array)
            #led.set(mic_dict[loudest_mic])
        # reset the LED and activate the corresponding lights

        return loudest_mic

    

    ### Code starts here ###

    LED_array = ['darkturquoise', 'black', 'black', 'black', 'black', 'darkturquoise', 'black', 'black', 'black', 'darkturquoise', 'black', 'black', 'black', 'darkturquoise', 'black', 'black', 'black',
                    'darkturquoise', 'black', 'black', 'black', 'darkturquoise', 'black', 'black', 'black', 'darkturquoise', 'black', 'black', 'black', 'darkturquoise', 'black', 'black', 'black', 'darkturquoise', 'black']
    
    mic1 = copy.deepcopy(LED_array)
    mic2 = copy.deepcopy(LED_array)
    mic3 = copy.deepcopy(LED_array)
    mic4 = copy.deepcopy(LED_array)
    mic5 = copy.deepcopy(LED_array)
    mic6 = copy.deepcopy(LED_array)
    mic7 = copy.deepcopy(LED_array)
    mic8 = copy.deepcopy(LED_array)
    mic1[14]='pink'
    mic1[15]='pink'
    mic1[16]='pink'

    mic2[18]='pink'
    mic2[19]='pink'
    mic2[20]='pink'

    mic3[22]='pink'
    mic3[23]='pink'
    mic3[24]='pink'

    mic4[26]='pink'
    mic4[27]='pink'
    mic4[28]='pink'

    mic5[30]='pink'
    mic5[31]='pink'
    mic5[32]='pink'

    mic6[2]='pink'
    mic6[3]='pink'
    mic6[4]='pink'

    mic7[6]='pink'
    mic7[7]='pink'
    mic7[8]='pink'

    mic8[10]='pink'
    mic8[11]='pink'
    mic8[12]='pink'
    
    print(mic1)
        

    # min value -32,768 to 32,767
    buffer = deque([],maxlen=5)
    recording_buffer = []
    signal_factor = 2.0
    noise_factor = 0.8
    mic_dict = {
        0:mic2,
        1:mic3,
        2:mic4,
        3:mic5,
        4:mic6,
        5:mic7,
        6:mic8,
        7:mic1
    }
    ## initialize music doa estimator
    print("beamformer loaded!")
    matrix_array = np.array([[0.02, -0.048, 0], [-0.02, -0.048, 0], [-0.048, -0.02, 0], [-0.048, 0.02, 0],
                         [-0.02, 0.048, 0], [0.02, 0.048, 0], [0.048, 0.02, 0], [0.048, -0.02, 0]])
    

    #code start here
    self.beamforming_processing_flag = True
    while (self.recording):
        while self.shared_buffer:
            
            buffer.append(self.shared_buffer.popleft())
            #print(len(buffer))
            if len(buffer)==1:
                print("calc DOA") #debug
                
                numpydata = (np.frombuffer(buffer[0], dtype=np.int16))
                numpydata = np.require(numpydata,dtype=np.int16,requirements=['O', 'W'])
                numpydata = np.reshape(numpydata,(2048,8))
                numpydata.setflags(write=1)
                buffer.clear() #clear the buffer to be filled again
                loudest_mic = estimateDOA(numpydata,LED_array,mic_dict)
                #loudest_mic = musicDOA(numpydata,matrix_array,LED_array,mic_dict)
                if loudest_mic is not None:
                    ### find the vector representing the 8 microphones and their signal strengths
                    ### the loudest mic and two of the next nearest microphones will have their signal increased
                    ### the rest will have their signals decreased
                    beamform_multiplier = np.full(8,noise_factor)
                    beamform_multiplier[loudest_mic]=signal_factor
                    if (loudest_mic + 1) > 7:
                        beamform_multiplier[0] = signal_factor
                    else:
                        beamform_multiplier[loudest_mic+1] = signal_factor
                    
                    if (loudest_mic - 1 ) < 0:
                        beamform_multiplier[7] = signal_factor
                    else:
                        beamform_multiplier[loudest_mic-1] = signal_factor
                    beamform_multiplier = np.array([beamform_multiplier]) 
                    # apply beamforming
                    numpydata = numpydata * beamform_multiplier
                            
                for i in range(len(numpydata)):
                    recording_buffer.append(numpydata[i])
            else:
                continue
    else:
        print("stop DOA")
        led.set('black')
        #dump remaining data into the buffer
        while self.shared_buffer:
            buffer.append(self.shared_buffer.popleft())
        for i in range(len(buffer)):
            numpydata = (np.frombuffer(buffer[0], dtype=np.int16))
            numpydata = np.require(numpydata,dtype=np.int16,requirements=['O', 'W'])
            numpydata = np.reshape(numpydata,(256,8))
            for i in range(len(numpydata)):
                    recording_buffer.append(numpydata[i])


    recording_buffer = numpy.array(recording_buffer)
    ### mixdown to mono channel ###
    print(recording_buffer) #before mixdown
    recording_buffer = recording_buffer * np.array([0.250,0.250,0.250,0.250,0.250,0.250,0.250,0.250])
    d = np.array([[1],[1],[1],[1],[1],[1],[1],[1]])
    recording_buffer = np.dot(recording_buffer,d)
    print(recording_buffer) #after mixdown
    recording_buffer = recording_buffer.astype(np.int16)
    filename = ("/home/pi/Desktop/recordings/DOA_" + socket.gethostname() + "_" + 
    str(datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S'))+".wav")
    self.session_file_list.append(filename)
    scipy.io.wavfile.write(filename,16000,recording_buffer)
    print(filename + " saved!")
    self.beamforming_processing_flag = False
    led.set("blue")
    sys.exit()


                    
        
    
                

                    
                    





