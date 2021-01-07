from commands.base_command import BaseCommand
from config import Config


# This is a convenient command that automatically generates a helpful
# message showing all available commands
class Senechal(BaseCommand):

    def __init__(self):
        description = "Ez az üzenet. Opcionális paraméter: egy parancs neve"
        params = None
        super().__init__(description, params, ['h', 'help', 'segitseg'])

    async def handle(self, params, message, client):
        from message_handler import COMMAND_ALIASES
        if len(params) > 0 and params[0].lower() in COMMAND_ALIASES:
            cmd = COMMAND_ALIASES[params[0].lower()]
            await cmd.help(params, message, client)
        else:
            from message_handler import COMMAND_HANDLERS
            msg = message.author.mention + "\n"

            # Displays all descriptions, sorted alphabetically by command name
            for cmd in sorted(COMMAND_HANDLERS.items()):
                if not hasattr(cmd[1], 'hidden'):
                    msg += "\n" + cmd[1].description

            if 'intro' in Config.senechalConfig:
                msg += "\n\n" + Config.senechalConfig['intro']

            await message.channel.send(msg)
