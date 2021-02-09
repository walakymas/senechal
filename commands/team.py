from commands.base_command import BaseCommand
from config import Config
from utils import *


class Team(BaseCommand):

    def __init__(self):
        description = "Check a csapat minden tagjára"
        super().__init__(description, ['spec'], ['t'])

    async def handle(self, params, message, client):
        s = "Sir        Skill Dice Result\n"
        (spec, modifier) = extract(params, ['---', 0])
        print(modifier)
        if len(params) > 0:
            for char in Character.pcs():
                data = char.get_data()
                for t, name, value, *name2 in get_checkable(data, spec):
                    (color, text, ro, success) = check(value, int(modifier), False)

                    if 'trait' == t and success > 2:
                        (color2, text2, ro2, success2) = check(20 - value, int(modifier), False)
                        s += f"{data['shortName']:10}    {value:2}   {ro:2} {text:10} {name2[0]} {ro2:2} {text2}\n"
                    else:
                        s += f"{data['shortName']:10}    {value:2}   {ro:2} {text}\n"
            await message.channel.send("```\n" + s + "```")
        else:
            await message.channel.send("Kérlek uram add meg mit ellenőrizzünk!")
