import yaml


class Config:
    config = {}
    characters = {}
    senechalConfig = {}
    prefix = "!"
    mainChannelId = 779078275111714917
    mainChannel = None

    def reload():
        with open(r'config.yml') as file:
            Config.config = yaml.load(file, Loader=yaml.FullLoader)
            if ('prefix' in Config.config):
                Config.prefix = Config.config['prefix']
            if ('mainChannel' in Config.config):
                Config.mainChannelId = Config.config['mainChannel']

        with open(r'senechal.yml') as file:
            Config.senechalConfig = yaml.load(file, Loader=yaml.FullLoader)

        with open(r'characters.yml') as file:
            Config.characters = yaml.load(file, Loader=yaml.FullLoader)
            for character in Config.characters.values():
                if ('memberId' in character):
                    g = 0;
                    for h in character['events']:
                        g += h['glory']
                    character['main']['Glory'] = g
                    for n, sg in character['skills'].items():
                        for sn, sv in sg.items():
                            if '.' == str(sv)[:1]:
                                sg[sn] = sg[sv[1:]]

    def pcs():
        for c in Config.characters.values():
            if "memberId" in c:
                yield c

    def npcs():
        for c in Config.characters.values():
            if not "memberId" in c:
                yield c
