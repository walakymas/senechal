from commands.base_command import BaseCommand
from utils import *
from database.eventstable import EventsTable
import re

class Event(BaseCommand):
    yearPattern = re.compile('^[yY]([0-9]+)$')

    def __init__(self):
        self.hidden = 1
        description = 'Event/history kezelés glory támogatással.'
        super().__init__(description, None, ['e', 'esemeny'], longdescription='''**!event [list]** karakter eventjeinek listája  
**!event {glory} {leírás}** új event  rögzítése aktuális karakterhez és évhez
amennyiben a leírás y{év} kezdetű, akkor azt is levágja és a megadott évhez rögzíti
**!event remove {id}** event eltávolítása
**!event modify {id} {glory} {leírás}** event módosítása''')

    async def handle(self, params, message, client):
        me = get_me(message)
        if me:
            if len(params)== 0 or 'list' == params[0].lower():
                msg = f"**{me['name']}**\n"
                glory = 0;
                for e in EventsTable().list(me['memberId']):
                    msg+=f"***Year: {e[3]}  Glory: {e[6]}*** *Id:{e[0]}*\n{e[5]}\n"
                    glory += int(e[6])
                await message.channel.send(f"**Összes Glory: {glory}**\n\n{msg}")
            elif 'modify' == params[0].lower():
                id = int(params[1])
                glory = int(params[2])
                EventsTable().update(id, message.content[message.content.index(" ")+len(params[0])+len(params[1])+len(params[2])+3:].strip(), glory)
                await message.channel.send("Updated")
            elif 'remove' == params[0].lower():
                EventsTable().remove(int(params[1]))
                await message.channel.send("Removed")
            else:
                glory = int(params[0])
                year = -1
                result = Event.yearPattern.match(params[1])
                msg = message.content[message.content.index(" ")+len(params[0])+1:].strip()
                if result:
                    year = int(params[1][1:])
                    msg = msg[len(params[1])+1:]
                EventsTable().insert(me['memberId'], msg, glory, year)
                await message.channel.send("inserted")
