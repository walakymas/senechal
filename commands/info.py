from commands.base_command  import BaseCommand

class Info(BaseCommand):

    def __init__(self):
        description = "Channel informations"
        params = None
        super().__init__(description, params)

    # Override the handle() method
    # It will be called every time the command is received
    async def handle(self, params, message, client):
        s = ""
        for guild in client.guilds:
            s+= "Guild: "+guild.name +"\n"
            for m in guild.channels:
                s += str(m.id) + ":"+m.name+"\n"
        await message.author.send(s);


