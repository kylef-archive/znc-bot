znc-bot
=======

znc-bot depends on a recent development build of ZNC compiled with modpython.

Installation
------------

To install znc-bot you can copy the source files onto your znc modules directory, which can usually be found at `~/.znc/modules` or `/usr/lib/znc/modules`.

Loading
-------

Loading znc-bot

.. code-block::

    /msg *status loadmod bot


Once the core bot has been loaded you can load any included plugins.

.. code-block::

    /msg *status loadmod security
    /msg *status loadmod rand


Bot API
-------

.. code-block:: python

    from bot.api import *

    class helloworld(Module):
        @command
        def hi(self, event, args):
            return "Hello there!"


Asyncronous HTTP
~~~~~~~~~~~~~~~~

.. code-block:: python

    from bot.api import *

    class trakt(Module):
        @command
        @http
        def trending(self, event, string):
            event.http('http://api.trakt.tv/movies/trending.json/my-api-key')

        @trending.http(200)
        def handle_trending(self, event, response):
            for movie in movies.json:
                event.write('{title} ({year}) - {overview}'.format(**movie)) 


