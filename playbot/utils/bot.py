from discord.ext import commands

from playbot.utils.client import MyDiscordClient


class MyDiscordBot(commands.bot.BotBase, MyDiscordClient):
    pass
