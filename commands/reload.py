import os
import subprocess
import sys

from commands.base_command import BaseCommand
from config import Config


class Reload(BaseCommand):

    def __init__(self):
        self.hidden = 1
        description = "Restart"
        super().__init__(description, None, ['frissito', 'restart'])

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        if ("pull" in Config.config):
            process = subprocess.Popen(["git", "pull"], stdout=subprocess.PIPE)
            print(process.communicate()[0])
        os.execv(sys.executable, ['python3'] + sys.argv)
