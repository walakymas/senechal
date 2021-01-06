from commands.base_command import BaseCommand
from config import Config
from utils import *


class Check(BaseCommand):

    def __init__(self):
        description = "Trait, stat, passion vagy skill check"
        params = ['spec']
        super().__init__(description, params, ['c'])

    async def handle(self, params, message, client):
        if message.author.id in Config.characters:
            pc = Config.characters[message.author.id]
            if 'memberId' in pc:
                (spec, modifier) = extract(params, ["---", 0])
                ctx = message.channel
                if (spec == "---"):
                    embed = discord.Embed(title=pc['name'], timestamp=datetime.datetime.utcnow(),
                                          color=discord.Color.blue())
                    s = ""
                    for t in Config.senechalConfig['traits']:
                        s += t[0] + ': ' + str(pc['traits'][t[0].lower()[:3]]) + "\n"
                        s += t[1] + ': ' + str(20 - pc['traits'][t[0].lower()[:3]]) + "\n"
                    embed.add_field(name=':hearts: Traits', value=s, inline=False);
                    s = ""
                    for pn, pv in pc['passions'].items():
                        s += pn + ': ' + str(pv) + "\n"
                    embed.add_field(name=':homes: Passions', value=s, inline=False);
                    s = ""
                    for t in Config.senechalConfig['stats']:
                        s += t + ': ' + str(pc['stats'][t.lower()[:3]]) + "\n"
                    embed.add_field(name=':muscle: Stats', value=s, inline=False);
                    s = ""
                    for n, sg in pc['skills'].items():
                        for sn, sv in sg.items():
                            s += sn + ': ' + str(sv) + "\n"
                    embed.add_field(name=':crossed_swords: Skills', value=s, inline=False);
                    await ctx.send(embed=embed)
                else:
                    for t, name, value, *name2 in getCheckable(pc, spec):
                        if 'trait' == t:
                            await embedTrait(ctx, pc, name, value, modifier, name2[0])
                        else:
                            await embedCheck(ctx, pc, name, value, modifier)

        await message.channel.send('Nem ismerem Önt jóuram!')
