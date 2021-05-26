from discord import TextChannel


async def send_help(channel: TextChannel, func):
    await channel.send('``` ' + func.__doc__.strip() + '```')