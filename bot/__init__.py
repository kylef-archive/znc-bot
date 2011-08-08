import re

import znc


class Module(znc.Module):
    def __init__(self):
        self.commands = CommandList()

        if hasattr(self, 'register_commands'):
            self.register_commands(self.commands.add)

    def find_bot(self):
        module = self.GetUser().GetModules().FindModule('bot')
        if module:
            return znc.AsPyModule(module).GetNewPyObj()
        return None

    # ZNC Module hooks

    def OnLoad(self, args, ret):
        bot = self.find_bot()

        if not bot:
            ret.s = 'bot: cannot find module'
            return False

        bot.plugins.append(self)
        return True

    def OnShutdown(self):
        bot = self.find_bot()

        if bot:
            try:
                bot.plugins.remove(self)
            except ValueError:
                # We wasn't loaded
                pass


class Event(dict):
    def reply(self, message):
        if not message:
            return

        if 'channel' in self:
            recipient = self['channel']
        else:
            recipient = self['nick']

        if isinstance(message, str):
            message = message.split('\n')

        for line in message:
            self['module'].PutIRC('PRIVMSG {} :{}'.format(recipient, line))


class Command(object):
    def __init__(self, name, regex=r'^(?P<line>.+)?$', callback=None, kwargs={}, description=None, usage=None, example=None):
        self.name = name
        self.regex = re.compile(regex)
        self.callback = callback
        self.default_kwargs = kwargs
        self.description = description
        self.usage = usage
        self.example = example

    def execute(self, event, line):
        match = self.regex.search(line)
        if not match:
            return 'Argument Error'

        kwargs = match.groupdict()
        if kwargs:
            args = tuple()
        else:
            args = match.groups()

        kwargs.update(self.default_kwargs)
        return self.callback(event, *args, **kwargs)


class CommandList(list):
    def add(self, *args, **kwargs):
        self.append(Command(*args, **kwargs))

    def find(self, name):
        for command in self:
            if command.name == name:
                return command
        return None


class Ping(object):
    def __init__(self):
        self.commands = CommandList()
        self.commands.add('ping', callback=self.ping)

    def ping(self, event, line):
        return 'pong'


class Utils(object):
    def __init__(self):
        self.commands = CommandList()
        self.commands.add('echo', callback=self.echo)
        self.commands.add('count', callback=self.count)

    def echo(self, event, line):
        return line

    def count(self, event, line):
        return str(len(line.split(',')))


class bot(znc.Module):
    description = 'Python Bot'

    def __init__(self):
        self.plugins = [self, Ping(), Utils()]
        self.commands = CommandList()
        self.commands.add('help', callback=self.help, usage='[command]')
        self.commands.add('which', r'^(?P<name>[\S]+)$', callback=self.which, usage='command')
        self.commands.add('commands', callback=self.plugin_commands, description='Show all commands a plugin includes', usage='plugin', example='bot')

    def find_plugin(self, name):
        for plugin in self.plugins:
            if plugin.__class__.__name__ == name:
                return plugin

    def find_command(self, name):
        for plugin in self.plugins:
            if hasattr(plugin, 'commands'):
                command = plugin.commands.find(name)
                if command:
                    return command
        return None

    def all_commands(self):
        commands = []

        for plugin in self.plugins:
            if hasattr(plugin, 'commands'):
                commands += plugin.commands

        return commands

    def handle_command(self, nick, channel=None, line=None):
        event = Event(module=self, nick=nick, line=line)
        if channel:
            event['channel'] = channel

        line = line.replace('\|', "\0p\0")  # Escaped pipes
        result = None

        for command in line.split('|'):
            command = command.strip()
            command = command.replace("\0p\0", '|')  # Unescaped pipes

            try:
                name, args = command.split(' ', 1)
            except ValueError:
                name = command
                args = ''

            if result:
                args += ' ' + result
            event['args'] = args

            command = self.find_command(name)

            if not command:
                event.reply('{}: Command not found'.format(name))
                return

            try:
                result = command.execute(event, args)
            except Exception as e:
                #raise e
                event.reply('{}: Failed to execute'.format(name))
                return

        event.reply(result)

    # Commands

    def help(self, event, line=None):
        if line:
            command = self.find_command(line)
            if not command:
                return '{}: Command not found'.format(line)

            page = []

            if command.description:
                page.append('{}: {}'.format(command.name, command.description))
            if command.usage:
                page.append('Usage: {}'.format(command.usage))
            if command.example:
                page.append('Example: {}'.format(command.example))

            if len(page) > 0:
                return "\n".join(page)

            return '{}: No help availible for this command'.format(command.name)
        return ', '.join([command.name for command in self.all_commands()])

    def which(self, event, name):
        for plugin in self.plugins:
            if not hasattr(plugin, 'commands'):
                continue

            for command in plugin.commands:
                if command.name == name:
                    return plugin.__class__.__name__
            return '{}: Plugin not found'.format(name)

    def plugin_commands(self, event, line):
        plugin = self.find_plugin(line)
        if not plugin:
            return '{}: Plugin not found'.format(line)

        if not hasattr(plugin, 'commands') and len(plugin.commands) is 0:
            return 'This plugin does not have any commands.'

        return ', '.join([command.name for command in plugin.commands])

    # ZNC Module hooks

    def OnLoad(self, *args):
        if 'control_character' not in self.nv:
            self.nv['control_character'] = '.'
        return True

    def OnPrivMsg(self, nick, message):
        self.handle_command(nick, message=str(message))

    def OnChanMsg(self, nick, channel, message):
        message = str(message)

        if message.startswith(self.nv['control_character']):
            self.handle_command(nick, channel, message[len(self.nv['control_character']):])
        else:
            match = re.search(r'^{}(:|,) (.+)$'.format(self.GetUser().GetCurNick()), message)
            if match:
                self.handle_command(nick, channel, match.groups()[1])
