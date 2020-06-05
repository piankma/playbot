config = None
logger = None
client = None


def init_client():
    from playbot.utils.bot import MyDiscordBot
    from playbot.utils.common import sget
    from playbot.cogs import register_cogs

    b = MyDiscordBot(command_prefix=sget(config, "common.commands.prefix"))
    register_cogs(b)

    b.run(sget(config, "secrets.token"), bot=True, reconnect=True)

    return b


def init_bot():
    from playbot.utils.config import load_config
    from playbot.utils.logger import init_logger

    global config, logger, client

    config = load_config()
    logger = init_logger()
    client = init_client()
