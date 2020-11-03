"""
takes in audio, passes it to the DOA to get the corresponding direction of arrivals then adjusts the gain levels accordingly


"""
import numpy as np
from collections import deque,Counter
from matrix_lite import led
from scipy.io import wavfile
import socket
import time
import datetime
import numpy
import copy



def beamform(self):

    def estimateDOA(arraydata,mic1,mic2,mic3,mic4,mic5,mic6,mic7,mic8,recording_array):
    
        
 


        peakvalues = []

        for i in range(len(arraydata)):
            for j in range(len(arraydata[i])):
                largest_data=max(arraydata[i],key=abs)
                #print(largest_data) #debug
                if abs(largest_data) > 2000: #this value can be changed depending on sensitivity
                    templist = list(arraydata[i])
                    ind = templist.index(largest_data) #add the index of loudest mic into peakvalues
                    peakvalues.append(ind)

        try:
            loudest_mic = Counter(peakvalues).most_common(1)
            loudest_mic = loudest_mic[0][0]
            print("loudest mic index is " + str(loudest_mic)) #debug
            
        except:
            print("no loudest mic")
            loudest_mic = None

        ###get the led array of the corresponding mics

        if loudest_mic == 0:
            led.set(recording_array)
            led.set(mic2)
            

        elif loudest_mic == 1:
            led.set(recording_array)
            led.set(mic3)
            

        elif loudest_mic == 2:
            led.set(recording_array)
            led.set(mic4)

        elif loudest_mic == 3:
            led.set(recording_array)
            led.set(mic5)

        elif loudest_mic == 4:
            led.set(recording_array)
            led.set(mic6)

        elif loudest_mic == 5:
            led.set(recording_array)
            led.set(mic7)

        elif loudest_mic == 6:
            led.set(recording_array)
            led.set(mic8)

        elif loudest_mic == 7:
            led.set(recording_array)
            led.set(mic1)
        

            


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
    signal_factor = 1.2
    noise_factor = 0.8
    print("beamformer loaded!")

    while (self.recording):
        while self.shared_buffer:
            
            buffer.append(self.shared_buffer.popleft())
            print(len(buffer))
            if len(buffer)==2:
                print("calc DOA") #debug
                
                numpydata = (np.frombuffer(buffer[0], dtype=np.int16))
                numpydata = np.require(numpydata,dtype=np.int16,requirements=['O', 'W'])
                print(len(np.frombuffer(buffer[0], dtype=np.int16)))
                numpydata = np.reshape(numpydata,(2048,8))
                numpydata.setflags(write=1)
                print(numpydata)
                print(len(numpydata))
                buffer.clear() #clear the buffer to be filled again
                loudest_mic = estimateDOA(numpydata,mic1,mic2,mic3,mic4,mic5,mic6,mic7,mic8,LED_array)
                print("loudest mic is" + str(loudest_mic))
                if loudest_mic is not None:
                    ### change the signal strengths accordingly to loudest_mic
                    for i in range(len(numpydata)):
                        for j in range(len(numpydata[i])):
                            if j == loudest_mic:
                                numpydata[i][j] = int(numpydata[i][j] * signal_factor)
                                
                            elif j == loudest_mic + 1:
                                numpydata[i][j] = int(numpydata[i][j] * signal_factor)
                                
                            elif j == loudest_mic - 1:
                                numpydata[i][j] = int(numpydata[i][j] * signal_factor)
                                
                            else:
                                numpydata[i][j] = int(numpydata[i][j] * noise_factor)
                               
                numpydata = numpydata.flatten()
                recording_buffer.append(numpydata)
            else:
                continue
    else:
        print("stop DOA")

    filename = ("/home/pi/Desktop/recordings/DOA_" + socket.gethostname() + "_" + 
    str(datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S'))+".wav")
    self.session_file_list.append(filename)
    scipy.io.wavfile.write(filename,16000,recording_buffer)
    print(filename + " saved!")
    sys.exit()


                    
        
    
                

                    
                    





