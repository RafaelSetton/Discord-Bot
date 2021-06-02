from discord.ext import tasks, commands
from time import sleep
from src.agenda import AgendaModel, Agenda
from datetime import datetime, time, timedelta
from json import dumps, dump, loads, load

class Notifier(commands.Cog):
    empty = """```+----+------+------+------+------------+
| ID | Nome | Data | Tipo | Disciplina |
+----+------+------+------+------------+
+----+------+------+------+------------+```"""

    def __init__(self, client):
        self.client = client
        #self.agenda_notifier.start()

    def cog_unload(self):
        self.agenda_notifier.cancel()

    @commands.command(name="notify_here")
    @commands.has_permissions(administrator=True)
    async def notify_here(self, ctx: commands.Context):
        with open(f"database/{Agenda.get_identifier(ctx.guild)}/config.json", 'r+') as file:
            config = loads(load(file))
            config['notification_channel'] = ctx.channel.id
            file.seek(0)
            dump(dumps(config), file)
        await ctx.send("Canal de notificações definido para " + ctx.channel.mention)

    @staticmethod
    def seconds_until(hours, minutes):
        given_time = time(hours, minutes)
        now = datetime.now()
        future_exec = datetime.combine(now, given_time)
        if (future_exec - now).days < 0: 
            future_exec = datetime.combine(now + timedelta(days=1), given_time)

        return (future_exec - now).total_seconds()

    @tasks.loop(hours=24)
    async def agenda_notifier(self):
        #sleep(self.seconds_until(12, 0)) 
        print('daily')
        for guild in self.client.guilds:
            today = AgendaModel.until(Agenda.get_identifier(guild), 1)
            if today != self.empty:
                config = loads(load(open(f"database/{Agenda.get_identifier(guild)}/config.json")))
                await guild.get_channel(config['notification_channel']).send(str(today))

    @agenda_notifier.before_loop
    async def before_agenda_notifier(self):
        print('waiting...')
        await self.client.wait_until_ready()


def setup(client):
    client.add_cog(Notifier(client))