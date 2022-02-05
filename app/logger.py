import logging
import logging.handlers
import os

class InOutLogger(logging.Logger):
    LOG_FORMATTER = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
  
    def __init__(self, config, version):
        if not os.path.exists(os.path.dirname(config.log_file_path)):
            os.makedirs(os.path.dirname(config.log_file_path))

        logging.Logger.__init__(self, name="InOut " + version + "")
        self.formatter = logging.Formatter(self.LOG_FORMATTER)
        self.setLevel(config.log_level.upper())
        self.propagate = False
        handler = logging.StreamHandler()
        handler.setFormatter(self.formatter)
        self.addHandler(handler) 

        handler = logging.FileHandler(config.log_file_path)
        handler.setFormatter(self.formatter)
        self.addHandler(handler) 

