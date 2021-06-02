from discord.ext import commands
from discord import Member
from discord.ext.commands.errors import CommandInvokeError
from src.helpers import log

class ChangeNick(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name='nick')
    @commands.has_permissions(administrator=True)
    async def nick(self, ctx: commands.Context, person: Member, nick: str):
        """Muda o nickname de alguém"""
        prev = person.nick
        try:
            await person.edit(nick=nick)
            log(ctx.guild, 'nick', f'{ctx.author.name}#{ctx.author.discriminator} mudou o nick de {person.name}#{person.discriminator}\n{prev} -> {nick}')
        except CommandInvokeError:
            await ctx.send(f"O cargo de {person.mention()} é mais alto que o meu.")


def setup(client):
    client.add_cog(ChangeNick(client))
