from discord import Intents
from os import environ, system
from dotenv import load_dotenv
from src.bot import MyBot
from threading import Thread

load_dotenv()
client = MyBot(command_prefix='rr', intents=Intents.all())


@client.ipc.route()
async def get_guild_count(_):
    return len(client.guilds)


@client.ipc.route()
async def get_guild_ids(_):
    return list(map(lambda g: g.id, client.guilds))


@client.ipc.route()
async def get_guild_info(request):
    data = await client.fetch_guild(request.guild_id)
    return {"name": data.name, "id": data.id, "icon_url": str(data.icon_url)}


def run_app():
    system("python app/app.py")


if __name__ == '__main__':
    Thread(target=run_app).start()
    client.run(environ['DISCORD_TOKEN'])
