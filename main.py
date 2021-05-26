from discord import Intents
from discord.ext import commands
from discord.errors import HTTPException
from app.flask_app import keep_alive
from src.helpers import send_help
from os import environ

# Load Env Variables
TOKEN = environ['DISCORD_TOKEN']

# Load Bot and Utils
client = commands.Bot(command_prefix='rr', intents=Intents.all())

client.load_extension('src.pokemon')
client.load_extension('src.agenda')
client.load_extension('src.setup_vote')
client.load_extension('src.nick')


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    print(f'Connected to the following guilds: {list(map(lambda g: g.name, client.guilds))}')


@client.event
async def on_error(event, *args):
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n')
        else:
            raise


@client.event
async def on_command_error(ctx: commands.Context, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('Você não tem permissão para fazer isso.')
    elif isinstance(error, commands.errors.MissingRequiredArgument):
        await send_help(ctx.command)
    else:
        raise error


@client.event
async def on_member_join(member):
    try:
        await member.create_dm()
        await member.dm_channel.send(
            f'Hi {member.name}, welcome to my Discord server!'
        )
    except HTTPException as err:
        with open('logs/err.txt', 'a') as log:
            log.write(f'Error in member join, member: {member}\n')
            log.write(str(err))


if __name__ == '__main__':
    keep_alive()
    client.run(TOKEN)
