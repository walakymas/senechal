import json
import logging
import random
from config import Config
from database.feasttable import FeastTable
from character import Character
import feast_rules as rules

log = logging.getLogger(__name__)


class Feast:
    def __init__(self, record):
        if not record:
            log.debug("No feast record found, initializing with default values.")
            # Initialize with default values
            self.id = -1
            self.created = None
            self.modified = None
            self.title = ''
            self.description = ''
            self.jdata = '{}'
            self.jdeck = '{}'
            self.data = {'participiants': {}, 'state': 'init', 'round': 0, 'rounds': 3, 'course': {}, 'royal': False, 'log': []}
            self.deck = Deck()
            self.id = FeastTable().insert(self)  # Initialize with default values; the new row's id
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
        self._upgrade()

    def _upgrade(self):
        """Older records lack the fields of the feast rules: fill in the defaults (not saved until the next update)."""
        self.data.setdefault('royal', False)
        self.data.setdefault('log', [])
        for p in self.data.get('participiants', {}).values():
            p.setdefault('geniality', 0)
            p.setdefault('left', False)
            p.setdefault('kept', [])
            p.setdefault('award', 0)
            p.setdefault('fumbled', False)

    def log_event(self, cid, text):
        self.data.setdefault('log', []).append({'round': self.data.get('round', 0), 'cid': str(cid), 'text': text})

    def add_participiant(self, cid):
        if (self.data['state'] == 'init'):
            cid = str(cid)
            c = Character.get_by_id(cid)
            if c is None:
                log.debug(f"Character {cid} does not exist.")
                return
            significant = rules.significant_traits(c.data.get('traits'), c.data.get('passions'))
            log.debug(f"Adding participiant with cid: {cid}")
            if cid not in self.data['participiants']:
                self.data['participiants'][cid] = {
                    'position': -1, 
                    'glory': 0, 
                    'state': 'init',
                    'rounds': {}, 
                    'activeCards':[],
                    'tags': [],
                    'significant': significant,
                    'geniality': 0,
                    'left': False,
                    'kept': [],
                    'award': 0,
                    'fumbled': False,
                    }
                log.debug(f"participiants {cid} added with initial score and empty cards.")
            else:
                log.debug(f"participiants {cid} already exists.")
            FeastTable().updateData(self);
        else:
            log.debug(f"Cannot add participiant {cid} after initialization.")

    def set_rounds(self, rounds):
        if (self.data['state'] == 'init'):
            log.debug(f"Setting rounds: {rounds}")
            self.data['rounds'] = rounds
            FeastTable().updateData(self)
        else:
            log.debug(f"Cannot set rounds after initialization.") 

    def set_participiant(self, cid, position, glory):
        if (self.data['state'] == 'init'):
            cid = str(cid)
            if cid in self.data['participiants']:
                log.debug(f"Setting participiants {cid} with position {position} and glory {glory}.")
                self.data['participiants'][cid]['position'] = position
                self.data['participiants'][cid]['glory'] = glory
                FeastTable().updateData(self)
            else:
                log.debug(f"participiants {cid} does not exist.")
        else:
            log.debug(f"Cannot set participiants {cid} after seating.")

    def number_of_cards(glory, position=None):
        return rules.number_of_cards(glory, position)

    def _draw_for(self, participiant, pround):
        """Draws the cards of a guest for the current round (none Above the Salt, below 1,000 Glory, while keeping a card
        that forbids drawing, or after leaving the feast)."""
        cards = []
        if not participiant.get('left') and not self.keeps_no_draw(participiant):
            for i in range(rules.number_of_cards(participiant['glory'], participiant['position'])):
                card = self.deck.draw()
                if card is None:
                    log.debug("No more cards to draw.")
                    break
                cards.append(card)
        pround['cards'] = cards
        FeastTable().updateDeck(self)

    def keeps_no_draw(self, participiant):
        feast = Config.feast()
        return any(feast.get(str(c), {}).get('keep', {}).get('draw', True) is False for c in participiant.get('kept', []))  # YAML: `draw: no` is False

    def draw_card(self, cid, force=False):
        cid = str(cid)
        if cid in self.data['participiants']: 
            log.debug(f"Drawing cards for participiants {cid}.")
            participiant = self.data['participiants'][cid]
            round = str(self.data['round'])
            pround = participiant['rounds'].get(round, {})
            if 'cards' in pround and not force:
                log.debug(f"Cards already drawn for participiants {cid} in round {round}.")
                return None
            self._draw_for(participiant, pround)
            participiant['rounds'][round] = pround
            FeastTable().updateData(self)
        else:
            log.debug(f"participiants {cid} does not exist. {self.data['participiants'].keys()}")
        return None    
    def card_enabled(cid, pround, significant = ()):
        """Can the character select card `cid` among the cards drawn in this round (`pround`)?
        A Host card is always enabled and it disables the other cards of the round; otherwise a card that is mandatory
        for one of the character's significant traits is enabled, and it disables the other cards."""
        cards = pround.get('cards', [])
        if cid not in cards:
            log.debug(f"Card {cid} is not enabled for the current round.")
            return False
        feast = Config.feast()

        def mandatory(card):
            return feast.get(str(card), {}).get('mandatory') in significant

        def host(card):
            return 'host' in feast.get(str(card), {}).get('tags', [])

        if host(cid):
            return True
        if any(host(card) for card in cards):
            log.debug("There is a host card in the round.")
            return False
        if mandatory(cid):
            return True
        for card in cards:
            if mandatory(card):
                log.debug(f"There is a mandatory card {card} in the round.")
                return False
        log.debug(f"Card {cid} is enabled for the current round.")
        return True

    def select_card(self, cid, card):
        cid = str(cid)
        if cid in self.data['participiants']:
            participiant = self.data['participiants'][cid]
            round = str(self.data['round'])  # JSON object keys are strings
            pround = participiant['rounds'].setdefault(round, {})
            if 'selected' in pround or participiant.get('left'):
                log.debug("Only one card can be played in a round.")
                return
            if Feast.card_enabled(card, pround, participiant['significant']):
                log.debug(f"Selecting card {card} for participiants {cid}.")
                pround['selected'] = card
                participiant['geniality'] += Config.feast().get(str(card), {}).get('geniality', 0)  # base Geniality of the card
                if 'keep' in Config.feast().get(str(card), {}).get('tags', []):
                    self.keep_card(cid, card)
                FeastTable().updateData(self)
        else:
            log.debug(f"participiants {cid} does not exist.")

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
        log.debug(f"Setting courses: {courses}")
        self.data['course'] = courses
        FeastTable().updateData(self)

    def setAction(self, cid, action):
        log.debug(f"Setting action for participiants {cid}: {action}")
        cid = str(cid)
        if cid in self.data['participiants']:
            rounds = self.data['participiants'][cid].setdefault('rounds', {})
            rounds.setdefault(str(self.data['round']), {})['action'] = action  # JSON object keys are strings
            FeastTable().updateData(self)
        else:
            log.debug(f"participiants {cid} does not exist.")

    def set_round_action(self, action, pid):
        log.debug(f"Setting round action for round {self.data['round']}: {action}")

        guest = self.data['participiants'][str(pid)] 
        if 'rounds' not in guest:
            guest['rounds'] = {}
        # JSON object keys are strings: an int key would not find the round after the data was saved and reloaded
        round = guest['rounds'].setdefault(str(self.data['round']), {})
        if ('action' in round) :
            log.debug(f"action set")
            return
        if action not in rules.ACTIVITIES:
            log.debug(f"Unknown action {action}.")
            return
        if action == 'card' and rules.number_of_cards(guest['glory'], guest['position']) == 0:
            log.debug("This guest cannot draw feast cards.")
            return
        round['action'] = action
        if self.data['round'] == 1:
            required = rules.first_round_requirement(guest.get('significant', []))
            if required and action not in required:
                round['requires'] = sorted(set(required.values()))  # a Temperate / Chaste roll must succeed first
        log.debug(f"Setting action for round {guest}: {action}")

        if ('card' == action and not round.get('requires')):
            self._draw_for(guest, round)
        FeastTable().updateData(self)

    def resolve_requirement(self, cid, trait, result):
        """The Temperate / Chaste roll of the first round: on a success the chosen activity goes on (the cards are drawn),
        otherwise the guest has to Indulge / Flirt instead."""
        guest = self.data['participiants'].get(str(cid))
        if guest is None or result not in rules.RESULTS:
            return False
        round = guest['rounds'].get(str(self.data['round']), {})
        if trait not in round.get('requires', []):
            return False
        round['requires'].remove(trait)
        if result in ('success', 'critical'):
            if round['action'] == 'card' and not round['requires'] and 'cards' not in round:
                self._draw_for(guest, round)
        else:
            round['requires'] = []
            round['action'] = rules.FORCED_ACTIVITY[trait]
            round.pop('cards', None)
            round['forced'] = True
        FeastTable().updateData(self)
        return True

    def record_result(self, cid, result):
        """Result (critical/success/failure/fumble) of the roll of a Gossip / Indulge / Flirt / Game round: Geniality."""
        guest = self.data['participiants'].get(str(cid))
        if guest is None or result not in rules.RESULTS:
            return False
        round = guest['rounds'].get(str(self.data['round']), {})
        if round.get('action') not in ('gossip', 'indulge', 'flirt', 'game') or 'result' in round or round.get('requires'):
            return False
        round['result'] = result
        guest['geniality'] += rules.activity_geniality(result)
        FeastTable().updateData(self)
        return True

    def seat_by_app(self, cid, result, second_result=None, app=None):
        """Seats a guest by the (unmodified) APP roll; a fumble needs the second roll."""
        guest = self.data['participiants'].get(str(cid))
        if self.data['state'] != 'init' or guest is None or result not in rules.RESULTS:
            return None
        if result == 'fumble':
            if second_result not in rules.RESULTS:
                return None
            guest['position'] = rules.seat_after_fumble(second_result)
            guest['fumbled'] = True
        else:
            guest['position'] = rules.seat_from_app_result(result)
            guest['fumbled'] = False
        if app is not None:
            guest['app'] = app  # the modified APP roll gives the order of drawing
        FeastTable().updateData(self)
        return guest['position']

    def keep_card(self, cid, card):
        """A Keeper card of the current hand stays with the guest (it gives its Geniality each round)."""
        guest = self.data['participiants'].get(str(cid))
        if guest is None or 'keep' not in Config.feast().get(str(card), {}).get('tags', []):
            return False
        if card not in guest['kept']:
            guest['kept'].append(card)
            FeastTable().updateData(self)
        return True

    def discard_kept(self, cid, card):
        guest = self.data['participiants'].get(str(cid))
        if guest is None or card not in guest['kept']:
            return False
        guest['kept'].remove(card)
        FeastTable().updateData(self)
        return True

    def leave(self, cid, result=None):
        """Leaving the feast. `result` is the Courtesy roll of a voluntary departure (None for a forced one):
        a critical success is worth 10 Glory, a fumble at a royal feast costs 1 Honor (noted in the log)."""
        guest = self.data['participiants'].get(str(cid))
        if guest is None or guest.get('left'):
            return False
        guest['left'] = True
        guest['geniality'] = rules.leave_geniality(guest['geniality'])
        if result == 'critical':
            guest['award'] += 10
        if result in ('success', 'critical'):
            self.log_event(cid, 'left politely, check Courtesy')
        elif result == 'fumble':
            self.log_event(cid, 'left rudely' + (' (royal feast: 1 Honor lost)' if self.data.get('royal') else ''))
        else:
            self.log_event(cid, 'left the feast')
        FeastTable().updateData(self)
        return True

    def return_to_feast(self, cid):
        guest = self.data['participiants'].get(str(cid))
        if guest is None or not guest.get('left') or self.data['state'] != 'feast':
            return False
        guest['left'] = False  # the Geniality starts again from 0 (a negative score was kept)
        FeastTable().updateData(self)
        return True

    def set_royal(self, royal):
        if self.data['state'] == 'init':
            self.data['royal'] = bool(royal)
            FeastTable().updateData(self)

    def end_round(self):
        """Closes the current round: Geniality of the seat and of the kept cards, the unplayed cards are discarded."""
        round = str(self.data['round'])
        feast = Config.feast()
        for cid, guest in self.data['participiants'].items():
            pround = guest['rounds'].setdefault(round, {})
            pround['discarded'] = [c for c in pround.get('cards', []) if c != pround.get('selected')]
            if guest.get('left'):
                continue
            guest['geniality'] += rules.seat_geniality(guest['position'], guest.get('fumbled', False))
            for c in guest.get('kept', []):
                guest['geniality'] += feast.get(str(c), {}).get('keep', {}).get('geniality', 0)

    def finish(self):
        """The end of the feast: Glory from the final Geniality."""
        results = rules.final_glory(self.data['participiants'], self.data.get('royal', False))
        for cid, glory in results.items():
            guest = self.data['participiants'][cid]
            guest['finalGlory'] = glory + guest.get('award', 0)
        self.data['state'] = 'end'

    def next_state(self):
        if self.data['state'] == 'init':
            self.data['state'] = 'feast'
            self.data['round'] = 1
        elif self.data['state'] == 'feast':
            self.end_round()
            if self.data['round'] < self.data['rounds']:
                self.data['round'] = 1 + self.data['round']
            else:
                self.finish()
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


    @staticmethod
    def card_ids():
        """The ids of the cards: the numeric keys of feast.yml (1..154 when it cannot be read)."""
        try:
            ids = sorted(int(k) for k in Config.feast() if str(k).isdigit())
        except Exception:
            ids = []
        return ids or list(range(1, 155))

    def shuffle(self):
        self.pos = -1
        self.deck = Deck.card_ids()
        random.shuffle(self.deck)