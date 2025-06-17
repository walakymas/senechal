from commands.base_command import BaseCommand
from utils import *
import os
class Images(BaseCommand):


    def __init__(self):
        description = 'képek felderítése'
        params = []
        super().__init__(description, params,
                         longdescription='''Képek''',aliases=['im'])

    async def handle(self, params, message, client):
        if (len(params)== 0 ):
            li = 20
        elif params[0]=='None':
            li = None
        else:
            li = int(params[0])

        dir = os.path.join("/var/www/senechalPictures", f"{message.channel.id}")
        from pathlib import Path
        Path(dir).mkdir(parents=True, exist_ok=True)
        async for msg in message.channel.history(limit=li): # no limit: None
            for at in msg.attachments:
#                print(f"{at.id} ... {at.filename} {at.content_type} ::: {at.url}")
                tempImage = os.path.join(dir, f"{at.id}_{at.filename}")
                if not os.path.isfile(tempImage):
                    await at.save(fp=tempImage)
                    os.utime(tempImage, (msg.created_at.timestamp(), msg.created_at.timestamp()))
                    print(f'saved {tempImage}')
                else:
                    print('exists')

