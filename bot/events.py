from io import StringIO

class EventQueue(object):
    def __init__(self):
        self.is_paused = 0
        self.events = []
        self.iter_events = []

    def __next__(self):
        if self.is_paused or not len(self.iter_events):
            raise StopIteration()

        event = self.iter_events.pop(0)
        if len(self.iter_events):
            event.next_event = self.iter_events[0]

        return event

    def __iter__(self):
        return self

    def append(self, event):
        event.queue = self
        self.events.append(event)
        self.iter_events.append(event)

    def clear(self):
        self.iter_events = []

    @property
    def finished(self):
        return len(self.iter_events) > 0

    def pause(self):
        self.is_paused += 1

    def resume(self):
        self.is_paused -= 1


class Event(object):
    def __init__(self, queue=None, **kwargs):
        self.queue = None
        self.stdin = ""
        self.kwargs = kwargs
        self.next_event = None

    def copy(self):
        return self.__class__(self.queue, **self.kwargs)

    def __getitem__(self, key):
        if key in self.kwargs:
            return self.kwargs[key]

    def __contains__(self, key):
        return key in self.kwargs

    def __setitem__(self, key, value):
        self.kwargs[key] = value

    def write(self, data):
        if not data:
            return

        if self.next_event:
            self.next_event.stdin += data
        else:
            self.reply(data)

    def error(self, data=None):
        if self.queue:
            self.queue.clear()

        if data:
            self.reply('\x0304' + data)

    def reply(self, message):
        if not message:
            return

        if 'channel' in self:
            recipient = self['channel']
        else:
            recipient = self['nick']

        if isinstance(message, str):
            message = message.split('\n')

        for line in message:
            self.network.PutIRC('PRIVMSG {} :{}'.format(recipient, line))

    @property
    def network(self):
        if 'network' in self:
            return self['module'].GetUser().FindNetwork(self['network'])

    @property
    def is_private(self):
        return 'channel' not in self

class CommandEvent(Event):
    pass

