import ConfigParser
import default_conf


class Config:
    def __init__(self, conf_file="parameter.ini", default=None):
        default = default or default_conf.default_conf
        self.config = ConfigParser.RawConfigParser(default)
        self.config.read(conf_file)
        
    def get(self, section, key):
        return self.config.get(section, key)
        
    def getGlobalParameter(self, parameter):
        return self.config.get("Global", parameter)
    
    def getKey(self, key):
        return self.config.get("key", key)

    def getFilterParameter(self, parameter):
        return self.config.get("Filter", parameter)
