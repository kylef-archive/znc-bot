import znc
from bot.http import *
from bot.decorators import is_interval
from bot.events import Event
import inspect

class IntervalTimer(znc.Timer):
    mod = None
    eventargs = {}
    def RunJob(self):
        if hasattr(self, 'function'):
            event = self.mod.event(**self.eventargs)
            self.function(event)

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
    
    def OnLoad(self, *args):
        for name,member in inspect.getmembers(self, is_interval):
            timer = self.CreateTimer(IntervalTimer, member.interval, 0)
            timer.function = member
            timer.mod = self
            timer.eventargs = member.eventargs
        return True

    def event(self, **kwargs):
        return Event(network=str(self.GetNetwork()), module=self, **kwargs)

