import functools

from discord import FFmpegPCMAudio, AudioSource, VoiceClient
from discord.errors import ClientException
from discord.ext.commands.errors import CommandInvokeError
from discord.ext import commands

from playbot import config
from playbot.utils.bot import MyDiscordBot
from playbot.utils.common import sget


class Radio(commands.Cog):
    def __init__(self, bot: MyDiscordBot):
        self.bot = bot

    async def _play_stream(self, audio_source: AudioSource, voice_client: VoiceClient):
        voice_client.play(audio_source)

    @property
    @functools.lru_cache()
    def stations_list(self) -> dict:
        """ get stations in a name:url dict """
        conf = sget(config, "radio_stations.list")
        listing = dict()

        for station in conf:
            name, url = station.get("name"), station.get("url")
            listing[name] = url

        return listing

    @property
    @functools.lru_cache()
    def stations_by_tag(self) -> dict:
        """ get stations grouped by tags """
        conf = sget(config, "radio_stations.list")
        listing = {}

        for station in conf:
            for tag in station.get("tags"):
                name, url = station.get("name"), station.get("url")
                if tag in listing:
                    listing[tag][name] = url
                else:
                    listing[tag] = dict()
                    listing[tag][name] = url

        return listing

    @property
    @functools.lru_cache()
    def stations_tags(self) -> list:
        """ get stations tag list """
        stations_by_tag = self.stations_by_tag
        return [key for key in stations_by_tag.keys()]

    @commands.group("radio")
    async def radio(self, context: commands.Context):
        if not context.invoked_subcommand:
            await context.send(
                "Playbot.\n"
                "/radio [lista|stop|play]"
            )

    @radio.group("lista", aliases=["list"])
    async def list(self, context: commands.Context):
        if not context.invoked_subcommand:
            await context.send("Która lista? `all`/`tags`/`tag [name]`")

    @list.command("all")
    async def list_all(self, context: commands.Context):
        stations = ",\n- ".join(self.stations_list.keys())
        return await context.send(f"**Lista wszystkich stacji:**\n- {stations}")

    @list.command("tags")
    async def list_tags(self, context: commands.Context):
        tags = ",\n- ".join(self.stations_tags)
        await context.send(f"**Lista wszystkich tagów:**\n- {tags}")

    @list.command("tag")
    async def list_tag(self, context: commands.Context, tag: str):
        if tag not in self.stations_by_tag:
            await context.send(f"Tag {tag} nie istnieje")
            return

        stations = ",\n- ".join(self.stations_by_tag.get(tag))
        await context.send(f"**Stacje pod tagiem {tag} to:**\n- {stations}")

    @radio.command("stop")
    async def stop(self, context: commands.Context):
        if not context.author.voice:
            await context.send("Dołącz do kanału głosowego")
            return

        if not self.bot.voice_clients:
            await context.send("Aktualnie nic nie jest odtwarzane")
            return

        for vc in self.bot.voice_clients:
            if vc.channel == context.author.voice.channel:
                vc.stop()
                await vc.disconnect()

    @radio.command("play")
    async def play(self, context: commands.Context, station: str=None):
        if not station:
            await context.send("Podaj nazwę stacji (w cudzysłowie)")
            return

        if not context.author.voice:
            await context.send(
                f"Dołącz najpierw do kanału głosowego, @{context.author}."
            )
            return

        if station not in self.stations_list.keys():
            await context.send(f"Nie odnaleziono stacji {station}")
            return
        else:
            station_url = self.stations_list.get(station)

        audio_source: AudioSource = FFmpegPCMAudio(station_url)

        try:
            voice_client: VoiceClient = await context.author.voice.channel.connect()
            await self._play_stream(audio_source, voice_client)
        except ClientException as ce:
            for vc in self.bot.voice_clients:
                if vc.channel == context.author.voice.channel:
                    vc.stop()
                    await self._play_stream(audio_source, vc)
                else:
                    await context.send("Błąd odtwarzania")
                    return
        except CommandInvokeError as cie:
            await context.send(
                f"Dołącz najpierw do kanału głosowego, {context.author}."
            )
            return
