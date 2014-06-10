import socket, select, hashlib, json, sys
from threading import Thread
import protocol

import sys
if sys.version_info < (3, 0):
    from urllib2 import urlopen
    from urllib2 import quote
else:
    from urllib.request import urlopen
    from urllib.parse import quote

HOST = "localhost"
RECV_BUFFER = 4096  # Keep this exp(2)
PORT = 5000         # Set 5000 as default chat port
RECV_DATA = None

def prompt() :
    sys.stdout.write('\x1b[36m<{}> '.format(name))
    sys.stdout.flush()
    sys.stdout.write("\033[0m")

def download_addr(hostname):
    global HOST
    global PORT

    REMOTE_SERVER_LINK = "http://ptpchatip.appspot.com/search?name={}".format(quote(hostname))
    buff = urlopen(REMOTE_SERVER_LINK)
    try:
        js = json.loads(buff.read().decode())
        print(js["description"])
        HOST = js["addr"]
        PORT = int(js["port"])
    except Exception:
        print("Server not found!")

 
#main function
if __name__ == "__main__":
    if(len(sys.argv) < 3) :
        print ('Usage : python3 new_client.py hostname nickname')
        sys.exit()


    download_addr(sys.argv[1])
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)

    # connect to remote host
    try :
        s.connect((HOST, PORT))
    except :
        print ('Unable to connect')
        sys.exit()

    name = sys.argv[2]
    

    # Register on server
    cmd = protocol.CMDMessage(name, {"register": name})
    s.send(cmd.dump())

    print ('Connected to remote host. Start sending messages as <{}>'.format(name))
    prompt()

    while 1:
        socket_list = [sys.stdin, s]
         
        # Get the list sockets which are readable
        read_sockets, write_sockets, error_sockets = select.select(socket_list , [], [])
         
        for sock in read_sockets:
            #incoming message from remote server
            if sock == s:
                data = sock.recv(4096)
                if not data :
                    print ('\nDisconnected from chat server')
                    sys.exit()
                else :
                    #print data
                    js = json.loads(protocol.decompress(data))

                    # If incoming message is a standard message
                    if js["type"] == "s_message":
                        print("\n<{}>: {}".format(js["sender"], js["content"]["text"], end=''))
                        prompt()
             
            #user entered a message
            else :
                msg = protocol.STDMessage(name, sys.stdin.readline().strip('\n'))
                s.send(msg.dump())
                prompt()
