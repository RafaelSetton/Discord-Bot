from discord.ext import commands
from discord import Message, Embed, Color


class Utils(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name='ping')
    async def ping(self, ctx: commands.Context):
        msg: Message = await ctx.message.reply("...")
        await msg.edit(content=f"🏓Pong!\nDelay: {(msg.created_at - ctx.message.created_at).microseconds//1000}ms")
    
    @commands.command(name='dashboard')
    async def dash(self, ctx: commands.Context):
        """Informações básicas e URL do painel"""
        embed = Embed()
        
        embed.color = Color.from_rgb(0, 255, 100)
        embed.set_footer(text="Rafael Setton", icon_url="https://cdn.discordapp.com/avatars/415999616157220864/"
                                                        "1e2cccb14d5fb03a554172c9c75e5535.webp?size=1024")

        embed.title = "Dashboard"
        embed.url = "https://mybot.rafaelsetton.repl.co"

        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Utils(client))
