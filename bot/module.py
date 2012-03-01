import znc
from bot.http import *
from bot.events import Event

class Module(znc.Module):
    module_types = [znc.CModInfo.NetworkModule, znc.CModInfo.UserModule]

    def find_bot(self):
        module = None

        if self.GetNetwork():
            module = self.GetNetwork().GetModules().FindModule('bot')

        if not module:
            module = self.GetUser().GetModules().FindModule('bot')

        if module:
            return znc.AsPyModule(module).GetNewPyObj()

        return None

    def event(self, **kwargs):
        return Event(network=str(self.GetNetwork()), module=self, **kwargs)

