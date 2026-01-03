import json
import random
from config import Config
from database.feasttable import FeastTable
from character import Character
class Feast:
    def __init__(self, record):
        if not record:
            print("No feast record found, initializing with default values.")
            # Initialize with default values
            self.id = -1
            self.created = None
            self.modified = None
            self.title = ''
            self.description = ''
            self.jdata = '{}'
            self.jdeck = '{}'
            self.data = {'participiants': {}, 'state': 'init', 'round': 0, 'rounds': 3, 'course': {}}
            self.deck = Deck()
            FeastTable().insert(self)  # Initialize with default values
            return
        self.id = record[0]
        self.created = record[1]
        self.modified = record[2]
        self.title = record[3]
        self.description = record[4]
        self.jdata = record[5]
        self.jdeck = record[6]
        self.data = json.loads(self.jdata)
        self.deck = Deck(self.jdeck)
    
    def add_participiant(self, cid):
        if (self.data['state'] == 'init'):
            cid = str(cid)
            c = Character.get_by_id(cid)
            significant = []
            for i in c.data['stats']:
                if c.data['stats'][i]>=16:
                    significant.push(i)
            print(f"Adding participiant with cid: {cid}")
            if cid not in self.data['participiants']:
                self.data['participiants'][cid] = {
                    'position': -1, 
                    'glory': 0, 
                    'state': 'init',
                    'rounds': {}, 
                    'activeCards':[],
                    'tags': [],
                    'significant': [],
                    }
                print(f"participiants {cid} added with initial score and empty cards.")
            else:
                print(f"participiants {cid} already exists.")
            FeastTable().updateData(self);
        else:
            print(f"Cannot add participiant {cid} after initialization.")

    def set_rounds(self, rounds):
        if (self.data['state'] == 'init'):
            print(f"Setting rounds: {rounds}")
            self.data['rounds'] = rounds
            FeastTable().updateData(self)
        else:
            print(f"Cannot set rounds after initialization.") 

    def set_participiant(self, cid, position, glory):
        if (self.data['state'] == 'init'):
            cid = str(cid)
            if cid in self.data['participiants']:
                print(f"Setting participiants {cid} with position {position} and glory {glory}.")
                self.data['participiants'][cid]['position'] = position
                self.data['participiants'][cid]['glory'] = glory
                FeastTable().updateData(self)
            else:
                print(f"participiants {cid} does not exist.")
        else:
            print(f"Cannot set participiants {cid} after seating.")

    # Todo fix intervals
    def number_of_cards(glory):
        if glory > 32000:
            return 6
        elif glory >16000: 
            return 5
        elif glory > 8000:
            return 4
        elif glory > 4000:
            return 3
        elif glory > 2000:
            return 2
        elif glory > 1000:
            return 1
        else:
            return 0

    def draw_card(self, cid, force=False):
        cid = str(cid)
        if cid in self.data['participiants']: 
            print(f"Drawing cards for participiants {cid}.")
            participiant = self.data['participiants'][cid]
            round = str(self.data['round'])
            pround = participiant['rounds'].get(round, {})
            if 'cards' in pround and not force:
                print(f"Cards already drawn for participiants {cid} in round {round}.")
                return None
            cardnum = Feast.number_of_cards(participiant['glory'])
            cards = []
            for i in range(cardnum):
                card = self.deck.draw()
                if card is not None:
                    cards.append(card)
                    print(f"Card drawn: {card} - {Config.feast()[str(card)] if str(card) in Config.feast() else 'Unknown'}")
                else:
                    print("No more cards to draw.")
            pround['cards'] = cards
            participiant['rounds'][round] = pround
            FeastTable().updateData(self)
            FeastTable().updateDeck(self)
        else:
            print(f"participiants {cid} does not exist. {self.data['participiants'].keys()}")
        return None    
    def card_enabled(cid, pround, significant = []):
        if 'cards' in pround and cid in pround['cards']: 
            card = Config.feast()[str(cid)]
            # check if the card has a host tag 
            if 'tags' in card and len(card['tags']) > 0:    
                for tag in card['tags']:
                    if 'host' == tag:
                        return True
            cards = pround['cards']
            # check if any cards has host tag or mandatory for the character
            for card in cards:
                if 'mandatory' in card and card['mandatory'] in significant:    
                    print(f"There is a mandatory card {card} in the round.")
                    return False
            if 'mandatory' in card and card['mandatory'] in significant:    
                return True
            for card in cards:
                if 'mandatory' in card and card['mandatory']in significant:    
                    print(f"There is a mandatory card {card} in the round.")
                    return False
            print(f"Card {card} is enabled for the current round.")
            return True
        print(f"Card {card} is not enabled for the current round.")
        return False

    def select_card(self, cid, card):
        if cid in self.data['participiants']:
            participiant = self.data['participiants'][cid]
            pround = participiant['rounds'].get(round, {})
            if Feast.card_enabled(card, pround, participiant['significant']):
                print(f"Selecting card {card} for participiants {cid}.")
                pround['selected'] = card
                FeastTable().updateData(self)
        else:
            print(f"participiants {cid} does not exist.")

    def get_data(self):
        result = {'id': self.id,
                  'created': self.created,
                  'modified': self.modified,
                  'title': self.title,
                  'description': self.description,
                  'data': self.data,
        #          'deck': self.deck.deck,
                  'pos': self.deck.pos}
        return result

    def set_courses(self, courses):
        print(f"Setting courses: {courses}")
        self.data['course'] = courses
        FeastTable().updateData(self)

    def setAction(self, cid, action):
        print(f"Setting action for participiants {cid}: {action}")
        if cid in self.data['participiants']:
            if self.data['round'] not in self.data['participiants'][cid]['round']:
                self.data['participiants'][cid]['round'] = {}
            self.data['participiants'][cid]['round'][self.data['round']]['action'] = action
            FeastTable().updateData(self)
        else:
            print(f"participiants {cid} does not exist.")
    def set_round_action(self, action, pid):
        print(f"Setting round action for round {self.data['round']}: {action}")

        guest = self.data['participiants'][str(pid)] 
        if 'rounds' not in guest:
            guest['rounds'] = {}
        if self.data['round'] not in guest['rounds']:
            guest['rounds'][self.data['round']] = {}
        round = guest['rounds'][self.data['round']]
        if ('action' in round) :
            print(f"action set")
            return
        round['action'] = action
        print(f"Setting action for round {guest}: {action}")

        if ('card' == action):
            round['cards'] = []
            cardnum = Feast.number_of_cards(guest['glory'])
            for i in range(cardnum):    
                card = self.deck.draw()
                if card is not None:
                    round['cards'].append(card)
                    print(f"Card drawn: {card} - {Config.feast()[str(card)] if str(card) in Config.feast() else 'Unknown'}")
                else:
                    print("No more cards to draw.")
            FeastTable().updateDeck(self)
        FeastTable().updateData(self)

    def next_state(self):
        if self.data['state'] == 'init':
            self.data['state'] = 'feast'
            self.data['round'] = 1
        elif self.data['state'] == 'feast':
            if self.data['round'] < self.data['rounds']:
                self.data['round'] = 1 + self.data['round'] 
            else:
                self.data['state'] = 'end'
        FeastTable().updateData(self)


class Deck:
    def __init__(self, record=None):
        if record:
            d = json.loads(record)
            if 'deck' in d:
                self.deck = d['deck']
                if 'pos' in d:
                    self.pos = int(d['pos'])
                else:
                    self.pos = -1
                return
        self.shuffle()

    def get_data(self):
        return {'deck': self.deck, 'pos': self.pos}

    def draw(self):
        self.pos += 1
        return self.deck[self.pos] if self.pos < len(self.deck) else None


    def shuffle(self):
        self.pos = -1
        self.deck =list(range(1, 155))
        random.shuffle(self.deck)