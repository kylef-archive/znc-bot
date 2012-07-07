from bot.api import *

class urban(Module):
    @command(name='urban', description='Search urban dictionary')
    @http
    def search(self, event, query):
        event.http('http://api.urbandictionary.com/v0/define', qs={'term':query})

    @search.http(200)
    def handle_search(self, event, response):
        result = response.json

        if 'list' in result:
            if 'definition' in result['list'][0]:
                definition = result['list'][0]['definition'].replace('\r\n', '')
                if len(definition) > 400:
                    return definition[:400] + '...'
                return definition

        return 'definition not found'

