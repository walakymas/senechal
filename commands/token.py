from commands.base_command import BaseCommand
from config import Config
from utils import *
from database.tokenstable import TokenTable
import asyncio

class Token(BaseCommand):

    def __init__(self):
        description = 'Token engedélyezése'
        super().__init__(description, None, ['tel'],
                         longdescription='''Token engedélyezés''')

    async def handle(self, params, message, client):
        print(f"params: {params[0]}")
        record = TokenTable().get_info_by_id(params[0])
        print(f"record: {record}")
        print(f"guild: {message.guild}") 
        if record :
          if message.guild:           
            for m in message.guild.members:
              #print(f" {m.id} : {m.name} : {record[1]}")
              if m.id == record[1] :
                embed = discord.Embed(title="Token Approve",
                          color=discord.Color.blue(),
                          timestamp=datetime.datetime.now()
                          )
                
                message = await m.send(embed=embed)
                await message.add_reaction("✅");
                await message.add_reaction("❌");
                reaction = None
                try:
                    reaction = await client.wait_for("raw_reaction_add",
                        check=lambda r: (r.message_id == message.id) and (r.user_id == m.id),
                        timeout=20,
                    )
                except asyncio.TimeoutError:
                    print(f"timeout")
                finally:
                    try:
                        await message.clear_reactions()
                    except discord.Forbidden:
                        print("Ooops")
                        pass
                if reaction :
                    if reaction.emoji.name == "✅":
                        print("SetEnable")
                        TokenTable().enable(record[0])
                        await message.delete()    
                exit
##                confirmation = Confirmation(client, message="Enable login")
##                await confirmation.confirm(user=message.author, text="Token")

