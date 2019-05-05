import json
from logging import getLogger, Formatter, StreamHandler, FileHandler
from os import path, makedirs


class RewardsLogger(object):
    def __init__(self, level='INFO', name=__name__):
        # Create the Logger
        self.logger = getLogger(name=name)
        try:
            self.logger.setLevel(level.upper())
        except ValueError:
            level = "INFO"
            self.logger.setLevel(level.upper())

        # Create a Formatter for formatting the log messages
        logger_formatter = Formatter(
            '%(asctime)s : %(levelname)s :: %(name)s :: %(module)s : %(message)s', '%Y-%m-%d %H:%M:%S'
        )

        # Add the console logger
        console_logger = StreamHandler()
        console_logger.setFormatter(logger_formatter)

        console_logger.setLevel(level.upper())

        # Add the Handler to the Logger
        self.logger.addHandler(console_logger)

        # Add the Handler for logging to file
        makedirs('logs', exist_ok=True)
        file_logger = FileHandler(path.join(path.abspath("."), r"logs\ms_rewards.log"), encoding="utf8")
        file_logger.setFormatter(logger_formatter)
        file_logger.setLevel(level.upper())
        self.logger.addHandler(file_logger)


class RewardsSearchHist(object):
    def __init__(self, config):
        self.config = config

    def get(self, user):
        user = user.split('@')[0].replace('.', '')
        try:
            with open(path.join(f'{self.config.config_dir}', f'{user}-{self.config.search_log_file}'), 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            search_hist = []
            return search_hist

    def save(self, search_history, user):
        user = user.split('@')[0].replace('.', '')
        with open(path.join(f'{self.config.config_dir}', f'{user}-{self.config.search_log_file}'), 'w') as f:
            json.dump(search_history, f, ensure_ascii=False)
