from discord.ext import commands
from collections import namedtuple
from json import JSONDecoder
from requests import get
from discord import Embed

Model = namedtuple("Poke", "name id sprites weight height types is_default")


class Poke:
    def __new__(cls, **kwargs):
        pops = []
        for k, v in kwargs.items():
            if k not in Poke._fields:
                pops.append(k)
        for p in pops:
            kwargs.pop(p)
        return Model(**kwargs)


class Pokemon(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @commands.command(name='pokedex', help="Traz informações sobre um certo pokemon")
    async def pokedex(self, ctx: commands.Context, name):
        url = "https://pokeapi.co/api/v2/pokemon/"
        poke = Poke(**JSONDecoder().decode(get(url+name).text))
        embed = Embed()
        embed.set_thumbnail(url=poke.sprites['front_default'])
        embed.set_footer(text="Por: Rafael Setton")
        embed.description = f"[Mais informações aqui!]({url+name})"
        embed.title = poke.name.title()

        embed.add_field(name="ID", value=f"#{poke.id}")
        embed.add_field(name="Peso", value=f"Peso: {(poke.weight/10):.1f}kg")
        embed.add_field(name="Altura", value=f"Altura: {(poke.height/10):.1f}m")
        embed.add_field(name="Tipos", value=f"Tipos: {', '.join([t['type']['name'] for t in poke.types])}")

        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Pokemon(client))
