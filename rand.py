import random

import bot


class rand(bot.Module):
    def __init__(self):
        super(rand, self).__init__()
        self.commands.add('yesno', callback=self.yesno, description='Yes, or no?')
        self.commands.add('coinflip', callback=self.coinflip, description='Heads or tails?')
        self.commands.add('dice', callback=self.dice, description='Roll a dice')
        self.commands.add('choice', callback=self.choice, description='Make a random choice', usage='<space seperated list>', example='sausage, bacon')

    def yesno(self, event, line):
        return self.choice(event, 'yes, no')

    def coinflip(self, event, line):
        return self.choice(event, 'Heads, Tails')

    def dice(self, event, line):
        return self.choice(event, ','.join([str(x) for x in range(1,7)]))

    def choice(self, event, line):
        return random.choice(line.split(',')).strip()
