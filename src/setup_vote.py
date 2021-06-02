from discord.ext import commands
from math import ceil


class SetupVote(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name='setup_vote')
    async def setup_vote(self, ctx: commands.Context, *params):
        """Organiza uma votação com os itens selecionados, separados por espaços"""
        emojis = ["0\ufe0f\u20e3", "1\ufe0f\u20e3", "2\ufe0f\u20e3", "3\ufe0f\u20e3", "4\ufe0f\u20e3", "5\ufe0f\u20e3", "6\ufe0f\u20e3", "7\ufe0f\u20e3", "8\ufe0f\u20e3",    "9\ufe0f\u20e3"]
        for _ in range(ceil(len(params) / 10)):
            indexes = range(min(10, len(params)))
            response = '\n'.join([f"{i}: {params[i]}" for i in indexes])
            await ctx.send(response)
            msg = ctx.channel.last_message
            for i in indexes:
                await msg.add_reaction(emojis[i])
            params = params[10:]


def setup(client):
    client.add_cog(SetupVote(client))
