import json
from logging import getLogger
from os import path


class Config(object):
    options = ['LOG_LEVEL', 'HEADLESS', 'MOBILE', 'PC', 'QUIZ', 'EMAIL', 'ALL', 'CONFIG_DIR', 'SEARCH_LOG_FILE',
               'LOGIN_DICT_FILE']

    headless = False
    mobile = False
    pc = False
    quiz = False
    email = False
    all = False
    log_level = 'info'
    config_dir = 'config'
    search_log_file = 'search.json'
    login_dict_file = 'ms_rewards_login_dict.json'
    login_dict = []
    login_dict_keys = []
    email_links = []
    email_links_file = 'email_links.txt'

    def __init__(self, environment_vars, cli_args):
        self.cli_args = cli_args
        self.environment_vars = environment_vars

        self.logger = getLogger()
        self.parse()

    def parse(self):
        for option in Config.options:
            if self.environment_vars.get(option):
                env_opt = self.environment_vars[option]
                if isinstance(env_opt, str):
                    # Clean out quotes, both single/double and whitespace
                    env_opt = env_opt.strip("'").strip('"').strip(' ')
                if option in ['HEADLESS', 'MOBILE', 'PC', 'QUIZ', 'ALL']:
                    if env_opt.lower() in ['true', 'yes']:
                        setattr(self, option.lower(), True)
                    elif env_opt.lower() in ['false', 'no']:
                        setattr(self, option.lower(), False)
                    else:
                        self.logger.error('%s is not true/yes, nor false/no for %s. Assuming %s',
                                          env_opt, option, getattr(self, option))
                else:
                    setattr(self, option.lower(), env_opt)
            elif vars(self.cli_args).get(option):
                setattr(self, option.lower(), vars(self.cli_args).get(option))
        try:
            with open(path.join(f'{self.config_dir}', f'{self.login_dict_file}'), 'r') as f:
                self.login_dict = json.load(f)
                self.login_dict_keys = list(self.login_dict.keys())
        except IOError as e:
            self.logger.error(f"Login File was not found, create it and retry {e}")
        try:
            with open(path.join(f'{self.config_dir}', f'{self.email_links_file}'), 'r') as f:
                self.email_links = []
                for link in f.readlines():
                    self.email_links.append(link)
        except IOError as e:
            if self.email:
                self.logger.error(f"***Email Links File not found, create it to use the e-mail links feature*** {e}")
                raise
            else:
                pass
