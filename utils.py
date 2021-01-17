import datetime
from os import remove
from os.path import join
from random import randint

import discord
from discord import HTTPException
from emoji import emojize

import settings
from config import Config
from database.markstable import MarksTable


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
    print(client)
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


def get_checkable(pc, spec):
    spec = spec.lower()
    for n, sg in pc['skills'].items():
        for sn, sv in sg.items():
            if sn.lower().startswith(spec):
                yield ['skill', sn, sv]
    for t in Config.senechalConfig['traits']:
        if t[0].lower().startswith(spec):
            yield ['trait', t[0], pc['traits'][t[0].lower()[:3]], t[1]]
        if t[1].lower().startswith(spec.lower()):
            yield ['trait', t[1], 20 - pc['traits'][t[0].lower()[:3]], t[0]]
    for t in Config.senechalConfig['stats']:
        if t.lower().startswith(spec):
            yield ['stat', t, pc['stats'][t.lower()[:3]]]
    for pn, pv in pc['passions'].items():
        if pn.lower().startswith(spec):
            yield ['pass', pn, pv]


def tr(a):
    return str(a) + '/' + str(20 - a)


def dice(size):
    return int(overwrite('debugdice', randint(1, size)))


def overwrite(cname, orig):
    if cname in Config.config and "---" != Config.config[cname]:
        return Config.config[cname]
    else:
        return orig


def get_me(message):
    i = int(overwrite('debugme', message.author.id))
    if i in Config.characters:
        return Config.characters[i]
    from database.lordtable import LordTable
    row = LordTable().get_by_value(0, 'mychannel', i)
    if row:
        return Config.characters[int(row[2])]
    return None


def get_embed(pc, description=0):
    if description:
        embed = discord.Embed(title=pc['name'],
                              description=pc['description'],
                              timestamp=datetime.datetime.now(),
                              color=discord.Color.blue())
    else:
        embed = discord.Embed(title=pc['name'], color=discord.Color.blue(),
                              timestamp=datetime.datetime.now(),
                              footer="alma")
    if 'url' in pc:
        embed.set_thumbnail(url=pc['url'])
        embed.set_footer(text=f"{Config.prefix}senechal")
    return embed


async def embed_pc(channel, pc, task, param):
    print(task)
    if task == "*" or task == "" or "base".startswith(task.lower()):
        embed = get_embed(pc, 1)
        from database.eventstable import EventsTable
        if 'memberId' in pc:
            pc['main']['Glory'] = EventsTable().glory(pc['memberId'])
        if 'main' in pc:
            for name, value in pc['main'].items():
                embed.add_field(name=name, value=value)
        await channel.send(embed=embed)
    if task == "*" or "stats".startswith(task.lower()):
        if 'stats' in pc:
            embed = get_embed(pc, 0)
            for s in Config.senechalConfig['stats']:
                embed.add_field(name=s, value=pc['stats'][s.lower()[:3]])
            embed.add_field(name="Damage", value=str(round((pc['stats']['str'] + pc['stats']['siz']) / 6)) + 'd6');
            embed.add_field(name="Healing Rate", value=str(round((pc['stats']['con'] + pc['stats']['siz']) / 10)));
            embed.add_field(name="Move Rate", value=str(round((pc['stats']['dex'] + pc['stats']['siz']) / 10)));
            embed.add_field(name="HP", value=str(round((pc['stats']['con'] + pc['stats']['siz']))));
            embed.add_field(name="Unconscious", value=str(round((pc['stats']['con'] + pc['stats']['siz']) / 4)));
            await channel.send(embed=embed)
    if task == "*" or "traits".startswith(task.lower()):
        if 'traits' in pc:
            embed = get_embed(pc, 0)
            traits = pc['traits'];
            result = "";
            for row in Config.senechalConfig['traits']:
                result += f"{row[0]:10} {traits[row[0].lower()[:3]]:2} / {row[1]:10} {20-traits[row[0].lower()[:3]]:2}\n"
            embed.add_field(name="Traits", value=f"```{result}```", inline=False)
            await channel.send(embed=embed)
    if task == "*" or "events".startswith(task.lower()):
        embed = get_embed(pc)
        from database.eventstable import EventsTable
        embed.add_field(name="Összes Glory", value=f"{EventsTable().glory(pc['memberId'])}", inline=False)
        msg = f""
        count = 0
        for (id, created, modified, year, lord, desc, glory) in EventsTable().list(pc['memberId']):
            count += 1
            if count > 25:
                count = 1
                await channel.send(embed=embed)
                embed = get_embed(pc, 0)
            embed.add_field(name=f"Year: {year}  Glory: {glory} Id:{id}", value=desc, inline=False)
        await channel.send(embed=embed)
    if task == "*" or "skills".startswith(task.lower()):
        if 'skills' in pc:
            embed = get_embed(pc, 0)
            for sn, sg in pc['skills'].items():
                s = ""
                for name, value in sg.items():
                    s += name + ": " + str(value) + "\n"
                embed.add_field(name=":crossed_swords:  " + sn, value=f"```{s}```", inline=False)
            await channel.send(embed=embed)
    if task == "*" or "marks".startswith(task.lower()):
        embed = get_embed(pc, 0)
        year = MarksTable().year()
        rows = MarksTable().list(lord=int(pc['memberId']), year=year)
        msg = f"```ID  Modified   Spec\n";
        marks = []
        for row in rows:
            if row[5] not in marks:
                marks.append(row[5])
                msg += f"{row[0]:3} {str(row[2])[:10]} {row[5]:15}\n"
        embed.add_field(name=f"Év: {year} pipák", value=msg+"```", inline=False )
        await channel.send(embed=embed)
    if task == "*" or "winter".startswith(task.lower()):
        winter = winterData(pc)
        i = int(pc['memberId'])
        embed = get_embed(pc)
        year = MarksTable().year()
        embed.add_field(name=f"{year} tele", value=f"```Stewardship: {winter['stewardship']}```", inline=False)
        msg = ""
        for h in winter['horses']:
            msg += f"  {h}\n"
        embed.add_field(name="Lovak", value=f"```{msg}```", inline=False)
        rows = MarksTable().list(lord=i, year=year)
        msg = f"\nModified   Spec\n";
        marks = []
        for row in rows:
            for t, name, value, *name2 in get_checkable(pc, row[5]):
                if name not in marks:
                    marks.append(name)
                    msg += f"{str(row[2])[:10]} {name:15} {value:2} \n"
        embed.add_field(name="Pipák", value=f"```{msg}```", inline=False)

        await channel.send(embed=embed)


def winterData(me):
    ss = 0;
    for s in get_checkable(me, 'stewardship'):
        ss = s[2]
    winter = {'stewardship': ss, 'horses':['charger', 'rouncy', 'rouncy', 'stumper', 'stumper' ]}
    if 'winter' in me:
        if 'stewardship' in me['winter']:
            winter['stewardship'] = me['winter']['stewardship']
        if 'horses' in me['winter']:
            winter['horses'] = me['winter']['horses']
    ss = 0;
    from database.lordtable import LordTable
    for r in LordTable().list(int(me['memberId']), 0):
        if r[3] == 'winter.stewardship':
            winter['stewardship'] = r[5];
        elif r[3] == 'winter.horses':
            winter['horses'] = r[5].strip().split(',')
    return winter


def check(base, modifier=0, emoji=True):
    ro = dice(20)
    r = ro;
    c = base + int(modifier)
    if c > 20:
        r -= c - 20
        c = 20
    if ro == c:
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
        return [color, success_emojis[success] + " " + successes[success], ro, success]
    else:
        return [color, successes[success], ro, success]


async def embed_check(ctx, lord, name, base, modifier):
    (color, text, ro, success) = check(base, modifier)

    embed = discord.Embed(title=lord['name'] + " " + name + " Check", timestamp=datetime.datetime.utcnow(), color=color)
    embed.add_field(name="Dobás", value=str(ro));
    embed.add_field(name=name, value=str(base));
    if (modifier != 0):
        embed.add_field(name="Módosító", value=str(modifier));
    embed.add_field(name="Eredmény", value=text, inline=False);

    await ctx.send(embed=embed)


async def embed_trait(ctx, lord, name, base, modifier, name2):
    (color, text, ro, success) = check(base, modifier)

    embed = discord.Embed(title=lord['name'] + " " + name + " Trait Check", timestamp=datetime.datetime.utcnow(),
                          color=color)
    embed.add_field(name="Eredmény", value=text + " (" + str(ro) + " vs " + str(base + int(modifier)) + ")", inline=False);
    if success > 2:
        (color, text, ro, success) = check(20 - base, 0)
        embed.add_field(name=name2, value=text + " (" + str(ro) + " vs " + str((20 - base)) + ")",
                        inline=False);

    await ctx.send(embed=embed)


async def embed_attack(ctx, lord, name, base, modifier, damage=-1, obase=-1, odamage=-1):
    (color, text, ro, success) = check(base, modifier)

    embed = discord.Embed(title=name + " Check", timestamp=datetime.datetime.utcnow(), color=color)
    embed.add_field(name=lord['name'], value=text + " (" + str(ro) + " vs " + str(base + modifier) + ")", inline=False);
    if damage >= 0 and success <= 2:
        sum = 0;
        if success == 2:
            damage += 4
        for x in range(damage):
            sum += dice(6)
        embed.add_field(name="Sebzés", value=str(sum));
    if obase > 0:
        (ocolor, otext, oro, osuccess) = check(obase, 0)
        embed.add_field(name="Opposer", value=otext + " (" + str(oro) + " vs " + str(obase) + ")", inline=False);
        if odamage >= 0 and osuccess <= 2:
            sum = 0;
            if osuccess == 2:
                odamage += 4
            for x in range(odamage):
                sum += dice(6)
            embed.add_field(name="Sebzés", value=str(sum));

    await ctx.send(embed=embed)


def extract(l, defa):
    res = list(l)[0:len(defa)] + defa[len(l):]
    return res


successes = ['?', 'Success', 'Critical', 'Fumble', 'Fail']
success_emojis = ['?', ':thumbsdown:', ':crown:', ':person_facepalming:', ':thumbsdown:']
