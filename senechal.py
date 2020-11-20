import discord
from discord.ext import commands
import datetime

from urllib import parse, request
import re
import yaml
import subprocess
from  random import randint

senechalBot = commands.Bot(command_prefix='!', description="Szolgálatára Jóuram avagy Hölgyem...")

@senechalBot.command()
async def d20(ctx):
    await ctx.send(randint(1,20))

@senechalBot.command()
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

@senechalBot.command()
async def sum(ctx, numOne: int, numTwo: int):
    """ Egyremegy 

    vagy mégsem"""
    await ctx.send(numOne + numTwo)

async def embedNpc(ctx, pc):
    embed = discord.Embed(title=pc['name'], description=pc['description'], timestamp=datetime.datetime.utcnow(), color=discord.Color.blue())
    if ('url' in pc):
        embed.set_thumbnail(url=pc['url'])
    await ctx.send(embed=embed)

@senechalBot.command()
async def npc(ctx, *,name=""):
    """PC ifnok a npc.yml alapján
    """
    if "all" == name:
        for pc in pcs.values():
            await embedPc(ctx, pc)
    else:
        count = 0
        for pc in npcs.values():
            if name.lower() in pc['name'].lower():
                count += 1
                await embedNpc(ctx, pc)
        if count == 0:
            await ctx.send(name +'? Ez a név iesmeretlen számomra. Utána érdeklődjem Jóuram?')

def tr(a):
    return str(a)+'/'+str(20-a)

async def embedPc(ctx, pc, task, param):
    if ("traits".startswith(task.lower())):
        embed = discord.Embed(title=pc['name'], timestamp=datetime.datetime.utcnow(), color=discord.Color.blue())
        traits = pc['traits'];
        result = "";
        for row in senechalConfig['traits']:
            print(row)
            result += row[0] +": "+str(traits[row[0].lower()[:3]])
            result += " / "
            result += row[1] +": "+str(20-traits[row[0].lower()[:3]])
            result += "\n"
        embed.add_field(name="Traits", value=result, inline=False)
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
        glory = 0;
        for h in pc['events']:
            glory += h['glory']
            embed.add_field(name=str(h['year'])+" Glory: "+str(h['glory']), value=h['description'], inline=False)
        embed.add_field(name="Összes Glory: "+str(glory), value=h['description'], inline=False)

    else:        
        embed = discord.Embed(title=pc['name'], description=pc['description'], timestamp=datetime.datetime.utcnow(), color=discord.Color.blue())
        for name, value in pc['main'].items():
            embed.add_field(name=name, value=value)
    embed.set_thumbnail(url=pc['url'])
    await ctx.send(embed=embed)


@senechalBot.command()
async def pc(ctx, name="", task="base", param=""):
    """PC ifnok a pc.yml alapján
    A task jelenleg alapértelmezésben base, de lehet statistics, traits vagy events is. Task nevénél elegendő 
    """
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

async def check(ctx, lord, name, base, modifier):
    color=discord.Color.blue()
    ro = randint(1,20)
##    ro = 16
    r = ro;
    c = base + modifier;
    if (c>20):
        r += c-20
        c=20
    success = '---'
    if r==c:
        success = "Critical"
        color=discord.Color.gold()
    elif r>c:
        success = "Fail"
        color=discord.Color.orange()
    elif ro==20:
        success = "Fumble"
        color=discord.Color.red()
    else:
        success = "Success"
        color=discord.Color.blue()

    embed = discord.Embed(title=lord['name'] +" "+ name + " Check", timestamp=datetime.datetime.utcnow(), color=color)
    embed.add_field(name="Dobás", value=str(ro));
    embed.add_field(name=name, value=str(base));
    if (modifier!=0):
        embed.add_field(name="Módosító", value=str(modifier));
    embed.add_field(name="Eredmény", value=success, inline=False);

    await ctx.send(embed=embed)

@senechalBot.command()
async def trait(ctx, lord="", trait="", modifier=0):
    """ Trait check
    Lovagnév részletét, egy trait nevének részletét és módosítót lehet megadni
    A lord és trait paraméter helyett * is írható  
    """
    for pc in pcs.values():
        if "*" == lord or lord.lower() in pc['name'].lower():
            for t in senechalConfig['traits']:
                if  "*" == trait or t[0].lower().startswith(trait.lower()):
                    await check(ctx, pc, t[0], pc['traits'][t[0].lower()[:3]], modifier)
                if  "*" == trait or t[1].lower().startswith(trait.lower()):
                    await check(ctx, pc, t[1], 20 - pc['traits'][t[0].lower()[:3]], modifier)

@senechalBot.command()
async def stat(ctx, lord="", stat="", modifier=0):
    """ Stat check
    Lovagnév részletét, egy stat nevének részletét és módosítót lehet megadni
    A lord és stat paraméter helyett * is írható  
    """
    for pc in pcs.values():
        if  "*" == lord or lord.lower() in pc['name'].lower():
            for t in senechalConfig['stats']:
                if  "*" == stat or t.lower().startswith(stat.lower()):
                    await check(ctx, pc, t, pc['statistics'][t.lower()[:3]], modifier)


@senechalBot.command(hidden=True)
async def frissito(ctx):
    if ("pull" in config):
        process = subprocess.Popen(["git","pull"], stdout=subprocess.PIPE)
        print(process.communicate()[0])

    database()
    await ctx.send("Egy kupa bort jóuram?"); 

@senechalBot.event
async def on_ready():
    await senechalBot.change_presence(status=discord.Status.idle)
    print('Készen állok a szolgálatra!')

@senechalBot.listen()
async def on_message(message):
    if "!20" == message.content:
        await d20(message.channel)

def database():
    global npcs, pcs, senechalConfig
    with open(r'senechal.yml') as file:
        senechalConfig = yaml.load(file, Loader=yaml.FullLoader)

    with open(r'npc.yml') as file:
        npcs = yaml.load(file, Loader=yaml.FullLoader)
 
    with open(r'pc.yml') as file:
        pcs = yaml.load(file, Loader=yaml.FullLoader)

database()
with open(r'config.yml') as file:
    config = yaml.load(file, Loader=yaml.FullLoader)
    print(config['token'])
    senechalBot.run(config['token'])

