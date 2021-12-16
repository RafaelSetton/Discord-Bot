"""
from: https://github.com/JakeCover/distest/blob/develop/example_tester.py
"""

from sys import argv
from distest import TestCollector, TestInterface
from distest.exceptions import ReactionDidNotMatchError
from distest import run_dtest_bot
from discord import Embed, Color, Message

# The tests themselves

test_collector = TestCollector()
ID_FOR_DELETION = None


@test_collector()
async def ping(interface: TestInterface.TestInterface):
    await interface.assert_reply_equals("rrping", "...")


@test_collector()
async def agadd(interface: TestInterface.TestInterface):
    msg = await interface.assert_reply_matches("rragadd Testando 20/10/2004 tarefa port valor=3",
                                               "'Testando' foi adicionado à agenda! (id=`d+`)")
    global ID_FOR_DELETION
    ID_FOR_DELETION = int(msg.content.split('`')[1])


@test_collector()
async def agdel(interface: TestInterface.TestInterface):
    await interface.assert_reply_equals("rragdel -1",
                                        "O evento `-1` não foi encontrado")
    await interface.assert_reply_equals(f"rragdel {ID_FOR_DELETION}", 'Testando foi deletado.')


@test_collector()
async def pokedex(interface: TestInterface.TestInterface):
    await interface.assert_reply_equals("rrpokedex naruto",
                                        "'naruto' não é um pokemon!")

    embed = Embed()
    embed.set_thumbnail(url="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/25.png")
    embed.set_footer(text="Por: Rafael Setton")
    embed.description = f"[Mais informações aqui!](https://pokeapi.co/api/v2/pokemon/pikachu)"
    embed.title = "Pikachu"

    embed.add_field(name="ID", value=f"#25")
    embed.add_field(name="Peso", value=f"Peso: 6.0kg")
    embed.add_field(name="Altura", value=f"Altura: 0.4m")
    embed.add_field(name="Tipos", value=f"electric")

    message = await interface.wait_for_reply("rrpokedex pikachu")
    await interface.assert_embed_equals(message, embed)


@test_collector()
async def dashboard(interface: TestInterface.TestInterface):
    embed = Embed()
    embed.color = Color.from_rgb(0, 255, 100)
    embed.set_footer(text="Rafael Setton",
                     icon_url="https://cdn.discordapp.com/avatars/415999616157220864/"
                              "1e2cccb14d5fb03a554172c9c75e5535.webp?size=1024")
    embed.title = "Dashboard"
    embed.url = "https://mybot.rafaelsetton.repl.co"

    message = await interface.wait_for_reply("rrdashboard")
    await interface.assert_embed_equals(message, embed)


@test_collector()
async def vote(interface: TestInterface.TestInterface):
    await interface.send_message(f"rrsetup_vote {' '.join([str(x) for x in range(9)])}")

    async def assert_voting(reply: Message):
        match = '\n'.join([f"{x}: {x}" for x in range(9)])
        await interface.assert_message_equals(reply, match)
        emojis = ["0\ufe0f\u20e3", "1\ufe0f\u20e3", "2\ufe0f\u20e3", "3\ufe0f\u20e3", "4\ufe0f\u20e3", "5\ufe0f\u20e3",
                  "6\ufe0f\u20e3", "7\ufe0f\u20e3", "8\ufe0f\u20e3"]
        reactions = [r.emoji for r in reply.reactions]
        for em in emojis:
            if em not in reactions:
                raise ReactionDidNotMatchError

    await interface.get_delayed_reply(5, assert_voting)


if __name__ == "__main__":
    run_dtest_bot(argv, test_collector)
