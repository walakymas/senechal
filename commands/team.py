from commands.base_command import BaseCommand
from config import Config
from utils import *


class Team(BaseCommand):

    def __init__(self):
        description = "Check a csapat minden tagjára"
        params = None
        super().__init__(description, ['spec'], ['t'])

    async def handle(self, params, message, client):
        s = "Sir        Skill Dice Result\n"
        (spec, modifier) = extract(params, ['---', 0])
        print(modifier)
        if len(params) > 0:
            for pc in Config.pcs():
                for t, name, value, *name2 in getCheckable(pc, spec):
                    (color, text, ro, success) = check(value, int(modifier))

                    if 'trait' == t and success > 2:
                        (color2, text2, ro2, success2) = check(20 - value, int(modifier))
                        s += f"{pc['shortName']:10}    {value:2}   {ro:2} {successes[success]:10} {name2[0]} {ro2:2} {successes[success2]}\n"
                    else:
                        s += f"{pc['shortName']:10}    {value:2}   {ro:2} {successes[success]}\n"
            await message.channel.send("```\n" + s + "```")
        else:
            await message.channel.send("Kérlek uram add meg mitt ellenőrizzünk!")
