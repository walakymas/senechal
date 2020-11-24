import discord
from discord.ext import commands
import datetime

from urllib import parse, request
import re
import yaml
import subprocess
from  random import randint
import sqlite3

senechalBot = commands.Bot(command_prefix='!', description="Szolgálatára Jóuram avagy Hölgyem...")
conn = sqlite3.connect('status.db')
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS status (last_modified text, key text, svalue text, ivalue int, rvalue real)')
conn.commit()

@senechalBot.command()
async def d20(ctx):
    await ctx.send(randint(1,20))

@senechalBot.command()
async def d6(ctx, num = 1 ):
    if (num > 1):
        sum = 0;
        s = '';
        for x in range(num):
            r = randint(1,6)
            sum += r
            if (x>0):
                s += '+';
            s += str(r)
        await ctx.send(s+'= '+str(sum))
    elif num == 1:
        await ctx.send(randint(1,6))

@senechalBot.command()
async def c(ctx, spec="", modifier=0):
    """ check unopposed resolution

    """
    if (spec==""):
        for pc in pcs.values():
            if ctx.author.nick == pc['name']:
                embed = discord.Embed(title=pc['name'], timestamp=datetime.datetime.utcnow(), color=discord.Color.blue())
                s= ""
                for t in senechalConfig['traits']:
                    s+= t[0]+': '+str(pc['traits'][t[0].lower()[:3]])+"\n"
                    s+= t[1]+': '+str(20 - pc['traits'][t[0].lower()[:3]])+"\n"
                embed.add_field(name=':hearts: Traits', value=s, inline=False);
                s= ""
                for pn, pv in pc['passions'].items():
                    s+= pn+': '+str(pv)+"\n"
                embed.add_field(name=':homes: Passions', value=s, inline=False);
                s= ""
                for t in senechalConfig['stats']:
                    s+= t+': '+str(pc['stats'][t.lower()[:3]])+"\n"
                embed.add_field(name=':muscle: Stats', value=s, inline=False);
                s= ""
                for n, sg in pc['skills'].items():
                    for sn, sv in sg.items():
                        s+= sn+': '+str(sv)+"\n"
                embed.add_field(name=':crossed_swords: Skills', value=s, inline=False);
                await ctx.send(embed=embed)
    else:
        for pc in pcs.values():
            if ctx.author.nick == pc['name']:
                for n, sg in pc['skills'].items():
                    for sn, sv in sg.items():
                        if  sn.lower().startswith(spec.lower()):
                            await emberCheck(ctx, pc, sn, sv, modifier)
                for t in senechalConfig['traits']:
                    if  t[0].lower().startswith(spec.lower()):
                        await emberCheck(ctx, pc, t[0], pc['traits'][t[0].lower()[:3]], modifier)
                    if  t[1].lower().startswith(spec.lower()):
                        await emberCheck(ctx, pc, t[1], 20 - pc['traits'][t[0].lower()[:3]], modifier)
                for t in senechalConfig['stats']:
                    if  t.lower().startswith(spec.lower()):
                        await emberCheck(ctx, pc, t, pc['stats'][t.lower()[:3]], modifier)
                for pn, pv in pc['passions'].items():
                    if  pn.lower().startswith(spec.lower()):
                        await emberCheck(ctx, pc, pn, pv, modifier)

@senechalBot.command()
async def sum(ctx, numOne: int, numTwo: int):
    """ Két szám összeadása 

    !sum num1 num2"""
    await ctx.send(numOne + numTwo)

@senechalBot.command()
async def npc(ctx, *,name=""):
    """PC ifnok a npc.yml alapján
    Ahol a megadott névrészlet illeszkedi a játékosok """
    for pc in npcs.values():
        if "*" == name or name.lower() in pc['name'].lower():
            count += 1
            await embedNpc(ctx, pc)
    if count == 0:
        await ctx.send(name +'? Ez a név ismeretlen számomra. Utána érdeklődjem Jóuram?')

@senechalBot.command()
async def me(ctx, task="base", param=""):
    for pc in pcs.values():
        if ctx.author.nick == pc['name']:
            await embedPc(ctx, pc, task, param)

@senechalBot.command()
async def pc(ctx, name="", task="base", param=""):
    """PC ifnok a pc.yml alapján
    A task jelenleg alapértelmezésben base, de lehet statistics, traits vagy events is. Task nevénél elegendő 
    """
    count = 0
    for pc in pcs.values():
        if "*" == name or name.lower() in pc['name'].lower():
            count+=1
            await embedPc(ctx, pc, task, param)
    if count == 0:
        embed = discord.Embed(title=name, timestamp=datetime.datetime.utcnow(), color=discord.Color.blue())
        await ctx.send(name +'? Sajnos nem ismerek ilyen lovagot')

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
                    await emberCheck(ctx, pc, t[0], pc['traits'][t[0].lower()[:3]], modifier)
                if  "*" == trait or t[1].lower().startswith(trait.lower()):
                    await emberCheck(ctx, pc, t[1], 20 - pc['traits'][t[0].lower()[:3]], modifier)

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
                    await emberCheck(ctx, pc, t, pc['stats'][t.lower()[:3]], modifier)

@senechalBot.command()
async def skill(ctx, lord="", skill="", modifier=0):
    """ Skill check
    Lovagnév részletét, egy skill nevének részletét és módosítót lehet megadni
    A lord és skill paraméter helyett * is írható  
    """
    for pc in pcs.values():
        if  "*" == lord or lord.lower() in pc['name'].lower():
            for n, sg in pc['skills'].items():
                for sn, sv in sg.items():
                    if  "*" == skill or skill.lower() in sn.lower():
                        await emberCheck(ctx, pc, sn, sv, modifier)

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

async def embedNpc(ctx, pc):
    embed = discord.Embed(title=pc['name'], description=pc['description'], timestamp=datetime.datetime.utcnow(), color=discord.Color.blue())
    if ('url' in pc):
        embed.set_thumbnail(url=pc['url'])
    await ctx.send(embed=embed)

def tr(a):
    return str(a)+'/'+str(20-a)

async def embedPc(ctx, pc, task, param):
    embed = discord.Embed(title=pc['name'], timestamp=datetime.datetime.utcnow(), color=discord.Color.blue())
    if (task == "*" or task == "" or "base".startswith(task.lower())):
        embed = discord.Embed(title=pc['name'], description=pc['description'], timestamp=datetime.datetime.utcnow(), color=discord.Color.blue())
        for name, value in pc['main'].items():
            embed.add_field(name=name, value=value)
    if (task == "*" or "stats".startswith(task.lower())):
        for s in senechalConfig['stats']:
            embed.add_field(name=s, value=pc['stats'][s.lower()[:3]])
        embed.add_field(name="Damage", value=str(round((pc['stats']['str']+pc['stats']['siz'])/6))+'d6');
        embed.add_field(name="Healing Rate", value=str(round((pc['stats']['con']+pc['stats']['siz'])/10)));
        embed.add_field(name="Move Rate", value=str(round((pc['stats']['dex']+pc['stats']['siz'])/10)));
        embed.add_field(name="HP", value=str(round((pc['stats']['con']+pc['stats']['siz']))));
        embed.add_field(name="Unconscious", value=str(round((pc['stats']['con']+pc['stats']['siz'])/4)));
    if (task == "*" or "traits".startswith(task.lower())):
        traits = pc['traits'];
        result = "";
        for row in senechalConfig['traits']:
            print(row)
            result += row[0] +": "+str(traits[row[0].lower()[:3]])
            result += " / "
            result += row[1] +": "+str(20-traits[row[0].lower()[:3]])
            result += "\n"
        embed.add_field(name="Traits", value=result, inline=False)
    if (task == "*" or "events".startswith(task.lower())):
        glory = 0;
        for h in pc['events']:
            glory += h['glory']
            embed.add_field(name=str(h['year'])+" Glory: "+str(h['glory']), value=h['description'], inline=False)
        embed.add_field(name="Összes Glory: "+str(glory), value=h['description'], inline=False)
    if (task == "*" or "skills".startswith(task.lower())):
        for name, sg in pc['skills'].items():
            s = ""
            for name, value in sg.items():
                s += name + ": " + str(value)+"\n"
            embed.add_field(name="=o=o=o= "+name+" =o=o=o=" , value=s, inline=False)
    embed.set_thumbnail(url=pc['url'])
    await ctx.send(embed=embed)


async def emberCheck(ctx, lord, name, base, modifier):
    color=discord.Color.blue()
    ro = randint(1,20)
##    ro = 16
    r = ro;
    c = base + modifier;
    if (c>20):
        r += c-20
        c=20
    success = '---'
    url = ''
    if r==c:
        success = ":crown: Critical"
        color=discord.Color.gold()
    elif r>c:
        success = ":thumbsdown: Fail"
        color=discord.Color.orange()
    elif ro==20:
        success = ":person_facepalming: Fumble"
        color=discord.Color.red()
    else:
        success = ":thumbsup: Success"
        color=discord.Color.blue()


    embed = discord.Embed(title=lord['name'] +" "+ name + " Check", timestamp=datetime.datetime.utcnow(), color=color)
    embed.add_field(name="Dobás", value=str(ro));
    embed.add_field(name=name, value=str(base));
    if (modifier!=0):
        embed.add_field(name="Módosító", value=str(modifier));
    embed.add_field(name="Eredmény", value=success, inline=False);

    await ctx.send(embed=embed)

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
    senechalBot.run(config['token'])

