from commands.base_command import BaseCommand
from utils import *


class Weapon(BaseCommand):

    def __init__(self):
        super().__init__("Támadás próba az aktuális karakternek", None, ['w'],
                         longdescription= '''**!weapon *{fegyver}* *{módosító}* *{ellenfél skill}* *{ellenfél sebzés kockák}* **
Kritikus siker esetén mindkét oldal esetén automatikusan 4 kockával növeli a sebzést ellenfél skillben már legyenek benne a módosítók. 
''')

    async def handle(self, params, message, client):
        pc = get_me(message, force=True)
        if pc:
            (spec, modifier, base2, damage2) = extract(params, [None, 0, -1, -1])
            weapon = pc.get_weapon(spec)
            if 'skill' in weapon:
                for t, name, value, *name2 in get_checkable(pc.get_data(), weapon['skill']):
                    await Weapon.embed(message.channel, pc, weapon, name, value, int(modifier),
                        int(base2), int(damage2))

    async def embed(ctx, character, weapon, name, base, modifier, obase=-1, odamage=-1):
        (color, text, ro, success) = check(base, modifier)

        data = character.get_data(True)
        embed = discord.Embed(title=data['name'] + " by " +name + " ", timestamp=datetime.datetime.utcnow(), color=color)
        embed.description = text + " (" + str(ro) + " vs " + str(base + modifier) + ")"
        damage = weapon['damage']
        if success == 3:
            embed.description += f"\n**Fumble** {weapon['fumble']}"
        if damage >= 0 and success <= 2:
            if damage == 0:
                damage = round((data['stats']['str'] + data['stats']['siz']) / 6)
            sum = 0;
            if success == 2:
                damage += 4
            s = '';
            for x in range(damage):
                d = dice(6);
                if sum > 0:
                    s += '+'
                s += str(d)
                sum += d
            embed.description += f" **Damage** {s} = {sum}"
        if 'description' in weapon:
            embed.description += f"\n**Weapon** {weapon['description']}"
        if obase > 0:
            (ocolor, otext, oro, osuccess) = check(obase, 0)
            embed.description += f"\n\n**Opposer** \n{otext} ({oro} vs  {obase})"
            if odamage >= 0 and osuccess <= 2:
                sum = 0;
                if osuccess == 2:
                    odamage += 4
                s = '';
                for x in range(odamage):
                    d = dice(6);
                    if sum > 0:
                        s += '+'
                    s += str(d)
                    sum += d
                embed.description += f" **Damage** {s} = {sum}"
            if success == 3:
                embed.description += f"\n**Fumble** Opponent's weapon dropped or broken"
            if osuccess <= 2:
                if success <= 2:
                    if oro == ro:
                        if "tie" in weapon:
                            embed.description += f"\n\n**Tie** {weapon['tie']}"
                        else:
                            embed.description += f"\n\n**Tie**"
                    elif oro > ro:
                        print('succ '+str(character.armor)+ ':'+str(character.shield))
                        red = character.shield['red'] + character.armor['red']
                        wound = sum - red
                        if wound < 0:
                            wound = 0
                        embed.description += f"\n\n**Partial succes**: opponent, reduction {red}, wound: {wound}"
                        if wound > data['stats']['con']:
                            embed.description += "\nMajor Wound, chirurgery needed"
                        Weapon.knocked(embed.description, data, sum)
                    else:
                        embed.description += f"\n\n**Partial succes**: {data['name']}"

                else:
                    print('succ '+str(character.armor))
                    red = character.armor['red']
                    wound = sum - red
                    if wound < 0:
                        wound = 0
                    embed.description += f"\n\n**Opponent won**, {data['name']}'s shield is innefective\nreduction {red}, wound: {wound}"
                    if wound > data['stats']['con']:
                        embed.description += "\nMajor Wound, chirurgery needed"
                    Weapon.knocked(embed.description, data, sum)
            elif success <= 2:
                embed.description += f"\n\n**{data['name']} won**, opponent's shield is innefective"
            else:
                embed.description += f"\n\n**Double fail**"


        await ctx.send(embed=embed)

    def knocked(description, data, sum):
        if sum > data['stats']['siz']:
            description += f"\n\n**{data['name']} Knocked down!!!**"
            if "horse" in data['combat']['spec']:
                ch = "horse"
            else:
                ch = "dex"
            for kt, kname, kvalue, *kname2 in get_checkable(data, ch):
                (kcolor, ktext, kro, ksuccess) = check(kvalue, 0)
                description += f"\n{kname} check: {ktext}"
