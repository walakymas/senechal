import yaml
import os
import json

class Config:
    inited = False

    authorization = False

    config = {}
    feastConfig = {}
    senechalConfig = {}
    prefix = "!"
    mainChannelId = 779078275111714917
    mainChannel = None

    def senechal():
        Config.reload()
        return Config.senechalConfig

    def feast():
        Config.reload()
        return Config.feastConfig

    def armor(spec):
        if spec in Config.senechal()['armors']:
            return Config.senechal()['armors'][spec]
        else:
            return Config.senechal()['armors']['Clothing']

    def shield(spec):
        if spec in Config.senechal()['shields']:
            return Config.senechal()['shields'][spec]
        else:
            return Config.senechal()['shields']['None']

    def weapon(spec):
        weapon = {}
        for n, v in Config.senechal()['weapons']['default'].items():
            weapon[n] = v
        for wn, wv in Config.senechal()['weapons'].items():
            if spec.lower() == wn.lower():
                for n, v in wv.items():
                    weapon[n] = v
                return weapon
        return weapon

    def reload(force=False):
        if force or not Config.inited:
            try:
                with open(r'config.yml') as file:
                    Config.config.update(yaml.load(file, Loader=yaml.FullLoader))
                    if ('prefix' in Config.config):
                        Config.prefix = Config.config['prefix']
                    if ('mainChannel' in Config.config):
                        Config.mainChannelId = Config.config['mainChannel']
            except IOError:
                Config.config = {'token': None}
                print("pre token"+os.environ['token'])
                if 'token' in os.environ:
                    print("exist")
                    Config.config['token'] = os.environ['token']
                if 'prefix' in os.environ:
                    Config.prefix = os.environ['prefix']
                if 'mainChannel' in os.environ:
                    Config.mainChannelId = os.environ['mainChannel']

            with open(r'senechal.yml') as file:
                Config.senechalConfig = yaml.load(file, Loader=yaml.FullLoader)
            with open(r'feast.json') as file:
                Config.feastConfig = json.load(file)
            Config.inited = True

    @staticmethod
    def pcs(name=None):
        Config.reload()
        for c in Config.characters.values():
            if ("memberId" in c) and ((not name) or (name.lower() in c['name'].lower())):
                print(f"{name} {c['name']}")
                yield c

    @staticmethod
    def npcs(name=None):
        Config.reload()
        for c in Config.characters.values():
            if ("memberId" not in c) and ((not name) or (name.lower() in c['name'].lower())):
                yield c
