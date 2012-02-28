import re

def regex(pattern=r'^(?P<line>.+)?$'):
    def decorator(func):
        r = re.compile(pattern)

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

        new_func.name = func.__name__

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

