from commands.base_command import BaseCommand
from utils import *
import tempfile
import yaml

class Me(BaseCommand):

    def __init__(self):
        description = "Saját karakter adatai"
        super().__init__(description, None, ['m', 'en'])

    async def handle(self, params, message, client):
        (task,*ex) = extract(params, ["base"])
        me = get_me(message)
        if me:
            i = me['memberId']
            if "download" == task:
                me2 = Config.charactersOrig[i]
                fp = next(tempfile._get_candidate_names())
                with open(fp, 'w') as file:
                    yaml.dump(me2, file, allow_unicode=True)
                await try_upload_file(client, message.channel, file_path=fp, filename=str(me['name'])+'.yaml', delete_after_send=True)
            else:
                await embed_pc(message.channel, me, task, params)
        else:
            print(Config.characters.keys())
