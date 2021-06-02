from discord import TextChannel, Guild
from os import chdir, path, mkdir
from pickle import dump as pdump
from json import dumps, dump as jdump


async def send_help(channel: TextChannel, func):
    await channel.send('``` ' + func.__doc__.strip() + '```')


def log(guild: Guild, command: str, log: str):
    chdir('database')
    direc = guild.name + '#' + str(guild.id)

    with open(path.join(direc, f'{command}.txt'), 'a+') as file:
        file.write(log + '\n\n')
    chdir('..')


def setup_guild(guild: Guild):
    _id = guild.name + '#' + str(guild.id)
    if not path.exists(f'database/{_id}'):
        mkdir(f'database/{_id}')
        with open(f'database/{_id}/agenda.pickle', 'wb') as file:
            pdump([], file)
        with open(f'database/{_id}/config.json', 'w') as file:
            jdump(dumps({'id': 0, 'notification_channel': guild.text_channels[0].id}), file)