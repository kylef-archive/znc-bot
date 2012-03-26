from bot.api import *

API_KEY = ''

class wordnik(Module):
    @command(description='Grabs a dictionary definition of a word')
    @http
    def define(self, event, word):
        event.word = word
        self.wordnik_api(event, word, 'definitions')

    @define.http(200)
    def defined(self, event, response):
        results = response.json
        lastSpeechType = None

        if not len(results):
            return event.error('No definition for {} found.'.format(event.word))

        for result in results:
            if result['partOfSpeech'] != lastSpeechType:
                event.reply('({})'.format(result['partOfSpeech']))
            lastSpeechType = result['partOfSpeech']

            event.reply('- {}'.format(result['text']))

    @command(description='Suggests correct spellings of a possible word')
    @http
    def spell(self, event, word):
        event.word = word
        self.wordnik_api(event, word, qs={'includeSuggestions':True})

    @spell.http(200)
    def spelt(self, event, response):
        word = response.json

        if 'canonicalForm' in word:
            event.reply('{} is a word.'.format(event.word))
        elif 'suggestions' not in word:
            event.reply('No suggestions for {} found.'.format(event.word))
        else:
            suggestions = ', '.join(word['suggestions'])
            event.reply('Suggestions for {}: {}'.format(event.word, suggestions))

    @command(description='Links to a pronunciation of a word')
    @http
    def pronounce(self, event, word):
        event.word = word
        self.wordnik_api(event, word, 'audio')

    @pronounce.http(200)
    def pronounced(self, event, response):
        result = response.json

        if len(result):
            event.reply(result[0]['fileUrl'])
        else:
            event.error('No pronounciation for {} found.'.format(event.word))

    def wordnik_api(self, event, word, resource='', qs=None):
        event.http('http://api.wordnik.com/v4/word.json/{}/{}'.format(word, resource), qs=qs, headers={'api_key': API_KEY})

