from discord.ext import commands
import discord

from .utils import checks
from collections import Counter

'''Module for moderator commands.'''


class Mod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def are_overwrites_empty(self, overwrites):
        """There is currently no cleaner way to check if a
        PermissionOverwrite object is empty"""
        original = [p for p in iter(overwrites)]
        empty = [p for p in iter(discord.PermissionOverwrite())]
        return original == empty

    @commands.command(enabled=True, hidden=True)
    async def show_roles(self, ctx, member: discord.Member):
        automation_channel = self.bot.get_channel(532946068967784508)
        await automation_channel.send(f"Role names on server: {[role.name for role in member.guild.roles]}")
        await automation_channel.send(f"Role ID's on server: {[role.id for role in member.guild.roles]}")

    @commands.command()
    @checks.mod_or_permissions(manage_guild=True)
    async def take_role(self, ctx, members: commands.Greedy[discord.Member], *, role: discord.Role):
        automation_channel = self.bot.get_channel(532946068967784508)
        for member in members:
                try:
                    await member.remove_roles(role)
                    await automation_channel.send(f"Roolin {role} poisto käyttäjältä {member.display_name} onnistui.")
                except discord.Forbidden:
                    await automation_channel.send(f"Roolin {role} poisto käyttäjältä {member.display_name} epäonnistui.")

    @commands.group(aliases=['purge'])
    @commands.guild_only()
    @checks.has_permissions(manage_messages=True)
    async def remove(self, ctx):
        """ Poistaa viestejä, jotka täyttää kriterian.
        Jotta voit käyttää tätä komentoa, sinulla tulee olla viestien hallinta oikeus.
        Näitä komentoja ei pysty käyttämään yksityisviesteissä.
        Kun komento on valmis, tulet saamaan viestin, jossa botti kertoo tilaston
        poistetuista viesteistä."""

    async def do_removal(self, ctx, limit, predicate, *, before=None, after=None):
        if limit > 2000:
            return await ctx.send(f'Annettiin liian monta viestiä etsittäväksi ({limit}/2000)')

        if before is None:
            before = ctx.message
        else:
            before = discord.Object(id=before)

        if after is not None:
            after = discord.Object(id=after)

        try:
            deleted = await ctx.channel.purge(limit=limit, before=before, after=after, check=predicate)
        except discord.Forbidden as e:
            return await ctx.send('Minulla ei ole oikeuksia poistaa viestejä.')
        except discord.HTTPException as e:
            return await ctx.send(f'Virhe: {e} (Yritä pienempää hakua?)')

        spammers = Counter(m.author.display_name for m in deleted)
        deleted = len(deleted)
        messages = [f'{deleted} viesti{" oli" if deleted == 1 else "ä"} on poistettu.']
        if deleted:
            messages.append('')
            spammers = sorted(spammers.items(), key=lambda t: t[1], reverse=True)
            messages.extend(f'**{name}**: {count}' for name, count in spammers)

        to_send = '\n'.join(messages)

        if len(to_send) > 2000:
            await ctx.send(f'Onnistuneesti poistettiin {deleted} viestiä.', delete_after=10)
        else:
            await ctx.send(to_send, delete_after=10)

    @remove.command()
    async def user(self, ctx, search, member: discord.Member, ):
        """Poistaa kaikki viestit tietyltä käyttäjältä"""
        search = int(search)
        await self.do_removal(ctx, search, lambda e: e.author == member)
        await ctx.message.delete()

    @remove.command(name='bot')
    async def _bot(self, ctx, search=10, prefix=None):
        """Poistaa botti käyttäjän viestit sekä viestit valinnaisella prefixillä.

        eg: ?purge bot ? poistaa Parempi Messis Botin viestit sekä varsinaiset komennon suoritus viestit.
        eg ?purge bot 3 poistaa 3 botti viestiä.
        eg: ?purge bot 3 ? poistaa kolme Parempi Messis Botin viestiä sekä varsinaiset komennon suoritus viestit.
        """

        def predicate(m):
            return (m.webhook_id is None and m.author.bot) or (prefix and m.content.startswith(prefix))

        await self.do_removal(ctx, search, predicate)
        await ctx.message.delete()

    @commands.command()
    async def ban(self, ctx, *, reason=None, member: discord.Member):
        if reason is None:
            await ctx.message("Please provide a reason. It's required.")
        if reason:
            try:
                await self.bot.ban(member, reason, delete_message_days=7)


                await self.bot.automation_channel.send(f"{member} was successfully banned and messages "
                                                       f"deleted from the past7 days.")
            except discord.Forbidden:
                await ctx.send(f"Banning {member} failed, no permissions to do so. :(")
            except discord.HTTPException:
                await ctx.send(f"Banning {member} failed, unexpected exception.")




def setup(bot):
    bot.add_cog(Mod(bot))

