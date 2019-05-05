from argparse import ArgumentParser, RawTextHelpFormatter
from os import environ
from random import shuffle

from rewardsbot import VERSION, BRANCH
from rewardsbot.config import Config
from rewardsbot.logger import RewardsLogger
from rewardsbot.ms_rewards import RewardsBot


def main():
    """Declare command line options"""
    parser = ArgumentParser(description='ms_rewards', formatter_class=RawTextHelpFormatter,
                            epilog='EXAMPLE: ms_rewards -h -m -pc -q -l INFO')
    core_group = parser.add_argument_group("Core", "Configuration of core functionality")
    core_group.add_argument('-v', '--version', action='version', version=VERSION)
    core_group.add_argument('-l', '--log-level', choices=['debug', 'info', 'warn', 'error', 'critical'],
                            dest='LOG_LEVEL', default=Config.log_level, help='Set logging level\n'
                                                                             'DEFAULT: info')
    bot_group = parser.add_argument_group("Bot", "Configuration of Bot Features")
    bot_group.add_argument('-H', '--headless', default=Config.headless, dest='HEADLESS',
                           action='store_true', help='Activates headless mode\n'
                                                     'DEFAULT: Off')
    bot_group.add_argument('-m', '--mobile', default=Config.mobile, dest='MOBILE',
                           action='store_true', help='Activates mobile search\n'
                                                     'DEFAULT: Off')
    bot_group.add_argument('-p', '--pc', default=Config.pc, dest='PC',
                           action='store_true', help='Activates PC search\n'
                                                     'DEFAULT: Off')
    bot_group.add_argument('-q', '--quiz', default=Config.quiz, dest='QUIZ',
                           action='store_true', help='Activates Quiz search\n'
                                                     'DEFAULT: Off')
    bot_group.add_argument('-e', '--email', default=Config.email, dest='EMAIL',
                           action='store_true', help='Parses email links to be processed\n'
                                                     'Requires the file email_links.txt in your config folder\n'
                                                     'DEFAULT: Off')
    bot_group.add_argument('-a', '--all', default=Config.all, dest='ALL',
                           action='store_true', help='Activates all automated modes\n'
                                                     '(equivalent to --mobile --pc --quiz)')
    args = parser.parse_args()

    if environ.get('LOG_LEVEL'):
        log_level = environ.get('LOG_LEVEL')
    else:
        log_level = args.LOG_LEVEL
    rl = RewardsLogger(level=log_level)
    rl.logger.info(msg='--------------------------------------------------')
    rl.logger.info(msg='-----------------------New------------------------')
    rl.logger.info(msg='--------------------------------------------------')
    rl.logger.info('Version: %s-%s', VERSION, BRANCH)
    config = Config(environment_vars=environ, cli_args=args)
    config_dict = {key: value for key, value in vars(config).items() if key.upper() in config.options}
    rl.logger.debug("Microsoft-Rewards-Bot configuration: %s", config_dict)
    rl.logger.debug("Users Loaded: %s", config.login_dict_keys)
    shuffle(config.login_dict_keys)
    for email in config.login_dict_keys:
        rewards = RewardsBot(email, config.login_dict[email], config)
        rewards.dailyrewards()


if __name__ == "__main__":
    main()
