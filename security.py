import hashlib
import base64

import bot


class security(bot.Module):
    def __init__(self):
        super(security, self).__init__()
        self.commands.add('hash', r'^((?P<algorithm>\S+) (?P<data>.+))?$', callback=self.hash, usage='[hash data]', example='sha256 hello world')
        self.commands.add('base64', callback=self.base64, usage='data', example='Encode the input with base64')
        self.commands.add('decode64', callback=self.decode64, usage='data', example='Decode the input with base64')

    def hash(self, event, algorithm=None, data=''):
        if not algorithm:
            if hasattr(hashlib, 'algorithms_available'):
                algorithms = hashlib.algorithms_available
            else:
                algorithms = ('md5', 'sha1', 'sha224', 'sha256', 'sha384', 'sha512')

            return ', '.join(algorithms)

        try:
            return hashlib.new(algorithm, bytes(data, 'utf8')).hexdigest()
        except ValueError:
            return '{}: Unknown algorithm'.format(algorithm)

    def base64(self, event, line):
        return str(base64.encodestring(bytes(line, 'utf8')), 'utf8')

    def decode64(self, event, line):
        return str(base64.decodestring(bytes(line, 'utf8')), 'utf8')
