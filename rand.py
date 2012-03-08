import random
from bot.api import *

EIGHTBALL_CHOICES = [
    "You may rely on it",
    "It is certain",
    "As I see it, yes",
    "Cannot predict now",
    "Yes definitely",
    "Most likely",
    "Concentrate and ask again",
    "Outlook good",
    "Yes",
    "Yes -- Definitely",
    "Outlook not so good",
    "Without a doubt",
    "Reply hazy, try again",
    "Better not tell you now",
]

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

    @command(alias='8ball')
    def eightball(self, event, line):
        return random.choice(EIGHTBALL_CHOICES)
