from discord import Intents
from discord.errors import HTTPException
from app.app import app
from src.helpers import send_help, setup_guild
from os import environ
from src.bot import MyBot
from discord.ext import commands

# Load Env Variables
TOKEN = environ['DISCORD_TOKEN']

# Load Bot and Utils
client = MyBot(command_prefix='rr', intents=Intents.all())


@client.event
async def on_error(event, *args):
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n')
        else:
            raise


@client.event
async def on_message(message):
    ctx = await client.get_context(message)
    await client.invoke(ctx)


@client.event
async def on_command_error(ctx: commands.Context, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('Você não tem permissão para fazer isso.')
    elif isinstance(error, commands.errors.MissingRequiredArgument):
        await send_help(ctx.channel, ctx.command)
    else:
        raise error


@client.event
async def on_member_join(member):
    try:
        await member.create_dm()
        await member.dm_channel.send(
            f'Hi {member.name}, welcome to my Discord server!')
    except HTTPException as err:
        with open('database/err.txt', 'a') as log:
            log.write(f'Error in member join, member: {member}\n')
            log.write(str(err))


@client.event
async def on_guild_join(guild):
    setup_guild(guild)

@client.ipc.route()
async def get_guild_count(data):
	return len(client.guilds)

@client.ipc.route()
async def get_guild_ids(data):
	return list(map(lambda g: g.id, client.guilds))


@client.ipc.route()
async def get_guild_info(data):
    data = await client.fetch_guild(data.guild_id)
    return {"name": data.name, "id": data.id, "icon_url": str(data.icon_url)}

if __name__ == '__main__':
    client.loop.create_task(app.run_task(host="0.0.0.0", debug=False))
    client.run(TOKEN)
