import os
import discord
from discord.ext import commands
from app.flask_app import keep_alive
from src.helpers import send_help
from discord.errors import HTTPException

# Load Env Variables
TOKEN = os.environ['DISCORD_TOKEN']
print("READY")

# Load Bot and Utils
intents = discord.Intents.all()
client = commands.Bot(command_prefix='rr', intents=intents)

client.load_extension('src.pokemon')
client.load_extension('src.agenda')
client.load_extension('src.setup_vote')



@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    print(f'Connected to the following guilds: {client.guilds}')


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
        if ctx.command.name == 'del':
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
        with open('err.log', 'a') as log:
            log.write(f'Error in member join, member: {member}\n')
            log.write(str(err))


if __name__ == '__main__':
    keep_alive()
    client.run(TOKEN)
