import socket
import bot


class dns(bot.Module):
    @bot.command(usage='fqdn or ip', example='github.com')
    def dns(self, event, line):
        result = socket.gethostbyaddr(line)
        return '{0} ({1})'.format(result[0], result[2][0])

