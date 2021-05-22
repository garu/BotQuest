"""testes para a reaction Infinite"""
import unittest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import MagicMock
from botquest.reactions import infinite


class TestInfinite(unittest.TestCase):
    """classe principal de testes"""
    def setUp(self):
        """configura o ambiente de testes"""
        self.msg = MagicMock(content='')
        self.bot = MagicMock()
        self.reaction = infinite.Reaction('infinite_test', self.bot)

    def _run_test(self):
        loop = asyncio.get_event_loop()
        task = loop.create_task(self.reaction.reaction(self.msg))
        res = loop.run_until_complete(task)
        return res

    def test_reaction_setup(self):
        """testa se a reaction inicia corretamente"""
        self.assertIs(type(self.reaction), infinite.Reaction)
        self.bot.db.query.assert_called_once()
        calls = self.bot.db.query.mock_calls
        self.assertRegex(
            calls[0][1][0],
            '^CREATE TABLE IF NOT EXISTS infinite',
            msg='table initialized'
        )

    def test_invalid_reaction(self):
        """testa que frases inválidas não são reconhecidas"""
        self.msg.content = 'infinity ou infinito da :elizabeth ou elizabeth:'
        self.bot.db.query.reset_mock()
        self._run_test()
        self.msg.channel.send.assert_not_called()
        self.bot.db.query.assert_not_called()

    def test_valid_reaction(self):
        """testa que frases válidas são processadas"""
        self.msg.content = 'BIOSHOCK INFINITE'
        self.bot.db.query.reset_mock()
        self.bot.db.query.return_value = None
        self._run_test()
        calls = self.bot.db.query.mock_calls
        self.assertEqual(len(calls), 2, msg='message triggered database lookup')
        self.assertRegex(calls[0][1][0], '^SELECT .+ FROM infinite', msg='looking for last entry')
        self.assertRegex(calls[1][1][0], '^INSERT INTO infinite', msg='inserting new entry')
        self.msg.channel.send.assert_called_once_with(
            ('Estamos a :zero: dias sem falar de Bioshock Infinite. Nosso recorde é '
             'de :zero: dias. :construction: <:elizabeth:590739833811632149> :construction:')
        )
        self.msg.channel.reset_mock()
        self.bot.db.query.return_value = {
            'guild_id': 123,
            'last_mention_date': str(datetime.today() - timedelta(days=123)),
            'record_days': 1,
            'last_vocalization': '1970-01-01 00:00:00'
        }
        self._run_test()
        self.msg.channel.send.assert_called_once_with(
            ('Estamos a :zero: dias sem falar de Bioshock Infinite. '
             'Nosso recorde é de :one::two::three: dias. '
             ':construction: <:elizabeth:590739833811632149> :construction:')
        )


if __name__ == '__main__':
    unittest.main()
