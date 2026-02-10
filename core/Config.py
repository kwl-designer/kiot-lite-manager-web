import configparser


class Config:
    def __init__(self, config_file='config.conf'):
        self.config = configparser.ConfigParser()
        self.config.read(config_file, encoding='utf-8')

    def get_broker_host(self):
        return self.config.get('broker', 'host')

    def get_broker_port(self):
        return self.config.getint('broker', 'port')

    def get_broker_username(self):
        return self.config.get('broker', 'username')

    def get_broker_password(self):
        return self.config.get('broker', 'password')

