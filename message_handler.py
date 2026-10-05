from commands.base_command import BaseCommand

# This, in addition to tweaking __all__ on commands/__init__.py, 
# imports all classes inside the commands package.
from commands import *

import re
from utils import dice
from config import Config
import json
from json import JSONDecodeError
from database.checktable import CheckTable
from utils import *

from dicing import dicePattern, roll_dice

# Register all available commands
COMMAND_HANDLERS = {c.__name__.lower(): c()
                    for c in BaseCommand.__subclasses__()}
COMMAND_ALIASES = {}
for c in COMMAND_HANDLERS.values():
    if (c.aliases):
        for a in c.aliases:
            COMMAND_ALIASES[a] = c
COMMAND_ALIASES.update(COMMAND_HANDLERS)

###############################################################################


async def handle_command(command, args, message, bot_client, mid=0):
    # Check whether the command is supported, stop silently if it's not
    # (to prevent unnecesary spam if our bot shares the same command prefix 
    # with some other bot)

    if command not in COMMAND_ALIASES:
        result = dicePattern.match(message.content[1:])
        if result:
            (db, size, modifier) = result.groups()
            char = get_me(message)
            text, toJson = roll_dice(db, size, modifier)
            if (char!=None and message!=None) :
                toJson['char']=char.data['dbid']
                print(json.dumps(toJson, indent=4, ensure_ascii=False))
                CheckTable().add(character=char.id, command=message.content, result=json.dumps(toJson, indent=4, ensure_ascii=False))
            await message.channel.send(message.author.display_name + ': ' + text)
        return

    print(f"{message.author.name}: {Config.prefix}{command} "
          + " ".join(args))

    # Retrieve the command
    cmd_obj = COMMAND_ALIASES[command]
    if len(args) > 0 and (args[0] == '?' or args[0] == 'help'):
        await cmd_obj.help(args, message, bot_client)
    elif cmd_obj.params and len(args) < len(cmd_obj.params):
        await message.channel.send(message.author.mention + " Insufficient parameters!")
    else:
        await cmd_obj.handle(args, message, bot_client)
