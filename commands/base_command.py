from config import Config


# Base command class
# Do not modify!
class BaseCommand:

    def __init__(self, description, params=None, aliases=None, longdescription=None):
        self.name = type(self).__name__.lower()
        self.params = params
        self.aliases = aliases
        desc = f"**{Config.prefix}{self.name}**"

        if self.params:
            desc += " " + " ".join(f"*<{p}>*" for p in params)

        desc += f": {description}."
        self.description = desc
        self.longdescription = longdescription

    async def help(self, params, message, client):
        if self.longdescription:
            await message.channel.send(self.longdescription)
        elif self.description:
            await message.channel.send(self.description)
        else:
            await message.channelsend(f"Can't help")

    # Every command must override this method
    async def handle(self, params, message, client):
        raise NotImplementedError  # To be defined by every command
