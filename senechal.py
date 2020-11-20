import discord
from discord.ext import commands
import datetime

from urllib import parse, request
import re
import yaml
from  random import randint


bot = commands.Bot(command_prefix='!', description="Szolgálatára Jóuram avagy Hölgyem...")

@bot.command()
async def d20(ctx):
    await ctx.send(randint(1,20))

@bot.command()
async def d6(ctx, num = 1 ):
    sum = 0;
    s = '';
    for x in range(num):
        r = randint(1,6)
        sum += r
        if (x>0):
            s += '+';
        s += str(r)
    await ctx.send(s+'= '+str(sum))

@bot.command()
async def sum(ctx, numOne: int, numTwo: int):
    await ctx.send(numOne + numTwo)

@bot.command()
async def pc(ctx, name="", task="base", param=""):
    await pcInfo(ctx, name, task, param)

@bot.command()
async def npc(ctx, name="", task="base", param=""):
    await npcInfo(ctx, name, task, param)

async def embedNpc(ctx, pc, task, param):
    embed = discord.Embed(title=pc['name'], description=pc['description'], timestamp=datetime.datetime.utcnow(), color=discord.Color.blue())
    if ('url' in pc):
        embed.set_thumbnail(url=pc['url'])
    await ctx.send(embed=embed)

async def npcInfo(ctx, name="", task="base", param=""):
    print(name+","+task)
    if "all" == name:
        for pc in pcs.values():
            await embedPc(ctx, pc, task, param)
    else:
        count = 0
        print(npcs)
        for pc in npcs.values():
            print(pc['name'])
            if name.lower() in pc['name'].lower():
                count += 1
                await embedNpc(ctx, pc, task, param)
        if count == 0:
            await ctx.send(name +'? Ez a név iesmeretlen számomra. Utána érdeklődjem Jóuram?')

def tr(a):
    return str(a)+'/'+str(20-a)

async def embedPc(ctx, pc, task, param):
    if ("traits".startswith(task.lower())):
        embed = discord.Embed(title=pc['name'], timestamp=datetime.datetime.utcnow(), color=discord.Color.blue())
        embed.add_field(name="Chaste / Lustful", value=tr(pc['traits']['cha']))
        embed.add_field(name="Energetic / Lazy", value=tr(pc['traits']['ene']))
        embed.add_field(name="Forgiving / Vengeful", value=tr(pc['traits']['for']))
        embed.add_field(name="Generous / Selfish", value=tr(pc['traits']['gen']))
        embed.add_field(name="Honest / Deceitful", value=tr(pc['traits']['hon']))
        embed.add_field(name="Just / Arbitrary", value=tr(pc['traits']['jus']))
        embed.add_field(name="Merciful / Cruel", value=tr(pc['traits']['mer']))
        embed.add_field(name="Modest / Proud", value=tr(pc['traits']['mod']))
        embed.add_field(name="Prudent / Reckless", value=tr(pc['traits']['pru']))
        embed.add_field(name="Spiritual / Worldly", value=tr(pc['traits']['spi']))
        embed.add_field(name="Temperate / Indulgent", value=tr(pc['traits']['tem']))
        embed.add_field(name="Trusting / Suspicious", value=tr(pc['traits']['tru']))
        embed.add_field(name="Valorous / Cowardly", value=tr(pc['traits']['val']))
    elif ("stats".startswith(task.lower())):
        embed = discord.Embed(title=pc['name'],timestamp=datetime.datetime.utcnow(), color=discord.Color.blue())
        for name, value in pc['statistics'].items():
            embed.add_field(name=name, value=value)
        embed.add_field(name="Damage", value=str(round((pc['statistics']['str']+pc['statistics']['siz'])/6))+'d6');
        embed.add_field(name="Healing Rate", value=str(round((pc['statistics']['con']+pc['statistics']['siz'])/10)));
        embed.add_field(name="Move Rate", value=str(round((pc['statistics']['dex']+pc['statistics']['siz'])/10)));
        embed.add_field(name="HP", value=str(round((pc['statistics']['con']+pc['statistics']['siz']))));
        embed.add_field(name="Unconscious", value=str(round((pc['statistics']['con']+pc['statistics']['siz'])/4)));
    elif ("events".startswith(task.lower())):
        embed = discord.Embed(title=pc['name'],timestamp=datetime.datetime.utcnow(), color=discord.Color.blue())
        for name, value in pc['statistics'].items():
            embed.add_field(name=name, value=value)
    else:        
        embed = discord.Embed(title=pc['name'], description=pc['description'], timestamp=datetime.datetime.utcnow(), color=discord.Color.blue())
        for name, value in pc['main'].items():
            embed.add_field(name=name, value=value)
    embed.set_thumbnail(url=pc['url'])
    await ctx.send(embed=embed)


async def pcInfo(ctx, name="", task="base", param=""):
    print(name+","+task)
    if "all" == name:
        for pc in pcs.values():
            await embedPc(ctx, pc, task, param)
    else:
        count = 0
        for pc in pcs.values():
            if name.lower() in pc['name'].lower():
                count+=1
                await embedPc(ctx, pc, task, param)
        if count == 0:
            embed = discord.Embed(title=name, timestamp=datetime.datetime.utcnow(), color=discord.Color.blue())
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

@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.idle)
    print('My Ready is Body')

@bot.command()
async def frissito(ctx):
    database()
    await ctx.send("Egykupa bort jóuram?"); 


@bot.listen()
async def on_message(message):
    if ("senechal" in message.content.lower() or "seneschal" in message.content.lower()):
        # in this case don't respond with the word "Tutorial" or you will call the on_message event recursively
        await message.channel.send("""Szólított uram?

Egyelőre a következő kérdésekre tudok érdemben válaszolni:

!pc """ +str(list(pcs)).replace("'","")+ """ [base|stats|traits] 
!pc all [base|stats|traits] 
!npc { névrészlet } 
!npc all
!d20
!d6 [{num}]""")
        await bot.process_commands(message)
    elif "!20" == message.content:
        await d20(message.channel)

npcs = {}
pcs = {}
def database():
    global npcs, pcs
    with open(r'npc.yml') as file:
        npcs = yaml.load(file, Loader=yaml.FullLoader)
        print(npcs)
 
    with open(r'pc.yml') as file:
        pcs = yaml.load(file, Loader=yaml.FullLoader)
        print(pcs)

database()
with open(r'config.yml') as file:
    config = yaml.load(file, Loader=yaml.FullLoader)
    print(config['token'])
    bot.run(config['token'])

