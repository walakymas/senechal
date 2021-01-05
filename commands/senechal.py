from commands.base_command import BaseCommand
from config                import Config

# This is a convenient command that automatically generates a helpful
# message showing all available commands
class Senechal(BaseCommand):

    def __init__(self):
        description = "Displays this help message"
        params = None
        super().__init__(description, params)

    async def handle(self, params, message, client):
        from message_handler import COMMAND_HANDLERS
        msg = message.author.mention + "\n"

        # Displays all descriptions, sorted alphabetically by command name
        for cmd in sorted(COMMAND_HANDLERS.items()):
            msg += "\n" + cmd[1].description

        if 'intro' in Config.senechalConfig:
            msg += "\n\n" + Config.senechalConfig['intro']

        await message.channel.send(msg)