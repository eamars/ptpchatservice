# Messaging Protocol based on JSON content file
# Ran Bao, UOC, 2014
# Version 1
#
#
# Structure:
# ....type
# ....version
# ....sender
# ....content
# ....checksum
# -----------------------------------------------
# Examples: 
#
# Standard Message:
#   type:                       "s_message"
#   version:                    "1"
#   sender:                     string type
#   content:
#   ....text:                   string type
#   checksum:                   md5 type
# 
# Multi-Media Message:
#   type:                       "m_message"
#   version:                    "1"
#   sender:                     string type
#   content:
#   ....text:                   string type
#   ....attachments_type        string type
#   ....attachments_filename    string type
#   ....attachments:            byte type
#   checksum:                   md5 type
#
# Command Message:
#   type:                       "cmd_messsage"
#   identifier:                 "1"
#   sender:                     string type
#   content:
#   ....command:                string type
#   ....identifier              string type
#   checksum:                   md5 type

import json, hashlib, zlib


def compress(data, level=9):
    return zlib.compress(data.encode(), level)

def decompress(data):
    return zlib.decompress(data).decode()


class Message(object):
    def __init__(self, sender, content, mtype):
        self.__type = mtype
        self.__version = 1
        self.__sender = sender
        self.__content = content
        self.__checksum = hashlib.md5(str(self.__content).encode()).hexdigest()

    def __str__(self):
        return "type: {}\nversion: {}\nsender: {}\ncontent: {}\nchecksum: {}".format(self.__type, 
                                                                                    self.__version,
                                                                                    self.__sender,
                                                                                    str(self.__content),
                                                                                    self.__checksum)

    def dump(self):
        return compress(json.dumps({"type": self.__type,
                        "version": self.__version,
                        "sender": self.__sender,
                        "content": self.__content,
                        "checksum": self.__checksum}))

    def get(self, name):
        fullname = "_{}__{}".format(self.__class__.__bases__[0].__name__, name)
        if fullname in self.__dict__:
            return self.__dict__[fullname]
        else:
            return "Not found"

class STDMessage(Message):
    def __init__(self, sender, text):
        super().__init__(sender, {"text": text}, "s_message")

class MTIMessage(Message):
    def __init__(self, sender, text, data):
        super().__init__(sender, {"text": text, "attachments": data}, "m_message")

def _c_mul(a, b):
    '''Substitute for c multiply function'''
    return ((int(a) * int(b)) & 0xFFFFFFFF)


def nice_hash(input_string):
    '''Takes a string name and returns a hash for the string. This hash value 
    will be os independent, unlike the default Python hash function.'''
    if input_string is None:
        return 0 # empty
    value = ord(input_string[0]) << 7
    for char in input_string:
        value = _c_mul(1000003, value) ^ ord(char)
    value = value ^ len(input_string)
    if value == -1:
        value = -2
    return value

class CMDMessage(Message):
    def __init__(self, sender, command):
        super().__init__(sender, {"command": command, "identifier": nice_hash(str(command))}, "cmd_message")

if __name__ == "__main__":
    cmd = CMDMessage("Maintainer", {"maintain": "stats"})
    msg = STDMessage("Server", "This is the message")
    print(cmd)

