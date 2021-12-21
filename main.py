from discord import Intents
from app.app import app
from os import environ
from src.bot import MyBot

client = MyBot(command_prefix='rr', intents=Intents.all())


@client.ipc.route()
async def get_guild_count(_):
    return len(client.guilds)


@client.ipc.route()
async def get_guild_ids(_):
    return list(map(lambda g: g.id, client.guilds))


@client.ipc.route()
async def get_guild_info(data):
    data = await client.fetch_guild(data.guild_id)
    return {"name": data.name, "id": data.id, "icon_url": str(data.icon_url)}


if __name__ == '__main__':
    # client.loop.create_task(app.run_task(host="localhost", debug=False))
    client.run(environ['DISCORD_TOKEN'])
