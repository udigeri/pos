from .config import Config
from .logger import PosLogger
from .web import Web

class App(object):
    APP_INITIAL_MSG = "POS web"

    def __init__(self, version, params):
        self.version = version
        print("{} {}".format(self.APP_INITIAL_MSG, self.version))
        self.config = Config(params = params)
        self.logger = PosLogger(self.config, version)
        self.logger.info(self.APP_INITIAL_MSG + " started")

    def run(self, application):
        self.application = application
        self.application.run(self.config, self.logger)

    def finished(self):
        self.logger.info(self.APP_INITIAL_MSG + " finished")


