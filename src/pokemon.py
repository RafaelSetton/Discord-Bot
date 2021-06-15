from discord.ext import commands
from json import loads, JSONDecodeError
from requests import get
from discord import Embed
from dataclasses import dataclass, fields


@dataclass
class Poke:
    name: str
    sprites: dict
    id: int
    height: float
    weight: int
    types: list
    is_default: bool
    


class Pokemon(commands.Cog):
    URL = "https://pokeapi.co/api/v2/pokemon/"

    def __init__(self, client):
        self.client = client
    
    @classmethod
    def create_embed(cls, pokemon: Poke):
        embed = Embed()
        embed.set_thumbnail(url=pokemon.sprites['front_default'])
        embed.set_footer(text="Por: Rafael Setton")
        embed.description = f"[Mais informações aqui!]({cls.URL+pokemon.name})"
        embed.title = pokemon.name.title()

        embed.add_field(name="ID", value=f"#{pokemon.id}")
        embed.add_field(name="Peso", value=f"Peso: {(pokemon.weight/10):.1f}kg")
        embed.add_field(name="Altura", value=f"Altura: {(pokemon.height/10):.1f}m")
        embed.add_field(name="Tipos", value=f"{', '.join([t['type']['name'] for t in pokemon.types])}")
        return embed

    @commands.command(name='pokedex', help="Traz informações sobre um certo pokemon")
    async def pokedex(self, ctx: commands.Context, name):
        try:
            field_names = set(f.name for f in fields(Poke))
            info = loads(get(self.URL+name).text)
            poke = Poke(**{k:v for k,v in info.items() if k in field_names})
        except JSONDecodeError:
            await ctx.send(f"'{name}' não é um pokemon!")
        else:
            await ctx.send(embed=self.create_embed(poke))


def setup(client):
    client.add_cog(Pokemon(client))
