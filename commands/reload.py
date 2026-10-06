import asyncio
import os
import subprocess
import sys

from commands.base_command import BaseCommand
from config import Config
from permissions import ADMIN


class Reload(BaseCommand):
    required_rights = ADMIN

    def __init__(self):
        self.hidden = 1
        description = "Restart"
        super().__init__(description, None, ['frissito', 'restart'],
                         longdescription='''Újraindítja a botot. Aamennyiben engedélyezve van a configban, előtte frissíti a githubról a configot és a forráskódot''')

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        if ("pull" in Config.config):
            process = await asyncio.to_thread(subprocess.run, ["git", "pull"], stdout=subprocess.PIPE)
            print(process.stdout)
        os.execv(sys.executable, ['python3'] + sys.argv)
