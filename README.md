znc-bot
-------

znc-bot depends on znc version 0.099 compiled with modpython

Installation
============

To install znc-bot you can copy the source files onto your znc modules directory, which can usually be found at `~/.znc/modules` or `/usr/lib/znc/modules`.

Loading
=======

Loading znc-bot

    /msg *status loadmod bot

Once the core bot has been loaded you can load any included plugins.

    /msg *status loadmod security
    /msg *status loadmod rand

