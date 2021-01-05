import sys

import settings
import discord
import message_handler
import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from events.base_event              import BaseEvent
from events                         import *
from multiprocessing                import Process
from config                         import Config

# Set to remember if the bot is already running, since on_ready may be called
# more than once on reconnects
this = sys.modules[__name__]
this.running = False

# Scheduler that will be used to manage events
sched = AsyncIOScheduler()


###############################################################################

def main():
    # Initialize the client
    print("Starting up...")
    client = discord.Client()

    # Define event handlers for the client
    # on_ready may be called multiple times in the event of a reconnect,
    # hence the running flag
    @client.event
    async def on_ready():
        if this.running:
            return

        this.running = True

        # Set the playing status
        await client.change_presence(
                activity=discord.Game(name=f"{Config.prefix}senechal since {datetime.datetime.utcnow()}"))
        print("Logged in!", flush=True)

        # Load all events
        print("Loading events...", flush=True)
        n_ev = 0
        for ev in BaseEvent.__subclasses__():
            event = ev()
            sched.add_job(event.run, 'interval', (client,), 
                          minutes=event.interval_minutes)
            n_ev += 1
        sched.start()
        print(f"{n_ev} events loaded", flush=True)

        for guild in client.guilds:
            for m in guild.channels:
                if m.id == Config.mainChannelId:
                    Config.mainChannel = m

    # The message handler for both new message and edits
    async def common_handle_message(message):
        text = message.content
        if text.startswith(Config.prefix) and text != Config.prefix:
            cmd_split = text[len(Config.prefix):].split()
            print (cmd_split)
            try:
                await message_handler.handle_command(cmd_split[0].lower(), 
                                      cmd_split[1:], message, client)
            except:
                print("Error while handling message", flush=True)
                raise
#        else:
#            print(f"{text} vs {Config.prefix}")
    @client.event
    async def on_message(message):
        await common_handle_message(message)

    @client.event
    async def on_message_edit(before, after):
        await common_handle_message(after)

    Config.database()
    # Finally, set the bot running
    print(Config.config['token'])
    client.run(Config.config['token'])

###############################################################################


if __name__ == "__main__":
    main()
