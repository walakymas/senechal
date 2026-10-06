"""Lets the HTTP API (worker threads) post messages and run bot commands through the Discord client
of the same process.

server.py fills `client` and `loop`; they stay None when only the API runs.
"""
import asyncio

from config import Config

client = None
loop = None


def send(channel_id, text, timeout=10):
    """Sends `text` to the channel; returns False if the bot is not running or the channel is unknown."""
    if client is None or loop is None:
        return False
    channel = client.get_channel(int(channel_id))
    if channel is None:
        return False
    asyncio.run_coroutine_threadsafe(channel.send(text), loop).result(timeout)
    return True


class WebAuthor:
    """The part of discord.Member the whitelisted commands use."""

    def __init__(self, did, name):
        self.id = int(did) if did else 0
        self.name = self.display_name = name
        self.mention = f"<@{self.id}>"


class WebMessage:
    """Stands in for the discord.Message of a command typed in the channel."""

    def __init__(self, content, channel, author):
        self.content = content
        self.channel = channel
        self.guild = getattr(channel, 'guild', None)
        self.author = author


def shown_command(content):
    """The command without the target (cid:.. / <@!..>) the web page appends: '!c Sword 0'."""
    words = content[len(Config.prefix):].split()
    return Config.prefix + ' '.join(w for w in words if not (w.startswith('cid:') or w.startswith('<@')))


async def _run_command(channel, content, did, author_name):
    import message_handler
    from utils import get_me
    message = WebMessage(content, channel, WebAuthor(did, author_name))
    from utils import strip_mention
    cmd_split = strip_mention(content[len(Config.prefix):].split())
    if not cmd_split:
        return
    char = get_me(message)
    await channel.send(f"{char.name if char else author_name}: `{shown_command(content)}`")
    await message_handler.handle_command(cmd_split[0].lower(), cmd_split[1:], message, client)


def run_command(channel_id, content, did, author_name, timeout=30):
    """Runs a bot command (full text with prefix) as if it was typed in the channel by the user.
    The channel first shows which command ran. Returns False if it could not be run."""
    if client is None or loop is None:
        return False
    channel = client.get_channel(int(channel_id))
    if channel is None:
        return False
    asyncio.run_coroutine_threadsafe(_run_command(channel, content, did, author_name), loop).result(timeout)
    return True
