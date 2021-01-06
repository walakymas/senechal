from commands.base_command import BaseCommand
from utils import *


class Event(BaseCommand):

    def __init__(self):
        self.hidden = 1
        description = ''
        super().__init__(description, ['task'])

    async def handle(self, params, message, client):
        me = getMe(message)
        if me:
            print('event:'+me['name'])