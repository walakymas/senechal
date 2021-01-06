from commands.base_command import BaseCommand
from config import Config
from database.database import Database
from utils import *


class Note(BaseCommand):

    def __init__(self):
        self.hidden = 1
        description = 'Under construction'
        super().__init__(description, ['task'],['n'])

    async def handle(self, params, message, client):
        me = getMe(message)
        if me:
            print('note:'+me['name'])