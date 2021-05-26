from discord import TextChannel, Guild
from os import mkdir, chdir, path

async def send_help(channel: TextChannel, func):
    await channel.send('``` ' + func.__doc__.strip() + '```')


def log(guild: Guild, command: str, log: str):
    chdir('logs')
    direc = guild.name + '#' + str(guild.id)
    try:
        mkdir(direc)
    except FileExistsError:
        pass
    with open(path.join(direc, f'{command}.txt'), 'a+') as file:
        file.write(log + '\n\n')
    chdir('..')
