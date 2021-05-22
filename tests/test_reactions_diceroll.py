"""testes para a reaction Diceroll"""
import asyncio
import random
import re
import unittest
from unittest.mock import MagicMock
from botquest.reactions import diceroll


class TestDiceroll(unittest.TestCase):
    """classe principal de testes"""
    def setUp(self):
        """configura o ambiente de testes"""
        self.msg = MagicMock(content='')
        bot = MagicMock()
        self.reaction = diceroll.Reaction('diceroll_test', bot)

    def _run_test(self):
        loop = asyncio.get_event_loop()
        task = loop.create_task(self.reaction.reaction(self.msg))
        res = loop.run_until_complete(task)
        return res

    def test_no_reaction(self):
        """testa comportamento para mensagens inválidas"""
        self._run_test()
        self.msg.channel.send.assert_not_called()

        self.msg.content = '!roll'
        self._run_test()
        self.msg.channel.send.assert_not_called()

        self.msg.content = '!roll something'
        self._run_test()
        self.msg.channel.send.assert_not_called()

        self.msg.content = '!roll 1d6 meep'
        self._run_test()
        self.msg.channel.send.assert_not_called()

    def test_reaction(self):
        """testa comportamento para mensagens válidas"""
        re_dice = r'\[(?:\*\*)?\d+(?:\*\*)?\]'  # [N] ou [**N**]
        re_mod = r'(?:([+\-]\d+) )'  # +3, -1, etc.
        re_total = r'\*\*(\-?\d+)\*\*'  # **X**
        re_expected = re.compile(fr'^((?:{re_dice} )+){re_mod}?= {re_total}$')

        for _ in range(500):
            dice_count = random.randint(1, 5)
            dice_size = random.randint(1, 20)
            dice_mod = random.randint(-3, +3)
            self.msg.channel.reset_mock()
            self.msg.content = f'!roll {dice_count}d{dice_size} '
            if dice_mod != 0:
                self.msg.content += ('+' if dice_mod >= 0 else '') + str(dice_mod)

            self._run_test()
            self.msg.channel.send.assert_called_once()
            calls = self.msg.channel.mock_calls
            res = calls[0][1][0]
            self.assertIsNotNone(res, msg=f'"{self.msg.content}" must return something')

            match = re_expected.search(res)
            self.assertTrue(match, msg=f'answer "{res}" for "{self.msg.content}" looks valid')

            matched_groups = match.groups(0)
            matched_rolls = [int(n) for n in re.split(r'\D+', matched_groups[0]) if n.isdigit()]
            matched_modifier = int(matched_groups[1])
            matched_result = int(matched_groups[2])

            self.assertEqual(len(matched_rolls), dice_count, msg='right amount of dice')
            self.assertEqual(
                sum(matched_rolls) + matched_modifier,
                matched_result,
                msg='dice total looks right')


if __name__ == '__main__':
    unittest.main()
