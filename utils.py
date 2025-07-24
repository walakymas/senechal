import datetime
from os import remove
from os.path import join
from random import randint

import discord
from discord import HTTPException, Embed
from emoji import emojize

import settings
from character import Character
from config import Config
from database.markstable import MarksTable
from database.checktable import CheckTable
import json
from json import JSONDecodeError


# Returns a path relative to the bot directory
def get_rel_path(rel_path):
    return join(settings.BASE_DIR, rel_path)


# Returns an emoji as required to send it in a message
# You can pass the emoji name with or without colons
# If fail_silently is True, it will not raise an exception
# if the emoji is not found, it will return the input instead
def get_emoji(emoji_name, fail_silently=False):
    alias = emoji_name if emoji_name[0] == emoji_name[-1] == ":" \
        else f":{emoji_name}:"
    the_emoji = emojize(alias, use_aliases=True)

    if the_emoji == alias and not fail_silently:
        raise ValueError(f"Emoji {alias} not found!")

    return the_emoji


# A shortcut to get a channel by a certain attribute
# Uses the channel name by default
# If many matching channels are found, returns the first one
def get_channel(client, value, attribute="name"):
    channel = next((c for c in client.get_all_channels()
                    if getattr(c, attribute).lower() == value.lower()), None)
    if not channel:
        raise ValueError("No such channel")
    return channel


# Shortcut method to send a message in a channel with a certain name
# You can pass more positional arguments to send_message
# Uses get_channel, so you should be sure that the bot has access to only
# one channel with such name
async def send_in_channel(client, channel_name, *args):
    await client.send_message(get_channel(client, channel_name), *args)


# Attempts to upload a file in a certain channel
# content refers to the additional text that can be sent alongside the file
# delete_after_send can be set to True to delete the file afterwards
async def try_upload_file(client, channel, file_path, content=None,
                          delete_after_send=False, retries=3, filename=None):
    used_retries = 0
    sent_msg = None
    while not sent_msg and used_retries < retries:
        try:
            sent_msg = await channel.send(file=discord.File(file_path, filename=filename), content=content)
        except HTTPException:
            used_retries += 1

    if delete_after_send:
        remove(file_path)

    if not sent_msg:
        await client.send_message(channel, "Oops, something happened. Please try again.")

    return sent_msg


def get_checkable(data, spec):
    spec = spec.lower().replace("_", " ")
    for n, sg in data['skills'].items():
        for sn, sv in sg.items():
            if sn.lower().startswith(spec):
                yield ['skill', sn, int(sv)]
    for t in Config.senechalConfig['traits']:
        if t[0].lower().startswith(spec):
            yield ['trait', t[0], int(data['traits'][t[0].lower()[:3]]), t[1]]
        if t[1].lower().startswith(spec.lower()):
            yield ['trait', t[1], 20 - int(data['traits'][t[0].lower()[:3]]), t[0]]
    for t in Config.senechalConfig['stats']:
        if t.lower().startswith(spec):
            yield ['stat', t, int(data['stats'][t.lower()[:3]])]
    for pn, pv in data['passions'].items():
        if pn.lower().startswith(spec):
            yield ['pass', pn, int(pv)]


def tr(a):
    return str(a) + '/' + str(20 - a)


def dice(size):
    return int(overwrite('debugdice', randint(1, size)))


def overwrite(cname, orig):
    if cname in Config.config and "---" != Config.config[cname]:
        return Config.config[cname]
    else:
        return orig


def get_me(message, force=False):
    cmd_split = message.content[len(Config.prefix):].split()
    me = None
    if cmd_split[-1].startswith('<@!'):
        print(f'get_me 1 "{cmd_split[-1][3:-1]}"')
        me = Character.get_by_memberid(cmd_split[-1][3:-1], force=force)
    elif cmd_split[-1].startswith('<@'):
        print(f'get_me 2 "{cmd_split[-1][3:-1]}"')
        me = Character.get_by_memberid(cmd_split[-1][2:-1], force=force)
    elif cmd_split[-1].startswith('++'):
        me = Character.get_by_name(cmd_split[-1][2:], force=force)
    elif cmd_split[-1].startswith('++'):
        me = Character.get_by_name(cmd_split[-1][2:], force=force)

    if me:
        return me
    else:
        return Character.get_by_memberid(message.author.id, force=force)


def get_embed(char, description=False):
    embed = discord.Embed(title=char.name,
                          color=discord.Color.blue(),
                          timestamp=datetime.datetime.now()
                          )

    if description:
        embed.description = char.get_data(False)['description']
    else:
        embed.description = ''
    if char.url:
        embed.set_thumbnail(url=char.url)
    embed.set_footer(text=f"{Config.prefix}senechal")
    return embed


def add_field(embed, name=None, value=None, inline=False, formatted=False):
    if not embed.description or len(embed.description) == 0:
        embed.description = ""
    if formatted:
        embed.description += f"{name} `{value}`   "
    else:
        embed.description += f"\n**{name}** {value}"


async def embed_char(channel, char, task, param, ctx=None, message=None):
    embeds = []
    data = char.get_data()
    marks = []
    year = MarksTable().year()
    rows = MarksTable().list(dbid=data['dbid'], year=year)
    for row in rows:
        if row[5] not in marks:
            marks.append(row[5])
    if task == "*" or task == "" or "base".startswith(task.lower()):
        embed = get_embed(char, True)
        if 'main' in data:
            from database.eventstable import EventsTable
            data['main']['Glory'] = EventsTable().glory(char.id)
        embed.description += "\n"
        skipp = ['Glory', 'Born', 'Squired', 'Knighted']

        for name, value in data['main'].items():
            if name not in skipp:
                embed.description += f"{name} `{value}`  "
        embed.description += "\n"
        if 'Born' in data['main']:
            embed.description += f"Born `{data['main']['Born']}` "
            embed.description += f"Year `{year}` "
            embed.description += f"Age `{year - int(data['main']['Born'])}` "
        if 'Squired' in data['main']:
            embed.description += f"Squired `{data['main']['Squired']}` "
        if 'Knighted' in data['main']:
            embed.description += f"Knighted `{data['main']['Knighted']}` "
        if 'stats' in data:
            embed.description += "\n\n"
            for s in Config.senechalConfig['stats']:
                add_field(embed, name=s, value=data['stats'][s.lower()[:3]], formatted=True)
            add_field(embed, name="Damage", value=str(char.get_damage()) + 'd6', formatted=True)
            add_field(embed, name="Damage", value=str(char.get_damage()) + 'd6', formatted=True)
            add_field(embed, name="Healing Rate", value=str(round((data['stats']['con'] + data['stats']['siz']) / 10)),
                      formatted=True)
            add_field(embed, name="Move Rate", value=str(round((data['stats']['dex'] + data['stats']['siz']) / 10)),
                      formatted=True)
            add_field(embed, name="HP", value=str(round((data['stats']['con'] + data['stats']['siz']))),
                      formatted=True)
            add_field(embed, name="Unconscious", value=str(round((data['stats']['con'] + data['stats']['siz']) / 4)),
                      formatted=True)
        embeds.append(embed)
    if task == "*" or "traits".startswith(task.lower()):
        if 'traits' in data:
            embed = get_embed(char)
            traits = data['traits']
            embed.description = f"**Traits**"
            for row in Config.senechalConfig['traits']:
                if row[0] in marks:
                    embed.description += f"\n__{row[0]:10}__"
                else:
                    embed.description += f"\n{row[0]:10}"
                embed.description += f" `{traits[row[0].lower()[:3]]:2}` / "
                if row[1] in marks:
                    embed.description += f"__{row[1]:10}__"
                else:
                    embed.description += f"{row[1]:10}"
                embed.description += f" `{20 - traits[row[0].lower()[:3]]:2}`"
            embeds.append(embed)
    if task == "*" or "events".startswith(task.lower()):
        if char.memberid:
            embed = get_embed(char)
            from database.eventstable import EventsTable
            embed.description += f"\n**Összes Glory**:  {EventsTable().glory(char.id)}"
            for (id, created, modified, year, lord, desc, glory, dbid) in EventsTable().list(char.id):

                if len(embed.description) + len(desc) > 2000:
                    embeds.append(embed)
                    embed = get_embed(char)
                embed.description += f"\n**Year: {year}  Glory: {glory} Id:{id}** {desc}"
            embeds.append(embed)

    if task == "*" or "passions".startswith(task.lower()):
        if 'passions' in data:
            embed = get_embed(char, 0)
            embed.description = ":crossed_swords:  **Passions**\n"
            for name, value in sorted(data['passions'].items()):
                if name in marks:
                    embed.description += f"__{name}__: `{value}`  "
                else:
                    embed.description += f"{name}: `{value}`  "
            embeds.append(embed)
        else:
            print("no passions")
    if task == "*" or "skills".startswith(task.lower()):
        if 'skills' in data:
            embed = get_embed(char, 0)
            for sn, sg in data['skills'].items():
                s = ""
                embed.description += f"\n:crossed_swords: **{sn}**\n"
                for name, value in sorted(sg.items()):
                    if name in marks:
                        embed.description += f"__{name}__: `{value}`  "
                    else:
                        embed.description += f"{name}: `{value}`  "
            embeds.append(embed)
    if task == "*" or "marks".startswith(task.lower()):
        embed = get_embed(char, 0)
        msg = f"```ID  Modified   Spec\n"
        marks = []
        for row in rows:
            if row[5] not in marks:
                marks.append(row[5])
                msg += f"{row[0]:3} {str(row[2])[:10]} {row[5]:15}\n"
        add_field(embed, name=f"Év: {year} pipák", value=msg + "```", inline=False)
        embeds.append(embed)
    if task == "*" or "combat".startswith(task.lower()):
        embed = get_embed(char)
        embed.description = f"**Combat**\n"
        w = char.get_weapon(data['combat']['weapon'])
        embed.description += f"\n **Weapon**: {data['combat']['weapon']}"
        if 'skill' in w:
            embed.description += f" **Skill**: `{w['skill']}`"
            embed.description += f" **Damage**: `{round((data['stats']['str'] + data['stats']['siz']) / 6)}d6`"
        embed.description += f"\n**Armor**: {data['combat']['armor']}"
        embed.description += f" **Shield**: {data['combat']['shield']}"
        a = Config.senechal()['armors'][data['combat']['armor']]
        s = Config.senechal()['shields'][data['combat']['shield']]
        embed.description += f"\n**Damage reduction**: `{a['red']} + {s['red']}`"
        embed.description += f" **Dex modifier**: `{a['dex']}`"
        embed.description += f" **Effective Dex**: `{data['stats']['dex'] + a['dex']}`"
        embeds.append(embed)
    if task == "*" or "winter".startswith(task.lower()):
        winter = winterData(char)
        embed = get_embed(char)
        add_field(embed, name=f"{year} tele", value=f"```Stewardship: {winter['stewardship']}```", inline=False)
        msg = ""
        for h in winter['horses']:
            msg += f"  {h}\n"
        add_field(embed, name="Lovak", value=f"```{msg}```", inline=False)
        msg = f"\nModified   Spec\n"
        marks = []
        for row in rows:
            for t, name, value, *name2 in get_checkable(data, row[5]):
                if name not in marks:
                    marks.append(name)
                    msg += f"{str(row[2])[:10]} {name:15} {value:2} \n"
        add_field(embed, name="Pipák", value=f"```{msg}```", inline=False)
        embeds.append(embed)
    if len(embeds) == 0:
        return
        return
    elif len(embeds) == 1:
        await channel.send(embed=embeds[0])
    else:
        paginator = EmbedPaginator(ctx, embeds)
        await paginator.run([message.author], channel=channel)
        await paginator.run([message.author], channel=channel)

def winterData(char):
    ss = 0
    data = char.get_data()
    for s in get_checkable(data, 'stewardship'):
        ss = s[2]
    winter = {'stewardship': ss, 'horses': ['charger', 'rouncy', 'rouncy', 'sumpter', 'sumpter']}
    if 'winter' in data:
        if 'stewardship' in data['winter']:
            winter['stewardship'] = data['winter']['stewardship']
        if 'horses' in data['winter']:
            winter['horses'] = data['winter']['horses']
    from database.lordtable import LordTable
    for r in LordTable().list(char.memberid, 0):
        if r[4] == 'winter.stewardship':
            winter['stewardship'] = r[5]
            winter['stewardship'] = r[5]
        elif r[4] == 'winter.horses':
            winter['horses'] = r[5].strip().split(',')
    return winter


def check(base, modifier=0, emoji=True):
    (color, text, r, ro, success) = check2(base, modifier, emoji)
    return [color, text, r, success]

def check2(base, modifier=0, emoji=True):
    ro = dice(20)
    r = ro
    c = base + int(modifier)
    if c > 20:
        r += c - 20
        c = 20
    if r == c or r > 20:
        color = discord.Color.gold()
        success = 2
    elif ro == 20:
        color = discord.Color.red()
        success = 3
    elif r > c:
        color = discord.Color.orange()
        success = 4
    else:
        color = discord.Color.blue()
        success = 1
    if emoji:
        return [color, success_emojis[success] + " " + successes[success], r, ro, success]
    else:
        return [color, successes[success], r, ro, success]


async def embed_check(ctx, data, name, base, modifier, message=None, char:Character=None):
    (color, text, r, ro, success) = check2(base, modifier)

    if (char!=None and message!=None) :
        toJson = {}
        toJson['action']='check'
        toJson['char']=data['dbid']
        c = {}
        toJson['c1']=c
        c['name']=name
        c['base']=base
        c['modifier']=modifier
        c['text']=text
        c['ro']=ro
        c['success']=successes[success]
        print(json.dumps(toJson, indent=4, ensure_ascii=False))
        CheckTable().add(character=char.id, command=message.content, result=json.dumps(toJson, indent=4, ensure_ascii=False))

    embed = discord.Embed(title=data['name'] + " " + name + " Check", timestamp=datetime.datetime.utcnow(), color=color)

    add_field(embed, name="Dobás", value=str(ro))
    add_field(embed, name=name, value=str(base))
    add_field(embed, name="Dobás", value=str(ro))
    add_field(embed, name=name, value=str(base))
    if modifier != 0:
        add_field(embed, name="Módosító", value=str(modifier))
    add_field(embed, name="Eredmény", value=text, inline=False)
    await ctx.send(embed=embed)


async def embed_trait(ctx, data, name, base, modifier, name2, message=None, char:Character=None):
    (color, text, r, ro, success) = check2(base, modifier)

    toJson = {}
    toJson['action']='trait'
    toJson['char']=data['dbid']
    c = {}
    toJson['c1']=c
    c['name']=name
    c['base']=base
    c['modifier']=modifier
    c['text']=text
    c['r']=r
    c['ro']=ro
    c['success']=successes[success]

    embed = discord.Embed(title=f"{data['name']} {name} Trait Check", timestamp=datetime.datetime.utcnow(),
                          color=color)
    add_field(embed, name="Eredmény", value=f"{text} ({r}  vs {base + int(modifier)})",
              inline=False)
    if success > 2:
        (color, text, r, ro, success) = check2(20 - base, 0)
        c = {}
        toJson['c2']=c
        c['name']=name2
        c['base']=20-base
        c['modifier']=modifier
        c['text']=text
        c['r']=r
        c['ro']=ro
        c['success']=successes[success]
        add_field(embed, name=name2, value=f"{text} ({r}  vs {20 -base})",
                  inline=False)
    if (char!=None and message!=None) :
        print(json.dumps(toJson, indent=4, ensure_ascii=False))
        CheckTable().add(character=char.id, command=message.content, result=json.dumps(toJson, indent=4, ensure_ascii=False))

    await ctx.send(embed=embed)


async def embed_attack(ctx, character, name, base, modifier, damage=-1, obase=-1, odamage=-1):
    (color, text, ro, success) = check(base, modifier)

    data = character.get_data(True)
    embed = discord.Embed(title=name + " Check", timestamp=datetime.datetime.utcnow(), color=color)
    add_field(embed, name=data['name'], value=text + " (" + str(ro) + " vs " + str(base + modifier) + ")",
              inline=False)
    if damage >= 0 and success <= 2:
        if damage == 0:
            damage = round((data['stats']['str'] + data['stats']['siz']) / 6)
        sum = 0
        sum = 0
        if success == 2:
            damage += 4
        s = ''
        s = ''
        for x in range(damage):
            d = dice(6)
            d = dice(6)
            if sum > 0:
                s += '+'
            s += str(d)
            sum += d
        add_field(embed, name="Sebzés", value=s + ' = ' + str(sum))
        add_field(embed, name="Sebzés", value=s + ' = ' + str(sum))
    if obase > 0:
        (ocolor, otext, oro, osuccess) = check(obase, 0)
        add_field(embed, name="Opposer", value=otext + " (" + str(oro) + " vs " + str(obase) + ")", inline=False)
        add_field(embed, name="Opposer", value=otext + " (" + str(oro) + " vs " + str(obase) + ")", inline=False)
        if odamage >= 0 and osuccess <= 2:
            sum = 0
            sum = 0
            if osuccess == 2:
                odamage += 4
            for x in range(odamage):
                sum += dice(6)
            add_field(embed, name="Sebzés", value=str(sum))
            add_field(embed, name="Sebzés", value=str(sum))

    await ctx.send(embed=embed)


def extract(l, defa):
    res = list(l)[0:len(defa)] + defa[len(l):]
    return res


successes = ['?', 'Success', 'Critical', 'Fumble', 'Fail']
success_emojis = ['?', ':thumbsup:', ':crown:', ':person_facepalming:', ':thumbsdown:']
