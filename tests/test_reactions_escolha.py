"""testes para a reaction Escolha"""
import asyncio
import unittest
from unittest.mock import MagicMock
from botquest.reactions import escolha


class TestEscolha(unittest.TestCase):
    """classe principal de testes"""

    def setUp(self):
        """configura o ambiente de testes"""
        self.msg = MagicMock(content='')
        bot = MagicMock()
        self.reaction = escolha.Reaction('escolha_test', bot)

    def _run_test(self):
        loop = asyncio.get_event_loop()
        task = loop.create_task(self.reaction.reaction(self.msg))
        res = loop.run_until_complete(task)
        return res

    def test_no_reaction(self):
        """testa comportamento para mensagens inválidas"""
        self._run_test()
        self.msg.channel.send.assert_not_called()

        self.msg.content = '!foo'
        self._run_test()
        self.msg.channel.send.assert_not_called()

        self.msg.content = '!escolha x'
        self._run_test()
        self.msg.channel.send.assert_called_once_with('Não encontrei as opções (separe com "ou")')

    def test_reaction(self):
        """testa comportamento para mensagens válidas"""
        (count_a, count_b) = (0, 0)
        self.msg.content = '!escolha A e B ou C'
        for _ in range(50):
            self.msg.channel.reset_mock()
            self._run_test()
            self.msg.channel.send.assert_called_once()
            calls = self.msg.channel.mock_calls
            res = calls[0][1][0]

            self.assertRegex(res, r'A e B|C')
            if res == 'A e B':
                count_a += 1
            elif res == 'C':
                count_b += 1
            else:
                raise Exception('invalido')
        self.assertTrue(count_a > 0)
        self.assertTrue(count_b > 0)

    def test_reaction_with_odds(self):
        """testa comportamento para escolhas com pesos diferentes"""
        self.msg.content = '!escolha X^10 ou  Y^3  ou Z'
        (count_x, count_y, count_z) = (0, 0, 0)
        for _ in range(1000):
            self.msg.channel.reset_mock()
            self._run_test()
            self.msg.channel.send.assert_called_once()
            calls = self.msg.channel.mock_calls
            res = calls[0][1][0]

            self.assertRegex(res, r'X|Y|Z')
            if res == 'X':
                count_x += 1
            elif res == 'Y':
                count_y += 1
            else:
                count_z += 1
        self.assertTrue(count_x > count_y)
        self.assertTrue(count_y > count_z)
        self.assertTrue(count_z > 0)


if __name__ == '__main__':
    unittest.main()
