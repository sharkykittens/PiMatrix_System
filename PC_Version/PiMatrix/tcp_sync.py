import time
import socket
import sys
from matrix_lite import led
from collections import deque



class tcpSlave(object):

    def __init__(self,pimatrix):

        self.blue = pimatrix.blue
        self.green = pimatrix.green

        def sync_clock():
            sync_packet()
            delay_packet()
            recv()

        def sync_packet():
            t2, t1 = recv()
            # t2 = slave receive time
            # t1 = master send time
            send(t2)
            return

        def delay_packet():
            recv()
            send(get_time())

        def recv():
            try:
                request = tcp_sync_connection.recv(4096)
                t = get_time()
                print("Request from " + str(request))
                return (t, request)
            except socket.error as e:
                print("Error while receiving request: " + str(e))

        def send(data):
            try:
                tcp_sync_connection.send(str(data).encode())
                #print("Sent to " + addr[0])
            except socket.error as e:
                ("Error while sending request: " + str(e))
                ("Tried to send: " + data)

        def get_time():
            return time.time()

        def shut_connection():
            sys.exit()

        # Code execution here


        # creates the TCP Socket for sync messages
        hostname = socket.gethostname()
        TCP_IP = "0.0.0.0"
        TCP_Sync_PORT = 8640
        TCPSync = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        TCPSync.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        TCPSync.bind((TCP_IP, 8640))
        TCPSync.listen(1)

        while True:
            print("TCP Sync waiting for connection at port 8640")
            tcp_sync_connection, tcp_client = TCPSync.accept()
            break

        try:
            while(1):
                print("\nReady to receive requests on port " + str(8640) + "...")
                data = tcp_sync_connection.recv(4096)
                data = data.decode("UTF-8")
                print(data)

                if(data == "sync"):
                    tcp_sync_connection.send("ready".encode())
                    num_of_times = tcp_sync_connection.recv(4096)
                    num_of_times = num_of_times.decode("UTF-8")
                    print(num_of_times)
                    
                    tcp_sync_connection.send("ready".encode())
                    for i in range(int(num_of_times)):
                        temp_list = self.blue[:]
                        led.set(temp_list)
                        sync_clock()
                        led.set('black')
                        temp_head = temp_list.pop(0)
                        temp_list.append(temp_head)
                        print(temp_list)
                        self.blue=temp_list[:]
                        
                    print("Done!")
                    led.set(self.green)
                    last_data = tcp_sync_connection.recv(4096)
                    last_data = last_data.decode("UTF-8")
                    print(data)
                    if (data == "final" or data == "sync"):
                        final_offset = tcp_sync_connection.recv(4096).decode()
                        print(type(final_offset))
                        print(final_offset)
                        #self.offset = float(final_offset)
                        print("Readjusting clock...")
                        led.set(self.green)

                else:
                    print()
        except socket.error as e:
            print("Error while handling requests: " + str(e))


