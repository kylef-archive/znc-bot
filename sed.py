import re
from bot.api import *

SUBSTITUTE_REGEX = re.compile(r'^s/(?P<pattern>[{0}]*)/(?P<repl>[{0}]*)/?$'.format("\w\d\s\^\$\(\)\<\[\]\{\\\|\>\.\*\+\>\-_\!'"))

class sed(Module):
    def __init__(self):
        self.previous_lines = {}

    def OnChanMsg(self, nick, chan, message):
        match = SUBSTITUTE_REGEX.match(str(message))
        if match and str(nick) in self.previous_lines:
            event = self.event(nick=str(nick), channel=str(chan), line=str(self.previous_lines[str(nick)]))
            self.substitute(event, string=self.previous_lines[str(nick)], **match.groupdict())
        else:
            self.previous_lines[str(nick)] = str(message)

    @command
    def sed(self, event, line):
        if event.stdin:
            data = event.stdin
            command = line
        else:
            command, data = line.split(' ', 1)

        self.substitute(event, string=data, **SUBSTITUTE_REGEX.match(command).groupdict())

    def substitute(self, event, *args, **kwargs):
        event.write('{} meant "{}"'.format(event['nick'], re.sub(*args, **kwargs)))

