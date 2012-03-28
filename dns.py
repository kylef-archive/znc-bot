import socket
from bot.api import *

class dns(Module):
    @command(usage='fqdn or ip', example='github.com')
    def dns(self, event, line):
        result = socket.gethostbyaddr(line)
        return '{0} ({1})'.format(result[0], result[2][0])

    @command
    @http
    def domain(self, event, line):
        event.http('https://dnsimple.com/domains/{}/check'.format(line), headers={'Accept':'application/json'})

    @domain.http(200)
    def domain_check(self, event, response):
        return '{name} ({status})'.format(**response.json)

