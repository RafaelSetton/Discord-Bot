from discord.ext import commands
from src.helpers import send_help
from os import listdir
from datetime import date as realdate, timedelta
from pickle import load, dump
from prettytable import PrettyTable
from discord.utils import get

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


class Agenda:
    def __init__(self):
        if 'id.pickle' not in listdir('./database'):
            self.id_counter = dict()
            dump(self.id_counter, open('./database/id.pickle', 'wb'))
        else:
            self.id_counter = load(open('./database/id.pickle', 'rb'))

        self.__file_name = './database/agenda.pickle'
        if 'agenda.pickle' not in listdir('./database'):
            self.__agenda = dict()
            with open(self.__file_name, 'xb') as file:
                dump(self.__agenda, file)
        else:
            self.__agenda = load(open(self.__file_name, 'rb'))

    def __where(self, guild, **pairs):
        for evt in self.__agenda[guild]:
            for name, value in pairs.items():
                if getattr(evt, name) != value:
                    break
            else:
                yield evt

    @staticmethod
    def __pretty(lista):
        table = PrettyTable()
        table.field_names = ["ID", "Nome", "Data", "Tipo", "Disciplina"]

        for evt in lista:
            _id = evt.id
            name = evt.name
            date = evt.date
            _type = evt.type
            subj = evt.subject
            table.add_row([_id, name, date, _type, subj])
        return '```' + table.get_string() + '```'   

    def __deadline(self, guild, dl: realdate):
        for evt in self.__agenda[guild]:
            if evt.date <= dl:
                yield evt

    def save(self):
        dump(self.__agenda, open(self.__file_name, 'wb'))
        dump(self.id_counter, open('./database/id.pickle', 'wb'))

    def add(self, guild: str, name: str, date: str, _type: str, subject: str,
            **others):
        try:
            self.__agenda[guild]
        except KeyError:
            self.__agenda[guild] = []
            self.id_counter[guild] = 0
        evt = Event(self.id_counter[guild], name, date, _type, subject,
                    **others)
        self.__agenda[guild].append(evt)
        self.id_counter[guild] += 1
        self.save()

    def until(self, guild, days):
        return self.__pretty(
            self.__deadline(guild, realdate.today() + timedelta(days=days)))

    def find(self, guild, pairs):
        try:
            return self.__pretty(self.__where(guild, **pairs))
        except AttributeError:
            return "Ops! Esse identificador não existe"

    def week(self, guild: str):
        return self.until(guild, 7)

    def delete(self, guild: str, index: int) -> Event:
        evt = get(self.__agenda[guild], id=index)
        self.__agenda[guild].remove(evt)
        self.save()
        return evt

    def all(self, guild: str):
        return self.__pretty(self.__agenda[guild])

    def get(self, guild: str, index):
        return get(self.__agenda[guild], id=index)


class AgendaCommands(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.agenda_handler = Agenda()

    @commands.command(name='agenda')
    async def agenda(self, ctx: commands.Context, *args, **kwargs):
        """
        rragenda
        add  : Adiciona um evento
        show : Mostra os eventos
        del  : Deleta um evento 
        """
        args = list(args)
        for i in range(len(args)-1, -1, -1):
            try:
                k, v = args[i].split('=')
            except ValueError:
                pass
            else:
                kwargs[k] = v
                args.pop(i)
        try:
            param = args[0]
        except IndexError:
            raise commands.errors.MissingRequiredArgument(self.agenda)
        if param == "show":
            await self.show(ctx, *args[1:], **kwargs)
        elif param == "add":
            try:
                await self.add(ctx, *args[1:], **kwargs)
            except TypeError:
                await send_help(ctx.channel, self.add)
        elif param == "del":
            await self.delete(ctx, args[1])
        else:
            response = "Sintaxe Invalida"
            await ctx.send(response)


    async def add(self, ctx: commands.Context, name, date, _type, subject, **other):
        """
        add [nome] [data(DD/MM/YYYY)] [tipo do evento] [materia] [?outros (chave=valor)]
            Cria um evento com as opções definidas.
        """
        self.agenda_handler.add(ctx.guild.name, name, date, _type, subject, **other)

        response = f"'{name}' foi adicionado à agenda!"
        await ctx.send(response)


    async def show(self, ctx: commands.Context, *params, **kwargs):
        """
        show
        all           : Todos os eventos
        week          : Os eventos nos próximos 7 dias
        [type]=[value]: Filtrar eventos (Use quantos filtros quiser)
        time [days]   : Mostra os eventos nos próximos [*days*] dias
        [id]          : Mostra detalhes do evento com o id indicado
        """
        try:
            param = params[0]
        except IndexError:
            if not kwargs:
                await send_help(ctx.channel, self.show)
            else:
                response = self.agenda_handler.find(ctx.guild.name, kwargs)
        else:
            if param == "week":
                response = self.agenda_handler.week(ctx.guild.name)
            elif param == "all":
                response = self.agenda_handler.all(ctx.guild.name)
            elif param == "time":
                response = self.agenda_handler.until(ctx.guild.name, int(params[1]))
            elif param.isdigit():
                response = self.agenda_handler.get(ctx.guild.name, int(param))
            else:
                response = "Sintaxe Invalida"
        finally:
            await ctx.send(response)


    async def delete(self, ctx: commands.Context, _id):
        if ctx.author.permissions_in(ctx.channel).manage_messages:
            try:
                deletado = self.agenda_handler.delete(ctx.guild.name, int(_id))
            except ValueError:
                await ctx.send(f"O evento `{_id}` não foi encontrado")
            else:
                await ctx.send(deletado.name + ' foi deletado.')
        else:
            raise commands.errors.MissingPermissions(['manage_messages'])


def setup(client):
    client.add_cog(AgendaCommands(client))