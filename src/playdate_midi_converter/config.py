from logging import Manager, RootLogger, Logger, ERROR
from configparser import SafeConfigParser, ConfigParser


class Config(object):
    parser: ConfigParser

    def __init__(self):
        super().__init__()
        self.parser = SafeConfigParser()

    def __getitem__(self, section):
        return self.parser.__getitem__(section)

    def __getattribute__(self, item):
        return self.__getitem__(item)

    def _load_defaults(self):
        self.parser.read_string("""
        [DEFAULTS]
        dev_mode = false
        max_notes = 512
        
        [synth]
        channels = 
        """)

    def read_files(self, *filenames: str, encoding: str = 'utf-8'):
        self.parser.read(filenames, encoding)

    def write(self, filename: str):
        with open(filename, 'w') as f:
            self.parser.write(f)


class Context(object):
    config: Config
    log_manager: Manager

    def __init__(self, cfg: Config, log_level: int = ERROR):
        super().__init__()
        self.config = cfg
        self.log_manager = Manager(RootLogger(log_level))

    def get_logger(self, name: str) -> Logger:
        return self.log_manager.getLogger(name)
