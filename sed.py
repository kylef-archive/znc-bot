import re
import bot

SUBSTITUTE_REGEX = re.compile(r'^s/(?P<pattern>[{0}]*)/(?P<repl>[{0}]*)/?$'.format("\w\d\s\^\$\(\)\<\[\]\{\\\|\>\.\*\+\>\-_'"))

class sed(bot.Module):
    def __init__(self):
        super(sed, self).__init__()
        self.previous_lines = {}

    def register_commands(self, add):
        add('sed', callback=self.sed)

    def OnChanMsg(self, nick, chan, message):
        match = SUBSTITUTE_REGEX.match(str(message))
        if match and str(nick) in self.previous_lines:
            event = bot.Event(module=self, nick=str(nick), channel=str(chan), line=str(self.previous_lines[str(nick)]))
            self.substitute(event, string=self.previous_lines[str(nick)], **match.groupdict())
        else:
            self.previous_lines[str(nick)] = str(message)

    def sed(self, event, line):
        sed, line = line.split(' ', 1)
        self.substitute(event, string=line, **SUBSTITUTE_REGEX.match(sed).groupdict())

    def substitute(self, event, *args, **kwargs):
        event.reply('{} meant "{}"'.format(event['nick'], re.sub(*args, **kwargs)))

