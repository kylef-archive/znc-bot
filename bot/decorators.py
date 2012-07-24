import re
from functools import wraps
from bot.http import HttpSock

def regex(pattern=r'^(?P<line>.+)?$'):
    def decorator(func):
        r = re.compile(pattern)

        @wraps(func)
        def new_func(plugin, event, line):
            match = r.search(line)

            if not match:
                event.error('{}: Invalid arguments'.format(event['name']))

            kwargs = match.groupdict()
            if kwargs:
                args = tuple()
            else:
                args = match.groups()

            return func(plugin, event, *args, **kwargs)
        return new_func
    return decorator

def command(func=None, **kwargs):
    def decorator(func):
        func.is_command = True

        for kwarg in kwargs:
            setattr(func, kwarg, kwargs[kwarg])

        if not getattr(func, 'name', False):
            func.name = func.__name__

        if not getattr(func, 'description', False) and func.__doc__:
            func.description = func.__doc__

        return func

    if func is not None:
        return decorator(func)

    return decorator

def is_command(func):
    return getattr(func, 'is_command', False)

def is_interval(func):
    return getattr(func,'is_interval', False)

def http(func):
    @wraps(func)
    def new_func(plugin, event, *args, **kwargs):
        def request(*rargs, **rkwargs):
            plugin.CreateSocket(HttpSock, event, new_func, *rargs, **rkwargs)

        event.http = request
        return func(plugin, event, *args, **kwargs)

    new_func.http_handlers = {}

    def http_handler_decorator(status=None):
        def handler(func):
            new_func.http_handlers[status] = func
            return func

        return handler

    new_func.http = http_handler_decorator

    return new_func

def interval(time, **kwargs):
    """
    Run command at regular intervals set by 'time'
    """
    def decorator(func):
        func.is_interval = True
        func.interval = time
        func.eventargs = kwargs
        return func
    
    return decorator

# IRC
def private(func):
    """
    Only allow this event to work on private messages
    """

    @wraps(func)
    def decorator(plugin, event, *args, **kwargs):
        if event.is_private:
            return func(plugin, event, *args, **kwargs)
        return 'This command must be run privately'
    return decorator

def opped(op=True, halfop=True):
    """
    Only allow this event to work channels who the sender has op
    """

    def decorator(func):
        @wraps(func)
        def new_func(plugin, event, *args, **kwargs):
            if (op and event['nick'].HasPerm(ord('@'))) or (halfop and event['nick'].HasPerm(ord('%'))):
                return func(plugin, event, *args, **kwargs)
            return 'Permission Denied'
        return new_func
    return decorator

