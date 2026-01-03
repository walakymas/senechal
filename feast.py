import json
import random

class Feast:
    def __init__(self, record):
        self.id = record[0]
        self.created = record[1]
        self.modified = record[2]
        self.title = record[3]
        self.description = record[4]
        self.jdata = record[5]
        self.jdeck = record[6]
        self.data = json.loads(self.jdata)
        self.deck = Deck(self.jdeck)

class Deck:
    def __init__(self, record=None):
        if record:
            d = json.loads(record)
            if 'deck' in d:
                self.deck = d['deck']
                if 'pos' in d:
                    self.pos = int(d['pos'])
                else:
                    self.pos = 1
                return
        self.suffle()

    def shuffle(self):
        self.pos = 0
        self.deck =list(range(1, 155))
        random.shuffle(self.deck)


