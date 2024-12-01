import discord
import message_handler
import datetime
import sys
import os

from config                         import Config
from database.database              import Database

# Set to remember if the bot is already running, since on_ready may be called
# more than once on reconnects
this = sys.modules[__name__]
this.running = False

def main():
    print("Starting up bot..."+os.environ['token'])
    intents = discord.Intents.default()
    intents.guilds = True
    intents.members = True
    intents.message_content = True
    client = discord.Client(intents=intents)

    # Define event handlers for the client
    # on_ready may be called multiple times in the event of a reconnect,
    # hence the running flag
    @client.event
    async def on_ready():
        if this.running:
            return

        this.running = True

        await client.change_presence(
                activity=discord.Game(name=f"{Config.prefix}senechal since {datetime.datetime.now()}"))
        print("Logged in!", flush=True)

        for guild in client.guilds:
            for m in guild.channels:
                if m.id == Config.mainChannelId:
                    Config.mainChannel = m
        Database.initiate()

    # The message handler for both new message and edits
    async def common_handle_message(message):
        text = message.content
        if text.startswith(Config.prefix) and text != Config.prefix:
            cmd_split = text[len(Config.prefix):].split()
            if cmd_split[-1].startswith('<@!'):
                cmd_split = cmd_split[0:-1]
            try:
                await message_handler.handle_command(cmd_split[0].lower(), 
                                      cmd_split[1:], message, client)
            except:
                print("Error while handling message", flush=True)
                raise

    @client.event
    async def on_message(message):
        print(message.content)
        await common_handle_message(message)

    @client.event
    async def on_message_edit(before, after):
        print(after.content)
        await common_handle_message(after)

    Config.reload()
    client.run(Config.config['token'])

###############################################################################


if __name__ == "__main__":
    main()
