import znc

from bot.commands import CommandList


class Module(znc.Module):
    module_types = [znc.UserModule, znc.NetworkModule]

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



