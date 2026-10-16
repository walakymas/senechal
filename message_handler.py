import logging
from commands.base_command import BaseCommand

# This, in addition to tweaking __all__ on commands/__init__.py, 
# imports all classes inside the commands package.
from commands import *

import re
import traceback
from utils import dice
from config import Config
import json
from json import JSONDecodeError
from database.checktable import CheckTable
from utils import *

from dicing import dicePattern, roll_dice
from permissions import has_rights, NO_RIGHTS

log = logging.getLogger(__name__)

# Register all available commands
COMMAND_HANDLERS = {c.__name__.lower(): c()
                    for c in BaseCommand.__subclasses__()}
COMMAND_ALIASES = {}
for c in COMMAND_HANDLERS.values():
    if (c.aliases):
        for a in c.aliases:
            if a in COMMAND_ALIASES:  # the last registered command wins; make the clash visible
                log.warning("alias '%s' of %s replaces %s", a, c.name, COMMAND_ALIASES[a].name)
            COMMAND_ALIASES[a] = c
COMMAND_ALIASES.update(COMMAND_HANDLERS)

###############################################################################


async def handle_command(command, args, message, bot_client, mid=0):
    # Check whether the command is supported, stop silently if it's not
    # (to prevent unnecesary spam if our bot shares the same command prefix 
    # with some other bot)

    if command not in COMMAND_ALIASES:
        result = dicePattern.match(message.content[len(Config.prefix):])
        if result:
            (db, size, modifier) = result.groups()
            char = get_me(message)
            try:
                text, toJson = roll_dice(db, size, modifier)
            except ValueError as ex:
                await message.channel.send(f"{message.author.mention} {ex}")
                return
            if (char!=None and message!=None) :
                toJson['char']=char.data['dbid']
                log.debug(json.dumps(toJson, ensure_ascii=False))
                CheckTable().add(character=char.id, command=message.content, result=json.dumps(toJson, indent=4, ensure_ascii=False))
            await message.channel.send(message.author.display_name + ': ' + text)
        return

    log.info("%s: %s%s", message.author.name, Config.prefix, command)
    log.debug("arguments: %s", args)

    # Retrieve the command
    cmd_obj = COMMAND_ALIASES[command]
    if len(args) > 0 and (args[0] == '?' or args[0] == 'help'):
        await cmd_obj.help(args, message, bot_client)
    elif getattr(cmd_obj, 'required_rights', 0) and not has_rights(message.author.id, cmd_obj.required_rights):
        await message.channel.send(message.author.mention + NO_RIGHTS)
    elif cmd_obj.params and len(args) < len(cmd_obj.params):
        await message.channel.send(message.author.mention + " Insufficient parameters!")
    else:
        try:
            await cmd_obj.handle(args, message, bot_client)
        except (ValueError, IndexError):
            # a missing parameter or a number that is not a number: tell the user instead of dying silently
            traceback.print_exc()
            await message.channel.send(f"{message.author.mention} Hibás vagy hiányzó paraméter, lásd: "
                                       f"`{Config.prefix}{command} help`")
