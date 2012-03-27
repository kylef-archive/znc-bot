from bot.api import *

class isup(Module):
    @command
    @http
    def isup(self, event, site):
        event.http('http://www.isup.me/' + site)

    @isup.http(200)
    def isup_result(self, event, response):
        if "It's just you." in response.content:
            event.reply('Looks UP from here.')
        elif "It's not just you!" in response.content:
            event.reply('Looks DOWN from here.')
        else:
            event.error('Not sure, unknown error')
