from tkinter import *
from threading import Thread
import socket, select, hashlib, json, sys
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
s = None
name = "Unknown"


class HistoryTextArea(object):
    def __init__(self, root, init_state='disabled', init_width=80, init_height=24):
        self.root = root
        self.text = Text(self.root, state=init_state, width=init_width, height=init_height)
        self.scrollbar = Scrollbar(self.root)

    def pack(self):
        self.text.pack(side=LEFT, expand=1)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.text.config(font='Menlo 12', yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.text.yview)
        self.update_tag()

    def write(self, string, tag=None, end='\n'):
        self.text.config(state='normal')
        self.text.insert('end', string + end, tag)
        self.text.config(state='disabled')
        self.text.update()
        self.text.see('end')

    def update_tag(self):
        '''update the tag infomation'''
        self.text.tag_config('pass', foreground='ForestGreen')
        self.text.tag_config('failed', foreground='Red')
        self.text.tag_config('info', foreground='Blue')
        self.text.tag_config('warning', foreground='DarkOrange')

class InputTextArea(object):
    def __init__(self, root, init_state='normal', init_width=80, init_height=24):
        self.root = root
        self.text = Text(self.root, state=init_state, width=init_width, height=init_height)
        self.text.config(highlightbackground="grey")
        self.scrollbar = Scrollbar(self.root)

        # recall the enter
        self.text.bind('<KeyRelease-Return>', self.enter_callback)
        self.text.bind('<Return>', lambda e: None)

    def pack(self):
        self.text.pack(side=LEFT, expand=1)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.text.config(font='Menlo 12', yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.text.yview)
        self.update_tag()

    def write(self, string, tag=None, end='\n'):
        self.text.insert('end', string + end, tag)
        self.text.update()
        self.text.see('end')

    def update_tag(self):
        '''update the tag infomation'''
        self.text.tag_config('pass', foreground='ForestGreen')
        self.text.tag_config('failed', foreground='Red')
        self.text.tag_config('info', foreground='Blue')
        self.text.tag_config('warning', foreground='DarkOrange')
        self.text.tag_config('self', foreground='Cyan')

    def enter_callback(self, event=None):
        '''handle the enter event'''
        # Write to screen
        linetext = self.text.get("1.0","end-1c").strip('\n')

        msg = protocol.STDMessage(name, linetext)
        sent_data = msg.dump()
        # If sent data > 4096 then raise error, do not send
        if len(sent_data) > RECV_BUFFER:
            ChatHistoryObject.write("Your message exceed the maximum length: 4096, Failed to send", tag='failed')
        else:
            # Send message
            s.send(sent_data)
            ChatHistoryObject.write("<Me>: {}".format(linetext), tag="pass")
            self.text.delete("1.0","end-1c")
        

        return event

def download_addr(hostname):
    global HOST
    global PORT

    REMOTE_SERVER_LINK = "http://ptpchatip.appspot.com/search?name={}".format(quote(hostname))
    buff = urlopen(REMOTE_SERVER_LINK)
    try:
        js = json.loads(buff.read().decode())
        ChatHistoryObject.write(js["description"], tag="info")
        HOST = js["addr"]
        PORT = int(js["port"])
    except Exception:
        ChatHistoryObject.write("Server not found!", tag="failed")


def recv_msg():
    global s
    global name
    download_addr(sys.argv[1])
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)

    # connect to remote host
    try :
        s.connect((HOST, PORT))
    except :
        ChatHistoryObject.write('Unable to connect', tag="failed")
        sys.exit()

    name = sys.argv[2]

    # Register on server
    cmd = protocol.CMDMessage(name, {"register": name})
    s.send(cmd.dump())

    ChatHistoryObject.write('Connected to remote host. Start sending messages as <{}>'.format(name), tag="pass")

    while 1:
        socket_list = [sys.stdin, s]
         
        # Get the list sockets which are readable
        read_sockets, write_sockets, error_sockets = select.select(socket_list , [], [])
         
        for sock in read_sockets:
            #incoming message from remote server
            if sock == s:
                data = sock.recv(4096)
                if not data :
                    ChatHistoryObject.write('Disconnected from chat server', tag="failed")
                    sys.exit()
                else :
                    #print data
                    try:
                        js = json.loads(protocol.decompress(data))
                    except Exception as e:
                        ChatHistoryObject.write(str(e), tag="warning")
                    

                    # If incoming message is a standard message
                    if js["type"] == "s_message":
                        ChatHistoryObject.write("<{}>: {}".format(js["sender"], js["content"]["text"].strip('\n')))



if __name__ == "__main__":
    if(len(sys.argv) < 3) :
        print ('Usage : python3 new_client.py hostname nickname')
        sys.exit()


    window = Tk()

    ChatHistoryFrame = Frame(window)
    ChatHistoryObject = HistoryTextArea(ChatHistoryFrame)
    ChatHistoryObject.pack()
    ChatHistoryFrame.pack()

    ChatInputTextFrame = Frame(window)
    ChatInputTextObject = InputTextArea(ChatInputTextFrame, init_height=8)
    ChatInputTextObject.pack()
    ChatInputTextFrame.pack()


    thread1 = Thread(target=recv_msg)
    thread1.start()


    window.mainloop()
