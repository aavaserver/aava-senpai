from discord.ext import commands
import discord
import datetime
import socket

from .utils import checks
from .utils import system


class Meta(commands.Cog):
    """Commands for utilities related to Discord or the Bot itself."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @checks.am_i_owner()
    async def get_memory_usage(self, ctx):
        await ctx.send(f'Memory usage in bytes: {system.memory_usage_psutil()}.')

    @commands.command()
    @checks.am_i_owner()
    async def get_threads(self, ctx):
        await ctx.send(f'Thread count: {system.current_processes_psutil()}.')

    @commands.command(hidden=True)
    @commands.is_owner()
    async def hello(self, ctx):
        """Displays my intro message."""
        await ctx.send('Hei! Olen kehitys robotti! kryptonian#4034 teki minut.')

    def get_bot_uptime(self):
        now = datetime.datetime.utcnow()
        delta = now - self.bot.uptime
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        if days:
            fmt = '{d} days, {h} hours and {m} minutes'
        elif hours < 1:
            fmt = '{m} minutes, ja {s} seconds'
        else:
            fmt = '{h} hours, {m} minutes, ja {s} seconds'
        return fmt.format(d=days, h=hours, m=minutes, s=seconds)

    @commands.command()
    async def uptime(self, ctx):
        """Tells you how long the bot has been up for. / Kertoo kuinka kauan botti on ollut päällä."""
        await ctx.send('Uptime: **{}**'.format(self.get_bot_uptime()))

    @commands.command(name="about")
    async def about_me(self, ctx):
        """Kertoo botista tietoja"""
        result = ['**Tietoja botista / information about the bot:**']
        result.append('- Kehittäjä: kryptonian (Discord ID: 157970669261422592, Github: samip5)')
        result.append(f'- Bot ID: {self.bot.user.name} (Discord ID: {self.bot.user.id})')
        result.append('- Aloitettu kehittämään/started development: 02.08.2019')
        result.append('- Kirjasto/library: discord.py (Python)')
        result.append(f'- Järjestelmän hostname / Host system hostname: {socket.gethostname()}')
        result.append(f'- Käynnissäolo aika / Bot uptime: {self.get_bot_uptime()}')
        await ctx.send('\n'.join(result))

    @commands.command(name='quit', hidden=True)
    @checks.am_i_owner()
    async def _quit(self, ctx):
        """Quits the bot."""
        channel = self.bot.get_channel(532946068967784508)
        await channel.send(f'Quit-Command: Goodbye.')
        await self.bot.logout()

    @commands.command(name='reload', hidden=True)
    @checks.am_i_owner()
    async def _reload(self, ctx, extension):
        try:
            await ctx.send(f"Reloading extension {extension}.")
            self.bot.unload_extension(extension)
            self.bot.load_extension(extension)
            await ctx.send(f"Successfully loaded {extension}.")
        except ModuleNotFoundError:
            await ctx.send(f'Loading failed, not found.')

    @commands.command(name='load', hidden=True)
    @checks.am_i_owner()
    async def _load(self, ctx, extension):
        try:
            await ctx.send(f'Loading extension {extension}.')
            self.bot.load_extension(extension)
            await ctx.send(f'Successfully loaded {extension}.')
        except ModuleNotFoundError:
            await ctx.send(f'Loading failed, not found.')

    async def bot_check(self, ctx):
        return await self.whitelisted_channels(ctx)

    async def whitelisted_channels(self, ctx):
        whitelisted_channels = [int('606936928129908736'),
                                int('568341807398649857'), int('557613503196954646')]

        if ctx.guild is None:
            return True
        elif ctx.channel.id in whitelisted_channels:
            return True
        else:
            return False


def setup(bot):
    bot.add_cog(Meta(bot))
