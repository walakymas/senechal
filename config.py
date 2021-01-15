import yaml
import os


class Config:
    config = {}
    characters = {}
    charactersOrig = {}
    senechalConfig = {}
    prefix = "!"
    mainChannelId = 779078275111714917
    mainChannel = None

    def reload():
        try:
            with open(r'config.yml') as file:
                Config.config = yaml.load(file, Loader=yaml.FullLoader)
                if ('prefix' in Config.config):
                    Config.prefix = Config.config['prefix']
                if ('mainChannel' in Config.config):
                    Config.mainChannelId = Config.config['mainChannel']
        except IOError:
            Config.config = {'token': os.environ['token']}
            if ('prefix' in os.environ):
                Config.prefix = os.environ['prefix']

            if ('mainChannel' in os.environ):
                Config.mainChannelId = os.environ['mainChannel']

        with open(r'senechal.yml') as file:
            Config.senechalConfig = yaml.load(file, Loader=yaml.FullLoader)

        with open(r'characters.yml') as file:
            Config.charactersOrig = yaml.load(file, Loader=yaml.FullLoader)

        with open(r'characters.yml') as file:
            Config.characters = yaml.load(file, Loader=yaml.FullLoader)
            for character in Config.characters.values():
                if ('memberId' in character):
                    for n, sg in character['skills'].items():
                        for sn, sv in sg.items():
                            if '.' == str(sv)[:1]:
                                sg[sn] = sg[sv[1:]]

    def pcs(name=None):
        for c in Config.characters.values():
            if ("memberId" in c) and ((not name) or (name.lower() in c['name'].lower())):
                print(f"{name} {c['name']}")
                yield c

    def npcs(name=None):
        for c in Config.characters.values():
            if (not "memberId" in c) and ((not name) or (name.lower() in c['name'].lower())):
                yield c
