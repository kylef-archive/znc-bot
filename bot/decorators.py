import re
from functools import wraps

def regex(pattern=r'^(?P<line>.+)?$'):
    def decorator(func):
        r = re.compile(pattern)

        @wraps(func)
        def new_func(plugin, event, line):
            match = r.search(line)

            if not match:
                return 'Invalid Arguments'

            kwargs = match.groupdict()
            if kwargs:
                args = tuple()
            else:
                args = match.groups()

            return func(plugin, event, *args, **kwargs)
        return new_func
    return decorator

def command(**kwargs):
    def decorator(func):
        func.is_command = True

        for kwarg in kwargs:
            setattr(func, kwarg, kwargs[kwarg])

        if not getattr(func, 'name', False):
            func.name = func.__name__

        return func
    return decorator

def is_command(func):
    return getattr(func, 'is_command', False)

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

