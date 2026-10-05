import json
import os
import subprocess
import sys

from commands.base_command import BaseCommand
from config import Config
from database.charactertable import CharacterTable
from database.playertable import PlayerTable
from database.proptable import PropertiesTable
from utils import *


class Admin(BaseCommand):

    def __init__(self):
        self.hidden = True
        description = "Adminisztrációs műveletek"
        super().__init__(description, None, None,
                         longdescription='''**!admin setChannel** az aktuális channel azonosítóját elmenti a properties táblába (`{prefix}channel` kulccsal), ide kerülnek a felhasználóknak szánt üzenetek''')


    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        rights = PlayerTable().rights(message.author.id)
        if rights <= 0 or not rights & 1:
            await message.channel.send(message.author.mention + " Nincs jogosultságod az admin parancshoz")
            return
        (task, *ex) = extract(params, [""])
        if "setchannel" == task.lower():
            PropertiesTable().set(f"{Config.prefix}channel", str(message.channel.id))
            await message.channel.send(f"Channel set: {message.channel.id}")
