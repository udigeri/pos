import yaml
import os

class Config():
    def __init__(self, params=None):
        self.params = params
        self.config_file_path = params.config_file_path
        self.environment = params.pos_env

        self._load_config_file(self.config_file_path)

        if not hasattr(self, 'log_level'): 
            setattr(self, 'log_level', 'info')
        if not hasattr(self, 'log_file_path'): 
            setattr(self, 'log_file_path', './pos.log')

        if not hasattr(self, 'web_port'): 
            setattr(self, 'web_port', '80')

    def _parse_section(self, key, value):
        if type(value) == dict:
            for subkey,subvalue in value.items():
                self._parse_section(key + "_" + subkey, subvalue)
        else:
            setattr(self, key, value)
 
    def _load_config_file(self, filepath):
        try:        
            with open(filepath, 'r') as ymlfile:
                cfg = yaml.safe_load(ymlfile)[self.environment]
                for key,value in cfg.items():
                    self._parse_section(key,value)
        except FileNotFoundError or NameError or KeyError or ValueError as err: 
            print(err)
