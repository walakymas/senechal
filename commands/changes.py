from commands.base_command import BaseCommand
from config                import Config

# This is a convenient command that automatically generates a helpful
# message showing all available commands
class Changes(BaseCommand):

    def __init__(self):
        description = "Változáslista"
        params = None
        super().__init__(description, params, ['valtozas'])

    async def handle(self, params, message, client):
        if 'changes' in Config.senechalConfig:
            # Discord messages are limited to 2000 characters: send the entries (separated by blank lines) in chunks
            chunk = ''
            for entry in Config.senechalConfig['changes'].strip().split('\n\n'):
                if chunk and len(chunk) + len(entry) + 2 > 1900:
                    await message.channel.send(chunk)
                    chunk = ''
                chunk += ('\n\n' if chunk else '') + entry
            if chunk:
                await message.channel.send(chunk)
