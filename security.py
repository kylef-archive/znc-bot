import hashlib
import base64

import bot


class security(bot.Module):
    @bot.command(usage='[hash data]', example='sha256 hello world')
    @bot.regex(r'^((?P<algorithm>\S+) (?P<data>.+))?$')
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

    @bot.command(usage='data', example='Encode the input with base64')
    def base64(self, event, line):
        return str(base64.encodestring(bytes(line, 'utf8')), 'utf8')

    @bot.command(usage='data', example='Decode the input with base64')
    def decode64(self, event, line):
        return str(base64.decodestring(bytes(line, 'utf8')), 'utf8')

    @bot.command(usage='data')
    def rot13(self, event, line):
        rot13_trans = str.maketrans('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz', 'NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm')
        return line.translate(rot13_trans)
