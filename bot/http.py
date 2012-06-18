from urllib.parse import urlparse, urlencode
import json
from xml.etree import ElementTree

import znc

HTTP_STATES = {
    'AWAITING_CONNECTION': 0,
    'CONNECTED': 1,
    'DISCONNECTED': 2,
    'HEADERS': 3,
    'BODY': 4,
}

class HttpResponse(object):
    def __init__(self, status_code, content='', headers={}):
        self.status_code = status_code
        self.content = content
        self.headers = headers

    def is_redirect(self):
        return (self.status_code == 301 or self.status_code == 302) and 'Location' in self.headers

    def __str__(self):
        return self.content

    def __repr__(self):
        return '<HttpResponse {} ({})>'.format(self.status_code, self.headers)

    @property
    def json(self):
        return json.loads(self.content)

    @property
    def xml(self):
        return ElementTree.fromstring(self.content)


class HttpSock(znc.Socket):
    HTTP_STATES = {
        'AWAITING_CONNECTION': 0,
        'CONNECTED': 1,
        'DISCONNECTED': 2,
        'HEADERS': 3,
        'BODY': 4,
    }

    def Init(self, event, func, url, qs=None, data=None, method=None, headers=None, timeout=5):
        self.state = HTTP_STATES['AWAITING_CONNECTION']

        o = urlparse(url)
        self.response = None
        self.headers = headers or {}
        self.path = o.path
        self.qs = qs
        self.data = data
        self.event = event
        self.func = func

        self.SetMaxBufferThreshold(80000)

        if self.event and self.event.queue:
            self.event.queue.pause()

        if method:
            self.method = method.upper()
        else:
            if self.data:
                self.method = 'POST'
            else:
                self.method = 'GET'

        if 'Host' not in self.headers:
            self.headers['Host'] = o.hostname

        if 'User-Agent' not in self.headers:
            self.headers['User-Agent'] = 'Mozilla/5.0 ({})'.format(znc.CZNC.GetTag())

        if o.query and not self.qs: # Use ?bla=foo in url if its provided
            self.qs = o.query

        # urlparse could give blank paths if we didn't provide one in the url.
        if len(self.path) == 0:
            self.path = '/'

        # urlparse will not give us a port unless we specified one in the url.
        port = o.port
        if not port:
            if o.scheme == 'https':
                port = 443
            elif o.scheme == 'http':
                port = 80
            else:
                raise Exception("Unsupported scheme: {}".format(o.scheme))

        self.EnableReadLine()
        self.Connect(o.hostname, port, timeout=timeout, ssl=(o.scheme == 'https'))

    def OnConnected(self):
        self.state = HTTP_STATES['CONNECTED']

        if self.qs:
            path = '{}?{}'.format(self.path, urlencode(self.qs))
        else:
            path = self.path

        self.Write("{} {} HTTP/1.0\r\n".format(self.method, path))

        if self.data:
            data_string = urlencode(self.data)
            self.headers['Conent-Length'] = len(data_string)

        for k,v in self.headers.items():
            self.Write("{}: {}\r\n".format(k, v))

        self.Write("\r\n")

        if self.data:
            self.Write("{}\r\n".format(data_string))

    def OnReadLine(self, line):
        line = line.strip()

        if self.state == HTTP_STATES['CONNECTED']: # HTTP/ver status_code status message
            self.state = HTTP_STATES['HEADERS']
            self.response = HttpResponse(int(line.split()[1]))
        elif self.state == HTTP_STATES['HEADERS']: # Key: Value
            if len(line) == 0:
                self.state = HTTP_STATES['BODY']
            else:
                key, value = line.split(': ')
                self.response.headers[key] = value
        elif self.state == HTTP_STATES['BODY']:
            self.response.content += line

    def OnTimeout(self):
        if 'timeout' in self.func.http_handlers:
            handler = self.func.http_handlers['timeout']
        elif None in self.func.http_handlers:
            handler = self.func.http_handlers[None]
        else:
            self.event.error('HTTP: Request timed out')
            return

        self.event.write(handler(self.GetModule(), self.event, self.response))

    def OnDisconnected(self):
        buf = self.GetInternalReadBuffer()
        if buf.s:
            self.OnReadLine(str(buf.s))

        self.state = HTTP_STATES['DISCONNECTED']

        handler = None

        if not self.response:
            self.event.error('HTTP error')
            return

        if self.response.status_code in self.func.http_handlers:
            handler = self.func.http_handlers[self.response.status_code]
        elif None in self.func.http_handlers:
            handler = self.func.http_handlers[None]
        elif self.response.status_code == 404:
            if not ('silent' in event and event['silent']):
                self.event.error('Page not found (404)')
            return
        else:
            self.event.error('HTTP: Unhandled response ({})'.format(self.response.status_code))
            return

        if handler:
            self.event.write(handler(self.GetModule(), self.event, self.response))

        if self.event.queue:
            self.event.queue.resume()

            bot = self.GetModule().find_bot()
            if not bot:
                bot = self.event['bot']

            bot.handle_event(self.event.queue)

