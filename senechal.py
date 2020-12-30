#!/usr/bin/env python

import os
import sys
import discord
from discord.ext import commands
import datetime

from urllib import parse, request
import re
import yaml
import subprocess
from  random import randint
import sqlite3

successes = ['?','Success','Critical','Fumble','Fail']

def database():
    global characters, senechalConfig
    with open(r'senechal.yml') as file:
        senechalConfig = yaml.load(file, Loader=yaml.FullLoader)

    with open(r'characters.yml') as file:
        characters = yaml.load(file, Loader=yaml.FullLoader)
        for c in characters:
            character = characters[c]
            if ('memberId' in character):
                g = 0;
                for h in character['events']:
                    g+=h['glory']
                character['main']['Glory']=g
                for n, sg in character['skills'].items():
                    for sn, sv in sg.items():
                        if '.' == str(sv)[:1]:
                            sg[sn]=sg[sv[1:]]


database()
intents = discord.Intents.all()
prefix = '!'
mainChannelId=779078275111714917 #:senechal
mainChannel=0
conn = sqlite3.connect('status.db')
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS status (last_modified text, key text, svalue text, ivalue int, rvalue real)')
c.execute('CREATE TABLE IF NOT EXISTS pcstat (last_modified text, type int, subtype int, key text, svalue text, ivalue int, rvalue real)')
conn.commit()
with open(r'config.yml') as file:
    config = yaml.load(file, Loader=yaml.FullLoader)
    if ('prefix' in config):
        prefix = config['prefix']
    if ('mainChannel' in config):
        mainChannelId = config['mainChannel']
senechalBot = commands.Bot(command_prefix=prefix, description="Szolgálatára Jóuram avagy Hölgyem...",intents=intents)

dicePattern = re.compile('([0-9]*)[dD]([0-9]+)([+-][0-9]+)?')

def dice(size):
    if ('fixDice' in config):
        return config['fixDice']
    else:
        return randint(1,size)

@senechalBot.command(aliases=['a'])
async def attack(ctx, spec="", modifier=0):
    if isinstance(ctx.channel, discord.DMChannel):
        await mainChannel.send('magán')
    else:
        await ctx.send('rendes channel')

@senechalBot.command(aliases=['o','op'])
async def opposed(ctx, spec="", modifier=0):
    if isinstance(ctx.channel, discord.DMChannel):
        await mainChannel.send('magán')
    else:
        await ctx.send('rendes channel')


@senechalBot.command()
async def team(ctx, spec="", modifier=0):
    s = "Name       Skill Dice Result\n"
    for pc in characters.values():
        if 'memberId' in pc:
            for n, sg in pc['skills'].items():
                for sn, sv in sg.items():
                    if  sn.lower().startswith(spec.lower()):
                        (color, text, ro, success) = check(sv, modifier)
                        s+=f"{pc['shortName']:10}    {sv:2}   {ro:2} {successes[success]}\n"
    await ctx.send("```\n"+s+"```")


@senechalBot.command(aliases=['check'])
async def c(ctx, spec="", modifier=0):
    """ check unopposed resolution

    """

    if ctx.author.id in characters:
        pc = characters[ctx.author.id]
        if (spec==""):
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
            for n, sg in pc['skills'].items():
                for sn, sv in sg.items():
                    if  sn.lower().startswith(spec.lower()):
                        await embedCheck(ctx, pc, sn, sv, modifier)
            for t in senechalConfig['traits']:
                if  t[0].lower().startswith(spec.lower()):
                    await embedCheck(ctx, pc, t[0], pc['traits'][t[0].lower()[:3]], modifier)
                    await embedCheck(ctx, pc, t[1], 20 - pc['traits'][t[0].lower()[:3]], modifier)
                if  t[1].lower().startswith(spec.lower()):
                    await embedCheck(ctx, pc, t[1], 20 - pc['traits'][t[0].lower()[:3]], modifier)
                    await embedCheck(ctx, pc, t[0], pc['traits'][t[0].lower()[:3]], modifier)
            for t in senechalConfig['stats']:
                if  t.lower().startswith(spec.lower()):
                    await embedCheck(ctx, pc, t, pc['stats'][t.lower()[:3]], modifier)
            for pn, pv in pc['passions'].items():
                if  pn.lower().startswith(spec.lower()):
                    await embedCheck(ctx, pc, pn, pv, modifier)
    else:
        await ctx.send('Nem ismerem Önt jóuram!')


@senechalBot.command()
async def me(ctx, task="base", param=""):
    if ctx.author.id in characters:
        await embedPc(ctx, characters[ctx.author.id], task, param)

@senechalBot.command(aliases=['npc','character','cha'])
async def pc(ctx, name="", task="base", param=""):
    """PC ifnok a pc.yml alapján
    A task jelenleg alapértelmezésben base, de lehet statistics, traits vagy events is. Task nevénél elegendő 
    """
    count = 0
    for pc in characters.values():
        if "*" == name or name.lower() in pc['name'].lower():
            count+=1
            await embedPc(ctx, pc, task, param)
    if count == 0:
        await ctx.send(name +'? Sajnos nem ismerek ilyen lovagot')

@senechalBot.command(aliases=['t','tr'])
async def trait(ctx, lord="", trait="", modifier=0):
    """ Trait check
    Lovagnév részletét, egy trait nevének részletét és módosítót lehet megadni
    A lord és trait paraméter helyett * is írható  
        """
    for pc in characters.values():
        if "*" == lord or lord.lower() in pc['name'].lower():
            for t in senechalConfig['traits']:
                if  "*" == trait or t[0].lower().startswith(trait.lower()):
                    await embedCheck(ctx, pc, t[0], pc['traits'][t[0].lower()[:3]], modifier)
                if  "*" == trait or t[1].lower().startswith(trait.lower()):
                    await embedCheck(ctx, pc, t[1], 20 - pc['traits'][t[0].lower()[:3]], modifier)

@senechalBot.command()
async def stat(ctx, lord="", stat="", modifier=0):
    """ Stat check
    Lovagnév részletét, egy stat nevének részletét és módosítót lehet megadni
    A lord és stat paraméter helyett * is írható  
    """
    for pc in characters.values():
        if  "*" == lord or lord.lower() in pc['name'].lower():
            for t in senechalConfig['stats']:
                if  "*" == stat or t.lower().startswith(stat.lower()):
                    await embedCheck(ctx, pc, t, pc['stats'][t.lower()[:3]], modifier)

@senechalBot.command()
async def skill(ctx, lord="", skill="", modifier=0):
    """ Skill check
    Lovagnév részletét, egy skill nevének részletét és módosítót lehet megadni
    A lord és skill paraméter helyett * is írható  
    """
    for pc in characters.values():
        if  "*" == lord or lord.lower() in pc['name'].lower():
            for n, sg in pc['skills'].items():
                for sn, sv in sg.items():
                    if  "*" == skill or skill.lower() in sn.lower():
                        await embedCheck(ctx, pc, sn, sv, modifier)

@senechalBot.command(hidden=True,aliases=['refresh'])
async def frissito(ctx):
    if ("pull" in config):
        process = subprocess.Popen(["git","pull"], stdout=subprocess.PIPE)
        print(process.communicate()[0])
        os.execv(sys.executable, ['python'] + sys.argv)
    database()
    await ctx.author.send("Egy kupa bort jóuram?"); 

@senechalBot.command()
async def info(ctx):
    s = ""
    for guild in senechalBot.guilds:
        s+= "Guild: "+guild.name +"\n"
        for m in guild.channels:
            s += str(m.id) + ":"+m.name+"\n"
    await ctx.author.send(s); 

@senechalBot.command(hidden=True)
async def senechal(ctx):
    if ('intro' in senechalConfig):
         await ctx.author.send(senechalConfig['intro']);

@senechalBot.command(hidden=True)
async def changes(ctx):
    if ('changes' in senechalConfig):
         await ctx.author.send(senechalConfig['changes']);

@senechalBot.event
async def on_ready():
    global mainChannel
    await senechalBot.change_presence(status=discord.Status.idle)
    print('Készen állok a szolgálatra!')
    for guild in senechalBot.guilds:
        for m in guild.channels:
            if m.id == mainChannelId:
                mainChannel = m

@senechalBot.event
async def on_message(message):
    if prefix == message.content[:1]:
        result = dicePattern.match(message.content[1:])
        if result:
            num =1
            (db, size, *other) = result.groups()
            if ('' != db):
                num = int(db)
            sum = 0;
            s = '';
            for x in range(num):
                r = dice(int(size))
                sum += r
                if (x>0):
                    s += '+';
                s += str(r)
            if result.group(3):
                sum += int(result.group(3))
                s+=result.group(3)
            await message.channel.send(message.author.display_name+': '+s+'= '+str(sum))
            return
    await senechalBot.process_commands(message)

async def embedNpc(ctx, npc):
    embed = discord.Embed(title=npc['name'], description=npc['description'], timestamp=datetime.datetime.utcnow(), color=discord.Color.blue())
    if ('url' in npc):
        embed.set_thumbnail(url=npc['url'])
    await ctx.send(embed=embed)

def tr(a):
    return str(a)+'/'+str(20-a)

def getEmbed(pc, description=0):
    embed = 0
    if (description):
        embed = discord.Embed(title=pc['name'], description=pc['description'], timestamp=datetime.datetime.utcnow(), color=discord.Color.blue())
    else:        
        embed = discord.Embed(title=pc['name'], timestamp=datetime.datetime.utcnow(), color=discord.Color.blue())
    if ('url' in pc):
        embed.set_thumbnail(url=pc['url'])
    return embed


async def embedPc(ctx, pc, task, param):
    if (task == "*" or task == "" or "base".startswith(task.lower())):
        embed = getEmbed(pc, 1)
        if ('main' in pc):
            for name, value in pc['main'].items():
                embed.add_field(name=name, value=value)
        await ctx.send(embed=embed)
    if (task == "*" or "stats".startswith(task.lower())):
        if 'stats' in  pc:
            embed = getEmbed(pc, 0)
            for s in senechalConfig['stats']:
                embed.add_field(name=s, value=pc['stats'][s.lower()[:3]])
            embed.add_field(name="Damage", value=str(round((pc['stats']['str']+pc['stats']['siz'])/6))+'d6');
            embed.add_field(name="Healing Rate", value=str(round((pc['stats']['con']+pc['stats']['siz'])/10)));
            embed.add_field(name="Move Rate", value=str(round((pc['stats']['dex']+pc['stats']['siz'])/10)));
            embed.add_field(name="HP", value=str(round((pc['stats']['con']+pc['stats']['siz']))));
            embed.add_field(name="Unconscious", value=str(round((pc['stats']['con']+pc['stats']['siz'])/4)));
            await ctx.send(embed=embed)
    if (task == "*" or "traits".startswith(task.lower())):
        if 'trait' in pc:
            embed = getEmbed(pc, 0)
            traits = pc['traits'];
            result = "";
            for row in senechalConfig['traits']:
                print(row)
                result += row[0] +": "+str(traits[row[0].lower()[:3]])
                result += " / "
                result += row[1] +": "+str(20-traits[row[0].lower()[:3]])
                result += "\n"
            embed.add_field(name="Traits", value=result, inline=False)
            await ctx.send(embed=embed)
    if (task == "*" or "events".startswith(task.lower())):
        if 'events' in pc:
            embed = getEmbed(pc, 0)
            glory = 0;
            count=0
            for h in pc['events']:
                count+=1
                if (count>20):
                    count=1
                    await ctx.send(embed=embed)
                    embed = getEmbed(pc, 0)
                glory += h['glory']
                embed.add_field(name=str(h['year'])+" Glory: "+str(h['glory']), value=h['description'], inline=False)
            embed.add_field(name="Összes Glory: "+str(glory), value=":glory:", inline=False)
            await ctx.send(embed=embed)
    if (task == "*" or "skills".startswith(task.lower())):
        if 'skills' in pc:
            embed = getEmbed(pc, 0)
            for sn, sg in pc['skills'].items():
                s = ""
                for name, value in sg.items():
                    s += name + ": " + str(value)+"\n"
                embed.add_field(name=":crossed_swords:  "+sn , value=s, inline=False)
            await ctx.send(embed=embed)

def check(base, modifier):
    color=discord.Color.blue()
    ro = dice(20)
    r = ro;
    c = base + modifier;
    if (c>20):
        r -= c-20
        c=20
    text = '---'
    success = 1
    if ro==c:
        text = ":crown: Critical"
        color=discord.Color.gold()
        success = 2
    elif ro==20:
        text = ":person_facepalming: Fumble"
        color=discord.Color.red()
        success = 3
    elif r>c:
        text = ":thumbsdown: Fail"
        color=discord.Color.orange()
        success = 4
    else:
        text = ":thumbsup: Success"
        color=discord.Color.blue()
        success = 1

    return [color, text, ro, success]    


async def embedCheck(ctx, lord, name, base, modifier):
    (color, text, ro, success) = check(base, modifier)

    embed = discord.Embed(title=lord['name'] +" "+ name + " Check", timestamp=datetime.datetime.utcnow(), color=color)
    embed.add_field(name="Dobás", value=str(ro));
    embed.add_field(name=name, value=str(base));
    if (modifier!=0):
        embed.add_field(name="Módosító", value=str(modifier));
    embed.add_field(name="Eredmény", value=text, inline=False);

    await ctx.send(embed=embed)

async def embedTrait(ctx, lord, name, base, modifier, name2):
    (color, text, ro, success) = check(base, modifier)

    embed = discord.Embed(title=lord['name'] +" "+ name + " Check", timestamp=datetime.datetime.utcnow(), color=color)
    embed.add_field(name="Dobás", value=str(ro));
    embed.add_field(name=name, value=str(base));
    if (modifier!=0):
        embed.add_field(name="Módosító", value=str(modifier));
    embed.add_field(name="Eredmény", value=text, inline=False);

    await ctx.send(embed=embed)

async def embedAttack(ctx, lord, name, base, modifier, damage):
    (color, text, ro, success) = check(base, modifier)

    embed = discord.Embed(title=lord['name'] +" "+ name + " Check", timestamp=datetime.datetime.utcnow(), color=color)
    embed.add_field(name="Dobás", value=str(ro));
    embed.add_field(name=name, value=str(base));
    if (modifier!=0):
        embed.add_field(name="Módosító", value=str(modifier));
    embed.add_field(name="Eredmény", value=text, inline=False);
    if damage >= 0:
        sum = 0;
        if success==2:
            damage += 4
        for x in range(damage):
            sum += dice(6)
        embed.add_field(name="Sebzés", value=str(modifier));

    await ctx.send(embed=embed)


senechalBot.run(config['token'])

