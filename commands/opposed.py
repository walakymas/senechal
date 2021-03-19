from commands.base_command import BaseCommand
from utils import *


class Opposed(BaseCommand):

    def __init__(self):
        description = "Opposed check"
        params = ["spec"]
        super().__init__(description, params, ['o'])

    async def handle(self, params, message, client):
        pc = get_me(message)
        if pc:
            (spec, *extra) = params
            (modifier, obase) = extract(extra, [0, -1])
            for t, name, value, *name2 in get_checkable(pc.get_data(), spec):
                await embed_attack(message.channel, pc, name, value, int(modifier), -1, int(obase), -1)
