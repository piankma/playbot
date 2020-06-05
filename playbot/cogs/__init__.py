from playbot.utils.bot import MyDiscordBot


def register_cogs(bot: MyDiscordBot):
    from playbot.cogs.radio import Radio

    bot.add_cog(Radio(bot))
