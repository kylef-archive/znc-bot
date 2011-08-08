import re


class Command(object):
    def __init__(self, name, regex=r'^(?P<line>.+)?$', callback=None, kwargs={}, description=None, usage=None, example=None):
        self.name = name
        self.regex = re.compile(regex)
        self.callback = callback
        self.default_kwargs = kwargs
        self.description = description
        self.usage = usage
        self.example = example

    def execute(self, event, line):
        match = self.regex.search(line)
        if not match:
            return 'Argument Error'

        kwargs = match.groupdict()
        if kwargs:
            args = tuple()
        else:
            args = match.groups()

        kwargs.update(self.default_kwargs)
        return self.callback(event, *args, **kwargs)


class CommandList(list):
    def add(self, *args, **kwargs):
        self.append(Command(*args, **kwargs))

    def find(self, name):
        for command in self:
            if command.name == name:
                return command
        return None

