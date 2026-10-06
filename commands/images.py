import logging
from commands.base_command import BaseCommand
from utils import *
from permissions import ADMIN
import os

log = logging.getLogger(__name__)
class Images(BaseCommand):
    required_rights = ADMIN

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

        dir = pictures_dir(message.channel.id)
        from pathlib import Path
        Path(dir).mkdir(parents=True, exist_ok=True)
        async for msg in message.channel.history(limit=li): # no limit: None
            for at in msg.attachments:
#                print(f"{at.id} ... {at.filename} {at.content_type} ::: {at.url}")
                if not is_archivable(at.filename):
                    log.debug('skipped %s', at.filename)
                    continue
                tempImage = os.path.join(dir, f"{at.id}_{os.path.basename(at.filename)}")
                if not os.path.isfile(tempImage):
                    await at.save(fp=tempImage)
                    os.utime(tempImage, (msg.created_at.timestamp(), msg.created_at.timestamp()))
                    log.debug('saved %s', tempImage)
                else:
                    log.debug('exists')

