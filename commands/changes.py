from commands.base_command import BaseCommand
from config                import Config

# This is a convenient command that automatically generates a helpful
# message showing all available commands
class Changes(BaseCommand):

    def __init__(self):
        description = "Változáslista"
        params = None
        super().__init__(description, params)

    async def handle(self, params, message, client):
        if 'changes' in Config.senechalConfig:
            await message.channel.send(Config.senechalConfig['changes'])
