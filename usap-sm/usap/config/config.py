import json

from mdclogpy import Level
from .logger import Log


class Config(object):
    # Static vars
    _logger_instance = None
    _config_path = None

    def __init__(self, xapp_name='usap-xapp', config_file='/usr/src/usap-xapp/config/config-file.json'):
        self.xapp_name = xapp_name
        self.cfg = None

        if Config._config_path is None:
            Config._config_path = config_file

        self.load_config()

        if Config._logger_instance is None:
            self.set_logger()
            Config._logger_instance = self.get_logger()

    def load_config(self):
        with open(Config._config_path, 'r') as file:
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
        with open(Config._config_path, 'r') as file:
            cfg = file.read()
            if cfg != None:
                self.cfg = json.loads(cfg)
                # following is required by the appmgr -  don't know why.
                cfgescaped = cfg.replace('"', '\\"').replace('\n', '\\n')
                data = '[{ "config": "' + cfgescaped + \
                    '", "metadata":{"configType":"json","xappName":"' + \
                    self.xapp_name + '"}}]'
        if data == None:
            Config._logger_instance.error("Config file %s empty or does not exists" %
                                          (Config._config_path))
        return data

    def set_logger(self):
        # set level
        if self.controls['active'] == True and self.controls.get('logger'):
            logLevel = self.controls['logger'].get('level')
            if logLevel.upper() == "ERROR":
                Config._logger_instance = Log('usap-xapp', Level.ERROR)
            elif logLevel.upper() == "WARNING":
                Config._logger_instance = Log('usap-xapp', Level.WARNING)
            elif logLevel.upper() == "INFO":
                Config._logger_instance = Log('usap-xapp', Level.INFO)
            elif logLevel.upper() >= "DEBUG":
                Config._logger_instance = Log('usap-xapp', Level.DEBUG)

        # App version
        Config._logger_instance.add_mdc(
            'version', self.get_item_by_key('appVersion'))

    @staticmethod
    def get_logger():
        if Config._logger_instance is None:
            raise Exception(
                'Logger not initialized. Ensure Config is initialized.')
        return Config._logger_instance
