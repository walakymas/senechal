from commands.base_command import BaseCommand
from config import Config
from utils import *


class Login(BaseCommand):

    def __init__(self):
        description = "Trait, stat, passion vagy skill próba"
        params = ['weblogin']
        super().__init__(description,
                         longdescription='''***!weblogin {spec} {modifier=0}*** A játékosok saját karakterhez indíthatnak próbát 
***!c {név} {spec} {modifier=0}*** A mesélő egy névrészlet megadásával azonosíthatja a karaktert
*spec* próbáratett tulajdonság nevének kezdő részlete
*modifier* aktuális módosító  
''')

    async def handle(self, params, message, client):
        char = get_me(message)
        if char:
            (spec, modifier) = extract(params, ["---", 0])
            await self.check(message.channel, char, spec, modifier)
        else:
            (name, spec, modifier) = extract(params, ["---", "---", 0])
            for char in Character.pcs(name):
                await self.check(message.channel, char, spec, modifier)

    async def check(self, ctx, char, spec, modifier):
        if spec == "---":
            data = char.get_data()
            embed = discord.Embed(title=char.name, timestamp=datetime.datetime.utcnow(),
                                  color=discord.Color.blue())
            if 'traits' in data:
                s = ""
                for t in Config.senechalConfig['traits']:
                    s += t[0] + ': ' + str(data['traits'][t[0].lower()[:3]]) + "\n"
                    s += t[1] + ': ' + str(20 - data['traits'][t[0].lower()[:3]]) + "\n"
                embed.add_field(name=':hearts: Traits', value=s, inline=False);
            if 'passions' in data:
                s = ""
                for pn, pv in sorted(data['passions'].items()):
                    s += pn + ': ' + str(pv) + "\n"
                embed.add_field(name=':homes: Passions', value=s, inline=False);
            if 'stats' in data:
                s = ""
                for t in Config.senechalConfig['stats']:
                    s += t + ': ' + str(data['stats'][t.lower()[:3]]) + "\n"
                embed.add_field(name=':muscle: Stats', value=s, inline=False);
            if 'skills' in data:
                s = ""
                for n, sg in sorted(data['skills'].items()):
                    for sn, sv in sg.items():
                        s += sn + ': ' + str(sv) + "\n"
                embed.add_field(name=':crossed_swords: Skills', value=s, inline=False);
            await ctx.send(embed=embed)
        else:
            data = char.get_data()
            for t, name, value, *name2 in get_checkable(data, spec):
                if 'trait' == t:
                    await embed_trait(ctx, data, name, value, modifier, name2[0])
                else:
                    await embed_check(ctx, data, name, value, modifier)

