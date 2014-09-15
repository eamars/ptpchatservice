import json

class Configuration:
    __version = "1.0"
    def __init__(self, filename):
        self.filename = filename
        self.body = {"version": self.__version}
    def load(self):
        fm = open(self.filename, 'r')
        try:
            self.body["data"] = json.loads(fm.read())["data"]
        except Exception as e:
            print(e)
        fm.close()
    def save(self):
        fm = open(self.filename, 'w')
        fm.write(json.dumps(self.body))

    def load_from_json(self, j):
        try:
            self.body["data"] = json.loads(j)
        except Exception as e:
            print(e)

    def load_from_dict(self, d):
        self.body["data"] = d

    def get(self, name):
        try:
            return self.body["data"][name]
        except Exception as e:
            print(e)


if __name__ == '__main__':
    data = {
            "RESET":    "\033[0m",
            "KRED":     "\x1B[31m",
            "KGRN":     "\x1B[32m",
            "KYEL":     "\x1B[33m",
            "KBLU":     "\x1B[34m",
            "KMAG":     "\x1B[35m",
            "KCYN":     "\x1B[36m",
            "KWHT":     "\x1B[37m"
    }

    c = Configuration("color.config")
    c.load_from_dict(data)
    c.save()
    print(c.body)
    print(c.get("KGRN"))
