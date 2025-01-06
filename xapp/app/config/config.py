import json

from mdclogpy import Level
from .logger import Log


class Config(object):
    def __init__(self, xapp_name='usap-xapp', config_file=None):
        self.config_file = config_file
        self.xapp_name = xapp_name
        self.cfg = None
        self.config()
        self.set_logger()

    def config(self):
        with open(self.config_file, 'r') as file:
            cfg = file.read()
            if cfg != None:
                self.cfg = json.loads(cfg)
                if self.cfg is not None:
                    self.controls = self.cfg['controls']

    def get_item_by_key(self, key):
        data = None
        if self.cfg.get(key) is not None:
            data = self.cfg[key]
        return data

    def get_config(self):
        data = None
        with open(self.config_file, 'r') as file:
            cfg = file.read()
            if cfg != None:
                self.cfg = json.loads(cfg)
                # following is required by the appmgr -  don't know why.
                cfgescaped = cfg.replace('"', '\\"').replace('\n', '\\n')
                data = '[{ "config": "' + cfgescaped + \
                    '", "metadata":{"configType":"json","xappName":"' + \
                    self.xapp_name + '"}}]'
        if data == None:
            self.logger.error("Config file %s empty or does not exists" %
                              (self.config_file))
        return data

    def set_logger(self):
        # set level
        if self.controls['active'] == True and self.controls.get('logger'):
            logLevel = self.controls['logger'].get('level')
            if logLevel.upper() == "ERROR":
                self.logger = Log('usap-xapp', Level.ERROR)
            elif logLevel.upper() == "WARNING":
                self.logger = Log('usap-xapp', Level.WARNING)
            elif logLevel.upper() == "INFO":
                self.logger = Log('usap-xapp', Level.INFO)
            elif logLevel.upper() >= "DEBUG":
                self.logger = Log('usap-xapp', Level.DEBUG)

        # App version
        self.logger.add_mdc('version', self.get_item_by_key('appVersion'))

    def get_logger(self):
        return self.logger
