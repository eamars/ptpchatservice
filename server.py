import socket, select, json, hashlib
from threading import Thread
import protocol
import sys
import time
if sys.version_info < (3, 0):
    from urllib2 import urlopen
    from urllib2 import quote
else:
    from urllib.request import urlopen
    from urllib.parse import quote

CONNECTION_LIST = []
NICKNAME_DICT = {}
HOST = "localhost"
RECV_BUFFER = 4096  # Keep this exp(2)
PORT = 5000         # Set 5000 as default chat port
RECV_DATA = None

SERVER_SOCKET = None

def prompt() :
    sys.stdout.write('<Server> ')
    sys.stdout.flush()

def server_message():
    while 1:
        msg = sys.stdin.readline()
        broadcast_message(None, "Server", msg)
        prompt()

def alive_message_test():
    alive = protocol.CMDMessage("Server", {"alive": True})
    while 1:
        broadcast(None, alive)
        time.sleep(1)



def get_name(sock):
    if sock not in NICKNAME_DICT or not sock:
        return "Unknown User"
    return NICKNAME_DICT[sock]

def process_command(sock, json_string):
    # json_string is {"command": command, "identifier": simple_hash(str(command), 5039)}
    if json_string["identifier"] == protocol.nice_hash(str(json_string["command"])):

        if "register" in json_string["command"]:
            register(sock, json_string["command"])
        if "maintain" in json_string["command"]:
            server_commands(json_string["command"])

def server_commands(json_string):
    if json_string["maintain"] == "stop":
        thread1.exit()
        thread2.exit()

def register(sock, json_string):
    if sock not in NICKNAME_DICT:
        NICKNAME_DICT[sock] = json_string["register"]
        print(" --register as <{}>".format(json_string["register"]))
    else:
        print("<{}> changed his/her name to <{}>", NICKNAME_DICT[sock], json_string["register"])
        NICKNAME_DICT[sock] = json_string["register"]

def broadcast(sock, message):
    global SERVER_SOCKET
    for client in CONNECTION_LIST:
        # Do not send the message to master socket and the client who has sent us the message
        if client != SERVER_SOCKET and client != sock:
            try:
                client.send(message.dump().encode())
            except Exception as e:
                #print("failed to send to {}: {}".format(get_name(sock), e))
                # Broken socket connection:
                # Client disconnect or offline
                client.close()
                CONNECTION_LIST.remove(client)

def broadcast_message(sock, sender, message):
    global SERVER_SOCKET
    for client in CONNECTION_LIST:
        # Do not send the message to master socket and the client who has sent us the message
        if client != SERVER_SOCKET and client != sock:
            msg = protocol.STDMessage(sender, message)
            try:
                #js = json.dumps({"sender": sender, "message": message})
                client.send(msg.dump().encode())
            except Exception as e:
                print("failed to send to {}: {}".format(get_name(sock), e))
                # Broken socket connection:
                # Client disconnect or offline
                client.close()
                CONNECTION_LIST.remove(client)

def message_listening():
    print(" --done")
    global RECV_DATA
    global SERVER_SOCKET
    # initilize the server connecton and bind the port
    SERVER_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    SERVER_SOCKET.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    SERVER_SOCKET.bind((HOST, PORT))
    SERVER_SOCKET.listen(10)

    # append the server to the connection list
    CONNECTION_LIST.append(SERVER_SOCKET)

    print("Chatting service initilized on {}:{}".format(HOST, PORT))

    while 1:
        # Get the list sockets which are ready to be read through select
        read_sockets, write_sockets, error_sockets = select.select(CONNECTION_LIST,[],[])

        for sock in read_sockets:
            # found new connection
            if sock == SERVER_SOCKET:
                # Handle the case in which there is a new connection recieved through server_socket
                sockfd, addr = SERVER_SOCKET.accept()
                CONNECTION_LIST.append(sockfd)
                print ("Client <{}> connected".format(str(addr)), end='')

            # incoming messages from client
            else:
                try:
                    RECV_DATA = sock.recv(RECV_BUFFER)
                    if RECV_DATA:
                        js = json.loads(RECV_DATA.decode().strip('\n'))
                        # test if it's the register info
                        if js["type"] == "cmd_message":
                            process_command(sock, js["content"])
                        else:
                            print("\n<{}>: {}".format(js["sender"], js["content"]["text"]),end='')
                            prompt()
                            broadcast_message(sock, js["sender"], js["content"]["text"])
                        
                        RECV_DATA = None
                except:
                    print("\nClient <{}> offline".format(get_name(sock)))
                    broadcast_message(sock, "Server", "Client <{}> offline\n".format(get_name(sock)))
                    sock.close()
                    try:
                        CONNECTION_LIST.remove(sock)
                    except Exception as e:
                        print("\nERROR: {} not in the list", format(sock))
                    continue

    SERVER_SOCKET.close()

def upload_addr():
    GREETINGS = """
    \033[93mHello Everyone! Welcome to my chat room\033[0m
    ---------------------------------------
    \033[95mRules:
    (1) Please do not say bad words
    (2) Love each other
    (3) Have Fun!\033[0m
    ---------------------------------------
    \033[94mYou need to know:
    (1) We do not save your chat history
    (2) The chatting protocol is developed by
        Ran Bao\033[0m
    """
    SERVER_NAME = "12202"
    REMOTE_SERVER_LINK = "http://ptpchatip.appspot.com/add?name={}&description={}&addr={}&port={}".format(quote(SERVER_NAME), quote(GREETINGS), HOST, PORT)
    urlopen(REMOTE_SERVER_LINK)

def main():
    # Upload the local server ip to ptpchatservice
    print("Uploading Server Details", end='')
    upload_addr()
    print(" --done")
    print("Intitilizing Chat service", end='')
    message_listening()

if __name__ == '__main__':

    # Get the local machine net ip address
    HOST = socket.gethostbyname(socket.gethostname())
    thread1 = Thread(target=server_message)
    thread2 = Thread(target=alive_message_test)
    thread1.start()
    thread2.start()
    main()
