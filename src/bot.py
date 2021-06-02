from discord.ext import commands, ipc
from src.helpers import setup_guild

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
    
    async def on_ready(self):
        print(f'{self.user} conectou ao Discord!')
        for guild in self.guilds:
            setup_guild(guild)    

    async def on_ipc_ready(self):
        print(f'Servidor IPC pronto!') 

    async def on_ipc_error(self, endpoint, error):
        print(endpoint, 'raised', error)

    def run(self, token, **kwargs):
        self.ipc.start()
        super().run(token, **kwargs)

