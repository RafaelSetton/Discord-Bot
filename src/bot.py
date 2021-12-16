from discord.ext import commands, ipc
from src.helpers import setup_guild, send_help
from discord.errors import HTTPException
from datetime import datetime


class MyBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ipc = ipc.Server(self, host="0.0.0.0", secret_key="RafaelSetton")
        self.load()
    
    def load(self):
        self.load_extension('src.pokemon')
        self.load_extension('src.agenda')
        self.load_extension('src.setup_vote')
        self.load_extension('src.nick')
        self.load_extension('src.notifier')
        self.load_extension('src.utils')
        
    def run(self, token, **kwargs):
        self.ipc.start()
        super().run(token, **kwargs)

    # Events
    async def on_ready(self):
        print(f'{self.user} conectou ao Discord!')
        for guild in self.guilds:
            setup_guild(guild)    

    async def on_error(self, event, *args):
        with open('err.log', 'a') as f:
            if event == 'on_message':
                f.write(f'Unhandled message: {args[0]}\n')
            else:
                raise

    async def on_message(self, message):
        ctx = await self.get_context(message)
        await self.invoke(ctx)

    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.errors.CheckFailure):
            await ctx.send('Você não tem permissão para fazer isso.')
        elif isinstance(error, commands.errors.MissingRequiredArgument):
            await send_help(ctx.channel, ctx.command)
        else:
            now = datetime.now()
            with open('err.log', 'a+') as log:
                log.write(f"({now.strftime('%Y/%m/%d - %H:%M:%S')}) em {ctx.guild.name}")
            raise error

    @staticmethod
    async def on_member_join(member):
        try:
            await member.create_dm()
            await member.dm_channel.send(
                f'Hi {member.name}, welcome to my Discord server!')
        except HTTPException as err:
            with open('database/err.txt', 'a') as log:
                log.write(f'Error in member join, member: {member}\n')
                log.write(str(err))

    @staticmethod
    async def on_guild_join(guild):
        setup_guild(guild)

    @staticmethod
    async def on_ipc_ready():
        print(f'Servidor IPC pronto!') 

    @staticmethod
    async def on_ipc_error(endpoint, error):
        print(endpoint, 'raised', error)
