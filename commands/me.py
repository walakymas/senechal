from commands.base_command import BaseCommand
from utils import *
import tempfile
import yaml

class Me(BaseCommand):

    def __init__(self):
        description = "Saját karakter adatai"
        params = None
        self.aliases = ['m']
        super().__init__(description, params)

    async def handle(self, params, message, client):
        (task,*ex) = extract(params, ["base"])
        if message.author.id in Config.characters:
            me = Config.characters[message.author.id]
            if "download" == task:
                fp = next(tempfile._get_candidate_names())
                print(fp)
                with open(fp, 'w') as file:
                    documents = yaml.dump(me, file, allow_unicode=True)
                await try_upload_file(client, message.channel, file_path=fp, filename=str(me['name'])+'.yaml', delete_after_send=True)
            else:
                await embedPc(message.channel, me, task, params)
        else:
            print(Config.characters.keys())
