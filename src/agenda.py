from discord.ext import commands
from src.helpers import send_help
from datetime import date as realdate, timedelta
from pickle import load, dump
from json import loads, dumps, load as jload, dump as jdump
from prettytable import PrettyTable
from discord.utils import get
from discord import Guild


class Event:
    def __init__(self, _id: int, name: str, date: str, _type: str,
                 subject: str, **others):
        self.id = _id
        self.name = name
        self.tipo = _type
        self.subject = subject
        self.__dict__.update(others)

        date = date.split('/')
        if len(date) == 2:
            d, m = date
            y = realdate.year
        else:
            d, m, y = date
        self.date = realdate(int(y), int(m), int(d))

    def __repr__(self):
        table = PrettyTable()
        table.field_names = self.__dict__.keys()
        table.add_row(self.__dict__.values())
        return '```' + table.get_string() + '```'


class AgendaModel:
    @staticmethod
    def agenda(guild):
        return load(open(f"database/{guild}/agenda.pickle", 'rb'))

    @staticmethod
    def id(guild):
        return loads(jload(open(f"database/{guild}/config.json")))["id"]

    @staticmethod
    def save(guild, agenda=None, _id=None):
        if agenda is not None:
            dump(agenda, open(f"database/{guild}/agenda.pickle", 'wb'))
        if _id is not None:
            with open(f"database/{guild}/config.json", 'r+') as file:
                obj = loads(jload(file))
                obj['id'] = _id
                file.seek(0)
                jdump(dumps(obj), file)

    @staticmethod
    def __pretty(lista):
        table = PrettyTable()
        table.field_names = ["ID", "Nome", "Data", "Tipo", "Disciplina"]

        for evt in lista:
            _id = evt.id
            name = evt.name
            data = evt.date
            tipo = evt.tipo
            subj = evt.subject
            table.add_row([_id, name, data, tipo, subj])
        return '```\n' + table.get_string() + '```'

    @classmethod
    def __where(cls, guild, **pairs):
        for evt in cls.agenda(guild):
            for name, value in pairs.items():
                if getattr(evt, name) != value:
                    break
            else:
                yield evt

    @classmethod
    def __deadline(cls, guild, dl: realdate):
        for evt in cls.agenda(guild):
            if evt.date <= dl:
                yield evt

    @classmethod
    def until(cls, guild, days):
        return cls.__pretty(
            cls.__deadline(guild, realdate.today() + timedelta(days=days)))

    @classmethod
    def find(cls, guild, pairs):
        try:
            return cls.__pretty(cls.__where(guild, **pairs))
        except AttributeError:
            return "Ops! Esse identificador não existe"

    @classmethod
    def week(cls, guild: str):
        return cls.until(guild, 7)

    @classmethod
    def all(cls, guild: str):
        return cls.__pretty(cls.agenda(guild))

    @classmethod
    def get(cls, guild: str, index):
        return get(cls.agenda(guild), id=index)

    @classmethod
    def add(cls, guild: str, name: str, date: str, _type: str, subject: str, **others):
        _id = cls.id(guild)
        evt = Event(_id, name, date, _type, subject,
                    **others)
        new = cls.agenda(guild) + [evt]
        cls.save(guild, new, _id + 1)
        return evt

    @classmethod
    def delete(cls, guild: str, index: int) -> Event:
        agenda = cls.agenda(guild)
        evt = get(agenda, id=index)
        agenda.remove(evt)
        cls.save(guild, agenda)
        return evt


class Agenda(commands.Cog):
    def __init__(self, client):
        self.client = client

    @staticmethod
    def get_identifier(guild: Guild):
        return guild.name + '#' + str(guild.id)

    @commands.command(name='agadd', help="Adiciona um evento à agenda")
    @commands.has_permissions(manage_messages=True)
    async def add(self, ctx: commands.Context, name, date, _type, subject, **other):
        """
        add [nome] [data(DD/MM/YYYY)] [tipo do evento] [materia] [?outros (chave=valor)]
            Cria um evento com as opções definidas.
        """
        evt = AgendaModel.add(self.get_identifier(ctx.guild), name, date, _type, subject, **other)

        response = f"'{name}' foi adicionado à agenda! (id=`{evt.id}`)"
        await ctx.send(response)

    @commands.command(name='agshow', help="Lista os eventos. Para mais informações: rrhelp agshow \n\n"
                                          "all           : Todos os eventos\n"
                                          "week          : Os eventos nos próximos 7 dias\n"
                                          "[key]=[value]: Filtrar eventos (Use quantos filtros quiser)\n"
                                          "time [d]   : Mostra os eventos nos próximos [d] dias\n"
                                          "[id]          : Mostra detalhes do evento com o id indicado")
    async def show(self, ctx: commands.Context, *params, **kwargs):
        try:
            exec(f"kwargs.update({','.join(p for p in params if '=' in p)})")
        except NameError:
            await ctx.send("Valores devem estar entre aspas simples (')")
            return
        params = list(filter(lambda p: '=' not in p, params))
        response = ""
        try:
            param = params[0]
        except IndexError:
            if not kwargs:
                await send_help(ctx.channel, self.show)
                return
            else:
                response = AgendaModel.find(self.get_identifier(ctx.guild), kwargs)
        else:
            if param == "week":
                response = AgendaModel.week(self.get_identifier(ctx.guild))
            elif param == "all":
                response = AgendaModel.all(self.get_identifier(ctx.guild))
            elif param == "time":
                response = AgendaModel.until(self.get_identifier(ctx.guild), int(params[1]))
            elif param.isdigit():
                response = AgendaModel.get(self.get_identifier(ctx.guild), int(param))
            else:
                response = "Sintaxe Invalida"
        finally:
            await ctx.send(response)

    @commands.command(name='agdel', help="Deleta o evento com o id selecionado")
    @commands.has_permissions(manage_messages=True)
    async def delete(self, ctx: commands.Context, _id):
        try:
            deletado = AgendaModel.delete(self.get_identifier(ctx.guild), int(_id))
        except ValueError:
            await ctx.send(f"O evento `{_id}` não foi encontrado")
        else:
            await ctx.send(deletado.name + ' foi deletado.')


def setup(client):
    client.add_cog(Agenda(client))
