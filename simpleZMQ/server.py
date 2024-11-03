#
#   Hello World server in Python
#   Binds REP socket to tcp://*:5555
#   Expects b"Hello" from client, replies with b"World"
#

import time
import zmq

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

try:

    while True:
        try:
            #  Wait for next request from client
            message = socket.recv(flags=zmq.NOBLOCK)
            
            print(f"Received request: {message}") 
            #  Send reply back to client
            socket.send_string("World")
        except zmq.Again:
            print ("No message received yet")
        #  Do some 'work'
        time.sleep(1)
       

except KeyboardInterrupt:
    print('!!FINISH!!')
