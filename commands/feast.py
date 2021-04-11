from commands.base_command import BaseCommand
from utils import *
from database.eventstable import EventsTable
import re

class Feast(BaseCommand):
    yearPattern = re.compile('^[yY]([0-9]+)$')

    def __init__(self):
        self.hidden = 0
        description = 'Feast'
        super().__init__(description, None, ['lakoma','l'], longdescription='''**!lakoma [draw|húz|huz]** ''')

    async def handle(self, params, message, client):
        me = get_me(message)
        if me:
            await message.channel.send(f"**{me.name}**\nhttps://raw.githubusercontent.com/walakymas/lakoma/main/images/{randint(1, 155)}.jpg")
