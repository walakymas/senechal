import discord
from discord.ext import commands
import datetime

from urllib import parse, request
import re

bot = commands.Bot(command_prefix='!', description="Szolgálatára Jóuram avagy Hölgyem...")

@bot.command()
async def ping(ctx):
    await ctx.send('Igen uram?')

@bot.command()
async def sum(ctx, numOne: int, numTwo: int):
    await ctx.send(numOne + numTwo)

@bot.command()
async def Perin(ctx, task="base", param=""):
    await pcInfo(ctx, 'perin', task, param)

@bot.command()
async def perin(ctx, task="base", param=""):
    await pcInfo(ctx, 'perin', task, param)

@bot.command()
async def pc(ctx, name="", task="base", param=""):
    await pcInfo(ctx, name, task, param)


async def pcInfo(ctx, name="", task="base", param=""):
    if (name == 'perin'):
        embed = discord.Embed(title=f"Sir Perin", description="Ide jöhet egy laza leírás", timestamp=datetime.datetime.utcnow(), color=discord.Color.blue())
        embed.add_field(name="Homeland", value=f"Salisbury")
        embed.add_field(name="Lord", value=f"Sir Roderick")
        embed.add_field(name="Home", value=f"Steeple Langford")
        embed.add_field(name="Distinctive Features", value=f"Strong speech")
        embed.add_field(name="Culture", value=f"Cymric (Pagan)")
        embed.add_field(name="Glory", value=f"1651")
        embed.add_field(name="Born", value=f"458")
        embed.add_field(name="Squired", value=f"472")
        embed.add_field(name="Knighted", value=f"479")
        embed.add_field(name="Family Characteristic", value=f"Clever at Games (+10 Gaming)")
        embed.set_thumbnail(url="https://i.pinimg.com/564x/33/45/2c/33452ccd88e91aabf2fc5d77b721264f.jpg")
        await ctx.send(embed=embed)
    else:
        await ctx.send(name +'? Sajnos nem ismerek ilyen lovagot')

@bot.command()
async def info(ctx):
    embed = discord.Embed(title=f"{ctx.guild.name}", description="Lorem Ipsum asdasd", timestamp=datetime.datetime.utcnow(), color=discord.Color.blue())
    embed.add_field(name="Server created at", value=f"{ctx.guild.created_at}")
    embed.add_field(name="Server Owner", value=f"{ctx.guild.owner}")
    embed.add_field(name="Server Region", value=f"{ctx.guild.region}")
    embed.add_field(name="Server ID", value=f"{ctx.guild.id}")
    # embed.set_thumbnail(url=f"{ctx.guild.icon}")
    embed.set_thumbnail(url="https://pluralsight.imgix.net/paths/python-7be70baaac.png")

    await ctx.send(embed=embed)

@bot.command()
async def youtube(ctx, *, search):
    query_string = parse.urlencode({'search_query': search})
    html_content = request.urlopen('http://www.youtube.com/results?' + query_string)
    # print(html_content.read().decode())
    search_results = re.findall('href=\"\\/watch\\?v=(.{11})', html_content.read().decode())
    print(search_results)
    # I will put just the first result, you can loop the response to show more results
    await ctx.send('https://www.youtube.com/watch?v=' + search_results[0])

# Events
@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.idle)
    print('My Ready is Body')


@bot.listen()
async def on_message(message):
    if "tutorial" in message.content.lower():
        # in this case don't respond with the word "Tutorial" or you will call the on_message event recursively
        await message.channel.send('This is that you want http://youtube.com/fazttech')
        await bot.process_commands(message)

bot.run('Nzc4NzI2OTc3OTkzMzEwMjM4.X7WMAw.nVMK9okNBVCs_1WLnVQPChc7AaI')

