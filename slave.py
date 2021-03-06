import socket
import runner
import os
import sys
import random
import string
from time import sleep

#Set this to the local IP of the master process
HOST = '128.213.48.45'
PORT = 2436
timeout = 300 #In seconds

if __name__ == '__main__':

    done = False

    if len(sys.argv) > 1:
        HOST = sys.argv[1]
    
    #Get a random 16 character identity    
    random.seed()
    identity = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(16))

    #Continue our loop until the master is no longer sending files
    while not done:
        #Request a file
        print "Requesting new config file\n"
        sock = socket.socket()
        sock.connect((HOST,PORT))
        sock.sendall(identity)
        sock.sendall("request.")
        config_file = sock.recv(4)

        #No files remaining, time to finish
        if config_file == "wait":
            print "All remaining config files are in progress. Sleeping."
            sleep(timeout)
            print "Waking up."
        
        elif config_file == "done":
            print "All config files complete. Shutting down."
            done = True

        #A new file has been sent. Copy it locally, then run it.
        else:
            config_file = sock.recv(int(config_file)) #Get the name of the file
            print "Running config file: " + config_file
            f = open(config_file,"w")
            data = sock.recv(8) #Get the data
            data = sock.recv(int(data))
            f.write(data)
            f.close()
            sock.close()
            runner.run(config_file, HOST, True, identity) #Run it
            os.remove(config_file) #Clean up
            sock = socket.socket()
            sock.connect((HOST,PORT))
            sock.sendall(identity)
            sock.send("complete") #We finished the file, tell the server
