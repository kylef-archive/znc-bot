import socket
import bot

class dns(bot.Module):
    def register_commands(self, add)
        add('dns', callback=self.dns, usage='fqdn or ip', example='github.com')

    def dns(self, event, line):
        result = socket.gethostbyaddr(line)
        return '{0} ({1})'.format(result[0], result[2][0])

