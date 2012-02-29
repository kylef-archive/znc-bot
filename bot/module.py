import znc


class Module(znc.Module):
    module_types = [znc.CModInfo.UserModule, znc.CModInfo.NetworkModule]

    def find_bot(self):
        module = None

        if self.GetNetwork():
            module = self.GetNetwork().GetModules().FindModule('bot')

        if not module:
            module = self.GetUser().GetModules().FindModule('bot')

        if module:
            return znc.AsPyModule(module).GetNewPyObj()

        return None

