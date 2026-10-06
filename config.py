import logging
import yaml
import os
import json
import psycopg2
from database.proptable import PropertiesTable

log = logging.getLogger(__name__)
class Config:
    inited = False

    authorization = False

    config = {}
    feastConfig = {}
    senechalConfig = {}
    prefix = "!"
    mainChannelId = 779078275111714917
    mainChannel = None
    hook = None

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
                with open(r'config.yml', encoding='utf-8') as file:
                    Config.config.update(yaml.safe_load(file) or {})
                    if ('prefix' in Config.config):
                        Config.prefix = Config.config['prefix']
                    if ('mainChannel' in Config.config): 
                        Config.mainChannelId = Config.config['mainChannel']
            except IOError:
                Config.config = {'token': None}
                if 'token' in os.environ:
                    Config.config['token'] = os.environ['token']
                if 'prefix' in os.environ:
                    Config.prefix = os.environ['prefix']
                if 'mainChannel' in os.environ:
                    Config.mainChannelId = int(os.environ['mainChannel'])

            with open(r'senechal.yml', encoding='utf-8') as file:
                Config.senechalConfig = yaml.safe_load(file)
            with open(r'feast.yml', encoding='utf-8') as file:
                Config.feastConfig = yaml.safe_load(file)

            try:
                Config.hook = PropertiesTable().getValue('hook')
            except psycopg2.Error as ex:  # e.g. the schema is not created yet on a fresh database
                log.warning("hook not loaded: %s", ex)
            
            Config.inited = True
