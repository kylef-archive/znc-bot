from bot.api import *

class gem(Module):
    @http
    @command()
    def gem(self, event, name):
        event.http('http://rubygems.org/api/v1/gems/{}.json'.format(name))

    @gem.http(200)
    def gem_200(self, event, request):
        return """
 gem name: {name} ({version})
     info: {info}
downloads: {downloads}
""".format(**request.json)

    @gem.http(404)
    def gem_404(self, event, request):
        return "gem not found"

