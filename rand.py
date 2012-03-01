import random
from bot.api import *

class rand(Module):
    @command(description='Yes or no?')
    def yesno(self, event, line):
        return self.choice(event, 'yes, no')

    @command(description='Heads or tails?')
    def coinflip(self, event, line):
        return self.choice(event, 'Heads, Tails')

    @command(description='Roll a dice')
    def dice(self, event, line):
        return self.choice(event, ','.join([str(x) for x in range(1,7)]))

    @command(description='Make a random choice', usage='<comma seperated list>', example='sausage, bacon')
    def choice(self, event, line):
        return random.choice(line.split(',')).strip()
