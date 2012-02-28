import znc

from bot.commands import CommandList


class Module(znc.Module):
    module_types = [znc.CModInfo.UserModule, znc.CModInfo.NetworkModule]

    def __init__(self):
        self.commands = CommandList()

        if hasattr(self, 'register_commands'):
            self.register_commands(self.commands.add)

    def find_bot(self):
        module = None

        if self.GetNetwork():
            module = self.GetNetwork().GetModules.FindModule('bot')

        if not module:
            module = self.GetUser().GetModules().FindModule('bot')

        if module:
            return znc.AsPyModule(module).GetNewPyObj()

        return None


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



