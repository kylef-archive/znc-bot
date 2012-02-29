import re
import inspect
import znc

from bot.decorators import *
from bot.module import Module, Event

class Ping(object):
    @command()
    def ping(self, event, line):
        return 'pong'


class Utils(object):
    @command()
    def echo(self, event, line):
        return line

    @command()
    def count(self, event, line):
        return str(len(line.split(',')))


class bot(znc.Module):
    description = 'Python Bot'

    def __init__(self):
        self.extra_plugins = [self, Ping(), Utils()]

    @property
    def plugins(self):
        if self.GetNetwork():
            for module in self.GetNetwork().GetModules():
                py_module = module = znc.AsPyModule(module)
                if py_module:
                    yield py_module.GetNewPyObj()

        for module in self.GetUser().GetModules():
            py_module = module = znc.AsPyModule(module)
            if py_module:
                yield py_module.GetNewPyObj()

        for plugin in self.extra_plugins:
            yield plugin

    def find_plugin(self, name):
        for plugin in self.plugins:
            if plugin.__class__.__name__ == name:
                return plugin

    @property
    def commands(self):
        for plugin in self.plugins:
            for command in inspect.getmembers(plugin, is_command):
                yield command[1]

    def find_command(self, name):
        for command in self.commands:
            if command.name == name:
                return command

    def handle_command(self, nick, channel=None, line=None):
        event = Event(module=self, nick=nick, line=str(line))
        if channel:
            event['channel'] = str(channel)
            event['_channel'] = channel

        event['network'] = str(self.GetNetwork())

        line = line.replace('\|', "\0p\0")  # Escaped pipes
        result = None

        for args in line.split('|'):
            args = args.strip()
            args = args.replace("\0p\0", '|')  # Unescaped pipes

            if not re.match('^[A-z0-9]', args):
                event.reply("Commands must start with a character.")
                return

            try:
                name, args = args.split(' ', 1)
            except ValueError:
                name = args
                args = ''

            if result:
                args += ' ' + result
            event['args'] = args

            c = self.find_command(name)

            if not c:
                event.reply('{}: Command not found'.format(name))
                return

            try:
                result = c(event, args)
            except Exception as e:
                #raise e
                event.reply('{}: Failed to execute'.format(name))
                return

        event.reply(result)

    # Commands

    @command()
    def help(self, event, line=None):
        if line:
            command = self.find_command(line)
            if not command:
                return '{}: Command not found'.format(line)

            page = []

            if getattr(command, 'description', False):
                page.append('{}: {}'.format(command.name, command.description))
            if getattr(command, 'usage', False):
                page.append('Usage: {}'.format(command.usage))
            if getattr(command, 'example', False):
                page.append('Example: {}'.format(command.example))

            if len(page) > 0:
                return "\n".join(page)

            return '{}: No help availible for this command'.format(command.name)
        return ', '.join([command.name for command in self.commands])

    @command()
    def which(self, event, name):
        for plugin in self.plugins:
            for command in inspect.getmembers(plugin, is_command):
                if command[1].name == name:
                    return plugin.__class__.__name__

        return '{}: Command not found'.format(name)

    @command(name='commands')
    def plugin_commands(self, event, line):
        plugin = self.find_plugin(line)
        if not plugin:
            return '{}: Plugin not found'.format(line)

        commands = [c[0] for c in inspect.getmembers(plugin, is_command)]

        if len(commands) is 0:
            return 'This plugin does not have any commands.'

        return ', '.join([name for name in commands])

    # ZNC Module hooks

    def OnLoad(self, *args):
        if 'control_character' not in self.nv:
            self.nv['control_character'] = '.'
        return True

    def OnPrivMsg(self, nick, message):
        self.handle_command(nick, line=str(message))

    def OnChanMsg(self, nick, channel, message):
        message = str(message)

        nick = channel.FindNick(str(nick))

        if message.startswith(self.nv['control_character']):
            line = message[len(self.nv['control_character']):]
            if line and re.match('^[A-z0-9]', line):
                self.handle_command(nick, channel, line)
        else:
            match = re.search(r'^{}(:|,) (.+)$'.format(self.GetNetwork().GetCurNick()), message)
            if match:
                self.handle_command(nick, channel, match.groups()[1])

