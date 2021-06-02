"""
from: https://github.com/JakeCover/distest/blob/develop/example_tester.py
"""

from sys import argv
from distest import TestCollector, TestInterface
from distest import run_dtest_bot

# The tests themselves

test_collector = TestCollector()
ID_FOR_DELETION = None


@test_collector()
async def ping(interface: TestInterface.TestInterface):
    await interface.assert_reply_equals("rrping", "...")
    

@test_collector()
async def agadd(interface: TestInterface.TestInterface):
    msg = await interface.assert_reply_matches("rragadd Testando 20/10/2004 tarefa port valor=3", "'Testando' foi adicionado à agenda! \(id=`\d+`\)")
    global ID_FOR_DELETION
    ID_FOR_DELETION = int(msg.content.split('`')[1])


@test_collector()
async def agdel(interface: TestInterface.TestInterface):
    await interface.assert_reply_equals("rragdel -1", 
    "O evento `-1` não foi encontrado")
    await interface.assert_reply_equals(f"rragdel {ID_FOR_DELETION}", 'Testando foi deletado.')


# Actually run the bot

if __name__ == "__main__":
    run_dtest_bot(argv, test_collector)

    