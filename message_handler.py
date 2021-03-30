from commands.base_command import BaseCommand

# This, in addition to tweaking __all__ on commands/__init__.py, 
# imports all classes inside the commands package.
from commands import *

import re
from utils import dice
from config import Config

dicePattern = re.compile('([0-9]*)[dD]([0-9]+)([+-][0-9]+)?')

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
            num = 1
            (db, size, *other) = result.groups()
            if ('' != db):
                num = int(db)
            sum = 0;
            s = '';
            for x in range(num):
                r = dice(int(size))
                sum += r
                if (x > 0):
                    s += '+';
                s += str(r)
            if result.group(3):
                sum += int(result.group(3))
                s += result.group(3)
            await message.channel.send(message.author.display_name + ': ' + s + '= ' + str(sum))
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
