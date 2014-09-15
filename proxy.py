import urllib.request as req

class Proxy():
    def __init__(self, proxy_addr):
        self.proxy_addr = proxy_addr
        self.http_proxy_template = 'http://{}{}'

    def login(self, username='', password=''):
        login_template = ''
        if username:
            login_template = '{}:{}@'.format(username, password)
    

        proxy = req.ProxyHandler({'http': self.http_proxy_template.format(login_template, self.proxy_addr)})
        auth = req.HTTPBasicAuthHandler()
        opener = req.build_opener(proxy, auth, req.HTTPHandler)
        req.install_opener(opener)
if __name__ == '__main__':
    p = Proxy('webgate.canterbury.ac.nz:3128')
    p.login('rba90', 'wenjia1994')
    print(req.urlopen('http://www.google.com').read())
        
