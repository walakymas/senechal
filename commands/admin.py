import json
import os
import subprocess
import sys

from commands.base_command import BaseCommand
from config import Config
from database.charactertable import CharacterTable
from utils import *


class Admin(BaseCommand):

    def __init__(self):
        self.hidden = True
        description = "Restart"
        super().__init__(description, None, ['save'],
                         longdescription='''Újraindítja a botot. Aamennyiben engedélyezve van a configban, előtte frissíti a githubról a configot és a forráskódot''')


    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        (task, *ex) = extract(params, ["save"])
        if "save" == task:
            year = MarksTable.year()
            for pc in Character.pcs():
                data = pc.data

                def map(m, p):
                    if not p in m:
                        m[p] = {}
                    return m[p]

                history = map(data, 'history')
                skills = map(history, 'skills')
                years = map(history, 'years')
                for sgn, sgv in data['skills'].items():
                    group = map(skills, sgn)
                    for sn, sv in sgv.items():
                        map(group, sn)[year] = sv

                def save(p):
                    stats = map(history, p)
                    for n, v in data[p].items():
                        map(stats, n)[year] = v
                save('stats')
                save('traits')
                save('passions')
                years[year] = 'saved'
                CharacterTable().set_json(data['dbid'], json.dumps(data, ensure_ascii=False, indent=2))
                await message.author.send(f"Saved {year} {pc.name}")