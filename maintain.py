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
PORT = 5000

def download_addr(hostname):
    global HOST

    REMOTE_SERVER_LINK = "http://ptpchatip.appspot.com/search?name={}".format(quote(hostname))
    buff = urlopen(REMOTE_SERVER_LINK)
    try:
        js = json.loads(buff.read().decode())
        print(js["description"])
        HOST = js["addr"]
        PORT = js["port"]
    except Exception:
        print("Server not found!")

download_addr("Wenjia")
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(2)

print(HOST, PORT)

try :
    s.connect((HOST, PORT))
except:
    print ('Unable to connect')
    sys.exit()


cmd = protocol.CMDMessage("Maintainer", {"maintain": "stop"})
s.send(cmd.dump().encode())